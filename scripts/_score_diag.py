# -*- coding: utf-8 -*-
"""P0-3: Kalite skoru analizi — duzeltmis sorgu."""
import sys
sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine

e = get_engine()
c = e.connect()

print("--- data_quality_score dagilimi ---")
for x in c.execute(text("""
    SELECT CASE 
        WHEN data_quality_score >= 80 THEN '80-100'
        WHEN data_quality_score >= 60 THEN '60-79'
        WHEN data_quality_score >= 40 THEN '40-59'
        WHEN data_quality_score >= 20 THEN '20-39'
        ELSE '0-19'
    END AS bucket, count(*) 
    FROM companies GROUP BY 1 ORDER BY 2 DESC
""")).fetchall():
    print(f"  {x[0]}: {x[1]}")

avg = c.execute(text("SELECT avg(data_quality_score) FROM companies")).scalar()
print(f"\n*** ORTALAMA SKOR: {avg:.2f} (hedef: 50+) {'BASARILI' if avg >= 50 else 'BASARISIZ'} ***")

print("\n--- Alan doluluklari (companies) ---")
for col in ["primary_phone", "primary_email", "website_domain", "tax_number", "nace_code"]:
    cnt = c.execute(text(f"SELECT count(*) FROM companies WHERE {col} IS NOT NULL AND {col} <> ''")).scalar()
    print(f"  {col}: {cnt}/9007 ({cnt*100/9007:.1f}%)")

print("\n--- source_records raw alanlar ---")
for col in ["raw_phone", "raw_email", "raw_website", "raw_tax_number", "raw_name"]:
    cnt = c.execute(text(f"SELECT count(*) FROM source_records WHERE {col} IS NOT NULL AND {col} <> ''")).scalar()
    print(f"  {col}: {cnt}")

print("\n--- raw_payload ic alanlar ---")
for key in ["adres", "sektor", "nace_code", "osb_parsel"]:
    cnt = c.execute(text(f"SELECT count(*) FROM source_records WHERE raw_payload->>'{key}' IS NOT NULL AND raw_payload->>'{key}' <> ''")).scalar()
    print(f"  {key}: {cnt}")

c.close()