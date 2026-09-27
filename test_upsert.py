from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    # Current state
    r = conn.execute(text("SELECT nace_code, title, version FROM nace_codes WHERE nace_code='47.79'")).fetchone()
    print(f"Current 47.79: {r}")
    
    # Try manual upsert
    try:
        conn.execute(text("""
            INSERT INTO nace_codes (nace_code, version, level, parent_code, title, sector_group, is_manufacturing)
            VALUES ('47.79', '2026.01.01_Mayis2026', 4, '47', 'Ikinci el esya ticareti', 'AGAC ISLERI', false)
            ON CONFLICT (nace_code) DO UPDATE SET
                version = EXCLUDED.version,
                level = EXCLUDED.level,
                parent_code = EXCLUDED.parent_code,
                title = EXCLUDED.title,
                sector_group = EXCLUDED.sector_group,
                is_manufacturing = EXCLUDED.is_manufacturing
        """))
        print("Manual upsert succeeded")
        conn.commit()
    except Exception as e:
        print(f"Manual upsert error: {e}")
    
    # Check after
    r = conn.execute(text("SELECT nace_code, title, version FROM nace_codes WHERE nace_code='47.79'")).fetchone()
    print(f"After manual upsert 47.79: {r}")