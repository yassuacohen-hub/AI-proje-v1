# VAULT-CLEANUP-BATCH — Brif

**Tarih:** 2026-09-23
**Sahip:** İHSAN (Orkestratör/Yönetim)
**Öncelik:** P2
**Mod:** code

## Amaç

ORKESTRA-VAULT-TEKRAR-01 audit raporundaki 3 sorunu kapat.

## Kapsam

1. **`.ALARM*` dosyaları:** `data/orchestrator/` altındaki bayat alarm dosyalarını say, içerikleri done görevlere aitse `_trash/` altına taşı (sil değil, geri alınabilir).
2. **UTF-8 temizliği:** `triggers/*.jsonl` BOM/mojibake kontrolü (`scripts/mojibake_onar.py --kontrol`).
3. **Arşivleme:** tetik dosyalarındaki `done` kayıtları arşive taşı; aktif kuyruğu kısalt.

## Kabul Kriterleri

1. Her adımın önce/sonra sayısı raporda.
2. Hiçbir dosya kalıcı silinmemiş (taşıma ile geri alınabilir).
3. `python scripts/gorev_kutusu.py bak --ajan ihsan` hâlâ çalışıyor (tetik dosyaları bozulmamış).
4. BOM yok, UTF-8.

## Kısıt

- Commit yok.
- Aktif (`bekliyor`/`alindi`) tetik kaydına dokunulmaz.
