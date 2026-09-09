import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    # Check companies table structure
    cols = conn.execute(text("""
        SELECT column_name, data_type FROM information_schema.columns
        WHERE table_name = 'companies' ORDER BY ordinal_position
    """))
    print("Companies columns:")
    for c in cols:
        print(f"  {c[0]}: {c[1]}")
    
    print("\n\n=== Join check ===")
    # Check if companies has source_record_id
    check = conn.execute(text("""
        SELECT c.company_id, c.legal_name, c.tax_number, c.primary_phone, c.website_domain,
               c.web_sitesi, c.vergi_no, c.osb_parsel, c.source_record_id,
               sr.source_id, sr.raw_payload
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara = TRUE
        LIMIT 3
    """))
    for row in check:
        import json
        print(f"Company: {row[1]}")
        print(f"  tax_number: {row[2]}")
        print(f"  primary_phone: {row[3]}")
        print(f"  website_domain: {row[4]}")
        print(f"  web_sitesi: {row[5]}")
        print(f"  vergi_no: {row[6]}")
        print(f"  osb_parsel: {row[7]}")
        print(f"  source_record_id: {row[8]}")
        print(f"  source_id: {row[9]}")
        if row[10]:
            payload = row[10]
            if isinstance(payload, str):
                payload = json.loads(payload)
            print(f"  payload: adres={payload.get('adres')}, telefon={payload.get('telefonler')}, vergi={payload.get('vergi_no')}, web={payload.get('web_sitesi')}")
        print()
    
    # Count companies with source_record_id linkage
    count = conn.execute(text("""
        SELECT 
            COUNT(*) AS total,
            COUNT(c.source_record_id) AS with_src,
            COUNT(CASE WHEN c.tax_number IS NOT NULL OR c.vergi_no IS NOT NULL THEN 1 END) AS with_vkn
        FROM companies c WHERE c.is_ankara = TRUE
    """)).first()
    print(f"\n=== Counts ===")
    print(f"Total: {count[0]}, With source_record_id: {count[1]}, With VKN: {count[2]}")