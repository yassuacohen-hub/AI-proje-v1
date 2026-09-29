import os
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    result = conn.execute(text('SELECT DISTINCT parent_code FROM nace_codes WHERE level = 6 AND parent_code IS NOT NULL AND parent_code NOT IN (SELECT nace_code FROM nace_codes WHERE level = 4) ORDER BY parent_code')).fetchall()
    print('Missing level 4 parent codes for level 6:')
    for row in result:
        print(row[0])