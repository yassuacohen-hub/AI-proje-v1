-- D-309: companies'a koken kolonlari (S1, KAHIN 2026-09-29)
-- uretim: 2026-09-29T23:58:25
--
-- D-308 bulgusu: 'her kaydin kokeni yazilir' kurali yaziliydi
-- ama companies'ta source/collected_at kolonu YOKTI; kural
-- beyan olarak kaliyordu. Bu migration onu FIILEN zorlar.
-- Mevcut veri SILINMEZ; sadece NULL baslangicli kolon eklenir.

ALTER TABLE public.companies ADD COLUMN IF NOT EXISTS collected_at timestamptz;
--   kaydin toplandigi an - kritik eksikti
ALTER TABLE public.companies ADD COLUMN IF NOT EXISTS source_name text;
--   kaynagin adi (ostim.org.tr, baskent.org.tr ...)
ALTER TABLE public.companies ADD COLUMN IF NOT EXISTS source_type text;
--   kaynagin turu (osb / chamber / directory)
ALTER TABLE public.companies ADD COLUMN IF NOT EXISTS source_file text;
--   hangi dosyadan geldi (izlenebilirlik)
ALTER TABLE public.companies ADD COLUMN IF NOT EXISTS source_line text;
--   kaynak dosyadaki satir (varsa)
ALTER TABLE public.companies ADD COLUMN IF NOT EXISTS collected_by text;
--   toplayan ajan veya process
