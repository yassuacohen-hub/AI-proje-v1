from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

statements = [
    # 1. Geçici tablo: company_best_nace (raw_nace'ten türetilen en iyi kodlar)
    # PostgreSQL compatible: DISTINCT ON ile en sık görülen
    """CREATE TEMP TABLE tmp_company_best_nace AS
    SELECT DISTINCT ON (sr.company_id)
        sr.company_id,
        UPPER(REPLACE(TRIM(part), ' ', '')) as best_nace
    FROM source_records sr
    CROSS JOIN LATERAL regexp_split_to_table(sr.raw_nace, '[,\;\|\s]+') as part
    JOIN nace_codes nc ON UPPER(REPLACE(TRIM(part), ' ', '')) = nc.nace_code
    WHERE sr.company_id IS NOT NULL
      AND sr.raw_nace IS NOT NULL
      AND sr.raw_nace <> ''
    ORDER BY sr.company_id, COUNT(*) OVER (PARTITION BY sr.company_id, UPPER(REPLACE(TRIM(part), ' ', ''))) DESC""",
    
    "CREATE INDEX idx_tmp_company_best_nace_cid ON tmp_company_best_nace(company_id)",
    
    # 2. NN.NN format düzeltme: raw_nace'ten türetilen varsa kullan
    """UPDATE companies c
    SET nace_code = cbn.best_nace
    FROM tmp_company_best_nace cbn
    WHERE c.company_id = cbn.company_id
      AND c.nace_code ~ '^[0-9]{2}\.[0-9]{2}$'
      AND c.nace_code NOT IN (SELECT nace_code FROM nace_codes)
      AND cbn.best_nace IS NOT NULL""",
    
    # 3. NN.NN format hala geçersizse NULL'a çek
    """UPDATE companies
    SET nace_code = NULL
    WHERE nace_code ~ '^[0-9]{2}\.[0-9]{2}$'
      AND nace_code NOT IN (SELECT nace_code FROM nace_codes)""",
    
    # 4. 6 haneli kodları 4 haneli parent'a kırp (validse)
    """UPDATE companies
    SET nace_code = split_part(nace_code, '.', 1) || '.' || split_part(nace_code, '.', 2)
    WHERE nace_code ~ '^[0-9]{2}\.[0-9]{2}\.[0-9]{2}$'
      AND split_part(nace_code, '.', 1) || '.' || split_part(nace_code, '.', 2) IN (SELECT nace_code FROM nace_codes)""",
    
    # 5. Hala 6 haneli kalanları NULL'a çek
    """UPDATE companies
    SET nace_code = NULL
    WHERE nace_code ~ '^[0-9]{2}\.[0-9]{2}\.[0-9]{2}$'""",
    
    # 6. 2 haneli kodları 4 haneli child'a genişlet (tek child varsa)
    """UPDATE companies c
    SET nace_code = (
        SELECT nc.nace_code
        FROM nace_codes nc
        WHERE nc.nace_code LIKE c.nace_code || '.%'
        LIMIT 1
    )
    WHERE c.nace_code ~ '^[0-9]{2}$'
      AND EXISTS (
          SELECT 1 FROM nace_codes nc2
          WHERE nc2.nace_code LIKE c.nace_code || '.%'
      )
      AND (
          SELECT COUNT(*) FROM nace_codes nc2
          WHERE nc2.nace_code LIKE c.nace_code || '.%'
      ) = 1""",
    
    # 6b. 2 haneli çoklu child varsa NULL
    """UPDATE companies
    SET nace_code = NULL
    WHERE nace_code ~ '^[0-9]{2}$'
      AND nace_code NOT IN (SELECT nace_code FROM nace_codes)""",
    
    # Yetim kodları düzelt
    """UPDATE companies c
    SET nace_code = NULL
    WHERE c.nace_code IS NOT NULL
      AND c.nace_code NOT IN (SELECT nace_code FROM nace_codes)""",
    
    # Rapor
    """SELECT 
        'NN.NN' as type, COUNT(*) as cnt FROM companies WHERE nace_code ~ '^[0-9]{2}\.[0-9]{2}$'
    UNION ALL
    SELECT '6-digit', COUNT(*) FROM companies WHERE nace_code ~ '^[0-9]{2}\.[0-9]{2}\.[0-9]{2}$'
    UNION ALL
    SELECT '2-digit', COUNT(*) FROM companies WHERE nace_code ~ '^[0-9]{2}$'
    UNION ALL
    SELECT 'orphan', COUNT(*) FROM companies c LEFT JOIN nace_codes nc ON c.nace_code = nc.nace_code WHERE c.nace_code IS NOT NULL AND nc.nace_code IS NULL
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