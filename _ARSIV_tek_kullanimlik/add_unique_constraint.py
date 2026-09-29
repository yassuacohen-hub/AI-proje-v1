import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text
engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    # Add unique constraint for ON CONFLICT
    try:
        result = conn.execute(text('''
            ALTER TABLE company_industries 
            ADD CONSTRAINT company_industries_company_nace_unique 
            UNIQUE (company_id, nace_code)
        '''))
        conn.commit()
        print('Unique constraint added successfully')
    except Exception as e:
        print(f'Error (might already exist): {e}')
        conn.rollback()
    
    # Verify
    result = conn.execute(text('''
        SELECT conname, contype, pg_get_constraintdef(oid) 
        FROM pg_constraint 
        WHERE conrelid = 'company_industries'::regclass
    ''')).fetchall()
    for row in result:
        print(f'{row[0]} | {row[1]} | {row[2]}')