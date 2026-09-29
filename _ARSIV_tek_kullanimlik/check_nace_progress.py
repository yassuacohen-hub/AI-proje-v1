from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    nn = conn.execute(text("""
        SELECT COUNT(*) FROM companies
        WHERE nace_code ~ '^[0-9]{2}\\.[0-9]{2}$'
    """)).scalar()
    print(f'NN.NN format: {nn}')
    
    six = conn.execute(text("""
        SELECT COUNT(*) FROM companies
        WHERE nace_code ~ '^[0-9]{2}\\.[0-9]{2}\\.[0-9]{2}$'
    """)).scalar()
    print(f'6-digit: {six}')
    
    two = conn.execute(text("""
        SELECT COUNT(*) FROM companies
        WHERE nace_code ~ '^[0-9]{2}$'
    """)).scalar()
    print(f'2-digit: {two}')