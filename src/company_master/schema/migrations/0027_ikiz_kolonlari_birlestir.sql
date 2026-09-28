-- 0027_ikiz_kolonlari_birlestir.sql
-- D-251/2: ikiz kolon yasak. D-254: kimlik degerleri company_identifiers'ta yasar.
--
-- Bu goc calismadan ONCE scripts/kimlik_ayikla.py --yaz kosulmus olmalidir;
-- aksi halde vergi_no icerigi kaybolur. Goc bunu kendisi denetler.
--
-- Olcum (2026-09-28, companies=9412):
--   vergi_no       761 dolu -> 590 oda uye no (aso), 41 osb uye no, 7 gecerli kimlik,
--                              123 kaynaksiz. Vergi numarasi DEGIL. Deftere gitti.
--   web_sitesi    5049 dolu -> 49 sadece TR (tasinir), 1 celiski (KAL-MET, TR kazanir)
--   adres         5798 dolu -> hedef kolon yok, duz yeniden adlandirma
--   osb_parsel      19 dolu -> hedef kolon yok, duz yeniden adlandirma
--   ip_adresi            -> user_activity_log'ta; audit_logs.ip_address emsali var

BEGIN;

-- 1) Kimlik defteri kosulmadan devam etme (D-245: kaynaksiz kayip yasak)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'companies'
          AND column_name = 'vergi_no'
    ) AND (SELECT count(*) FROM company_identifiers) = 0
      AND EXISTS (SELECT 1 FROM companies WHERE vergi_no IS NOT NULL AND vergi_no <> '')
    THEN
        RAISE EXCEPTION
            'Kimlik defteri bos. Once: python scripts/kimlik_ayikla.py --yaz';
    END IF;
END $$;

-- 2) Kimlik defterine tekillik: ayni firma + tip + deger bir kez yazilir
CREATE UNIQUE INDEX IF NOT EXISTS uq_company_identifiers_deger
    ON company_identifiers (company_id, identifier_type, identifier_value);

CREATE INDEX IF NOT EXISTS idx_company_identifiers_tip
    ON company_identifiers (identifier_type);

-- 3) web_sitesi -> website_domain: sadece hedefi bos olanlar tasinir.
--    Celisen tek kayit (KAL-MET) icin TR deger dogru; D-251/6 geregi
--    urun sahibi karar verdi, otomatik kural degil, nokta atisi duzeltme.
UPDATE companies
   SET website_domain = web_sitesi
 WHERE web_sitesi IS NOT NULL AND web_sitesi <> ''
   AND (website_domain IS NULL OR website_domain = '');

UPDATE companies
   SET website_domain = 'http://kal-met.com'
 WHERE company_id = 'b0ee3d30-42a4-421f-8618-b4eca8b096a8'
   AND website_domain = 'http://www.isim.org.tr';

-- 4) tax_number yalnizca D-246 kapisini gecen degerleri tutar.
--    Gecmeyenler company_identifiers'ta durur, burada temizlenir.
--    ONCE normalize: asagidaki karsilastirma rakam disini atarak yapiliyor,
--    ama kolonun kendisi biciminde kalirsa (ornek "123-456") 7. bolumdeki
--    sekil kisiti onu geri cevirir ve goc komple geri doner.
UPDATE companies
   SET tax_number = regexp_replace(tax_number, '\D', '', 'g')
 WHERE tax_number IS NOT NULL
   AND tax_number <> regexp_replace(tax_number, '\D', '', 'g');
UPDATE companies c
   SET tax_number = NULL
 WHERE c.tax_number IS NOT NULL
   AND NOT EXISTS (
        SELECT 1 FROM company_identifiers ci
         WHERE ci.company_id = c.company_id
           AND ci.identifier_type IN ('vkn', 'tckn')
           AND ci.identifier_value = regexp_replace(c.tax_number, '\D', '', 'g')
   );

UPDATE companies c
   SET tax_number = ci.identifier_value
  FROM company_identifiers ci
 WHERE ci.company_id = c.company_id
   AND ci.identifier_type = 'vkn'
   AND (c.tax_number IS NULL OR c.tax_number = '');

