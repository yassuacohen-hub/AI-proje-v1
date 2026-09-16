# BATCH-02 — kilo zinciri: NAV-IA-04 → NAV-IA-03 → DATA-LOG-01

**Tarih:** 2026-09-16 · **Karar:** D-37 (batch tur), D-43 · **Kaynak plan:** `docs/plans/NAV-PLAN-01_v4.md` (§2, §3.4, §4, tablo satır 184-187)

## Kurallar (üç görev için ortak — BATCH-01 ile aynı)
- Tanımlar plan dosyasında; burada tekrar edilmez. **Planı oku, plandaki teslim ölçütlerini karşıla.**
- Her görev bitince `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id <ID> --ozet "..."` **zorunlu**. Zincir sonraki halkayı otomatik açar.
- Commit **atma**; roo teslimleri tek commit + PR ile işler.
- UI'ya dokunan her teslimden önce `python scripts/streamlit_restart.py`.
- `web_app.py` değişince `docker compose up -d --build api` + `curl` ile yeni endpoint 404 dışı.
- Kodlama: UTF-8, BOM/NUL yok; `python scripts/kodlama_denetim.py` temiz.
- Hedefli test + tam regresyon: `python -m pytest tests/ -q --continue-on-collection-errors`; sayıları özete yaz.
- Grafik yalnız `web_dashboard/charts.py` yardımcılarıyla (Plotly); **ECharts kodu yok** (D-30).
- Özet biçimi: değişen dosya listesi + test sayısı + eksik/erteleme.
- BATCH-01 çıktıları (`musteri_yonetimi.py`, `TabTanimi.ust`, `ESKI_URL`, `ust_sayfalar()/alt_sekmeler()`) **üzerine** inşa et; yeniden yazma.

## 1) NAV-IA-04 — Sol-alt hesap kartı (plan §3.4)
- Dosyalar: `app.py` (`render_sidebar` altı), `web_dashboard/tabs/admin_auth.py`, `tests/test_dashboard_nav.py` (+ hesap kartı testleri).
- Ölçüt: `st.popover("👤 {email|Misafir}")` içinde rol/süre, "Şifre değiştir" (change-password), "Çıkış" (`admin_cikis`), misafirse "Giriş yap" (AUTH-GATE-01 modalını açar).
- `render_admin_login/cikis/sifre_degistir` kart/modal içine taşınır; `kimlik` ve `yonetim` `SECTIONS`'tan çıkar; `render_yonetim_bilesik` (app.py) kaldırılır, alt paneller ilgili üst sayfalarda çağrılır. `_env_kimlik` yalnız `DEBUG=1`.
- Geriye dönük: eski `?bolum=kimlik|yonetim` adresleri `ESKI_URL` ile ilgili üst sayfaya yönlenir (test).

## 2) NAV-IA-03 — Proje Yönetimi sayfası (plan §2, tablo satır 186)
- Dosyalar: yeni `web_dashboard/tabs/proje_yonetimi.py`, `web_dashboard/tabs/__init__.py` (alt sekme kayıtları), yeni `tests/test_proje_yonetimi.py`.
- Ölçüt: 5 alt sekme, **Karar Defteri en üstte**; `PageHeader` + `Section` (ADMIN-UI-10) deseni, `st.subheader` yok; mevcut render fonksiyonları (karar defteri, görev panosu vb.) yeniden yazılmaz, çağrılır.

## 3) DATA-LOG-01 — Giriş etkinliği + arama kaydı (plan tablo satır 187)
- Dosyalar: `web_app.py` (login ve `/api/companies` arama olaylarını kaydet), yeni migration `src/company_master/schema/migrations/0015_*.sql` (+ `migrate.py` target 15), `web_dashboard/tabs/musteri_yonetimi.py` (Giriş Etkinliği + Aramalar sekmeleri gerçek veri), `tests/test_data_log.py` (yeni).
- Ölçüt: iki tablo (`login_events`, `search_events`; tenant/user/ts/ip-maskeli/sorgu); KVKK: IP son oktet maskeli, e-posta maskeli; SQLite + PostgreSQL uyumlu SQL; API'de kayıt hatası isteği düşürmez (try/except + log).
- Docker rebuild + curl: login sonrası `login_events` satırı oluşuyor.

## Kilit
`app.py`, `admin_auth.py`, `musteri_yonetimi.py`, `web_app.py`, `tabs/__init__.py` zincir sıralı olduğundan çakışma yok; kilit kilo'da kalır, roo onayda düşürür. cline eşzamanlı REV-BATCH-01 yapıyor — **yalnız okur**, dosyalara dokunmaz.
