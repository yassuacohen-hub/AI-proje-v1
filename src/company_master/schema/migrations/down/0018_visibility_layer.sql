-- Down Migration 0018: Katmanlı Görünürlük & Kontör Sistemi Geri Alma
-- Tablolar silinir (CASCADE ile bağlantılar temizlenir)

DROP TABLE IF EXISTS admin_kvkk_mode CASCADE;
DROP TABLE IF EXISTS module_cost CASCADE;
DROP TABLE IF EXISTS plan_field_group CASCADE;
