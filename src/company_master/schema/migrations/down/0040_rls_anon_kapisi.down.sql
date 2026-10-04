-- 0040 geri alma: anon/authenticated icin varsayilan+mevcut yetkiyi eski
-- (acik) haline dondurur.
--
-- UYARI: bu dosya calistirilirsa 7 tablo YENIDEN internete acik hale gelir.
-- Sadece 0040'in kendisi hatali cikarsa kullanilir.

BEGIN;

DO $$
DECLARE
    tablo text;
BEGIN
    FOREACH tablo IN ARRAY ARRAY[
        'ihale_ekler', 'ihale_ilanlari', 'ihale_ilgilendirme_alanlari',
        'ihale_katilimcilar', 'ihale_kaynaklari', 'ihale_takip',
        'sorgu_talepleri'
    ]
    LOOP
        EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY', tablo);
        EXECUTE format('GRANT ALL ON TABLE %I TO anon, authenticated', tablo);
    END LOOP;
END $$;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL ON TABLES TO anon, authenticated;

COMMIT;
