from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT source_id, source_name, url, collection_method
        FROM sources
        WHERE source_name ILIKE '%osb%' 
           OR source_name ILIKE '%ivek%'
           OR source_name ILIKE '%ostim%'
           OR source_name ILIKE '%baskent%'
           OR source_name ILIKE '%organize%'
    """)).fetchall()
    for r in rows:
        print('{} | {} | {} | {}'.format(r[0], r[1], r[2], r[3]))