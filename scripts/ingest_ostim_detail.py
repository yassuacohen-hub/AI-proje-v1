#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""OSTIM detay scraper ciktisini DB ye yazar."""
from __future__ import annotations
import json, logging, re, sys
from pathlib import Path
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_engine

DETAY_PATH = ROOT / "data" / "ostim" / "firmalar_detayli.jsonl"
LOG_PATH = ROOT / "logs" / "ingest_ostim_detail.log"
GENERIC_OSB_URL = "https://www.ostimonline.com/Home/OstimMain"
WEB_BLOCKLIST = (
    "ostimradyo.com",
    "ostim.org.tr",
    "ostimonline.com",
    "isim.org.tr",
    "osp.com.tr",
    "facebook.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "instagram.com",
    "youtube.com",
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()])
log = logging.getLogger("ingest_ostim_detail")

VKN_PATTERN = re.compile(r"\b(\d{11})\b")
PARSEL_PATTERN = re.compile(r"\bPARSEL\b", re.IGNORECASE)

def normalize_website(v):
    if not v: return None
    s = v.strip()
    if not s: return None
    if s == GENERIC_OSB_URL or "OstimMain" in s: return None
    low = s.lower()
    if any(b in low for b in WEB_BLOCKLIST):
        log.debug("Web blocklist filtresi: %s", s)
        return None
    return s

def extract_vkn(unvan):
    if not unvan: return None
    m = VKN_PATTERN.search(unvan)
    return m.group(1) if m else None

def is_parsel_payload(v):
    if not v: return False
    return len(v) <= 80

def extract_parsel(t):
    if not t: return None
    return t.strip() if PARSEL_PATTERN.search(t) else None

def main():
    if not DETAY_PATH.exists():
        log.error("Dosya yok: %s", DETAY_PATH); return 1
    records = []
    for line in DETAY_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line: records.append(json.loads(line))
    log.info("Toplam detay kaydi: %d", len(records))
    stats = {"total": len(records), "matched": 0, "adres_written": 0,
             "website_written": 0, "vkn_extracted": 0, "parsel_extracted": 0,
             "no_match": 0, "errors": 0}
    engine = get_engine()
    batch_size = 100
    conn = engine.connect()
    try:
        for i, rec in enumerate(records):
            unvan = (rec.get("unvan") or "").strip()
            if not unvan: stats["no_match"] += 1; continue
            web = normalize_website(rec.get("web_sitesi"))
            adres = (rec.get("adres") or "").strip() or None
            vkn = extract_vkn(unvan)
            raw_parsel = rec.get("osb_parsel")
            parsel = extract_parsel(raw_parsel) if is_parsel_payload(raw_parsel) else None
            if not parsel: parsel = extract_parsel(adres)
            payload_json = json.dumps({"adres": adres, "sektor": rec.get("sektor"), "sosyal_medya": rec.get("sosyal_medya"), "yetkili": rec.get("yetkili"), "vergi_no_extracted": vkn, "osb_parsel_extracted": parsel, "slug": rec.get("slug"), "cekilme_tarihi": rec.get("cekilme_tarihi"), "detay_kaynagi": rec.get("kaynak")}, ensure_ascii=False)
            try:
                row = conn.execute(
                    text("SELECT company_id, source_record_id FROM companies WHERE LOWER(TRIM(legal_name)) = LOWER(:n) LIMIT 1"),
                    {"n": unvan}).first()
                if not row:
                    stats["no_match"] += 1; continue
                stats["matched"] += 1
                company_id, source_record_id = row[0], row[1]
                conn.execute(
                    text("UPDATE companies SET website_domain = COALESCE(:web, website_domain), primary_phone = COALESCE(:phone, primary_phone), primary_email = COALESCE(:email, primary_email), tax_number = COALESCE(:vkn, tax_number), vergi_no = COALESCE(:vkn, vergi_no), web_sitesi = COALESCE(:web, web_sitesi), osb_parsel = COALESCE(:parsel, osb_parsel) WHERE company_id = :cid"),
                    {"web": web, "phone": (rec.get("telefonler") or [None])[0], "email": (rec.get("emailler") or [None])[0], "vkn": vkn, "parsel": parsel, "cid": company_id})
                conn.execute(
                    text("UPDATE source_records SET raw_payload = raw_payload || (:payload)::jsonb, raw_website = COALESCE(:web, raw_website), raw_tax_number = COALESCE(:vkn, raw_tax_number) WHERE source_record_id = :sid"),
                    {"payload": payload_json, "web": web, "vkn": vkn, "sid": source_record_id})
                if web: stats["website_written"] += 1
                if vkn: stats["vkn_extracted"] += 1
                if parsel: stats["parsel_extracted"] += 1
                if adres: stats["adres_written"] += 1
            except Exception as e:
                stats["errors"] += 1; log.exception("Kayit hatasi (%s): %s", unvan, e)
                conn.rollback()
            if (i + 1) % batch_size == 0:
                conn.commit()
                log.info(f"Batch tamamlandi: {i+1}/{len(records)} | matched={stats['matched']}, errors={stats['errors']}")
        conn.commit()
    except Exception as e:
        log.exception("Genel hatay: %s", e)
        try: conn.rollback()
        except: pass
    finally:
        if conn:
            try: conn.close()
            except: pass
    log.info("SONUC: %s", json.dumps(stats, ensure_ascii=False))
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())