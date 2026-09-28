-- 0029: Indeksleri terk edilmis kolondan canli kolona tasi.
--
-- D-250/1: puan kolonu `data_quality_score` (0-100) -> `identity_completeness` (0-10).
-- 0024-0028 kolonu tasidi; INDEKSLER tasinmadi. Olcum (2026-09-28):
--   27 indeksin 5'i hala `data_quality_score` uzerinde, 1'i canli kolonda.
-- Sonuc: panelin siralama/kapsama sorgulari indekssiz kaliyordu; planlayici
-- seq scan'e dusuyordu. Yarim gocun performans ayagi.
--
-- Kolon DUSURULMEZ: 9412 satir hala dolu, dusurme ayri karar (veri kaybi).
-- Bu goc yalniz erisim yolunu duzeltir.

-- 1) Terk edilmis kolon uzerindeki tekil/siralama indeksleri
DROP INDEX IF EXISTS idx_companies_quality_score;
CREATE INDEX IF NOT EXISTS idx_companies_identity_completeness
    ON companies(identity_completeness);

DROP INDEX IF EXISTS idx_companies_ankara_osb_score;
CREATE INDEX IF NOT EXISTS idx_companies_ankara_osb_tamlik
    ON companies(is_ankara, is_osb_member, identity_completeness DESC);

DROP INDEX IF EXISTS idx_companies_source_record_score;
CREATE INDEX IF NOT EXISTS idx_companies_source_record_tamlik
    ON companies(is_ankara, is_osb_member, source_record_id, identity_completeness DESC);

-- 2) Kapsayici (covering) indeksler — INCLUDE listesi canli kolona gecer
DROP INDEX IF EXISTS idx_companies_dashboard_covering;
CREATE INDEX IF NOT EXISTS idx_companies_dashboard_covering
    ON companies(created_at DESC)
    INCLUDE (identity_completeness, score_version, tax_number, website_domain,
             osb_parcel, address, primary_phone, primary_email, nace_code);

DROP INDEX IF EXISTS idx_companies_kpi_covering;
CREATE INDEX IF NOT EXISTS idx_companies_kpi_covering
    ON companies(is_ankara, is_osb_member)
    INCLUDE (identity_completeness, score_version, tax_number, website_domain,
             osb_parcel, address, primary_phone, primary_email, nace_code);