-- 5) Turkce kolonlari dusur / yeniden adlandir (D-251/1, D-251/5 idempotent)
--
--    ONCE: 0011'in search_text kolonu GENERATED ... STORED ve vergi_no'ya
--    bagli. Bagimli kolon durdukca DROP COLUMN vergi_no hata verir; CASCADE
--    ile gecmek ise arama indeksini sessizce goturur. Bu yuzden kolon
--    once dusurulur, 6. bolumde vergi_no'suz hali geri kurulur.
DROP INDEX IF EXISTS idx_companies_search_text_trgm;
ALTER TABLE companies DROP COLUMN IF EXISTS search_text;

DROP INDEX IF EXISTS idx_companies_vergi_no;
DROP INDEX IF EXISTS idx_companies_vergi_no_lower;
DROP INDEX IF EXISTS idx_companies_web_sitesi;
DROP INDEX IF EXISTS idx_companies_adres;
DROP INDEX IF EXISTS idx_companies_dashboard_covering;
DROP INDEX IF EXISTS idx_companies_search_composite;
-- 0010'un KPI indeksi: INCLUDE listesinde vergi_no/osb_parsel/adres var.
-- Elle dusurulmezse DROP COLUMN onu sessizce goturur, KPI yavaslar ve
-- kimse fark etmez. Aciktan dusur, 6. bolumde geri kur.
DROP INDEX IF EXISTS idx_companies_kpi_covering;

ALTER TABLE companies DROP COLUMN IF EXISTS vergi_no;
ALTER TABLE companies DROP COLUMN IF EXISTS web_sitesi;

DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['companies',         'adres',      'address'],
        ['companies',         'osb_parsel', 'osb_parcel'],
        ['user_activity_log', 'ip_adresi',  'ip_address']
    ];
    i INT;
BEGIN
    FOR i IN 1 .. array_length(esleme, 1) LOOP
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = esleme[i][1]
              AND column_name = esleme[i][2]
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = esleme[i][1]
              AND column_name = esleme[i][3]
        ) THEN
            EXECUTE format(
                'ALTER TABLE %I RENAME COLUMN %I TO %I',
                esleme[i][1], esleme[i][2], esleme[i][3]
            );
        END IF;
    END LOOP;
END $$;

-- 6) Dusen indeksleri Ingilizce kolon adlariyla geri kur
CREATE INDEX IF NOT EXISTS idx_companies_address
    ON companies(address);

CREATE INDEX IF NOT EXISTS idx_companies_dashboard_covering
    ON companies(created_at DESC)
    INCLUDE (data_quality_score, tax_number, website_domain, osb_parcel,
             address, primary_phone, primary_email, nace_code);

CREATE INDEX IF NOT EXISTS idx_companies_kpi_covering
    ON companies(is_ankara, is_osb_member)
    INCLUDE (data_quality_score, tax_number, website_domain, osb_parcel,
             address, primary_phone, primary_email, nace_code);

-- 0011'in arama kolonu: vergi_no kaldirildi, geri kalan alanlar ayni.
ALTER TABLE companies
ADD COLUMN IF NOT EXISTS search_text TEXT GENERATED ALWAYS AS (
    COALESCE(legal_name, '') || ' ' ||
    COALESCE(trade_name, '') || ' ' ||
    COALESCE(primary_phone, '') || ' ' ||
    COALESCE(primary_email, '') || ' ' ||
    COALESCE(tax_number, '')
) STORED;

CREATE INDEX IF NOT EXISTS idx_companies_search_text_trgm
    ON companies USING GIN (search_text gin_trgm_ops)
    WHERE is_ankara = TRUE AND is_osb_member = TRUE;

-- 7) D-254 mandali: tax_number'a bir daha oda/OSB uye no yazilamaz.
--    Bu kural uygulama katmaninda degil burada durur; boylece hangi
--    betik yazarsa yazsin atlayamaz. Kisit SEKIL denetler (10 hane VKN
--    veya 11 hane TCKN); ALGORITMA denetimi D-246 kapisinin isidir
--    (kimlik_dogrula). Sekil kapisi 590 oda uye no'sunu (5-6 hane) ve
--    41 OSB uye no'sunu tek basina geri ceviriyor - yasanan hata buydu.
ALTER TABLE companies DROP CONSTRAINT IF EXISTS ck_companies_tax_number_sekil;
ALTER TABLE companies ADD CONSTRAINT ck_companies_tax_number_sekil
    CHECK (tax_number IS NULL OR tax_number ~ '^[0-9]{10}$|^[0-9]{11}$');

COMMIT;
