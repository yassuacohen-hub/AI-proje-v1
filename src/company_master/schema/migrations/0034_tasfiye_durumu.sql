-- 0034: BORC-TASFIYE-IKIZ-01 / bolum 1 — tasfiye halindeki firmalar "aktif" gorunmesin
--
-- TESPIT: Unvaninda "(IFLAS NEDENIYLE) TASFIYE HALINDE" oneki tasiyan 23 firma
-- panelde status='active' (9 adet) veya 'unknown' (14 adet) olarak duruyordu.
-- Satisci iflas etmis firmayi ariyordu.
--
-- BU GOC BIRLESTIRME YAPMAZ, SATIR SILMEZ. Sadece durumu dogru isaretler.
-- Birlestirme ayri borctur (asagidaki gerekce).
--
-- NEDEN BIRLESTIRME YOK: olcumde onekli kayitlarin kanonik ikizinden DAHA ZENGIN
-- oldugu cikti (ornek: Palme Makina — adres, nace_code, e-posta, telefon, e-posta
-- dogrulama kanitlari YALNIZCA onekli kayitta). "Onekliyi sil" plani veri
-- kaybettirirdi. Ayrica companies'e 23 tablo FK veriyor; hepsinin tasinmasi
-- ayrica olculmeden yapilamaz (D-262).
--
-- IKIZ DE ISARETLENIR: onekli kayit ile oneksiz ikizi AYNI tuzel kisidir. Sadece
-- birini isaretlemek paneli celiskili yapardi (ayni firma hem tasfiye hem aktif).
--
-- KAYNAK DURUSU: bu isaret UNVAN METNINDEN turetilmistir, ticaret sicil teyidi
-- DEGILDIR. Unvani guncellenmemis tasfiye firmalari bu gocle yakalanmaz.

BEGIN;

ALTER TABLE companies DROP CONSTRAINT IF EXISTS companies_status_check;
ALTER TABLE companies ADD CONSTRAINT companies_status_check
    CHECK (status IN ('active', 'inactive', 'unknown', 'liquidation'));

COMMENT ON COLUMN companies.status IS
    'active/inactive/unknown/liquidation. liquidation: unvanda "TASFIYE HALINDE" '
    'oneki tespit edildi (goc 0034). Kaynak unvan metnidir, ticaret sicil teyidi degildir.';

-- Onekli kayitlar + onekleri silindiginde ayni ada inen ikizleri.
-- lower() Turkce I tuzagi tasir ama karsilastirma simetrik oldugundan eslesme bozulmaz.
WITH sade AS (
    SELECT
        company_id,
        lower(regexp_replace(
            regexp_replace(
                legal_name,
                '^\(?\s*(İFLAS NEDENİYLE)?\s*\)?\s*TASFİYE HALİNDE\s*', ''),
            '[^0-9A-Za-zÇĞİÖŞÜçğıöşü]', '', 'g')) AS anahtar,
        legal_name ~ '^\(?\s*(İFLAS NEDENİYLE)?\s*\)?\s*TASFİYE HALİNDE\s*' AS onekli
    FROM companies
    WHERE legal_name IS NOT NULL
),
hedef AS (
    SELECT DISTINCT s.company_id
    FROM sade s
    JOIN (SELECT DISTINCT anahtar FROM sade WHERE onekli) o USING (anahtar)
)
UPDATE companies c
SET status = 'liquidation'
FROM hedef h
WHERE c.company_id = h.company_id;

COMMIT;
