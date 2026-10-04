from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    ostim_id = '0a27baf8-6dfa-4e57-851b-412470f480e7'
    
    # Check for records with ASO-like fields but kaynak=None
    # Look for nested structure in raw_payload
    rows = conn.execute(text("""
        SELECT sr.source_record_id, sr.raw_name, sr.raw_payload
        FROM source_records sr
        WHERE sr.source_id = :sid
          AND sr.raw_payload->>'kaynak' IS NULL
    """), {"sid": ostim_id}).fetchall()
    print(f"Total with kaynak=None: {len(rows)}")
    
    # Check which of these have ASO-like structure
    aso_like = []
    for r in rows:
        payload = r[2]
        if payload and isinstance(payload, dict):
            # Check for ASO fields
            has_asofmt = False
            if 'naceKod' in payload or 'meslekGrubu' in payload or 'ticaretSicilNo' in payload:
                has_asofmt = True
            # Check nested
            elif 'payload' in payload and isinstance(payload['payload'], dict):
                p = payload['payload']
                if 'naceKod' in p or 'meslekGrubu' in p or 'ticaretSicilNo' in p:
                    has_asofmt = True
            if has_asofmt:
                aso_like.append(r)
    
    print(f"Records with ASO-like format AND kaynak=None: {len(aso_like)}")
    for r in aso_like[:20]:
        print(f"  {r[0]} | {r[1][:60]}")