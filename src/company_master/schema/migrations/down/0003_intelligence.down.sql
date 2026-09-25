-- Migration 0003 down: Entity resolution ve intelligence tablolarını geri al
-- Migration 0003_intelligence.sql'in tersidir

-- FK dependency sırasına göre ters sırada sil
DROP TABLE IF EXISTS momentum_snapshot;
DROP TABLE IF EXISTS commercial_signals;
DROP TABLE IF EXISTS company_state;
DROP TABLE IF EXISTS company_events;
DROP TABLE IF EXISTS evidence;

-- Not: 0002'de eklenen FK constraint'i de kaldır
ALTER TABLE company_products DROP CONSTRAINT IF EXISTS fk_company_products_evidence;

DROP TABLE IF EXISTS entity_resolution;
DROP TABLE IF EXISTS evidence;
DROP TABLE IF EXISTS company_events;
DROP TABLE IF EXISTS company_state;
DROP TABLE IF EXISTS commercial_signals;
DROP TABLE IF EXISTS momentum_snapshot;

-- Not: Bu migration 0002_relations.sql'e FK ekler (company_products.evidence_id)
-- Bu constraint 0002'yi down ederken de kaldırılmalı (yukarıda yapıldı)