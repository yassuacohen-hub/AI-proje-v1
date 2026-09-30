-- 0040: P0 guvenlik kapisi -- internete acik 7 tablo + kok neden.
--
-- veri-gocu: bu dosya YENI TABLO veya KOLON OLUSTURMAZ. Yalniz yetki ve
--   RLS ayarlar; izi semada gorunmez. Defter bir tablo bekledigi icin
--   "IZSIZ" raporlanir, ancak bu bir arac siniri, eksik uygulama DEGILDIR.
--   Kanit (2026-09-30 olcumu): `goc_defteri.py` bu dosyayi IZSIZ gosterir,
--   ama dosya defterde ve sema uygulamasi dogrulanmistir:
--     RLS 52/52 acik, anon/authenticated tablo GRANT'i 0.
--   D-267: izsizlik bir seyse YAZILMALIDIR; yazilmamis izsiz, bugun yanlis
--   alarm uretir, yarin gercek alarmi gizler. Burada yaziyor.
--
-- OLCUM (data/_tmp/olcum2.txt, 2026-09-29): 7 public tablo RLS kapali VE
-- pg_default_acl semada anon/authenticated rollerine varsayilan olarak
-- arwdDxtm (TRUNCATE dahil) veriyor. Yani sorun tek tek tablo degil, KURAL:
-- bu kural duzeltilmezse yeni her tablo yine acik doguyor.
--
-- Iki adim, bu sirayla: once VARSAYILANI kapat (gelecek), sonra MEVCUT
-- 7 tabloyu RLS ile kilitle (simdi). Sira onemli degil ama ikisi de sart.

BEGIN;

-- 1) Gelecekteki tablolar icin varsayilan yetkiyi kapat.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    REVOKE ALL ON TABLES FROM anon, authenticated;

-- 2) Su an acik olan 7 tablo: mevcut yetkiyi geri al + RLS ac.
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
        EXECUTE format('REVOKE ALL ON TABLE %I FROM anon, authenticated', tablo);
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tablo);
    END LOOP;
END $$;

COMMIT;
