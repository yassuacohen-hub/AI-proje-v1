import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text
engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    result = conn.execute(text('SELECT DISTINCT parent_code, COUNT(*) as cnt FROM nace_codes WHERE level = 4 GROUP BY parent_code ORDER BY cnt DESC LIMIT 10')).fetchall()
    for row in result:
        print(f'Parent: \"{row[0]}\" Count: {row[1]}')