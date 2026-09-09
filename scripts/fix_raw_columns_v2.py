import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.begin() as conn:
    print("=== source_records raw_* kolonlarini duzeltme ===\n")

    # 1) raw_address - adres field'ini cektik
    print("[1] ADRES (raw_address)...")
    r = conn.execute(text("""
        UPDATE source_records sr
        SET raw_address = sr.raw_payload->>'adres'
        WHERE sr.raw_payload IS NOT NULL
          AND sr.raw_payload->>'adres' IS NOT NULL
          AND sr.raw_payload->>'adres' != ''
    """))
    print(f"    updated: {r.rowcount}")

    # 2) raw_website - web_sitesi field'ini cektik
    print("[2] WEB SITESI (raw_website)...")
    r = conn.execute(text("""
        UPDATE source_records sr
        SET raw_website = sr.raw_payload->>'web_sitesi'
        WHERE sr.raw_payload IS NOT NULL
          AND sr.raw_payload->>'web_sitesi' IS NOT NULL
          AND sr.raw_payload->>'web_sitesi' != ''
    """))
    print(f"    updated: {r.rowcount}")

    # 3) raw_tax_number - vergi_no_extracted'ten cektik
    print("[3] VERGI NO (raw_tax_number)...")
    r = conn.execute(text("""
        UPDATE source_records sr
        SET raw_tax_number = sr.raw_payload->>'vergi_no'
        WHERE sr.raw_payload IS NOT NULL
          AND sr.raw_payload->>'vergi_no' IS NOT NULL
          AND sr.raw_payload->>'vergi_no' != ''
    """))
    print(f"    vergi_no (direct): {r.rowcount}")

    # Also try vergi_no_extracted
    r = conn.execute(text("""
        UPDATE source_records sr
        SET raw_tax_number = sr.raw_payload->>'vergi_no_extracted'
        WHERE sr.raw_payload IS NOT NULL
          AND sr.raw_payload->>'vergi_no_extracted' IS NOT NULL
          AND sr.raw_payload->>'vergi_no_extracted' != ''
          AND (sr.raw_tax_number IS NULL OR sr.raw_tax_number = '')
    """))
    print(f"    vergi_no_extracted: {r.rowcount}")

    # 4) raw_nace - nace_code field'ini cektik
    print("[4] NACE CODE (raw_nace)...")
    r = conn.execute(text("""
        UPDATE source_records sr
        SET raw_nace = sr.raw_payload->>'nace_code'
        WHERE sr.raw_payload IS NOT NULL
          AND sr.raw_payload->>'nace_code' IS NOT NULL
          AND sr.raw_payload->>'nace_code' != ''
    """))
    print(f"    updated: {r.rowcount}")

    # 5) raw_email - BUG DÜZELTME!
    #    Eski emailler array stringi olarak yazildi - temizle
    print("[5] EMAIL (raw_email) BUG DÜZELTME...")
    r = conn.execute(text("""
        UPDATE source_records sr
        SET raw_email = NULL
        WHERE sr.raw_email IS NOT NULL
          AND sr.raw_email !~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    """))
    print(f"    hatali email temizlendi: {r.rowcount}")

    # 6) companies nace_name ve nace_source - CONSTRAINT UYUMLU HALDE
    print("[6] NACE NAME / NACE SOURCE (companies)...")
    r = conn.execute(text("""
        UPDATE companies c
        SET nace_name = NULLIF(sr.raw_payload->>'nace_name_tr', ''),
            nace_code = NULLIF(sr.raw_payload->>'nace_code', ''),
            nace_source = CASE
                WHEN sr.raw_payload->>'nace_source' = 'sektor_reverse' THEN 'sector_default'
                WHEN sr.raw_payload->>'nace_source' = 'none' THEN 'unknown'
                ELSE COALESCE(NULLIF(sr.raw_payload->>'nace_source', ''), 'unknown')
            END
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id
          AND sr.raw_payload IS NOT NULL
          AND (c.nace_name IS NULL OR c.nace_name = '')
          AND (c.nace_code IS NULL OR c.nace_code = '')
    """))
    print(f"    updated: {r.rowcount}")

    # Fix nace_source for all records (including ones that already have values)
    print("[7] NACE SOURCE DÜZELTME (mevcutlar)...")
    r = conn.execute(text("""
        UPDATE companies c
        SET nace_source = CASE
            WHEN sr.raw_payload->>'nace_source' = 'sektor_reverse' THEN 'sector_default'
            WHEN sr.raw_payload->>'nace_source' = 'none' THEN 'unknown'
            ELSE c.nace_source
        END
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id
          AND sr.raw_payload IS NOT NULL
          AND sr.raw_payload->>'nace_source' IN ('sektor_reverse', 'none')
    """))
    print(f"    nace_source fixed: {r.rowcount}")

    # Final stats
    print("\n=== SONUÇ ===")
    print("\n--- source_records raw_* doluluk ---")
    for col in ["raw_address", "raw_phone", "raw_email", "raw_website", "raw_tax_number", "raw_nace"]:
        cnt = conn.execute(text(
            f"SELECT COUNT(*) FROM source_records WHERE {col} IS NOT NULL AND {col} != ''"
        )).scalar()
        total = conn.execute(text("SELECT COUNT(*) FROM source_records")).scalar()
        print(f"  {col}: {cnt}/{total} ({cnt/total*100:.1f}%)")

    print("\n--- companies doluluk ---")
    for col in ["primary_phone", "primary_email", "nace_code", "nace_name", "nace_source"]:
        cnt = conn.execute(text(
            f"SELECT COUNT(*) FROM companies WHERE {col} IS NOT NULL AND {col} != '' AND {col} != 'None'"
        )).scalar()
        total = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
        print(f"  {col}: {cnt}/{total} ({cnt/total*100:.1f}%)")