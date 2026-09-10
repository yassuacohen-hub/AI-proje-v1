import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.begin() as conn:
    print("=== PRIMARY_PHONE 'None' DÜZELTME ===\n")

    # 1) 'None' stringlerini NULL'a çevir
    print("[1] 'None' stringlerini NULL'a çevirme...")
    r = conn.execute(text("""
        UPDATE companies
        SET primary_phone = NULL
        WHERE primary_phone = 'None'
    """))
    print(f"    NULL'a çevrildi: {r.rowcount}")

    # 2) Telefon boş olanlara raw_payload telefonlar dizisinden ilk elemanı koy
    print("[2] Telefon NULL olanlara telefonlar dizisinden doldurma...")
    r = conn.execute(text("""
        UPDATE companies c
        SET primary_phone = sr.raw_payload->'telefonler'->>0
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id
          AND (c.primary_phone IS NULL OR c.primary_phone = '')
          AND sr.raw_payload IS NOT NULL
          AND sr.raw_payload ? 'telefonler'
          AND jsonb_typeof(sr.raw_payload->'telefonler') = 'array'
          AND jsonb_array_length(sr.raw_payload->'telefonler') > 0
          AND sr.raw_payload->'telefonler'->>0 IS NOT NULL
          AND sr.raw_payload->'telefonler'->>0 != 'null'
    """))
    print(f"    populated from telefonler: {r.rowcount}")

    # 3) Email kontrolü - 'None' stringlerini temizle
    print("[3] primary_email 'None' stringlerini temizleme...")
    r = conn.execute(text("""
        UPDATE companies
        SET primary_email = NULL
        WHERE primary_email = 'None'
    """))
    print(f"    email None cleaned: {r.rowcount}")

    # 4) Email boş olanlara emailler dizisinden ilk elemanı koy
    print("[4] Email NULL olanlara emailler dizisinden doldurma...")
    r = conn.execute(text("""
        UPDATE companies c
        SET primary_email = sr.raw_payload->'emailler'->>0
        FROM source_records sr
        WHERE c.source_record_id = sr.source_record_id
          AND (c.primary_email IS NULL OR c.primary_email = '')
          AND sr.raw_payload IS NOT NULL
          AND sr.raw_payload ? 'emailler'
          AND jsonb_typeof(sr.raw_payload->'emailler') = 'array'
          AND jsonb_array_length(sr.raw_payload->'emailler') > 0
          AND sr.raw_payload->'emailler'->>0 IS NOT NULL
          AND sr.raw_payload->'emailler'->>0 != 'null'
          AND sr.raw_payload->'emailler'->>0 ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    """))
    print(f"    populated from emailler: {r.rowcount}")

    # Final stats
    print("\n=== SONUÇ ===")
    result = conn.execute(text("""
        SELECT
            COUNT(*) FILTER (WHERE primary_phone IS NULL) as phone_null,
            COUNT(*) FILTER (WHERE primary_phone = 'None') as phone_none,
            COUNT(*) FILTER (WHERE primary_phone IS NOT NULL AND primary_phone != '' AND primary_phone != 'None') as phone_valid,
            COUNT(*) FILTER (WHERE primary_email IS NULL) as email_null,
            COUNT(*) FILTER (WHERE primary_email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$') as email_valid,
            COUNT(*) as total
        FROM companies WHERE is_ankara = TRUE
    """)).fetchone()
    print(f"phone NULL: {result[0]}, None: {result[1]}, valid: {result[2]}")
    print(f"email NULL: {result[3]}, valid: {result[4]}, total: {result[5]}")