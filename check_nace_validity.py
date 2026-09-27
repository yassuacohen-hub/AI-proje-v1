import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    result = conn.execute(text("""
        SELECT company_id, nace_validity, nace_code, nace_source
        FROM companies
        WHERE nace_validity ~ '^\d{2}\.\d{2}'
        ORDER BY nace_validity
        LIMIT 100
    """)).fetchall()
    for row in result:
        print(f'{row[0]} | {row[1]} | {row[2]} | {row[3]}')