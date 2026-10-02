-- Migration 0047 down: company_edges tablosunu düşür
--
-- Karar: D-251/5 (DROP da idempotent yazılır), D-253 (göç defteri)
-- veri-gocu: company_edges tablosu DROP (Faz 3 Entity Graph geri alma)

BEGIN;

DROP TABLE IF EXISTS company_edges;

COMMIT;
