-- Migration 0018 down: Katmanlı Görünürlük & Kontör Sistemi
-- Migration 0018_visibility_layer.sql'in tersidir

-- Indexler
DROP INDEX IF EXISTS idx_module_cost_active;
DROP INDEX IF EXISTS idx_module_cost_tier;
DROP INDEX IF EXISTS idx_module_cost_module;
DROP INDEX IF EXISTS idx_plan_field_group_group;
DROP INDEX IF EXISTS idx_plan_field_group_plan;
DROP INDEX IF EXISTS idx_admin_kvkk_admin;

-- Tablolar (FK dependency sırasına göre)
DROP TABLE IF EXISTS module_cost;
DROP TABLE IF EXISTS admin_kvkk_mode;
DROP TABLE IF EXISTS plan_field_group;