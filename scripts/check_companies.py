import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    print("=== Companies table columns ===")
    result = conn.execute(text("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'companies'
        ORDER BY ordinal_position
    """)).fetchall()
    for row in result:
        print(f"  {row[0]}")

    print("\n=== Companies data quality score stats ===")
    result = conn.execute(text("""
        SELECT
            COUNT(*) as total,
            AVG(data_quality_score) as avg_score,
            MIN(data_quality_score) as min_score,
            MAX(data_quality_score) as max_score,
            COUNT(CASE WHEN data_quality_score IS NULL OR data_quality_score = 0 THEN 1 ELSE 0 END) as zero_score
        FROM companies WHERE is_ankara = TRUE
    """)).fetchone()
    print(f"Total: {result[0]}")
    print(f"Avg score: {result[1]:.2f}")
    print(f"Min: {result[2]}, Max: {result[3]}")
    print(f"Zero score: {result[4]}")

    # Check actual tax_number values (samples)
    print("\n=== tax_number sample values ===")
    result = conn.execute(text("""
        SELECT company_id, legal_name, tax_number
        FROM companies
        WHERE tax_number IS NOT NULL AND tax_number != ''
        LIMIT 5
    """)).fetchall()
    for row in result:
        print(f"  {row[0]}: {row[1][:30]}... -> tax_number='{row[2]}'")

    print("\n=== osb_parsel sample values ===")
    result = conn.execute(text("""
        SELECT company_id, legal_name, osb_parsel
        FROM companies
        WHERE osb_parsel IS NOT NULL AND osb_parsel != ''
        LIMIT 5
    """)).fetchall()
    for row in result:
        print(f"  {row[0]}: {row[1][:30]}... -> osb_parsel='{row[2]}'")

    print("\n=== vergi_no sample values ===")
    result = conn.execute(text("""
        SELECT company_id, legal_name, vergi_no
        FROM companies
        WHERE vergi_no IS NOT NULL AND vergi_no != ''
        LIMIT 5
    """)).fetchall()
    for row in result:
        print(f"  {row[0]}: {row[1][:30]}... -> vergi_no='{row[2]}'")