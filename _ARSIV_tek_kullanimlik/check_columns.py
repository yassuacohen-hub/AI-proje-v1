import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    result = conn.execute(text('SELECT column_name, data_type FROM information_schema.columns WHERE table_name = \'nace_codes\' ORDER BY ordinal_position')).fetchall()
    for row in result:
        print(f'{row[0]} | {row[1]}')