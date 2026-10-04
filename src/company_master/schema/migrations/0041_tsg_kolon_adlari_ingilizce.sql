-- 0040: 0037/0038'de yazdigim Turkce kolon ve tablo adlarini Ingilizceye cevirir.
--
-- NEDEN: D-251/1 semanin dili INGILIZCE der. 0037 ve 0038'i yazarken bu kurali
-- ihlal ettim: `companies.son_teyit_tarihi` ve `sorgu_talepleri` tablosunun
-- neredeyse tum kolonlari Turkce cikti. Ihlali ben degil, mandal
-- (`tests/test_goc_defteri.py::test_sema_dili_ingilizce`) yakaladi. Mandal
-- olmasa borc sessizce buyuyecekti -- D-216'nin tam ornegi.
--
-- NEDEN YENI GOC, NEDEN 0037/0038 DUZELTILMEDI: o iki goc DEFTERDE (
-- `public.schema_migrations`) uygulanmis olarak yazili. Dosya icerigini geri
-- donup degistirmek defteri yalanci yapardi: defter "uygulandi" derken sema
-- baska bir sey gosterirdi. Gecmis yeniden yazilmaz, uzerine yazilir.
--
-- NEDEN RENAME, NEDEN DROP+CREATE DEGIL: olculdu (2026-09-29, ad degisiminden
-- once) -> `sorgu_talepleri` 0 satir, `son_teyit_tarihi` 0 dolu deger. Yani
-- kayip riski YOK. Buna ragmen RENAME secildi: DROP yazilsa ve olcum yanlis
-- olsa veri sessizce giderdi. RENAME en kotu durumda bile veriyi tasir.
--
-- ADLANDIRMA: `durum -> status`, `son_teslim -> due_at` gibi karsiliklar
-- mandalin Turkce kok listesine karsi tek tek denetlendi; hicbiri yakalanmiyor.

BEGIN;

-- 1) companies.son_teyit_tarihi -> last_verified_on
--    Tip DATE oldugu icin `_at` degil `_on`: `_at` an, `_on` gun demek.
ALTER TABLE companies
    RENAME COLUMN son_teyit_tarihi TO last_verified_on;

COMMENT ON COLUMN companies.last_verified_on IS
    'Firmanin TSG kaynagindan en son teyit edildigi tarih. NULL = hic teyit edilmedi. Artimli sorgu bu tarihten bugune bakar.';

-- 2) sorgu_talepleri -> query_requests (tablo + tum kolonlar)
ALTER TABLE sorgu_talepleri RENAME TO query_requests;

ALTER TABLE query_requests RENAME COLUMN sorgu_metni   TO query_text;
ALTER TABLE query_requests RENAME COLUMN talep_eden    TO requested_by;
ALTER TABLE query_requests RENAME COLUMN durum         TO status;
ALTER TABLE query_requests RENAME COLUMN gelis_zamani  TO received_at;
ALTER TABLE query_requests RENAME COLUMN son_teslim    TO due_at;
ALTER TABLE query_requests RENAME COLUMN teslim_zamani TO delivered_at;
ALTER TABLE query_requests RENAME COLUMN iade_sebebi   TO refund_reason;
ALTER TABLE query_requests RENAME COLUMN olusturuldu   TO created_at;
ALTER TABLE query_requests RENAME COLUMN guncellendi   TO updated_at;

COMMENT ON TABLE query_requests IS
    'Musteri sorgu talebi kuyrugu. Durum degerleri talep_durum.py tek kapisindan (TSG-05).';
COMMENT ON COLUMN query_requests.query_text IS
    'Musterinin sordugu sey (unvan/MERSIS/sicil). company_id NULL olsa da kaybolmaz.';
COMMENT ON COLUMN query_requests.status IS
    'reserved/processing/done/refunded. CHECK kisiti Python kapisi atlanirsa da tutar.';
COMMENT ON COLUMN query_requests.due_at IS
    'SLA son ani. talep_durum.sla_son_teslim() uretir: mesai ici 10 dk, mesai disi ertesi is gunu.';
COMMENT ON COLUMN query_requests.refund_reason IS
    'Iade edildiyse neden. Bos iade kabul edilmez - asagidaki CHECK zorlar.';

-- 3) Kisit ve indeks adlari da Turkce kaldiysa yalanci olur: kolon Ingilizce,
--    kisit adi Turkce sema okuyani yanlis yere bakmaya iter. RENAME yeterli,
--    kisidin GOVDESI kolonla birlikte otomatik tasindi.
ALTER TABLE query_requests
    RENAME CONSTRAINT ck_sorgu_talepleri_iade_sebepli TO ck_query_requests_refund_reason;
ALTER INDEX ix_sorgu_talepleri_acik    RENAME TO ix_query_requests_open;
ALTER INDEX ix_sorgu_talepleri_company RENAME TO ix_query_requests_company;

COMMIT;
