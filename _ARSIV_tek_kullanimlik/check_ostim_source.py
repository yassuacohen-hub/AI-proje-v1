from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check sources table
    rows = conn.execute(text("""
        SELECT source_id, name, base_url, type
        FROM sources
        ORDER BY source_id
    """)).fetchall()
    print("Sources:")
    for r in rows:
        print(f"  {r[0]} | {r[1]} | {r[2]} | {r[3]}")
    
    # Check source_records with OSTIM source_id
    ostim_source = conn.execute(text("""
        SELECT source_id FROM sources WHERE name ILIKE '%ostim%'
    """)).fetchone()
    
    if ostim_source:
        ostim_id = ostim_source[0]
        print(f"\nOSTIM source_id: {ostim_id}")
        
        # Check records with this source_id
        rows = conn.execute(text("""
            SELECT sr.source_record_id, sr.raw_name, sr.source_id, sr.company_id
            FROM source_records sr
            WHERE sr.source_id = :sid
        """), {"sid": ostim_id}).fetchall()
        print(f"Records with OSTIM source_id: {len(rows)}")
        
        # Check how many have company_id NULL
        rows_null = conn.execute(text("""
            SELECT sr.source_record_id, sr.raw_name, sr.source_id, sr.company_id
            FROM source_records sr
            WHERE sr.source_id = :sid AND sr.company_id IS NULL
        """), {"sid": ostim_id}).fetchall()
        print(f"OSTIM records with company_id=NULL: {len(rows_null)}")
        
        # Check 102 ASO records
        aso_rows = conn.execute(text("""
            SELECT sr.source_record_id, sr.raw_name, sr.raw_payload
            FROM source_records sr
            WHERE sr.source_id = :sid
              AND sr.raw_payload->>'type' = 'ASO'
        """), {"sid": ostim_id}).fetchall()
        print(f"ASO type records: {len(aso_rows)}")
        for r in aso_rows[:10]:
            print(f"  {r[0]} | {r[1][:60]}")