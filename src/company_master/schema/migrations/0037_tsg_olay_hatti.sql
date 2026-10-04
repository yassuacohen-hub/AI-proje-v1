-- 0037: Ticaret Sicili Gazetesi (TSG) olay hattinin sema kapilari.
--
-- NEDEN: TSG akisinin uc kapisi semada YOKTU (olculdu, 2026-09-29):
--   1. companies.son_teyit_tarihi        -> kolon yok. "Bu firmayi en son ne
--      zaman gazeteden teyit ettik" sorusunun cevabi hicbir yerde durmuyordu.
--      Bu kolon olmadan artimli sorgu (TOBB "Tarih Araligina Gore Sorgulama"
--      kutusu) her seferinde bastan tarar; maliyet firma basina sabit kalmaz.
--   2. company_events'te ilan kimligi yok -> ayni ilan iki kez cekilirse iki
--      satir olur. D-303 dersi: TEKILLIK KOLONDA OLMAZSA KODDA TUTMAZ.
--      Gazete ilaninin kendi GUID'i kaynakta tekil; UNIQUE onu semaya bagliyor.
--   3. Ilanda gecen KISI (ortak / mudur / tasfiye memuru) icin alan yok.
--
-- KVKK (urun sahibi karari, 2026-09-29): Gazete TCKN'yi zaten MASKELI
-- yayinliyor, yani TCKN hic toplanmiyor. Ad + rol TTK 35/3 geregi ALENI.
-- Karar: ad DB'ye YAZILIR, musteriye SUNUMDA MASKELENIR. Maskeleme sunum
-- katmaninin isidir; bu yuzden sema ham adi tutar, rapor katmani maskeler.
-- Hukuki gorus (KVKK-TCKN-02) hala acik ama bloke edici degil: gorus aksi
-- cikarsa kolon DROP edilir, 0037.down bunu zaten yapiyor.
--
-- TAVAN (ponytail): event_person TEK kisi tutar. Bir ilanda birden cok kisi
-- geciyorsa (ornek: 3 ortakli devir) her kisi AYRI company_events satiri olur;
-- ayri bir company_event_persons tablosu acilmadi. Cok kisili ilan orani
-- pilotta olculecek (TSG-PILOT-20); oran yuksek cikarsa tablo o zaman acilir.

BEGIN;

-- 1) Teyit tarihi: artimli sorgunun dayanagi.
-- dusen-iz: companies.son_teyit_tarihi
-- Bu TEK iz 0041'de last_verified_on'a RENAME edildi (D-251/1 Ingilizce sema
-- kurali). Dosyanin GERI KALANI (source_guid, event_person, person_role,
-- indeks) hala gecerli; o yuzden dosya-bazli "ustunden-gecen" DEGIL, tekli
-- "dusen-iz" kullanildi.
ALTER TABLE companies
    ADD COLUMN IF NOT EXISTS son_teyit_tarihi DATE;

COMMENT ON COLUMN companies.son_teyit_tarihi IS
    'Firmanin TSG kaynagindan en son teyit edildigi tarih. NULL = hic teyit edilmedi. Artimli sorgu bu tarihten bugune bakar.';

-- 2) Ilan kimligi + kisi alanlari.
ALTER TABLE company_events
    ADD COLUMN IF NOT EXISTS source_guid  TEXT,
    ADD COLUMN IF NOT EXISTS event_person TEXT,
    ADD COLUMN IF NOT EXISTS person_role  TEXT;

COMMENT ON COLUMN company_events.source_guid IS
    'Kaynak ilanin kendi tekil kimligi (TSG ilan GUID). Ayni ilan iki kez yazilamaz.';
COMMENT ON COLUMN company_events.event_person IS
    'Ilanda gecen kisi adi (ortak/mudur/tasfiye memuru). TTK 35/3 aleni. Sunumda MASKELENIR - KVKK karari 2026-09-29.';
COMMENT ON COLUMN company_events.person_role IS
    'Kisinin ilandaki rolu. Etiket sozlugu pilot olcumunden doldurulur; tahminle yazilmaz.';

-- Tekillik: GUID dolu satirlarda. Kismi indeks, cunku TSG disi olaylarin
-- (ise alim sinyali, haber) GUID'i yok ve hepsi NULL olurdu -> ciplak UNIQUE
-- Postgres'te NULL'lari cakistirmaz ama niyeti belirsiz birakirdi.
CREATE UNIQUE INDEX IF NOT EXISTS uq_company_events_source_guid
    ON company_events(source_guid)
    WHERE source_guid IS NOT NULL;

COMMIT;
