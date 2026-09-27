# Brief — ALTYAPI-MOJIBAKE-BARIYER-01 (P0)

## Kök Neden
2026-09-23'te `scripts/mojibake_onar.py` tek-dosya modunda **doğru UTF-8** kaynak
dosyalar üzerinde ters yönde çalıştı: `Görev` -> `GÃ¶rev`. 110 satır bozuldu,
regresyon 7 -> 14 kırmızıya çıktı. Araç kendi hasarını ölçmüyor.

## Bulgular
- `dosya_onar` (L79): `if not kontrol and duzeltilen:` -> **hasar delta kontrolü yok**.
- `kalan` (L81) yazımdan **sonra** hesaplanıyor; bariyer olarak kullanılmıyor.
- Tek-dosya modunda uzantı filtresi yok; `.py` dosyaları da onarılabiliyor.
- L140 özet satırı `kalan` sayısını `degisen=` etiketiyle basıyor (yanlış etiket).

## Yapılacaklar
1. `dosya_onar` içinde onarım **öncesi** hasar sayılsın (`onceki`).
2. `kalan > onceki` ise **yazma yok**, `IPTAL` satırı basılsın, `duzeltilen=0` dönsün.
3. Tek-dosya modunda kaynak uzantıları (`.py/.json/.yml/.yaml/.toml/.ini/.cfg`)
   için `--zorla` olmadan reddet (exit 3).
4. L140 etiket hatasını düzelt: gerçek değişen sayısı basılsın.
5. En az 2 test: (a) temiz UTF-8 dosya değişmeden kalır, (b) `.py` reddedilir.

## Dosyalar
- `scripts/mojibake_onar.py`
- `tests/test_mojibake_bariyer.py`

## Kabul
- Yeni testler yeşil, regresyon 7 kırıktan fazla olmasın.
- `python scripts/mojibake_onar.py <temiz.md>` dosyayı değiştirmez.

## Sahibi
ihsan — mod: code
