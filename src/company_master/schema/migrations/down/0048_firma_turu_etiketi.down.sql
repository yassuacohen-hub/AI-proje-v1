-- Migration 0048 down: KVKK kapsam bayrağı + company_type kısıtını geri al
--
-- Not: company_type kolonunun KENDİSİ 0048'den ÖNCE vardı (migrasyon dosyasının
-- kendi notu: "ZATEN VAR, 9412 satırda 0 dolu"). Bu yüzden down işlemi
-- kolonu DROP ETMEZ — yalnız 0048'in eklediği kısıt ve yeni kolonu geri alır.

BEGIN;

ALTER TABLE public.companies
    DROP CONSTRAINT IF EXISTS ck_companies_company_type_deger;

ALTER TABLE public.companies
    DROP COLUMN IF EXISTS kvkk_kapsam;

COMMIT;
