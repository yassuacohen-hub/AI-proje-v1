import os
from dotenv import load_dotenv
load_dotenv('C:/Huginn Data Projesi/Huginn Data Insights/.env')
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with create_engine(os.getenv('DATABASE_URL')).connect() as conn:
    from sqlalchemy import text
    
    # Find ALL rows where nace_validity has a NACE code pattern (not a tag)
    result = conn.execute(text("""
        SELECT company_id, nace_validity, nace_code, nace_source
        FROM companies
        WHERE nace_validity ~ '^\d{2}\.\d{2}(\.\d{2})?$'
        AND nace_validity NOT IN ('fallback', 'medium', 'title_default', 'unknown')
        ORDER BY nace_validity
    """)).fetchall()
    
    print(f'Found {len(result)} rows with NACE code in nace_validity')
    
    # First, check which ones have nace_code already populated (conflicts)
    conflicts = []
    to_fix = []
    
    for row in result:
        company_id = row[0]
        nace_from_validity = row[1]
        nace_code = row[2]
        nace_source = row[3]
        
        # Check if nace_code is already populated (conflict)
        if nace_code and nace_code.strip():
            print(f'CONFLICT: {row[0]} has nace_code={row[2]} but nace_validity={row[1]}')
        else:
            # nace_code is NULL or empty, move from nace_validity
            result = conn.execute(text("""
                UPDATE companies 
                SET nace_code = :nace_validity, 
                    nace_validity = 'fallback',  -- default tag, can be refined later
                    nace_source = 'fallback_from_validity'
            WHERE company_id = :cid
            """), {"cid": row[0], "nace_validity": row[1]})
            
            if result.rowcount > 0:
                print(f'Fixed: {row[0]} -> nace_code={row[1]}')
            else:
                print(f'FAILED: {row[0]}')
    
    conn.commit()
    print('Done!')