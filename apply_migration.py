import sys
sys.path.insert(0, r'c:\Huginn Data Projesi\Huginn Data Insights\src')

from company_master.db.connection import get_engine
from sqlalchemy import text

engine = get_engine()

# Apply the corrected migration
# The osbs table uses: osb_id, name, city, district, website, osb_type, status, source_id, verified_at, created_at, operational_status, fiili_durum
# NOT: code, url, type, updated_at (old migration used wrong column names)

with engine.begin() as conn:
    # 1. fiili_durum kolonu zaten var - sadece default'u ayarla
    try:
        conn.execute(text("ALTER TABLE osbs ALTER COLUMN fiili_durum SET DEFAULT 'isletmede'"))
        print("fiili_durum default set: OK")
    except Exception as e:
        print(f"fiili_durum default: {e}")
    
    # 2. OSBÜK kayıdını ekle - sadece mevcut kolonları kullan
    try:
        conn.execute(text("""
            INSERT INTO osbs (osb_id, name, city, district, website, osb_type, status, operational_status, fiili_durum, created_at)
            VALUES (
                'a75c3e60-0000-0000-0000-000000000001',
                'Organize Sanayi Bölgeleri Birliği (OSBÜK)',
                'Ankara',
                'Merkez',
                'https://osbuk.org/view/osb/osbliste.php',
                'dizin',
                'active',
                'operating',
                'isletmede',
                NOW()
            )
            ON CONFLICT (osb_id) DO NOTHING
        """))
        print("OSBÜK record inserted: OK")
    except Exception as e:
        print(f"OSBÜK insert: {e}")
    
    # 3. Beypazarı OSB fiili_durumunu kamulaştirma olarak değiştir
    try:
        conn.execute(text("""
            UPDATE osbs SET fiili_durum = 'kamulastirma', operational_status = 'expropriated'
            WHERE name ILIKE '%Beypazarı%' OR name ILIKE '%Beypazar%'
        """))
        print("Beypazarı OSB fiili_durum updated: OK")
    except Exception as e:
        print(f"Beypazarı update: {e}")
    
    # 4. Anadolu Geri Dönüşüm OSB fiili_durumunu kamulaştirma olarak değiştir
    try:
        conn.execute(text("""
            UPDATE osbs SET fiili_durum = 'kamulastirma', operational_status = 'expropriated'
            WHERE name ILIKE '%Anadolu Geri%' OR name ILIKE '%Geri Dönüşüm%'
        """))
        print("Anadolu Geri Dönüşüm OSB fiili_durum updated: OK")
    except Exception as e:
        print(f"Anadolu update: {e}")
    
    # 5. HAB OSB adını düzelt
    try:
        conn.execute(text("""
            UPDATE osbs SET name = 'Ankara Uzay ve Havacılık İhtisas OSB'
            WHERE name ILIKE '%HAB%' OR website = 'https://hab.org.tr'
        """))
        print("HAB OSB name updated: OK")
    except Exception as e:
        print(f"HAB update: {e}")
    
    # 6. Başkent OSB web adresini değiştir
    try:
        conn.execute(text("""
            UPDATE osbs SET website = 'https://www.baskentosb.org.tr'
            WHERE name ILIKE '%Başkent%' OR website = 'https://baskentosb.org'
        """))
        print("Başkent OSB website updated: OK")
    except Exception as e:
        print(f"Başkent update: {e}")

# Verify
with engine.connect() as conn:
    result = conn.execute(text("SELECT count(*) FROM osbs"))
    count = result.fetchone()[0]
    print(f"\nFinal osbs count: {count}")
    
    result = conn.execute(text("SELECT fiili_durum, count(*) FROM osbs GROUP BY fiili_durum"))
    for row in result:
        print(f"  fiili_durum={row[0]}: {row[1]} records")
    
    result = conn.execute(text("SELECT name, website, fiili_durum FROM osbs ORDER BY name"))
    print("\nAll OSB records:")
    for row in result:
        print(f"  {row[0]} | {row[1]} | {row[2]}")