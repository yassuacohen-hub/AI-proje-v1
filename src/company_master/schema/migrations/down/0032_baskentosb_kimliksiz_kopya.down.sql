-- Migration 0032 down: TAM GERI ALINAMAZ (D-251/4 geregi aciktan yazilir).
--
-- 0032 761 kimliksiz kopya satiri SILDI ve 243 companies referansini,
-- 92 firma bagini kimlikli esine TASIDI.
--
-- GERI GELMEYEN: silinen 761 satir. Bunlar ayni firmalarin external_id'siz
-- eski cekimiydi; ham adlari 761/761 oraninda kimlikli yeni satirlarda
-- duruyor, bu yuzden BILGI kaybi yok, SATIR kaybi var.
--
-- GERI GELMEYEN 2: tasinan referanslarin eski hedefi. companies.source_record_id
-- artik yeni (kimlikli) satiri gosteriyor; eski kimlik yok oldugu icin
-- otomatik geri cevrilemez.
--
-- Satirlar gerekiyorsa ham JSONL'den yeniden yuklenir:
--   python scripts/ingest_ivedik_baskent.py
-- Yeniden yukleme artik external_id uretir; kimliksiz satir bir daha olusmaz.

-- Geri alinacak sema degisikligi yok: 0032 yalniz veri tasidi/sildi.
SELECT 1;
