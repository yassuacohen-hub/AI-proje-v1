import sys
sys.path.insert(0, 'Huginn Data Insights')
from src.company_master.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.begin() as conn:
    # Remove ghost migration records that don't exist on disk
    conn.execute(text("DELETE FROM schema_migrations WHERE filename = '0062_osb_master_15.sql'"))
    conn.execute(text("DELETE FROM schema_migrations WHERE filename = '0063_osbs_fiili_durum_rename.sql'"))
    conn.execute(text("DELETE FROM schema_migrations WHERE filename = '0060_mersis_tobb_data.sql'"))
    print('Cleaned up migration records')

    # Verify cleanup
    result = conn.execute(text('SELECT filename FROM schema_migrations ORDER BY filename'))
    for row in result:
        print(f'  {row[0]}')