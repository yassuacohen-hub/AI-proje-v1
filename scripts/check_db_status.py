import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    # Check companies columns
    cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'companies' ORDER BY ordinal_position"))
    print("Companies columns:", [c[0] for c in cols])
    
    # Check if address column exists
    has_addr = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.columns WHERE table_name='companies' AND column_name='address')")).scalar()
    print(f"Has address column: {has_addr}")
    
    # Count source_records with raw_payload
    total = conn.execute(text("SELECT COUNT(*) FROM source_records")).scalar()
    with_payload = conn.execute(text("SELECT COUNT(*) FROM source_records WHERE raw_payload IS NOT NULL")).scalar()
    print(f"Total source_records: {total}, with raw_payload: {with_payload}")
    
    # Check raw_phone distribution
    cnt = conn.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE raw_phone IS NOT NULL) as p,
            COUNT(*) FILTER (WHERE raw_email IS NOT NULL) as e,
            COUNT(*) FILTER (WHERE raw_website IS NOT NULL) as w,
            COUNT(*) FILTER (WHERE raw_address IS NOT NULL) as a,
            COUNT(*) FILTER (WHERE raw_tax_number IS NOT NULL) as t,
            COUNT(*) as total
        FROM source_records
    """)).first()
    print(f"raw_phone: {cnt[0]}, raw_email: {cnt[1]}, raw_website: {cnt[2]}")
    print(f"raw_address: {cnt[3]}, raw_tax_number: {cnt[4]}, total: {cnt[5]}")
    
    # Check companies fields
    ccnt = conn.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE primary_phone IS NOT NULL) as p,
            COUNT(*) FILTER (WHERE primary_email IS NOT NULL) as e,
            COUNT(*) FILTER (WHERE website_domain IS NOT NULL) as w,
            COUNT(*) FILTER (WHERE web_sitesi IS NOT NULL) as ws,
            COUNT(*) FILTER (WHERE tax_number IS NOT NULL) as t,
            COUNT(*) FILTER (WHERE nace_validity IS NOT NULL) as n,
            COUNT(*) FILTER (WHERE osb_parsel IS NOT NULL) as o,
            COUNT(*) as total
        FROM companies
    """)).first()
    print(f"\nCompanies:")
    print(f"  primary_phone: {ccnt[0]}, primary_email: {ccnt[1]}, website_domain: {ccnt[2]}")
    print(f"  web_sitesi: {ccnt[3]}, tax_number: {ccnt[4]}, nace_validity: {ccnt[5]}")
    print(f"  osb_parsel: {ccnt[6]}, total: {ccnt[7]}")