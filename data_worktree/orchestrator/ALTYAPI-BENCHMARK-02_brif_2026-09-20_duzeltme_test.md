# Brief (DÜZELTME): ALTYAPI-BENCHMARK-02 — Rapor Doldurma

**Görev ID:** ALTYAPI-BENCHMARK-02
**Sahip:** SALİH (Test Danışman)
**Öncelik:** P2
**Tahmini Süre:** 1s
**Tür:** Geri gönderim (rapor eksik)

---

## NEDEN GERİ GELDİ

Görev `done` işaretlenmişti, ancak rapor dosyası **boş şablon** halindeydi.

Dosya: `data/orchestrator/ALTYAPI-BENCHMARK-02_rapor_2026-09-20_denetim.md`

Tespit edilen eksikler:

| # | Bölüm | Durum |
|---|-------|-------|
| 1 | `## Degisen dosyalar` | `- (doldur)` — doldurulmamış |
| 2 | `## Test sonuclari` → `Sonuc:` | `(doldur)` — doldurulmamış |
| 3 | `## Bulgular` renk tablosu (4 satır) | Tüm satırlar `(doldur)` |
| 4 | `## Bulgular` giriş metni | D-67 şablon talimatı silinmemiş |
| 5 | `## Eksik / erteleme` | `- (yoksa "yok" yaz)` — şablon metni kalmış |

Buna rağmen üst tabloda `Durum | 🟢 tamam` yazıyordu. **D-67 ihlali.**

---

## YAPILACAK İŞ

### 1. Ölçüm verisinin varlığını doğrula
`docs/raporlar/benchmark_2026-09-20.md` dosyasını aç.
- **Varsa ve 4 tablo doluysa:** Adım 2'ye geç.
- **Yoksa veya tablolar boşsa:** Ölçümü gerçekten yap (orijinal brif: `ALTYAPI-BENCHMARK-02_brif_2026-09-20_test.md`, İŞ MADDELERİ bölümü).

### 2. Raporu doldur
`data/orchestrator/ALTYAPI-BENCHMARK-02_rapor_2026-09-20_denetim.md` içindeki **her `(doldur)` yerini** gerçek veriyle değiştir:

- **Degisen dosyalar:** Gerçek dosya listesi. Hiçbir dosya değişmediyse `- Dosya değişmedi (ölçüm görevi).` yaz.
- **Test sonuclari:** `python -X utf8 -m pytest tests/ -q` çalıştır, çıkan sayıyı yaz (ör. `1413 passed, 6 failed`).
- **Bulgular tablosu:** `docs/raporlar/benchmark_2026-09-20.md` ölçümlerinden çıkan gerçek bulgular. Her satır için bulgu metni + oran. Bulgu yoksa satırı sil, `- Bulgu yok.` yaz.
- **Bulgular giriş metni:** D-67 talimat satırlarını (`- D-67: bos birakilamaz...` ve `- Renkli siniflandirma:...`) **sil**. Bunlar şablon açıklaması, rapor içeriği değil.
- **Eksik / erteleme:** Gerçek eksik varsa yaz, yoksa `- yok` yaz.

### 3. Durum alanını dürüst işaretle
Üst tablodaki `Durum` satırı:
- Tüm ölçümler tamsa → `🟢 tamam`
- Kısmi ölçüm varsa → `🟡 kismi` + `Eksik / erteleme` bölümünde ne eksik olduğunu yaz

---

## YASAK

- `(doldur)` metni raporda kalamaz. Teslim öncesi `findstr /C:"(doldur)" <dosya>` ile kontrol et, çıktı boş olmalı.
- Ölçüm yapmadan tablo doldurmak. Veri yoksa ölç, uyduramazsın.
- Rapor dosyası ve `docs/raporlar/benchmark_2026-09-20.md` dışına dokunma.

---

## TESLİM

- Rapor yazımı ve teslim komutları **YASU üzerinden** yürür (D-59).
- Teslim öncesi kendi kontrolün:
  1. `findstr /C:"(doldur)" data\orchestrator\ALTYAPI-BENCHMARK-02_rapor_2026-09-20_denetim.md` → çıktı boş
  2. `## Bulgular` başlığı var ve altında gerçek bulgu var
  3. Rapor UTF-8, BOM yok

---

## DEĞERLENDİRME KRİTERLERİ

1. ✓ Raporda hiç `(doldur)` yok
2. ✓ D-67 şablon talimat satırları silinmiş
3. ✓ Bulgular gerçek ölçüm verisine dayanıyor
4. ✓ Test sonucu sayısı yazılı
5. ✓ Durum alanı gerçek duruma uygun
