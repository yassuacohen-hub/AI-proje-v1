-- Migration 0022: companies.legal_name UNIQUE kısıtı
-- Hayalet kayıt temizleme sonrası tekrar oluşmaması için (VERI-HAYALET-TEMIZ-01)
-- D-235: veri kaynağı kuralları mandalı

CREATE UNIQUE INDEX IF NOT EXISTS uq_companies_legal_name ON companies(legal_name);

-- Not: UNIQUE CONSTRAINT yerine UNIQUE INDEX kullanıyoruz çünkü
-- partial index (WHERE legal_name IS NOT NULL) daha esnektir.
-- Eğer CONSTRAINT istenirse:
-- ALTER TABLE companies ADD CONSTRAINT uq_companies_legal_name UNIQUE (legal_name);