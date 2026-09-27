from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

statements = [
    # Force 2-digit codes with multiple children to NULL
    """UPDATE companies
    SET nace_code = NULL
    WHERE nace_code IN ('98', '71', '16', '78')""",
    
    # Final rapor
    """SELECT 
        'NN.NN' as type, COUNT(*) as cnt FROM companies WHERE nace_code ~ '^[0-9]{2}\.[0-9]{2}$'
    UNION ALL
    SELECT '6-digit', COUNT(*) FROM companies WHERE nace_code ~ '^[0-9]{2}\.[0-9]{2}\.[0-9]{2}$'
    UNION ALL
    SELECT '2-digit', COUNT(*) FROM companies WHERE nace_code ~ '^[0-9]{2}$'
    UNION ALL
    SELECT 'orphan', COUNT(*) FROM companies c LEFT JOIN nace_codes nc ON c.nace_code = nc.nace_code WHERE c.nace_code IS NOT NULL AND nc.nace_code IS NULL
    UNION ALL
    SELECT 'valid', COUNT(*) FROM companies c JOIN nace_codes nc ON c.nace_code = nc.nace_code
    UNION ALL
    SELECT 'NULL', COUNT(*) FROM companies WHERE nace_code IS NULL""",
    
    # 10.11 ve 29.10 örnek firmaları
    """SELECT company_id, nace_code FROM companies WHERE nace_code = '10.11' LIMIT 3""",
    """SELECT company_id, nace_code FROM companies WHERE nace_code = '29.10' LIMIT 3""",
]

print("SQL calistiriliyor...")
with engine.begin() as conn:
    for i, stmt in enumerate(statements):
        try:
            print(f"\nStatement {i+1}...")
            result = conn.execute(text(stmt))
            if result.returns_rows:
                rows = result.fetchall()
                for row in rows:
                    print(f"  {row}")
            else:
                print(f"  OK (rowcount: {result.rowcount})")
        except Exception as e:
            print(f"  HATA: {e}")
            print(f"  SQL (ilk 200): {stmt[:200]}...")
            break

print("\nTamamlandi!")