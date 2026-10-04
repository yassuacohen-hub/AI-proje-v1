-- 0040 geri alma: Ingilizce adlari 0037/0038'deki Turkce adlara dondurur.
--
-- DIKKAT: bu dosya semayi D-251/1 ihlaline GERI GOTURUR. Yalnizca 0040'in
-- kendisi hatali cikarsa kullanilir. Calistirilirsa mandal
-- (test_sema_dili_ingilizce) yine kirmizi yanar -- ve bu DOGRU davranistir,
-- sema gercekten ihlalli duruma donmustur.
--
-- Sira yukaridakinin TERSI: once indeks/kisit, sonra kolon, EN SON tablo adi.
-- Tablo adi basta dondurulurse sonraki ifadeler yeni adi bulamaz.

BEGIN;

ALTER INDEX ix_query_requests_company RENAME TO ix_sorgu_talepleri_company;
ALTER INDEX ix_query_requests_open    RENAME TO ix_sorgu_talepleri_acik;
ALTER TABLE query_requests
    RENAME CONSTRAINT ck_query_requests_refund_reason TO ck_sorgu_talepleri_iade_sebepli;

ALTER TABLE query_requests RENAME COLUMN query_text    TO sorgu_metni;
ALTER TABLE query_requests RENAME COLUMN requested_by  TO talep_eden;
ALTER TABLE query_requests RENAME COLUMN status        TO durum;
ALTER TABLE query_requests RENAME COLUMN received_at   TO gelis_zamani;
ALTER TABLE query_requests RENAME COLUMN due_at        TO son_teslim;
ALTER TABLE query_requests RENAME COLUMN delivered_at  TO teslim_zamani;
ALTER TABLE query_requests RENAME COLUMN refund_reason TO iade_sebebi;
ALTER TABLE query_requests RENAME COLUMN created_at    TO olusturuldu;
ALTER TABLE query_requests RENAME COLUMN updated_at    TO guncellendi;

ALTER TABLE query_requests RENAME TO sorgu_talepleri;

ALTER TABLE companies RENAME COLUMN last_verified_on TO son_teyit_tarihi;

COMMIT;
