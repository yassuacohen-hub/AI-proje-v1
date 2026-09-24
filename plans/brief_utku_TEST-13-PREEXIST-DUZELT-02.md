# Brief: TEST-13-PREEXIST-DUZELT-02

## Bağlam

TEST-13-PREEXIST-DUZELT-01 raporu (`data/orchestrator/TEST-13-PREEXIST-DUZELT-01_rapor_2026-09-23_utku.md`)
"13 pre-existing test failure tamamen giderildi" diyor ancak orkestratör doğrulaması
(tam `pytest` suite'i, worktree kökünden) **7 failed** gösterdi:

```
FAILED tests/test_app_menu_rol.py::test_admin_token_menuyu_buyutur
FAILED tests/test_d66_bypass_tetikleme.py::test_bypass_logging_kaydedilir
FAILED tests/test_d87_atama_otomasyonu_fixed.py::test_dash_ux_02b_atanabiliyor
FAILED tests/test_d87_atama_otomasyonu_fixed.py::test_brifsiz_atama_reddedilir
FAILED tests/test_d87_atama_otomasyonu_fixed.py::test_case_insensitive_lookup
FAILED tests/test_dashboard_nav.py::test_alt_sekmeler_sistem_analyst
FAILED tests/test_naming_audit.py::test_muafiyet_listesi_bayatlamadi
```

`test_d87_atama_otomasyonu_fixed.py` orijinal brief'te (DUZELT-01) açıkça 13 hedeften
biri olarak listelenmişti (3 test) — rapor bu dosyaya hiç değinmemiş, kaynak kod
düzeltmesi yapılmamış.

## Görev

1. `test_d87_atama_otomasyonu_fixed.py` — 3 test, kök nedeni bul, düzelt:
   - `test_dash_ux_02b_atanabiliyor`
   - `test_brifsiz_atama_reddedilir`
   - `test_case_insensitive_lookup`
2. `test_app_menu_rol.py::test_admin_token_menuyu_buyutur` — kök nedeni bul, düzelt.
3. `test_dashboard_nav.py::test_alt_sekmeler_sistem_analyst` — kök nedeni bul, düzelt.
4. `test_d66_bypass_tetikleme.py::test_bypass_logging_kaydedilir` — brief'te "flaky,
   izole geçiyor" olarak zaten not edilmişti; izole/tam-suite farkının kök nedenini
   (state sızması) araştır, mümkünse gider. Gerekçeli notla erteleme kabul edilir.
5. `test_naming_audit.py::test_muafiyet_listesi_bayatlamadi` — **DOKUNMA**, bu ihsan'ın
   pano hijyeni işi (MUAF listesinden düşmesi gereken kapanmış görevler).

## Kabul kriteri

Tam `pytest` suite'i (worktree kökünden, `python -m pytest -q`) çalıştırılıp gerçek
sonuç (fail sayısı dahil) rapora yazılır — kısmi/alt-dosya sonucu değil. Kalan her
fail için gerekçeli not zorunlu.
