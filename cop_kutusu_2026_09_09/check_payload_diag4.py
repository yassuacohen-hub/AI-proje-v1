import sys
sys.path.insert(0, 'src')
from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()
with engine.connect() as conn:
    # Check fields that don't have direct company columns
    fields_to_check = [
        ("yetkili", "authorized person"),
        ("sosyal_medya", "social media"),
        ("meslekGrubu", "profession group"),
        ("ticaretSicilNo", "trade registry no"),
        ("nace_name_tr", "nace name TR"),
        ("naceDetay", "nace detail"),
        ("naceKod", "nace code alt"),
        ("cekilme_tarihi", "collection date"),
        ("detay_kaynagi", "detail source"),
        ("osb_parsel_extracted", "osb parcel extracted"),
        ("vergi_no_extracted", "tax number extracted"),
    ]
    
    for field, desc in fields_to_check:
        r = conn.execute(text(f"SELECT COUNT(*) FROM source_records WHERE raw_payload->>'{field}' IS NOT NULL AND raw_payload->>'{field}' != ''")).scalar()
        print(f'{desc} ({field}): {r} records with non-empty values')
    
    # Check if companies already have nace_name populated
    r2 = conn.execute(text("SELECT COUNT(*) FROM companies WHERE nace_name IS NOT NULL AND nace_name != ''")).scalar()
    print(f'\nCompanies with nace_name populated: {r2}')
    
    # Check if companies already have osb_parsel populated
    r3 = conn.execute(text("SELECT COUNT(*) FROM companies WHERE osb_parsel IS NOT NULL AND osb_parsel != ''")).scalar()
    print(f'Companies with osb_parsel populated: {r3}')
    
    # Check overall data quality score distribution
    r4 = conn.execute(text("SELECT AVG(data_quality_score), MIN(data_quality_score), MAX(data_quality_score) FROM companies WHERE data_quality_score IS NOT NULL")).fetchone()
    print(f'\nQuality score stats: avg={r4[0]}, min={r4[1]}, max={r4[2]}')
    
    # Count zero quality scores
    r5 = conn.execute(text("SELECT COUNT(*) FROM companies WHERE data_quality_score = 0")).scalar()
    print(f'Companies with zero quality score: {r5}')
    
    # Count companies with quality score < 50
    r6 = conn.execute(text("SELECT COUNT(*) FROM companies WHERE data_quality_score < 50")).scalar()
    print(f'Companies with quality score < 50: {r6}')
