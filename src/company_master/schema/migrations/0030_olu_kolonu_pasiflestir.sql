-- 0030: `data_quality_score` kolonunu PASIFLESTIR (dusurme, ad degistirme YOK).
--
-- URUN SAHIBI KARARI (D-259): "data quality score dusurulsun ya da pasif hale
-- getirilsin; firma kimlik dosyalari belirli bir olgunluga ulasinca revize edip
-- kullanabiliriz." -> VERI SILINMEZ. 9412 satir oldugu gibi kalir.
--
-- NEDEN AD DEGISTIRMIYORUZ (gerekce, D-258):
--   Ad degisikligi bu projede 7 kez yarim kaldi (indeksler, sema beyani, SQL
--   esikleri, kiracı saglik, dedup silme karari, sabit esik 30.0, ikincil DDL).
--   0024-0028 kolonu tasidi, 0029 indeksleri tasidi. 8. yarim gocu uretmenin
--   anlami yok: kolon zaten OLU (indeks 0, VIEW 0, canli src/ okuyucusu 0).
--   Ad degisikligi riski ekler, deger eklemez.
--
-- NEDEN SADECE MANDAL DA YETMIYOR:
--   Mandal kod tarafini tutar; DB'ye psql ile bakan insan kolonu dolu gorur ve
--   "demek ki kullaniliyor" der. Aciklama VERININ YANINDA durmali.
--
-- SECILEN YOL: COMMENT ON COLUMN (veri + sema tarafi) + tests/test_olu_kolon.py
-- (kod tarafi mandali). Ikisi birlikte; biri digerinin yerini tutmaz.
--
-- OLCUM (2026-09-28):
--   dolu satir : 9412 / 9412  (%100)  -> korunuyor
--   indeks     : 0            (0029 hepsini canli kolona tasidi)
--   VIEW       : 0
--   COMMENT    : yok          -> bu goc ekliyor
--   canli src/ okuyucusu: 0   (D-259'da web_dashboard/js kesildi)
--
-- Idempotent: COMMENT ON COLUMN ayni degeri yeniden yazar, hata vermez.
-- Geri alma: down/0030_olu_kolonu_pasiflestir.down.sql (COMMENT'i sifirlar).

COMMENT ON COLUMN companies.data_quality_score IS
'PASIF (D-259, 2026-09-28). OKUMAYIN, YAZMAYIN. Terk edilmis 0-100 skalali puan; '
'canli puan kolonu identity_completeness (0-10). 9412 satirlik veri BILEREK '
'korunuyor: urun sahibi, firma kimlik dosyalari olgunlasinca bu puani revize edip '
'yeniden kullanmak istiyor. Yeni kodun bu kolona dokunmasi tests/test_olu_kolon.py '
'tarafindan engellenir. Yeniden acmak bir KAHIN karari gerektirir.';
