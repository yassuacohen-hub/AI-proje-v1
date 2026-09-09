#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Merged JSONL -> companies BULK UPSERT (hizli ingest).

Sorun: uzak DB roundtrip ~8 sn; satir satir 2 sorgu = saatler.
Cozum:
  1) Tek SELECT ile mevcut (unvan -> company_id) haritasi
  2) Yeni kayitlari tek cok satirli INSERT . ON CONFLICT (tax_number) DO NOTHING
  3) Eslesenleri tek cok satirli UPDATE . FROM (VALUES ..) ile doldur

Paralel calisan baska ajan varsa (kalite recalc) deadlock riski olur;
oturum boyunca DB bos iken calsitirin.
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import psycopg2  # noqa: E402  (yalnizca error tipleri icin import edildi)
from sqlalchemy import text  # noqa: E402
from company_master.db.connection import get_engine  # noqa: E402

INPUT_FILE = ROOT / "data" / "merged" / "multi_osb_merged.jsonl"
BATCH = 250


def oku() -> list[dict]:
    kayitlar: list[dict] = []
    for ln in INPUT_FILE.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            continue
        rec = json.loads(ln)
        unvan = (rec.get("unvan") or "").strip()[:255]
        if not unvan:
            continue
        tel = rec.get("telefonlar") or []
        eml = rec.get("emailler") or []
        vkn = rec.get("vergi_no")
        kayitlar.append({
            "unvan": unvan,
            "unvan_key": unvan.lower().strip(),
            "vkn": str(vkn) if (vkn and len(str(vkn)) == 10) else None,
            "nace": (rec.get("nace_kod") or "")[:10] or None,
            "phone": (str(tel[0])[:30] if tel else None),
            "email": (str(eml[0])[:120] if eml else None),
            "web": (rec.get("web_sitesi") or "")[:255] or None,
            "adres": ((rec.get("adres") or "").strip()[:500] or None),
        })
    return kayitlar


def coklu_insert(conn, kayitlar, adres_var: bool) -> None:
    """Cok satirli INSERT ... ON CONFLICT (tax_number) DO NOTHING (tek sorgu)."""
    valf = ",".join(
        "(:c%d, :t%d, :t%d, :v%d, :n%d, :n%d, :ph%d, :em%d, :w%d, :w%d, TRUE, TRUE%s)"
        % (i, i, i, i, i, i, i, i, i, i, (", :a%d" % i) if adres_var else "")
        for i in range(len(kayitlar))
    )
    cols = (
        "company_id, legal_name, trade_name, tax_number, nace_code, "
        "nace_validity, primary_phone, primary_email, website_domain, "
        "web_sitesi, is_ankara, is_osb_member"
    )
    if adres_var:
        cols += ", adres"
    sql = f"INSERT INTO companies ({cols}) VALUES {valf} " \
          "ON CONFLICT (tax_number) DO NOTHING"
    p: dict = {}
    for i, r in enumerate(kayitlar):
        p.update({
            f"c{i}": r["cid"], f"t{i}": r["unvan"], f"v{i}": r["vkn"],
            f"n{i}": r["nace"], f"ph{i}": r["phone"], f"em{i}": r["email"],
            f"w{i}": r["web"],
        })
        if adres_var:
            p[f"a{i}"] = r["adres"]
    conn.execute(text(sql), p)


