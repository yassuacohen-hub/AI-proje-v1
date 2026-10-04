from sqlalchemy import create_engine, text, inspect
import os
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    # Assumption 2: OSB kaynak listesi
    rows = conn.execute(text("""
        SELECT source_id, source_name, identifier, base_url
        FROM sources
        WHERE identifier ILIKE '%osb%' OR source_name ILIKE '%osb%'
    """)).fetchall()
    print('Assumption 2 - OSB kaynak listesi:')
    for r in rows:
        print('  {} | {} | {} | {}'.format(r[0], r[1], r[2], r[3]))
    
    # Assumption 4: Kalıcı durum tablosu (ihale_ilanlari)
    insp = inspect(engine)
    tables = insp.get_table_names()
    tender_tables = [t for t in tables if 'ihale' in t.lower()]
    print('')
    print('Assumption 4 - Kalıcı durum tablolari: {}'.format(tender_tables))
    
    # Assumption 1: Base scraper class
    base_path = 'src/company_master/etl/scrapers/base_osfb_scraper.py'
    exists = os.path.exists(base_path)
    print('Assumption 1 - Base scraper class: {}'.format('EXISTS' if exists else 'MISSING'))