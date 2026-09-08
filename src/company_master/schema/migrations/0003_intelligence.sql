-- Migration 0003: Entity resolution ve intelligence tabloları
-- Kaynak: V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md §3.14–§3.19
-- Ön koşul: 0001_core.sql, 0002_relations.sql

-- §3.14 Entity resolution kayıtları
CREATE TABLE IF NOT EXISTS entity_resolution (
    resolution_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_record_id UUID REFERENCES source_records(source_record_id),
    company_id       UUID REFERENCES companies(company_id),
    match_score      NUMERIC(5,2),
    match_method     TEXT,  -- vkn_exact, name_fuzzy, manual, ...
    decision         TEXT CHECK (decision IN ('matched', 'possible_match', 'new_company', 'rejected')),
    reviewed         BOOLEAN DEFAULT FALSE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_entity_resolution_company ON entity_resolution(company_id);
CREATE INDEX IF NOT EXISTS idx_entity_resolution_record ON entity_resolution(source_record_id);

-- §3.15 Kanıt katmanı (Intelligence Engine temeli)
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id         UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    source_id          UUID REFERENCES sources(source_id),
    evidence_type      TEXT,
    title              TEXT,
    content_reference  TEXT,
    observed_at        TIMESTAMPTZ,
    published_at       TIMESTAMPTZ,
    freshness_score    NUMERIC(5,2),
    source_reliability NUMERIC(5,2),
    independence_score NUMERIC(5,2),
    evidence_strength  NUMERIC(5,2),
    raw_reference      TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_evidence_company ON evidence(company_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source_id);

-- 0002'de ertelenen FK: company_products.evidence_id → evidence
ALTER TABLE company_products
    ADD CONSTRAINT fk_company_products_evidence
    FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id);

-- §3.16 Şirket olayları (Intelligence katmanına geçiş kapısı)
CREATE TABLE IF NOT EXISTS company_events (
    event_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    event_type      TEXT,
    event_date      DATE,
    detection_date  DATE,
    direction       TEXT CHECK (direction IN ('positive', 'negative', 'mixed', 'stable', 'unknown')),
    magnitude       NUMERIC(5,2),
    evidence_id     UUID REFERENCES evidence(evidence_id),
    confidence      NUMERIC(5,2),
    common_cause_id UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_company_events_company ON company_events(company_id);
CREATE INDEX IF NOT EXISTS idx_company_events_date ON company_events(event_date);

-- §3.17 Algoritmik türetilmiş güncel ticari durum
CREATE TABLE IF NOT EXISTS company_state (
    company_id                UUID PRIMARY KEY REFERENCES companies(company_id) ON DELETE CASCADE,
    growth_state              TEXT,
    investment_state          TEXT,
    hiring_state              TEXT,
    capacity_state            TEXT,
    export_state              TEXT,
    financial_pressure_state  TEXT,
    overall_commercial_state  TEXT,
    state_confidence          NUMERIC(5,2),
    calculated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- §3.18 Ticari sinyaller
CREATE TABLE IF NOT EXISTS commercial_signals (
    signal_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id        UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    signal_type       TEXT,
    signal_value      TEXT,
    direction         TEXT CHECK (direction IN ('positive', 'negative', 'mixed', 'stable', 'unknown')),
    strength          NUMERIC(5,2),
    recency           NUMERIC(5,2),
    independence      NUMERIC(5,2),
    causal_relevance  NUMERIC(5,2),
    evidence_strength NUMERIC(5,2),
    baseline_delta    NUMERIC(5,2),
    detected_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_commercial_signals_company ON commercial_signals(company_id);
CREATE INDEX IF NOT EXISTS idx_commercial_signals_detected ON commercial_signals(detected_at);

-- §3.19 Momentum anlık görüntüsü (momentum yalnızca sinyal sayısı değildir)
CREATE TABLE IF NOT EXISTS momentum_snapshot (
    snapshot_id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id            UUID NOT NULL REFERENCES companies(company_id) ON DELETE CASCADE,
    momentum_score        NUMERIC(5,2),
    velocity              NUMERIC(8,4),
    acceleration          NUMERIC(8,4),
    signal_independence   NUMERIC(5,2),
    contradiction_penalty NUMERIC(5,2),
    baseline_change       NUMERIC(5,2),
    calculated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_momentum_snapshot_company ON momentum_snapshot(company_id);
