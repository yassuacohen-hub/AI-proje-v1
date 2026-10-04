-- 0049: Fırsat motoru — Need/Fit/Timing/Ensemble dört skor tablosu
--
-- Karar: D-249 (skor NULL varsayılan, "veri yok" ≠ "0 puan"), D-253 (göç defteri),
--        D-256 (tek yazma kapısı deseni), D-260 (kanıtsız beyan yasak), D-319 (K4 resmi skor seti)
-- SSOT: AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md:229-240 (Three-Score System),
--       :215-228 (Opportunity Gates), :241-266 (Ensemble Skorlama formülü)
--
-- NEDEN YENİ GÖÇ: D-319 ile K4'ün Need/Fit/Timing/Ensemble skor seti resmi skor seti
-- olarak kabul edildi (K-B açık sorusu kapandı). Bugün bu dört skor için tablo yok.
--
-- SKOR KOLONLARI (NUMERIC(5,2), DEFAULT NULL — "veri yok" ≠ "0 puan", D-249):
--   1. need_score         — İhtiyaç Olasılığı   (SSOT:231)
--   2. fit_score          — Ürün Uyumu          (SSOT:234, V8 Bulgu #3: ağırlık %20→%35)
--   3. timing_score       — Zamanlama           (SSOT:237)
--   4. ensemble_score     — Birleşik Skor       (SSOT:240, hesap: :241-266)
--
-- BİLİNEN SINIRLAMA (F3 bağımlılığı, docs/HUGINN_V10_PLAN_NETLESTIRME_2026-09-18.md:60-77):
-- fit_score'un girdisi olan company_capabilities/certifications/key_personnel tabloları
-- şema olarak VAR (0004_faz_1_2.sql) ama ETL doldurması henüz yapılmadı (F3 tamamlanmadı).
-- Bu göç şema+hesaplayıcı iskeletini kurar; gerçek hesaplama bu görevde ÇALIŞTIRILMAZ (D-238).
--
-- COMMENT: Her kolona SSOT satır numarası + Türkçe resmi ad yazılır (D-259/1 deseni).

BEGIN;

-- 1) company_opportunity_scores tablosu
-- FK: companies PK'si `company_id`'dir, `id` DEĞİL (0001_core.sql:35,
-- test_schema_validation.py::test_companies_table_structure de bunu ölçer).
CREATE TABLE IF NOT EXISTS company_opportunity_scores (
    company_id UUID PRIMARY KEY REFERENCES companies(company_id) ON DELETE CASCADE,
    need_score NUMERIC(5,2),
    fit_score NUMERIC(5,2),
    timing_score NUMERIC(5,2),
    ensemble_score NUMERIC(5,2),
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    score_version TEXT NOT NULL DEFAULT 'v1'
);

-- 2) COMMENT'ler — SSOT satır numarası + Türkçe resmi ad
COMMENT ON TABLE company_opportunity_scores IS 'Fırsat motoru — Need/Fit/Timing/Ensemble dört skor. SSOT: 01_versiyon_9_baglam_dokumani.md:215-266. D-319 ile resmi skor seti.';

COMMENT ON COLUMN company_opportunity_scores.need_score IS 'SSOT:231 — İhtiyaç Olasılığı (0.0-1.0, NULL=veri yok)';
COMMENT ON COLUMN company_opportunity_scores.fit_score IS 'SSOT:234 — Ürün Uyumu (0.0-1.0, NULL=veri yok). F3 bağımlılığı: company_capabilities/certifications/key_personnel ETL doldurması tamamlanana kadar sparse/NULL beklenir.';
COMMENT ON COLUMN company_opportunity_scores.timing_score IS 'SSOT:237 — Zamanlama (0.0-1.0, NULL=veri yok)';
COMMENT ON COLUMN company_opportunity_scores.ensemble_score IS 'SSOT:240,241-266 — Birleşik Skor (0.0-1.0, NULL=veri yok). Ağırlık: need 0.30, fit 0.35, timing 0.20, evidence 0.15 + field/signal bonus.';
COMMENT ON COLUMN company_opportunity_scores.calculated_at IS 'Hesaplanma zamanı';
COMMENT ON COLUMN company_opportunity_scores.score_version IS 'Skor hesaplama sürümü (ör. v1, v2)';

-- 3) ARALIK KISITLARI (0.0 - 1.0)
--
-- NEDEN: SSOT 6.2 (baglam:229-240) dort skoru 0.0-1.0 araliginda tanimlar.
-- NUMERIC(5,2) tek basina bu araligi KORUMAZ (999.99'a kadar kabul eder);
-- kolon adi icerigi dogrulamaz (D-245). Bu nedenle kisi Python'a birakildiysa
-- "sessizce bozuk veri" olusur. Kisit veritabaninda olmalidir (D-267/1:
-- kisit unutulmaz, koruma disarida birakilirsa kaybolur).
--
-- NOT: Kisit adlari explicit olsa bile ADD CONSTRAINT idempotent DEGILDIR;
-- bu yuzden pg_constraint kataloğundan varlik kontrolu yapilir (D-251/5).
DO $$
DECLARE
    kisit_adlari TEXT[] := ARRAY[
        'ck_cos_need_score_aralik',
        'ck_cos_fit_score_aralik',
        'ck_cos_timing_score_aralik',
        'ck_cos_ensemble_score_aralik'
    ];
    k TEXT;
    varlik BOOLEAN;
BEGIN
    FOREACH k IN ARRAY kisit_adlari LOOP
        SELECT EXISTS (
            SELECT 1 FROM pg_constraint
            WHERE conrelid = 'company_opportunity_scores'::regclass
              AND conname = k
        ) INTO varlik;

        IF NOT varlik THEN
            EXECUTE format(
                'ALTER TABLE company_opportunity_scores ADD CONSTRAINT %I '
                'CHECK (%I BETWEEN 0.0 AND 1.0)',
                k, k LIKE 'ck_cos_need%'      THEN 'need_score'
                     k LIKE 'ck_cos_fit%'     THEN 'fit_score'
                     k LIKE 'ck_cos_timing%'  THEN 'timing_score'
                                           ELSE 'ensemble_score'
                END
            );
            RAISE NOTICE '0049: % kisiti eklendi', k;
        END IF;
    END LOOP;
END $$;

-- 4) İndeksler
CREATE INDEX IF NOT EXISTS idx_company_opportunity_scores_ensemble
    ON company_opportunity_scores(ensemble_score);
CREATE INDEX IF NOT EXISTS idx_company_opportunity_scores_calculated_at
    ON company_opportunity_scores(calculated_at);

COMMIT;
