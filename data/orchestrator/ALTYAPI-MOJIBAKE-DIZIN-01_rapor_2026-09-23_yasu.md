# ALTYAPI-MOJIBAKE-DIZIN-01 Raporu

- **Sahip**: Yasu
- **Tarih**: 2026-09-23
- **Durum**: ✅ Tamamlandı

## Değişiklikler — `scripts/mojibake_onar.py`

1. **`--dizin <yol>`** eklendi: dizini `**/*.md` ile gezer (alt dizinler dahil).
2. **Karşılıklı dışlama**: `--dizin` ile dosya argümanı aynı anda verilemez
   (argparse değil manuel kontrol — pozisyonel argüman grubuyla temiz çıkmıyor;
   `return 2` ile hata).
3. **Dry-run varsayılan** (dizin modu): yazmak için açıkça `--uygula` şart.
   Tek-dosya modu **eski davranışını korudu** (D-48 geri uyum: varsayılan yazar,
   `--kontrol` yalnız rapor).
4. **Özet satırı**: `taranan=N degisen=M` — hem dizin hem tek-dosya modunda,
   0 değişiklikte de basılır.

## Testler — `tests/test_mojibake_dizin.py` (7 test)

- ✅ dizin taraması bozuk dosyayı bulur (alt dizin dahil)
- ✅ `--uygula` olmadan disk değişmez (dry-run guvencesi)
- ✅ `--uygula` ile yazar, cp1252 izleri temizlenir
- ✅ `--dizin` + dosya argümanı birlikte verilirse hata (dışlama)
- ✅ boş dizinde `taranan=0 degisen=0` satırı çıkar
- ✅ tek-dosya geri uyum: eski çağrım yazmaya devam eder (D-48)
- ✅ `--kontrol` davranışı korunur (yazma yok)

**Sonuç: 7/7 PASSED (1.06s)**

Not: Test dosyası bilinçli olarak **saf ASCII + unicode escape** yazıldı —
test kaynak dosyasının kendisi mojibake taşıyıp kendi doğruluğunu
kaybetmesin (ilk denemede test dosyası yazım sırasında bozulmuştu; bu bir
araç zinciri bulgusu olarak not edildi: editör → dosya yazımında cp1254/UTF-8
geçişleri mojibake üretebiliyor; kodlama_denetim.py ratchet'ine test dosyaları
da dahil olmalı).

## Doğrulama (gerçek koşu)

```
python scripts/mojibake_onar.py --dizin "plans"
→ plans/ altında 45 .md tarandı, degisen=0 (plans temiz)
```
