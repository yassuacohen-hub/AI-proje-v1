import sys
sys.path.insert(0, 'C:/Projeler/Huginn Data Insights/src')
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
with engine.connect() as conn:
    avg = conn.execute(text('SELECT AVG(data_quality_score) FROM companies')).scalar()
    print(f'Ortalama Kalite Skoru: {avg}')