-- D-307: Supabase lint — search_path_mutable (KAHIN 2026-09-29)
-- uretim: 2026-09-29T23:04:50
--
-- Bu fonksiyonlar TRIGGER'dir; tam yol/tablo adiyla cagrilir.
-- search_path sabitlemek davranisi DEGISTIRMEZ, yalnizca
-- guvenlik sertlestirir (supabase_lint aramasi).


-- pg_trgm extension'ini public semadan 'extensions' semasina
-- tasi (supabase_lint: extension_in_public). Diger tum
-- extension'lar zaten 'extensions' semasinda; bu tutarli.
-- Operator siniflari GLOBAL nesnedir; indeksler OID uzerinden
-- bagli oldugu icin tasima indeksleri bozmaz.
CREATE SCHEMA IF NOT EXISTS extensions;
ALTER EXTENSION pg_trgm SET SCHEMA extensions;
