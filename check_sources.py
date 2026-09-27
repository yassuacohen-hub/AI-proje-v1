from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Check sources table
    result = conn.execute(text("SELECT * FROM sources")).fetchall()
    print('Sources table:')
    for r in result:
        print(f'  {r}')
    
    # Check osbs table
    result = conn.execute(text("SELECT * FROM osbs")).fetchall()
    print('OSBs table:')
    for r in result:
        print(f'  {r}')
    
    # Check source_records
    result = conn.execute(text("SELECT COUNT(*) FROM source_records")).scalar()
    print(f'source_records count: {result}')