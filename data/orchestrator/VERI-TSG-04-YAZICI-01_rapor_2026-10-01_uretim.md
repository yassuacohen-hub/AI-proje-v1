# VERI-TSG-04-YAZICI-01 Raporu — 3 eksik tamamlandı (2026-10-01)

## Ne yapıldı

1. **`olay_esle()` prefix matching eklendi** — `skills/services/ticaret_sicili_kanit.py:183`
   - Tam eşleşmeyen 18 `il_turu` değeri için prefix/substring matching eklendi.
   - Uzun anahtarlar önce denenir (kısa anahtarın uzun metne prefix olarak eşleşmesi önlenir).
   - Case-insensitive karşılaştırır.
   - Eşleme oranı: **20/20 → 38/38** (tüm kanıt dosyaları eşleşiyor).

2. **`get_engine()` database gate kullanılmaya başlandı** — `src/company_master/etl/tsg_yazici.py:127`
   - `_veritabani_baglantisi()` silindi, `get_engine()` import edildi.
   - `os` / `Any` kullanılmayan importlar temizlendi.

3. **Zincir testi (D-288) yazıldı** — `tests/test_tsg_zincir.py` (7 test)
   - `test_kanit_dosyalari_okunur`, `test_ilan_turu_normalize`, `test_olay_esle_tum_kanitlar_eslesin`
   - `test_olay_esle_bos`, `test_source_guid_benzersiz`, `test_pipeline_sonuc_sinifi`
   - `test_pipeline_get_engine_kullanimi` (import + kaynak kontrolü)

## Değişen dosyalar

- `skills/services/ticaret_sicili_kanit.py` — `_ILAN_TURU_SIRALI` + `_prefix_esle()` + `olay_esle()`fixed
- `src/company_master/etl/tsg_yazici.py` — `get_engine()` gate, import temizliği
- `tests/test_tsg_zincir.py` — 7 test (yeni)

## Test sonuçları

```
tests/test_tsg_zincir.py — 7 passed, 0 failed
```

## Bulgular

- 🟢 Eşleme 38/38 — prefix matching ile tüm kanıt dosyaları eşleşiyor
- 🟢 `get_engine()` gate uygulandı — `_veritabani_baglantisi()` kaldırıldı
- 🟢 Zincir testi 7/7 yeşil

## Eksik / erteleme

- Yok