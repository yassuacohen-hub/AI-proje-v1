import json, sys, os
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

PROJE_KOK = Path(__file__).resolve().parents[1]
engine = get_engine()
conn = engine.connect()

rows = conn.execute(text("SELECT legal_name, company_id, website_domain, web_sitesi, adres, tax_number, vergi_no FROM companies WHERE is_ankara = TRUE")).fetchall()
db = {}
for name, cid, web_dom, web_site, adres, tax, vergi in rows:
    db[name.strip()] = {
        "cid": cid,
        "web": bool(web_dom or web_site),
        "adres": bool(adres),
        "tax": bool(tax or vergi),
    }

files = [
    ("data/ostim/firmalar_vkn_ekli.jsonl", ["web_sitesi", "adres"]),
    ("data/ostim/firmalar_detayli.jsonl", ["web_sitesi", "adres"]),
    ("data/ostim/firmalar_detailed.jsonl", ["web_sitesi", "adres"]),
    ("data/baskent/firmalar.jsonl", ["web_sitesi", "adres"]),
    ("data/aso/aso_full.jsonl", ["adres"]),
    ("data/orchestrator/merged_companies.jsonl", ["web_sitesi", "adres"]),
    ("data/ivedik/firmalar.jsonl", ["web_sitesi", "adres"]),
]

stats = {"web": 0, "adres": 0, "vergi": 0, "matched": 0}

for f, fields in files:
    if not os.path.exists(f):
        continue
    lines = open(f, "r", encoding="utf-8").read().splitlines()
    recs = [json.loads(l) for l in lines if l.strip()]
    for r in recs:
        unvan = (r.get("unvan") or "").strip()
        if not unvan or unvan not in db:
            continue
        info = db[unvan]
        cid = info["cid"]
        web = (r.get("web_sitesi") or "").strip()
        adres = (r.get("adres") or "").strip()
        vergi = (r.get("vergi_no") or r.get("tax_number") or "").strip()
        if not web and not adres and not vergi:
            continue
        updates = {}
        params = {"cid": cid}
        if web and "web_sitesi" in fields and not info["web"]:
            updates["website_domain = :web"] = True
            params["web"] = web.lower().strip()
            stats["web"] += 1
            info["web"] = True
        if adres and "adres" in fields and not info["adres"]:
            updates["adres = :adres"] = True
            params["adres"] = adres[:500]
            stats["adres"] += 1
            info["adres"] = True
        if vergi and not info["tax"]:
            updates["tax_number = :tax, vergi_no = :tax2"] = True
            params["tax"] = vergi
            params["tax2"] = vergi
            stats["vergi"] += 1
            info["tax"] = True
        if updates:
            sql = "UPDATE companies SET " + ", ".join(updates.keys()) + ", updated_at = NOW() WHERE company_id = :cid"
            conn.execute(text(sql), params)
            stats["matched"] += 1

conn.commit()

# Recalculate quality
result = conn.execute(text("""
    WITH scored AS (
        SELECT c.company_id, (
            CASE WHEN COALESCE(c.primary_phone, sr.raw_phone) IS NOT NULL AND COALESCE(c.primary_phone, sr.raw_phone) <> '' THEN 10 ELSE 0 END
            + CASE WHEN COALESCE(c.primary_email, sr.raw_email) IS NOT NULL AND COALESCE(c.primary_email, sr.raw_email) <> '' THEN 5 ELSE 0 END
            + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NOT NULL AND COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) <> '' THEN 15 ELSE 0 END
            + CASE WHEN COALESCE(c.adres, sr.raw_payload->>'adres') IS NOT NULL AND COALESCE(c.adres, sr.raw_payload->>'adres') <> '' THEN 20 ELSE 0 END
            + CASE WHEN COALESCE(c.osb_parsel, sr.raw_payload->>'osb_parsel') IS NOT NULL AND COALESCE(c.osb_parsel, sr.raw_payload->>'osb_parsel') <> '' THEN 15 ELSE 0 END
            + CASE WHEN sr.raw_payload->>'sektor' IS NOT NULL AND sr.raw_payload->>'sektor' <> '' THEN 10 ELSE 0 END
            + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) <> '' THEN 20 ELSE 0 END
            + CASE WHEN (sr.raw_payload->>'nace_code' IS NOT NULL AND sr.raw_payload->>'nace_code' <> '') OR (sr.raw_nace IS NOT NULL AND sr.raw_nace <> '') THEN 5 ELSE 0 END
            + CASE WHEN COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '' THEN -15 ELSE 0 END
            + CASE WHEN COALESCE(c.adres, sr.raw_payload->>'adres') IS NULL OR COALESCE(c.adres, sr.raw_payload->>'adres') = '' THEN -10 ELSE 0 END
            + CASE WHEN COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) IS NULL OR COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) = '' THEN -5 ELSE 0 END
            + CASE WHEN (COALESCE(c.primary_phone, sr.raw_phone) IS NULL OR COALESCE(c.primary_phone, sr.raw_phone) = '')
                      AND (COALESCE(c.primary_email, sr.raw_email) IS NULL OR COALESCE(c.primary_email, sr.raw_email) = '')
                      AND (COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) IS NULL OR COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) = '')
                     THEN -5 ELSE 0 END
        ) AS new_score
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
    )
    UPDATE companies c
    SET data_quality_score = GREATEST(0, LEAST(100, scored.new_score))
    FROM scored
    WHERE c.company_id = scored.company_id
"""), {"adres": "adres", "sektor": "sektor", "nace_code": "nace_code", "osb_parsel": "osb_parsel"})
updated = result.rowcount or 0
avg = conn.execute(text("SELECT AVG(data_quality_score) FROM companies WHERE is_ankara = TRUE")).scalar()
zero = conn.execute(text("SELECT COUNT(*) FROM companies WHERE is_ankara = TRUE AND data_quality_score = 0")).scalar()

print("backfill stats:", stats)
print("updated:", updated)
print("avg:", avg)
print("zero:", zero)

sonuc = {
    "task": "P41: Kalite skorunu 50+ yukseltmek icin kapsamli backfill",
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "database": {
        "connection": "DATABASE_URL (Supabase PostgreSQL)",
        "total_ankara_companies": 10105,
    },
    "backfill_actions": [
        {"step": 1, "name": "Veri dosyalarindan adres/web/vergi backfill", "stats": stats}
    ],
    "recalculation": {
        "records_updated": updated,
        "new_avg_quality_score": float(avg or 0),
        "new_zero_score_count": int(zero or 0),
    },
    "final_state": {
        "avg_quality_score": float(avg or 0),
        "zero_score_count": int(zero or 0),
        "total_companies_updated": stats["web"] + stats["adres"] + stats["vergi"],
    },
    "analysis": {
        "bottleneck": "VKN kapsami cok dusuk. Web ve adres backfill ile sinirli artis saglandi.",
        "path_to_50_plus": "VKN ve web scraping ile ek kapsam gerekli.",
    },
}

out_path = PROJE_KOK / "data/orchestrator/p41_result.json"
out_path.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
print("Saved to:", out_path)
conn.close()
