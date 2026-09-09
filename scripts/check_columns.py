import sys
sys.path.insert(0, 'C:/Projeler/Huginn Data Insights/src')
from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='companies'"))
    all_cols = [c[0] for c in cols]
    print('Companies columns:')
    for c in all_cols:
        print(f'  {c}')
    
    # Count non-null for each
    print('\nNon-null counts:')
    for c in all_cols:
        try:
            cnt = conn.execute(text(f"SELECT COUNT(*) FROM companies WHERE {c} IS NOT NULL")).scalar()
            total = conn.execute(text("SELECT COUNT(*) FROM companies")).scalar()
            print(f'  {c}: {cnt}/{total} ({cnt/total*100:.1f}%)')
        except:
            pass