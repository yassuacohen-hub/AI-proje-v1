-- 0046: Risk motoru — 8 güven skoru tablosu
--
-- Karar: D-249 (skor NULL varsayılan), D-253 (göç defteri), D-256 (tek yazma kapısı), D-260 (kanıtsız beyan yasak)
-- SSOT: yedekler/Huginn Data Insights (HUGIns).txt:791-822 (8 skor), 824-849 (4 kademeli öneri)
--
-- NEDEN YENİ GÖÇ: Bugün skor tablosu yok. Faz 2 (Risk Motoru) ilk adımı.
--
-- SKOR KOLONLARI (NUMERIC(5,2), DEFAULT NULL — "veri yok" ≠ "0 puan", D-249):
--   1. corporateness_score     — Kurumsallık Skoru        (SSOT:792)
--   2. reliability_score       — Güvenilirlik Skoru       (SSOT:796)
--   3. reputation_score        — İtibar Skoru             (SSOT:800)
--   4. cyber_security_score    — Siber Güvenlik Skoru     (SSOT:804)
--   5. operational_power_score — Operasyonel Güç Skoru    (SSOT:808)
--   6. transparency_score      — Şeffaflık Skoru          (SSOT:812)
--   7. fraud_risk_score        — Fraud Risk Skoru         (SSOT:816)
--   8. overall_trust_score     — Genel Güven Skoru        (SSOT:820)
--
-- ÖNERİ KADEMESİ (SSOT:824-849): recommendation_tier
--   'calisilabilir' | 'dikkatli_calisilmali' | 'ek_inceleme_gerekli' | 'yuksek_riskli'
--
-- COMMENT: Her kolona SSOT satır numarası + Türkçe resmi ad yazılır (D-259/1 deseni).

BEGIN;

-- 1) company_risk_scores tablosu
-- FK: companies PK'si `company_id`'dir, `id` DEĞİL (0001_core.sql:35,
-- test_schema_validation.py::test_companies_table_structure de bunu ölçer).
CREATE TABLE IF NOT EXISTS company_risk_scores (
    company_id UUID PRIMARY KEY REFERENCES companies(company_id) ON DELETE CASCADE,
    corporateness_score NUMERIC(5,2),
    reliability_score NUMERIC(5,2),
    reputation_score NUMERIC(5,2),
    cyber_security_score NUMERIC(5,2),
    operational_power_score NUMERIC(5,2),
    transparency_score NUMERIC(5,2),
    fraud_risk_score NUMERIC(5,2),
    overall_trust_score NUMERIC(5,2),
    recommendation_tier TEXT,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    score_version TEXT NOT NULL DEFAULT 'v1'
);

-- 2) COMMENT'ler — SSOT satır numarası + Türkçe resmi ad
COMMENT ON TABLE company_risk_scores IS 'Risk motoru — 8 güven skoru + öneri kademesi. SSOT: HUGIns.txt:791-849. Faz 2 ilk adım.';

COMMENT ON COLUMN company_risk_scores.corporateness_score IS 'SSOT:792 — Kurumsallık Skoru (0-100, NULL=veri yok)';
COMMENT ON COLUMN company_risk_scores.reliability_score IS 'SSOT:796 — Güvenilirlik Skoru (0-100, NULL=veri yok)';
COMMENT ON COLUMN company_risk_scores.reputation_score IS 'SSOT:800 — İtibar Skoru (0-100, NULL=veri yok)';
COMMENT ON COLUMN company_risk_scores.cyber_security_score IS 'SSOT:804 — Siber Güvenlik Skoru (0-100, NULL=veri yok)';
COMMENT ON COLUMN company_risk_scores.operational_power_score IS 'SSOT:808 — Operasyonel Güç Skoru (0-100, NULL=veri yok)';
COMMENT ON COLUMN company_risk_scores.transparency_score IS 'SSOT:812 — Şeffaflık Skoru (0-100, NULL=veri yok)';
COMMENT ON COLUMN company_risk_scores.fraud_risk_score IS 'SSOT:816 — Fraud Risk Skoru (0-100, NULL=veri yok)';
COMMENT ON COLUMN company_risk_scores.overall_trust_score IS 'SSOT:820 — Genel Güven Skoru (0-100, NULL=veri yok)';
COMMENT ON COLUMN company_risk_scores.recommendation_tier IS 'SSOT:824-849 — Öneri kademesi: calisilabilir | dikkatli_calisilmali | ek_inceleme_gerekli | yuksek_riskli';
COMMENT ON COLUMN company_risk_scores.calculated_at IS 'Hesaplanma zamanı';
COMMENT ON COLUMN company_risk_scores.score_version IS 'Skor hesaplama sürümü (ör. v1, v2)';

-- 3) recommendation_tier CHECK kısıtı — yalnız 4 kademeden biri veya NULL
-- D-251/5: göç idempotent olmalı. `ADD CONSTRAINT` tekrar çalıştırılırsa
-- "constraint already exists" ile patlar; bu yüzden DO bloğu + information_schema
-- kontrolü ile sarıldı (0026_kimlik_kolonlari_ingilizce.sql deseni).
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint c
        JOIN pg_class t ON t.oid = c.conrelid
        WHERE t.relname = 'company_risk_scores'
          AND c.conname = 'ck_company_risk_scores_recommendation_tier'
    ) THEN
        ALTER TABLE company_risk_scores
            ADD CONSTRAINT ck_company_risk_scores_recommendation_tier
            CHECK (
                recommendation_tier IS NULL
                OR recommendation_tier IN (
                    'calisilabilir',
                    'dikkatli_calisilmali',
                    'ek_inceleme_gerekli',
                    'yuksek_riskli'
                )
            );
    END IF;
END $$;

-- 4) İndeksler
CREATE INDEX IF NOT EXISTS idx_company_risk_scores_overall_trust
    ON company_risk_scores(overall_trust_score);
CREATE INDEX IF NOT EXISTS idx_company_risk_scores_recommendation_tier
    ON company_risk_scores(recommendation_tier);
CREATE INDEX IF NOT EXISTS idx_company_risk_scores_calculated_at
    ON company_risk_scores(calculated_at);

COMMIT;