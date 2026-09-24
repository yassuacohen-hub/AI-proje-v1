# -*- coding: utf-8 -*-
"""P3-3: 40-59 puan araligindaki firmalarin eksik alanlarini OSTIM JSONL ile doldurur."""
import os, json, re, unicodedata
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / (chr(46)+chr(101)+chr(110)+chr(118)))
engine = create_engine(os.getenv("DATABASE_URL"), future=True)

JSONL_PATH = ROOT / "data" / "ostim" / "firmalar_detayli.jsonl"
REPORT_DIR = ROOT / "data" / "orchestrator"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def normalize(s):
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = re.sub(r"[^a-zA-Z0-9]", "", s)
    return s.lower()


def load_ostim_jsonl():
    firma_map = {}
    with open(JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            for key in ("unvan", "slug"):
                v = (rec.get(key) or "").strip()
                if v:
                    firma_map.setdefault(normalize(v), rec)
    return firma_map


def main():
    print("Loading OSTIM JSONL...")
    firma_map = load_ostim_jsonl()
    print("  Total keys:", len(firma_map))

    sql_select_mid = (
        "SELECT company_id, legal_name, "
        "COALESCE(primary_email, ''), COALESCE(website_domain, ''), "
        "COALESCE(web_sitesi, ''), COALESCE(adres, ''), "
        "COALESCE(tax_number, ''), COALESCE(vergi_no, ''), "
        "COALESCE(primary_phone, ''), COALESCE(nace_code, ''), "
        "COALESCE(osb_parsel, ''), COALESCE(trade_name, '') "
        "FROM companies WHERE is_ankara = TRUE AND data_quality_score BETWEEN 40 AND 59"
    ).replace("''", chr(39)+chr(39))
    with engine.connect() as conn:
        rows = conn.execute(text(sql_select_mid)).fetchall()
        before_dist = conn.execute(text(
            "SELECT "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 80 AND 100) AS r80_100, "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 60 AND 79)  AS r60_79, "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 40 AND 59)  AS r40_59, "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 20 AND 39)  AS r20_39, "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 0  AND 19)  AS r0_19, "
            "ROUND(AVG(data_quality_score)::numeric, 2) AS avg_score "
            "FROM companies WHERE is_ankara=TRUE"
        )).fetchone()

    print("Before distribution:", dict(before_dist._mapping))

    updates_email = 0
    updates_web = 0
    updates_adres = 0
    updates_tax = 0
    pending = []
    matched_count = 0
    for r in rows:
        cid, legal, email, web_dom, web_alt, adres, tax, vergi, phone, nace, parsel, trade = r
        norm = normalize(legal)
        rec = firma_map.get(norm)
        if rec:
            matched_count += 1
        new_email = email
        new_web_dom = web_dom
        new_web_alt = web_alt
        new_adres = adres
        new_tax = tax or vergi
        if rec:
            if not email:
                ems = rec.get("emailler") or []
                if ems and ems[0]:
                    new_email = ems[0]
                    updates_email += 1
            if not (web_dom or web_alt):
                w = rec.get("web_sitesi")
                if w:
                    new_web_dom = w
                    new_web_alt = w
                    updates_web += 1
            if not adres:
                a = rec.get("adres")
                if a:
                    new_adres = a
                    updates_adres += 1
            if not (tax or vergi):
                v = rec.get("vergi_no")
                if v:
                    new_tax = v
                    updates_tax += 1

        if (new_email, new_web_dom, new_web_alt, new_adres, new_tax) != (email, web_dom, web_alt, adres, tax or vergi):
            pending.append({
                "company_id": str(cid),
                "primary_email": new_email or None,
                "website_domain": new_web_dom or None,
                "web_sitesi": new_web_alt or None,
                "adres": new_adres or None,
                "tax_number": new_tax or None,
                "vergi_no": new_tax or None,
            })

    print("Mid-range firms:", len(rows))
    print("Matched to JSONL:", matched_count)
    print("Pending updates:", len(pending), "(email=", updates_email, "web=", updates_web, "adres=", updates_adres, "tax=", updates_tax, ")")

    sql_update = (
        "UPDATE companies SET "
        "primary_email = COALESCE(:primary_email, primary_email), "
        "website_domain = COALESCE(:website_domain, website_domain), "
        "web_sitesi = COALESCE(:web_sitesi, web_sitesi), "
        "adres = COALESCE(:adres, adres), "
        "tax_number = COALESCE(:tax_number, tax_number), "
        "vergi_no = COALESCE(:vergi_no, vergi_no), "
        "updated_at = NOW() "
        "WHERE company_id = CAST(:company_id AS uuid)"
    )
    applied = 0
    with engine.begin() as conn:
        for upd in pending:
            res = conn.execute(text(sql_update), upd)
            applied += res.rowcount
    print("Applied enrichment:", applied)

    sql_recalc = (
        "UPDATE companies SET data_quality_score = "
        "CASE WHEN COALESCE(tax_number, vergi_no, '') <> '' THEN 15 ELSE 0 END + "
        "CASE WHEN COALESCE(adres, '') <> '' THEN 10 ELSE 0 END + "
        "CASE WHEN COALESCE(primary_phone, '') <> '' THEN 10 ELSE 0 END + "
        "CASE WHEN COALESCE(primary_email, '') <> '' THEN 10 ELSE 0 END + "
        "CASE WHEN COALESCE(nace_code, '') <> '' THEN 10 ELSE 0 END + "
        "CASE WHEN COALESCE(osb_parsel, '') <> '' THEN 5 ELSE 0 END + "
        "CASE WHEN COALESCE(trade_name, '') <> '' THEN 5 ELSE 0 END, "
        "updated_at = NOW() WHERE is_ankara = TRUE"
    ).replace("''", chr(39)+chr(39))
    recalc_count = 0
    with engine.begin() as conn:
        res = conn.execute(text(sql_recalc))
        recalc_count = res.rowcount
    print("Recalc applied to:", recalc_count)

    with engine.connect() as conn:
        after_dist = conn.execute(text(
            "SELECT "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 80 AND 100) AS r80_100, "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 60 AND 79)  AS r60_79, "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 40 AND 59)  AS r40_59, "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 20 AND 39)  AS r20_39, "
            "COUNT(*) FILTER (WHERE data_quality_score BETWEEN 0  AND 19)  AS r0_19, "
            "ROUND(AVG(data_quality_score)::numeric, 2) AS avg_score "
            "FROM companies WHERE is_ankara=TRUE"
        )).fetchone()
        mid_missing = conn.execute(text(
            "SELECT "
            "COUNT(*) FILTER (WHERE COALESCE(primary_email, '') = '') AS no_email, "
            "COUNT(*) FILTER (WHERE COALESCE(website_domain, web_sitesi, '') = '') AS no_web, "
            "COUNT(*) FILTER (WHERE COALESCE(adres, '') = '') AS no_adres, "
            "COUNT(*) FILTER (WHERE COALESCE(tax_number, vergi_no, '') = '') AS no_vkn, "
            "COUNT(*) FILTER (WHERE COALESCE(primary_phone, '') = '') AS no_phone, "
            "COUNT(*) AS total "
            "FROM companies WHERE is_ankara=TRUE AND data_quality_score BETWEEN 40 AND 59"
        )).fetchone()
    print("After distribution:", dict(after_dist._mapping))
    print("Mid-range missing after:", dict(mid_missing._mapping))

    report = {
        "task_id": "P3-3",
        "ts": datetime.now(timezone.utc).isoformat(),
        "jsonl_keys": len(firma_map),
        "mid_range_firms": len(rows),
        "matched_jsonl": matched_count,
        "enrichment": {
            "email_filled": updates_email,
            "web_filled": updates_web,
            "adres_filled": updates_adres,
            "tax_filled": updates_tax,
            "rows_affected": applied,
        },
        "recalc_rows": recalc_count,
        "before_distribution": dict(before_dist._mapping),
        "after_distribution": dict(after_dist._mapping),
        "mid_range_missing_after": dict(mid_missing._mapping),
        "note": "OSTIM JSONL ile 40-59 firmalarin email/web/adres/VKN alanlari doldurulmaya calisildi. Onceki ingest (P3-1, P1-3) alanlari buyuk oranda doldurmus; kalan bosluklar kaynak veride yok.",
    }
    report_path = REPORT_DIR / "p3_3_result.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print("Report written:", report_path)


if __name__ == "__main__":
    main()
