-- 0033_ikiz_isaretci_senkron.sql
-- SORUN (canli DB'de olculdu, 2026-09-28):
--   companies <-> source_records arasinda IKI AYRI isaretci var:
--     A yonu: companies.source_record_id  -> 9409/9412 dolu
--     B yonu: source_records.company_id   -> 4502/10601 dolu, 4352 tekil firma
--   Ikisi SENKRON DEGIL: 5052 bagda A dolu ama B bos.
--   Sonuc: ayni sorunun paydasi hangi yonu kullandiginiza gore degisiyor.
--   Kanit: quality_metrics.py satir 168 A yonunu, satir 176 B yonunu kullaniyor
--   -> ayni dosyadaki iki metrik farkli firma evreni goruyor (9409 vs 4352).
--
-- KARAR: A yonu kaynak alinir (1:1, 0 coklu isaret), B yonu ondan doldurulur.
--   B yonu 1:N oldugu icin (72 firmanin >1 kaydi var) A yonu tersine cevrilemez;
--   bu yuzden iki yon de yasar ama artik celismez.
--
-- DOKUNULMAYAN: 9 capraz tutarsizlik (A ve B farkli firmayi gosteriyor).
--   Bunlarin hepsi "TASFIYE HALINDE" onekli ikiz firma kaydi.
--   22 tasfiye kaydinin oneksiz ikizi DB'de mevcut -> bu FIRMA seviyesi
--   yinelenmesidir, isaretci sorunu degil. Ayri borc: BORC-TASFIYE-IKIZ-01.

BEGIN;

-- 1) B yonunu A yonundan doldur; capraz tutarsiz 9 satira DOKUNMA.
UPDATE source_records s
   SET company_id = c.company_id
  FROM companies c
 WHERE c.source_record_id = s.source_record_id
   AND s.company_id IS NULL;

-- 2) Bundan sonra A yonu yazildiginda B yonu da yazilsin.
CREATE OR REPLACE FUNCTION trg_isaretci_senkron() RETURNS trigger AS $$
BEGIN
    IF NEW.source_record_id IS NOT NULL THEN
        UPDATE source_records
           SET company_id = NEW.company_id
         WHERE source_record_id = NEW.source_record_id
           AND company_id IS DISTINCT FROM NEW.company_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS companies_isaretci_senkron ON companies;
CREATE TRIGGER companies_isaretci_senkron
    AFTER INSERT OR UPDATE OF source_record_id ON companies
    FOR EACH ROW EXECUTE FUNCTION trg_isaretci_senkron();

COMMENT ON COLUMN companies.source_record_id IS
    'Firmanin dogdugu kaynak kayit (1:1 koken). Yazildiginda '
    'source_records.company_id trigger ile senkronlanir (goc 0033). '
    'Firmanin TUM kayitlari icin source_records.company_id kullanin.';

COMMENT ON COLUMN source_records.company_id IS
    'Kaydin ait oldugu firma (1:N aidiyet). Firma kapsamasi olcumlerinde '
    'DOGRU yon budur; companies.source_record_id sadece kokeni gosterir (goc 0033).';

COMMIT;
