-- Migration 0022: companies.legal_name UNIQUE kısıtı
-- Hayalet kayıt temizleme sonrası tekrar oluşmaması için (VERI-HAYALET-TEMIZ-01)
-- D-235: veri kaynağı kuralları mandalı

-- NULL legal_name kısıt dışı: SQL'de NULL != NULL, ama niyeti açık yazıyoruz.
CREATE UNIQUE INDEX IF NOT EXISTS uq_companies_legal_name
    ON companies(legal_name)
    WHERE legal_name IS NOT NULL;

-- UNIQUE INDEX seçildi (CONSTRAINT değil): partial index'i yalnız index destekler.