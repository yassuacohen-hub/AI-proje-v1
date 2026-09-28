-- 0036: NACE kumesinin iki olu kolonunu dusurur.
--
-- BORCUN ADI YARISI YANLISTI (D-267/1 deseni). Devir notu iki kolonu ayni
-- fiile bagliyordu: "is_manufacturing + nace_name dusur". Olculdugunde
-- ikisinin gerekcesi AYNI DEGIL; biri sifir bilgi, digeri yanlis kolon.
--
-- 1) nace_codes.is_manufacturing  -> GERCEK OLU (D-249: tek degerli = sifir bilgi)
--      3319 satirin 3319'u 'false'. Tek bir 'true' yok.
--      Yazan: src/company_master/etl/nace_sozluk_yukle.py -- her zaman SABIT False.
--      Uretimde OKUYAN: yok (D-266 cagiran taramasi; sadece olcum scriptleri
--      ve dokumanlar deger okuyor). Cagirani olmayan kolon duzeltilmez, dusurulur.
--
-- 2) companies.nace_name -> YANLIS KOLON (D-252/7), "olu" DEGILDI
--      52 / 9412 dolu; 8 farkli deger: 'Metalurji ve Makina Sanayi' (22),
--      'Diger' (17), 'KIMYA-LABARATUVAR' (4), 'GIDA' (4), 'Medikal - Ilac' (2),
--      'Endustriyel Market' (1), 'Elektrikli Cihaz Sanayi' (1), 'Savunma' (1).
--      Hicbiri NACE adi degil; OSB sitesinin kendi sektor etiketi.
--      Yazan: scripts/ingest_osb_scrapers.py  -> nace_name = COALESCE(:sektor, ...)
--      Yani OSB'nin 'sektor' alani dogrudan NACE adi kolonuna akiyordu.
--      URETIM OKUYANI VARDI: web_app.py /api/match SELECT listesi.
--      Bu yuzden "cagirani yok, dusur" gerekcesi bu kolon icin YANLISTI.
--
-- NEDEN YINE DE DUSUYOR (olculen gerekce, beyan degil):
--   a) Puan/eslestirmeye girmiyor: _match_puan() sadece nace_code, osb_id,
--      is_ankara, identity_completeness, website/email/telefon okuyor. nace_name
--      hicbir bilesende gecmiyor (web_app.py:1163-1225 okundu).
--   b) Cagiran fiilen deger gormuyor: SELECT sarti
--      "nace_code IS NOT NULL AND is_ankara" ile 8289 satir donuyor, bunlardan
--      nace_name DOLU olan = 2. Yani 8287 satirda alan NULL gidiyor.
--      52 dolu satirin 50'si zaten bu cagirana hic ugramiyor (nace_code NULL).
--   c) Tuketici yok: hicbir .html/.js sablonu ve hicbir test nace_name'e
--      dokunmuyor (0 sonuc). Yanit sozlugune girip kimsenin okumadigi alan.
--   d) KAYNAK KAYBI YOK (D-246/4): 52 degerin 47'si ham arsivde aynen duruyor
--      (source_records.raw_payload ->> 'sektor', 47/47 birebir esit). Kalan 5
--      firmanin kaydinda 'sektor' anahtari yok; bu 5 deger 'Diger'/sektor
--      etiketi sinifinda, NACE bilgisi tasimiyor. Ham arsiv kalicidir.
--
-- OLCUM (D-260: iki oran birden):
--   nace_codes.is_manufacturing : 3319 / 3319 satir 'false'  (kolon capinda tek deger)
--   companies.nace_name         : firma kapsamasi 52 / 9412 = binde 5.5
--                                 uretim cagiraninin gordugu 2 / 8289
--   ham arsivde ayni deger      : 47 / 52  (geri kalan 5'te payload anahtari yok)
--
-- IKIZ KOLON (D-263): olusmuyor. Dusurulen iki kolonun yerine yeni kolon
-- gelmiyor. Sektor etiketi ihtiyaci varsa kaynagi raw_payload->>'sektor'tir
-- ve o ham arsivde durur; NACE adi ihtiyaci nace_codes.title'dan karsilanir.
--
-- ETL YOLU AYNI TURDA KESILIYOR (D-267/6): bu goc gecmisi temizler;
-- ingest_osb_scrapers.py / nace_eksik_doldur.py / fix_raw_columns_v2.py /
-- p45_validate_and_dedup.py / nace_sozluk_yukle.py ayni commit'te yaziyi
-- birakir. Yoksa bir sonraki ETL kosusu kolonu geri dogurur.

BEGIN;

ALTER TABLE nace_codes DROP COLUMN IF EXISTS is_manufacturing;
ALTER TABLE companies DROP COLUMN IF EXISTS nace_name;

COMMIT;
