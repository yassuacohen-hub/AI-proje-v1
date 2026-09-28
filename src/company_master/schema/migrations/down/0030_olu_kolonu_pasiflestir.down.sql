-- 0030 geri alma: kolon yorumunu sifirlar.
--
-- DIKKAT: bu dosya YALNIZCA aciklamayi siler. Kolonun kendisi ve 9412 satirlik
-- veri 0030'da da dokunulmadi, burada da dokunulmuyor. Bu gocun tek izi
-- yorumdur; geri alma da yalniz onu kaldirir.
--
-- Bunu kosmak kolonu "yeniden kullanilabilir" yapmaz: kod tarafi mandali
-- tests/test_olu_kolon.py ayrica kaldirilmalidir ve bu bir KAHIN kararidir.
--
-- Idempotent: yorum yoksa IS NULL yine hata vermez.

COMMENT ON COLUMN companies.data_quality_score IS NULL;
