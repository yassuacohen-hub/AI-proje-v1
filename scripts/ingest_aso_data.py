#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ASO (Ankara Sanayi Odası) verilerini DB'ye yazar.

ASO data format (data/aso/aso_full.jsonl):
    unvan, ticaretSicilNo, detailToken, naceKod, naceDetay,
    meslekGrubu, adres, eposta, telefonlar, yetkililer

Bu script firmaları companies tablosunda isim eşleştirmesi yaparak
günceller; eşleşme yoksa yeni kayıt olarak ekler.
"""
from __future__ import annotations
import json, logging, re, sys
from pathlib import Path
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_engine

ASO_PATH = ROOT / "data" / "aso" / "aso_full.jsonl"
LOG_PATH = ROOT / "logs" / "ingest_aso.log"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()])
log = logging.getLogger("ingest_aso")

VKN_PATTERN = re.compile(r"\b(\d{10,11})\b")


def extract_vkn(unvan: str | None) -> str | None:
    if not unvan:
        return None
    m = VKN_PATTERN.search(unvan)
    return m.group(1) if m else None


def clean_unvan(unvan: str | None) -> str | None:
    if not unvan:
        return None
    prefix = "(İFLAS NEDENİYLE) TASFİYE HALİNDE "
    if unvan.startswith(prefix):
        unvan = unvan[len(prefix):]
    return unvan.strip()


def main() -> int:
    if not ASO_PATH.exists():
        log.error("Dosya yok: %s", ASO_PATH)
        return 1
    records = []
    with open(ASO_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    log.warning("Geçersiz JSON satırı atlandı")

    log.info("Toplam ASO kaydı: %d", len(records))
    stats = {"total": len(records), "matched": 0, "inserted": 0,
             "adres_written": 0, "vkn_extracted": 0,
             "no_match": 0, "errors": 0}
    engine = get_engine()
    batch_size = 50
    conn = engine.connect()
    try:
        for i, rec in enumerate(records):
            raw_unvan = (rec.get("unvan") or "").strip()
            unvan = clean_unvan(raw_unvan)
            if not unvan:
                stats["no_match"] += 1
                continue
            try:
                row = conn.execute(
                    text("SELECT company_id, source_record_id FROM companies "
                         "WHERE LOWER(TRIM(legal_name)) = LOWER(:n) LIMIT 1"),
                    {"n": unvan}).first()
                if row:
                    company_id, source_record_id = row[0], row[1]
                    stats["matched"] += 1
                else:
                    fuzzy = conn.execute(
                        text("SELECT company_id, source_record_id FROM companies "
                             "WHERE LOWER(legal_name) LIKE LOWER(:pattern) LIMIT 1"),
                        {"pattern": "%" + unvan[:20] + "%"}).first()
                    if fuzzy:
                        company_id, source_record_id = fuzzy[0], fuzzy[1]
                        stats["matched"] += 1
                    else:
                        # Insert new company
                        phone_list = rec.get("telefonlar") or []
                        phone = None
                        if phone_list:
                            first = phone_list[0]
                            if isinstance(first, dict):
                                phone = first.get("no")
                            elif isinstance(first, str):
                                phone = first
                        result = conn.execute(
                            text("INSERT INTO companies (legal_name, trade_name, "
                                 "primary_phone, primary_email, is_ankara, "
                                 "is_osb_member, data_quality_score, "
                                 "created_at, updated_at) "
                                 "VALUES (:name, :name, :phone, :email, TRUE, TRUE, 0, NOW(), NOW()) "
                                 "RETURNING company_id"),
                            {"name": unvan, "phone": phone,
                             "email": rec.get("eposta")})
                        company_id = result.first()[0]
                        sr_result = conn.execute(
                            text("INSERT INTO source_records (source_id, external_id, "
                                 "raw_name, raw_address, raw_phone, raw_email, "
                                 "raw_website, raw_tax_number, raw_nace, raw_payload) "
                                 "VALUES ((SELECT source_id FROM sources WHERE source_name = 'aso.org.tr' LIMIT 1), "
                                 ":ext, :name, :adres, :phone, :email, NULL, :vkn, :nace, "
                                 "(:payload)::jsonb) RETURNING source_record_id"),
                            {"ext": rec.get("ticaretSicilNo"), "name": unvan,
                             "adres": (rec.get("adres") or "").strip() or None,
                             "phone": phone, "email": rec.get("eposta"),
                             "vkn": rec.get("ticaretSicilNo"),
                             "nace": rec.get("naceKod"),
                             "payload": json.dumps({"sektor": rec.get("meslekGrubu"),
                                 "naceKod": rec.get("naceKod"),
                                 "naceDetay": rec.get("naceDetay"),
                                 "meslekGrubu": rec.get("meslekGrubu"),
                                 "ticaretSicilNo": rec.get("ticaretSicilNo"),
                                 "kaynak": "aso.org.tr"}, ensure_ascii=False)})
                        source_record_id = sr_result.first()[0]
                        conn.execute(
                            text("UPDATE companies SET source_record_id = :sid WHERE company_id = :cid"),
                            {"sid": source_record_id, "cid": company_id})
                        stats["inserted"] += 1
                    stats["matched"] += 1

                phone_list = rec.get("telefonlar") or []
                phone = None
                if phone_list:
                    first = phone_list[0]
                    if isinstance(first, dict):
                        phone = first.get("no")
                    elif isinstance(first, str):
                        phone = first
                email = rec.get("eposta")
                adres = (rec.get("adres") or "").strip() or None
                vkn = extract_vkn(raw_unvan) or rec.get("ticaretSicilNo")

                if vkn:
                    conn.execute(
                        text("UPDATE companies SET vergi_no = COALESCE(vergi_no, :vkn) "
                             "WHERE company_id = :cid AND (vergi_no IS NULL OR vergi_no = '')"),
                        {"vkn": vkn, "cid": company_id})
                    stats["vkn_extracted"] += 1
                if phone:
                    conn.execute(
                        text("UPDATE companies SET primary_phone = COALESCE(primary_phone, :phone) "
                             "WHERE company_id = :cid"),
                        {"phone": phone, "cid": company_id})
                if email:
                    conn.execute(
                        text("UPDATE companies SET primary_email = COALESCE(primary_email, :email) "
                             "WHERE company_id = :cid"),
                        {"email": email, "cid": company_id})
                if adres:
                    conn.execute(
                        text("UPDATE companies SET description = COALESCE(description, :adres) "
                             "WHERE company_id = :cid"),
                        {"adres": adres, "cid": company_id})
                    if source_record_id:
                        conn.execute(
                            text("UPDATE source_records SET raw_payload = "
                                 "raw_payload || (:payload)::jsonb, "
                                 "raw_address = COALESCE(:adres, raw_address), "
                                 "raw_phone = COALESCE(:phone, raw_phone), "
                                 "raw_email = COALESCE(:email, raw_email) "
                                 "WHERE source_record_id = :sid"),
                            {"payload": json.dumps({"adres": adres,
                                 "naceKod": rec.get("naceKod"),
                                 "naceDetay": rec.get("naceDetay"),
                                 "meslekGrubu": rec.get("meslekGrubu"),
                                 "ticaretSicilNo": rec.get("ticaretSicilNo"),
                                 "kaynak": "aso.org.tr"}, ensure_ascii=False),
                             "adres": adres, "phone": phone, "email": email,
                             "sid": source_record_id})
                    stats["adres_written"] += 1
            except Exception as e:
                stats["errors"] += 1
                log.exception("Kayit hatasi (%s): %s", unvan, e)
                conn.rollback()
            if (i + 1) % batch_size == 0:
                conn.commit()
                log.info("Batch: %d/%d | matched=%d inserted=%d errors=%d",
                         i + 1, len(records), stats["matched"], stats["inserted"], stats["errors"])
        conn.commit()
    except Exception as e:
        log.exception("Genel hatay: %s", e)
        try:
            conn.rollback()
        except:
            pass
    finally:
        if conn:
            conn.close()
    log.info("SONUC: %s", json.dumps(stats, ensure_ascii=False))
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
