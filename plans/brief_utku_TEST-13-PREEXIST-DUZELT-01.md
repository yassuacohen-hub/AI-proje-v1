# Brief: TEST-13-PREEXIST-DUZELT-01

## Bağlam

Roo'nun 4-fix oturumu (SSE trailer parse, dialog refactor, admin_auth temizlik) sonrası
tam `pytest` suite'inde 13 test hatası tespit edildi. `git stash` ile doğrulandı: bu
hatalar oturumun dokunduğu 3 dosyadan (`ninerouter_client.py`, `admin_auth.py`, `app.py`)
bağımsız — **önceden var olan, ilgisiz hatalar**.

Detay: [`d193_menu_e2e_report.md`](../d193_menu_e2e_report.md) sonundaki
"Ek Bulgu: Tam Test Suite'te 13 Pre-Existing Hata" bölümü.

## Görev

1. Aşağıdaki 13 testi tek tek çalıştır, gerçek kök nedeni bul, düzelt:
   - `test_admin_performance.py` (3 test)
   - `test_d87_atama_otomasyonu_fixed.py` (3 test)
   - `test_marka_denetim_muafiyet.py::test_kok_denetimi_temiz`
   - `test_naming_audit.py::test_acik_gorevlerde_yeni_d57_ihlali_yok`
   - `test_sayfa_iskeleti.py::test_ekranda_subheader_kalmaz[admin_panel]`
   - `test_tabs_ia.py::test_menudeki_alt_sekme_sayisi`
   - `test_user_settings.py::test_panel_formu_sema_uzerinden_uretir`
2. Ayrıca 2 flaky testi incele (regresyon değil ama kök neden belirsiz):
   - `test_app_menu_rol.py::test_admin_token_menuyu_buyutur`
   - `test_d66_bypass_tetikleme.py::test_bypass_logging_kaydedilir`
   - İzole çalıştırıldığında hep geçiyor, tam suite'te bazen fail. Muhtemel neden:
     Streamlit `AppTest` session-state veya dosya sistemi durumunun testler arası
     sızması (pollution/order-dependency).

## Kabul kriteri

Tam `pytest` suite'i (worktree kökünden) yeşil veya kalan hatalar için gerekçeli not.
