from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))

# Dogru normalize fonksiyonlari - Python tarafiyla test edilmis
statements = [
    # 1. Companies normalize - simple_norm: upper + remove spaces
    """CREATE TEMP TABLE tmp_companies_norm AS
    SELECT 
        company_id,
        legal_name,
        tax_number,
        UPPER(REPLACE(TRIM(legal_name), ' ', '')) AS norm_name,
        REGEXP_REPLACE(tax_number::text, '\D', '', 'g') AS norm_tax
    FROM companies
    WHERE legal_name IS NOT NULL""",
    
    "CREATE INDEX idx_tmp_companies_norm_name ON tmp_companies_norm(norm_name)",
    "CREATE INDEX idx_tmp_companies_norm_tax ON tmp_companies_norm(norm_tax)",
    
    # 2. Source_records normalize
    """CREATE TEMP TABLE tmp_sources_norm AS
    SELECT 
        source_record_id,
        raw_name,
        raw_tax_number,
        UPPER(REPLACE(TRIM(raw_name), ' ', '')) AS norm_name,
        REGEXP_REPLACE(raw_tax_number::text, '\D', '', 'g') AS norm_tax
    FROM source_records
    WHERE company_id IS NULL""",
    
    "CREATE INDEX idx_tmp_sources_norm_name ON tmp_sources_norm(norm_name)",
    "CREATE INDEX idx_tmp_sources_norm_tax ON tmp_sources_norm(norm_tax)",
    
    # 3. Eslestirme: Vergi no - CTE ile
    """WITH tax_matches AS (
        SELECT tsn.source_record_id, tcn.company_id
        FROM tmp_sources_norm tsn
        JOIN tmp_companies_norm tcn ON tsn.norm_tax = tcn.norm_tax
        WHERE tsn.norm_tax <> ''
    )
    UPDATE source_records sr
    SET company_id = tm.company_id
    FROM tax_matches tm
    WHERE sr.source_record_id = tm.source_record_id
      AND sr.company_id IS NULL""",
    
    # 4. Eslestirme: Unvan birebir (coklu olmayanlar)
    """WITH name_matches AS (
        SELECT tsn.source_record_id, tcn.company_id
        FROM tmp_sources_norm tsn
        JOIN tmp_companies_norm tcn ON tsn.norm_name = tcn.norm_name
        WHERE tsn.norm_name <> ''
          AND tcn.norm_name NOT IN (
              SELECT norm_name FROM tmp_companies_norm
              GROUP BY norm_name HAVING COUNT(*) > 1
          )
    )
    UPDATE source_records sr
    SET company_id = nm.company_id
    FROM name_matches nm
    WHERE sr.source_record_id = nm.source_record_id
      AND sr.company_id IS NULL""",
    
    # 5. Rapor
    """SELECT 
        'tax_match' AS type, COUNT(*) AS count
    FROM source_records
    WHERE company_id IS NOT NULL
      AND company_id IN (
          SELECT company_id FROM tmp_companies_norm
          WHERE norm_tax IN (SELECT norm_tax FROM tmp_sources_norm WHERE norm_tax <> '')
      )
    UNION ALL
    SELECT 
        'name_exact' AS type, COUNT(*) AS count
    FROM source_records
    WHERE company_id IS NOT NULL
      AND company_id IN (
          SELECT company_id FROM tmp_companies_norm tcn
          WHERE tcn.norm_name IN (
              SELECT norm_name FROM tmp_sources_norm WHERE norm_name <> ''
          )
          AND tcn.norm_name NOT IN (
              SELECT norm_name FROM tmp_companies_norm
              GROUP BY norm_name HAVING COUNT(*) > 1
          )
      )
    UNION ALL
    SELECT 
        'name_multiple' AS type, COUNT(*) AS count
    FROM source_records sr
    WHERE sr.company_id IS NOT NULL
      AND sr.company_id IN (
          SELECT company_id FROM tmp_companies_norm
          WHERE norm_name IN (
              SELECT norm_name FROM tmp_sources_norm WHERE norm_name <> ''
          )
          AND norm_name IN (
              SELECT norm_name FROM tmp_companies_norm
              GROUP BY norm_name HAVING COUNT(*) > 1
          )
      )
    UNION ALL
    SELECT 
        'unmatched' AS type, COUNT(*) AS count
    FROM source_records
    WHERE company_id IS NULL""",
    
    # 6. Dagilim
    """SELECT company_id, COUNT(*) as cnt
    FROM source_records
    WHERE company_id IS NOT NULL
    GROUP BY company_id
    ORDER BY cnt DESC
    LIMIT 10""",
    
    # Temizlik
    "DROP TABLE IF EXISTS tmp_companies_norm",
    "DROP TABLE IF EXISTS tmp_sources_norm",
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