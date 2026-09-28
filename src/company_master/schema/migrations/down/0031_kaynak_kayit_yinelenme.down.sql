-- Migration 0031 down: UNIQUE(source_id, external_id) kisiti dusurulur.
--
-- TAM GERI ALINAMAZ (D-251/4 geregi aciktan yazilir):
-- 0031 yinelenen 3120 satiri SILDI. Silinen satirlar birebir kopyaydi
-- (olcum: icerigi farkli grup 0, farkli firmaya bagli grup 0), bu yuzden
-- BILGI kaybi yok; ama SATIRLAR bu down ile geri gelmez.
-- Geri gerekiyorsa ham JSONL dosyalarindan yeniden yuklenir:
--   python scripts/ingest_ivedik_baskent.py
-- Yeniden yukleme artik duzeltilmis _content_hash ile calisir; kopya uretmez.

ALTER TABLE source_records
    DROP CONSTRAINT IF EXISTS source_records_source_external_uniq;
