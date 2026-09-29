import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    result = conn.execute(text("SELECT nace_code, level, title FROM nace_codes WHERE title IS NULL OR title = '' ORDER BY level, nace_code")).fetchall()
    print(f'Empty titles count: {len(result)}')
    for row in result[:30]:
        print(f'  {row[0]} | Level: {row[1]} | Title: "{row[2]}"')
    print(f'Total empty titles: {len(result)}')