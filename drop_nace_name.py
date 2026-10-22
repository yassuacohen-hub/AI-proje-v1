import sys
sys.path.insert(0, 'Huginn Data Insights')
from src.company_master.db import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.begin() as conn:
    # Drop the nace_name column that was added by the old migration
    conn.execute(text('ALTER TABLE public.companies DROP COLUMN IF EXISTS nace_name'))
    print('Dropped nace_name column')