# Brif: ORKESTRA-STALE-TEMIZLIK-01

- **Görev:** Bayat (stale) görev/tetik kalıntılarını temizle
- **Sahip:** yasu
- **Öncelik:** P1

## İş Maddeleri

1. `data/orchestrator/triggers/*.jsonl` içinde `durum: alindi` olup uzun süredir (24 saatten eski) `teslim`/`done` olmamış kayıtları tespit et, listele.
2. Her bir orphan `alindi` kaydı için: ilgili görev board'da hâlâ `aktif` mi kontrol et; değilse tetik kaydını `iptal_stale` yap.
3. `data/orchestrator/decision_log.jsonl` içinde tekrarlayan/geçersiz kayıt var mı denetle, varsa not düş (silme, sadece raporla).
4. `data/orchestrator/file_locks.json` içinde sahibi artık aktif olmayan kilitleri tespit et ve raporla.
5. Bulguları `data/orchestrator/ORKESTRA-STALE-TEMIZLIK-01_rapor_<tarih>_denetim.md` dosyasına yaz.

## Test / Doğrulama

- `python scripts/gorev_kutusu.py bakim` çalıştır, çıktısını rapora ekle.
- `python -X utf8 -m pytest tests/ -q` — mevcut bilinen failure sayısından fazla yeni failure olmamalı.

## Teslim

- `python scripts/gorev_kutusu.py teslim --ajan yasu --task-id ORKESTRA-STALE-TEMIZLIK-01 --ozet "..."`
