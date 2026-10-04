from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Search for records with meslekGrubu or ticaretSicilNo anywhere in JSON
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND (sr.raw_payload::text LIKE '%meslekGrubu%' OR sr.raw_payload::text LIKE '%ticaretSicilNo%')
    """), {"sid": ostim_id}).fetchall()
    print(f"Records with meslekGrubu or ticaretSicilNo anywhere in JSON: {len(rows)}")
    
    # Check which have kaynak=NULL
    aso_null = []
    for r in rows:
        if r[2] and r[2].get('kaynak') is None:
            aso_null.append(r)
    
    print(f"Of those, with kaynak=None: {len(aso_null)}")
    for r in aso_null[:20]:
        print(f"  {r[0]} | {r[1][:60]}")