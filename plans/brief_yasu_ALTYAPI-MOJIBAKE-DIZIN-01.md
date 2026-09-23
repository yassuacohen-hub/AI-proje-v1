# Brif — ALTYAPI-MOJIBAKE-DIZIN-01 (yasu)

## Görev Özeti
`scripts/mojibake_onar.py` yalnız tek dosya alıyor. Vault genelinde bozuk
karakter taraması için dizin argümanı gerekiyor.

## Yapılacak
1. `--dizin <yol>` argümanı ekle: verilen dizini `**/*.md` ile gez.
2. `--dizin` ve tek dosya argümanı **birbirini dışlar** (argparse mutually exclusive group).
3. Varsayılan davranış **kuru çalışma** (dry-run) olsun; yazma için `--uygula` şartı.
   Toplu dosya yazan araçta varsayılanın yazmak olması veri kaybı riskidir.
4. Özet satırı bas: `taranan=N degisen=M` — 0 değişiklikte de satır çıkmalı.

## Çıktı
- `scripts/mojibake_onar.py`
- `tests/test_mojibake_dizin.py` — 2 test: dizin taraması bozuk dosyayı bulur;
  `--uygula` olmadan dosya diskte DEĞİŞMEZ.

## Doğrulama
```
python -m pytest tests/test_mojibake_dizin.py -q
python scripts/mojibake_onar.py --dizin "Huginn Data Insights/plans"
```

## Kurallar
- D-48: minimum diff, mevcut tek-dosya yolunu bozma (geri uyumlu kal).
- D-86: Windows cmd.exe; yol argümanlarını tırnak içinde test et (boşluklu dizin var).

## Süre Tahmini
2s

## İlgili Nodlar
- [[AGENTS]]
