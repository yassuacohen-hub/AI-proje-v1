-- 0051: F3 Kredi cuzdani - kullanim_log + kredi_hareket
--
-- Karar: BORC-KREDI-PAKET-01 (docs/BORC_DEFTERI.md:69) - PREMIUM internete
--        cikis icin kredi/paket/kota tablosu yok (F0 olcumu).
-- SSOT: docs/PAKET_KOTA_TASARIMI.md S5 ve S7 sira 3-4.
--
-- KAPSAM (YAGNI): yalniz SEMA + yazma kapisi. Webhook/odeme saglayici kodu
-- YOK - ilk odeme talebi gelince eklenir. Mimir cagri noktasi da bu
-- gecvende eklenmez (salih dosya kilidi).
--
-- PK: companies(company_id) UUID tipinde (olculdu: pg_index + information_schema), companies(company_id) (olculdu: pg_index).
-- NUMARA: brief 0050 diyordu; 0050_scrape_audit_log.sql D-323 ile zaten
-- alindi. Cakisma yaratmamak icin 0051.
--
-- Tarih: 2026-10-03
-- Tablo 1: kullanim_log (her tuketim bir satir)
CREATE TABLE IF NOT EXISTS kullanim_log (
    id           BIGSERIAL PRIMARY KEY,
    company_id   UUID   NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    tur          TEXT    NOT NULL,
    source_name   TEXT,
    maliyet_kredi INTEGER NOT NULL DEFAULT 0,
    ts           TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_kullanim_company_ts ON kullanim_log (company_id, ts);
-- Tablo 2: kredi_hareket (alis/satis; negatif = harcam)
CREATE TABLE IF NOT EXISTS kredi_hareket (
    id         BIGSERIAL PRIMARY KEY,
    company_id UUID   NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    miktar     INTEGER NOT NULL,
    neden      TEXT    NOT NULL,
    ts         TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_kredi_hareket_company_ts ON kredi_hareket (company_id, ts);
