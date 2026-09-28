-- Migration 0027 down: ikiz kolon birlestirmesi geri alinir (KISMEN).
--
-- TAM GERI ALINAMAZ. Aciktan yaziyorum (D-251/4):
--
--   1) `vergi_no` ve `web_sitesi` kolonlari DROP edildi. Icerikleri
--      company_identifiers defterinde ve website_domain'de yasiyor, ama
--      "hangi deger hangi kolondan geldi" ayrimi tutulmadi. Bu down
--      kolonlari BOS olarak geri acar; iceriklerini geri yazmaz.
--      Veri geri istenirse: scripts/kimlik_ayikla.py defteri kaynak alir.
--   2) `tax_number` temizligi (D-246 kapisindan gecmeyen 754 deger NULL'landi)
--      geri alinmaz; o degerler company_identifiers'ta durur, sahte VKN
--      olarak companies'e geri yazmak D-254'un tam ihlalidir.
--
-- Bu down SEMAYI 0027 oncesine dondurur: Turkce kolon adlari, eski indeksler,
-- sekil kisitinin kalkmasi. VERIYI dondurmez.

BEGIN;

-- 7) D-254 sekil kisiti kalkar
ALTER TABLE companies DROP CONSTRAINT IF EXISTS ck_companies_tax_number_sekil;

-- 6) 0027'nin kurdugu Ingilizce indeksler ve search_text dusurulur.
--    search_text GENERATED kolon; bagimli oldugu kolonlar yeniden
--    adlandirilmadan once dusmeli, yoksa RENAME hata verir.
DROP INDEX IF EXISTS idx_companies_search_text_trgm;
ALTER TABLE companies DROP COLUMN IF EXISTS search_text;
DROP INDEX IF EXISTS idx_companies_address;
DROP INDEX IF EXISTS idx_companies_dashboard_covering;
DROP INDEX IF EXISTS idx_companies_kpi_covering;

-- 5) Kolon adlari Turkce'ye doner (D-251/5: hedef varsa atla)
DO $$
DECLARE
    esleme TEXT[][] := ARRAY[
        ['companies',         'address',    'adres'],
        ['companies',         'osb_parcel', 'osb_parsel'],
        ['user_activity_log', 'ip_address', 'ip_adresi']
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

-- Dusurulen ikiz kolonlar BOS olarak geri acilir (yukaridaki 1. maddeye bakiniz)
ALTER TABLE companies ADD COLUMN IF NOT EXISTS vergi_no    TEXT;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS web_sitesi  TEXT;

-- 0011/0010'un eski indeksleri Turkce adlarla geri kurulur
CREATE INDEX IF NOT EXISTS idx_companies_vergi_no ON companies(vergi_no);
CREATE INDEX IF NOT EXISTS idx_companies_web_sitesi ON companies(web_sitesi);
CREATE INDEX IF NOT EXISTS idx_companies_adres ON companies(adres);

ALTER TABLE companies
ADD COLUMN IF NOT EXISTS search_text TEXT GENERATED ALWAYS AS (
    COALESCE(legal_name, '') || ' ' ||
    COALESCE(trade_name, '') || ' ' ||
    COALESCE(primary_phone, '') || ' ' ||
    COALESCE(primary_email, '') || ' ' ||
    COALESCE(tax_number, '') || ' ' ||
    COALESCE(vergi_no, '')
) STORED;

CREATE INDEX IF NOT EXISTS idx_companies_search_text_trgm
    ON companies USING GIN (search_text gin_trgm_ops)
    WHERE is_ankara = TRUE AND is_osb_member = TRUE;

-- 2) Kimlik defteri indeksleri kalkar (defterin kendisi 0027 oncesi de vardi)
DROP INDEX IF EXISTS uq_company_identifiers_deger;
DROP INDEX IF EXISTS idx_company_identifiers_tip;

COMMIT;
