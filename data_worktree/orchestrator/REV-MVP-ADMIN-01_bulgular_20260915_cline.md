[[Huginn Data Insights/data/orchestrator/REV-MVP-ADMIN-01_bulgular_20260915_cline.md]]

# REV-MVP-ADMIN-01 — MVP Admin 4 Ekran Capraz Denetim (rapor-only)

**Inceleyen:** cline · **Tarih:** 2026-09-15 · **Kapsam:** salt-okunur rapor, kod degisikligi yok
**Denetlenen dosyalar:** `ana_kontrol.py`, `admin_kpi.py`, `admin_panel.py` (render_decision_tab), `admin_extras.py` (render_user_management), `admin_auth.py`, backend uclari (`web_app.py` 2484/2547), `scripts/dash04_api_client.py`, testler (web_dashboard_tabs, admin_extras_kullanici, admin_auth_login, admin_panel_tab, user_settings).

**Dogrulama:** ilgili 5 test dosyasi **103 passed**; `kodlama_denetim.py` temiz (EXIT 0); denetlenen 5 sekme dosyasinda working-tree degisikligi yok.

## Bulgular

### K-1 -- admin_extras.py:57 -- Onayla butonu tier sabit terminal (YUKSEK)
Dosya:satir web_dashboard/tabs/admin_extras.py:57, json tier terminal sabit.
Onem Y (Yuksek). Backend api_admin_approve (web_app.py:2547-2620) tier gore kredi yukler, yalnizca enterprise api_key uretir. UI secici yok; her onay terminal yazilir. Plan (MVP_ADMIN_minimum_canli.md satir 41) tier secimini tanimlamamis, bosluk kodda kalicilasmis.
Oneri: Onay satirina tier secim kutusu eklensin; en azindan takip gorevi acilsin.

### O-1 -- admin_panel.py:250-256 -- render_ayarlar_tab mojibake (ORTA)
Dosya:satir web_dashboard/tabs/admin_panel.py:250-256, Sistem-Ayarlar ve Sekme-rehberi dizeleri cift kodlanmis (bayt duzeyinde dogrulandi C3 A2 C5 A1).
Onem O (Orta). kodlama_denetim.py temiz der cunku BOM/NUL/UTF-16 ariyor, mojibake yakalamiyor: denetim kapsami boslugu. Ayarlar sekmasi MVP 4 ekran disi; render_decision_tab metinleri temiz.
Oneri: 2 dize normalize edilsin, denetime mojibake taramasi eklensin.
### D-1 -- admin_kpi.py:366-369 -- Yenile clear+rerun deseni (DUSUK)
Dosya:satir web_dashboard/tabs/admin_kpi.py:366-369; karsilastir ana_kontrol.py:156-157.
Onem D (Dusuk). clear + rerun buton isleyici icinde sirali; sonsuz dongu riski yok. admin_kpi global clear, ana_kontrol hedefli clear: tutarsiz ama zararsiz. admin_extras onay/kredi sonrasi ayni guvenli desen.
Oneri: tutarlilik icin hedefli clear; zorunlu degil.

### D-2 -- admin_auth.py:22 -- login GET+query sifre (DUSUK, bilincli)
Dosya:satir web_dashboard/tabs/admin_auth.py:22, get_api login params email/password.
Onem D (Dusuk). Backend GET+query bekler (web_app.py:2484); POST 405 doner (MVP-KUL-FIX-01, test_admin_auth_login.py:41-63 sabitli). Stale-token temizligi testli (9-38). Degisiklik kontrati kirar.
Oneri: degisiklik yok; backend POSTa tasinirsa istemciyle birlikte.

## Test kapsami (madde 5)
test_admin_extras_kullanici.py, test_admin_auth_login.py, test_web_dashboard_tabs.py kapsamli; bosluk yok.
Bosluk: K-1 duzeltilirse tier secici icin yeni test gerekir; mevcut test_admin_extras_kullanici.py:104 sabit terminal bekler, guncellenmeli.
Fail-closed dogru: tum sekmeler except APIError ile net uyari (admin_extras.py:26,101; admin_auth.py:28-30).

## Kapsam Disi
Kapsam disi bug gozlenmedi.

## Sonuc
Bulgu sayisi: K:1 / Y:0 / O:1 / D:2. MVP canli cikisi engelleyen bulgu yok.