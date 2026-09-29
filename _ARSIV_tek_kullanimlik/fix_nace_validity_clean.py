import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    
    # For all 86 rows where nace_validity has a NACE code pattern,
    # update nace_validity to 'fallback' (or appropriate validity tag)
    result = conn.execute(text("""
        UPDATE companies 
        SET nace_validity = 'fallback'
        WHERE nace_validity ~ '^\d{2}\.\d{2}(\.\d{2})?$'
        AND nace_validity NOT IN ('fallback', 'medium', 'title_default', 'unknown')
        AND nace_code IS NOT NULL
        AND nace_code = nace_validity
    """))
    
    print(f'Updated {result.rowcount} rows')
    conn.commit()
    print('Done!')