def coklu_update(conn, kayitlar, adres_var: bool) -> None:
    """Cok satirli UPDATE ... FROM (VALUES ...) (tek sorgu)."""
    valf = ",".join(
        "(:c%d, :v%d, :n%d, :ph%d, :em%d, :w%d%s)"
        % (i, i, i, i, i, i, (", :a%d" % i) if adres_var else "")
        for i in range(len(kayitlar))
    )
    p: dict = {}
    for i, r in enumerate(kayitlar):
        p.update({
            f"c{i}": r["cid"], f"v{i}": r["vkn"], f"n{i}": r["nace"],
            f"ph{i}": r["phone"], f"em{i}": r["email"], f"w{i}": r["web"],
        })
        if adres_var:
            p[f"a{i}"] = r["adres"]
    if adres_var:
        sql = (
            "UPDATE companies SET "
            "tax_number = COALESCE(tax_number, v.vkn), "
            "nace_code = COALESCE(nace_code, v.nace), "
            "nace_validity = COALESCE(nace_validity, v.nace), "
            "primary_phone = COALESCE(primary_phone, v.phone), "
            "primary_email = COALESCE(primary_email, v.email), "
            "web_sitesi = COALESCE(web_sitesi, v.web), "
            "website_domain = COALESCE(website_domain, v.web), "
            "adres = COALESCE(adres, v.adres), updated_at = NOW() "
            f"FROM (VALUES {valf}) AS v(cid, vkn, nace, phone, email, web, adres) "
            "WHERE companies.company_id = v.cid::uuid"
        )
    else:
        sql = (
            "UPDATE companies SET "
            "tax_number = COALESCE(tax_number, v.vkn), "
            "nace_code = COALESCE(nace_code, v.nace), "
            "nace_validity = COALESCE(nace_validity, v.nace), "
            "primary_phone = COALESCE(primary_phone, v.phone), "
            "primary_email = COALESCE(primary_email, v.email), "
            "web_sitesi = COALESCE(web_sitesi, v.web), "
            "website_domain = COALESCE(website_domain, v.web), "
            "updated_at = NOW() "
            f"FROM (VALUES {valf}) AS v(cid, vkn, nace, phone, email, web) "
            "WHERE companies.company_id = v.cid::uuid"
        )
    conn.execute(text(sql), p)


def main() -> None:
    if not INPUT_FILE.exists():
        print(f"HATA: {INPUT_FILE} yok")
        sys.exit(1)

    kayitlar = oku()
    print(f"Girdi: {len(kayitlar)} kayit", flush=True)

    eng = get_engine()
    with eng.begin() as conn:
        conn.execute(text("SET LOCAL statement_timeout = '300s'"))

        adres_var = conn.execute(text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name='companies' AND column_name='adres'"
        )).fetchone() is not None

        # --- 1) mevcut unvan haritasi (tek sorgu) ---
        unvan_map = {
            r[1]: r[0] for r in conn.execute(text(
                "SELECT company_id, "
                "LOWER(TRIM(COALESCE(trade_name, legal_name))) FROM companies"
            )).fetchall()
        }
        print(f"Mevcut unvan haritasi: {len(unvan_map)}", flush=True)

        upd: list[dict] = []
        ins: list[dict] = []
        for k in kayitlar:
            cid = unvan_map.get(k["unvan_key"])
            if cid:
                upd.append({**k, "cid": cid})
            else:
                ins.append({**k, "cid": str(uuid.uuid4())})
        print(f"Eklenecek: {len(ins)} | Guncellenecek: {len(upd)}", flush=True)

        # --- 2) INSERT: cok satirli, ON CONFLICT tax_number DO NOTHING ---
        yeni = 0
        for i in range(0, len(ins), BATCH):
            parca = ins[i:i + BATCH]
            coklu_insert(conn, parca, adres_var)
            yeni += len(parca)
            print(f"  insert ilerleme: {yeni}/{len(ins)}", flush=True)

        # --- 3) UPDATE: EXISTS kayitlari eksik alanlara gore doldur ---
        gunc = 0
        for i in range(0, len(upd), BATCH):
            parca = upd[i:i + BATCH]
            coklu_update(conn, parca, adres_var)
            gunc += len(parca)
            print(f"  update ilerleme: {gunc}/{len(upd)}", flush=True)

    print(f"\nBULK INGEST TAMAM: {len(ins)} eklendi, {len(upd)} guncellendi",
          flush=True)


if __name__ == "__main__":
    main()