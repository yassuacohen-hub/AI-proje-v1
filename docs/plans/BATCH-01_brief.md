# BATCH-01 — kilo zinciri: AUTH-GATE-01 → NAV-IA-01 → NAV-IA-02

**Tarih:** 2026-09-16 · **Karar:** D-37 (batch tur) · **Kaynak plan:** `docs/plans/NAV-PLAN-01_v4.md` (bölüm 2.2, 2.3, 3, 4 ve tablo satır 181-186)

## Kurallar (üç görev için ortak)
- Tanımlar plan dosyasında; burada tekrar edilmez. **Planı oku, plandaki teslim ölçütlerini karşıla.**
- Her görev bitince `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id <ID> --ozet "..."` **zorunlu** (NAV-FIX-02'de atlandı). Zincir sonraki halkayı otomatik açar.
- Commit **atma**; roo üç teslimi tek commit + PR ile işler.
- UI'ya dokunan her teslimden önce `python scripts/streamlit_restart.py`.
- `web_app.py` değişince `docker compose up -d --build api` + `curl` ile yeni endpoint 404 dışı.
- Kodlama: UTF-8, BOM/NUL yok; `python scripts/kodlama_denetim.py` (varsa) veya elle doğrula.
- Hedefli test + tam regresyon: `python -m pytest tests/ -q --continue-on-collection-errors`; sayıları özete yaz.
- Özet biçimi: değişen dosya listesi + test sayısı + eksik/erteleme.

## 1) AUTH-GATE-01 — Giriş kapısı modalı (plan §3)
- Dosyalar: `src/company_master/ui/components/modal.py` (`kapatilabilir: bool = True`), `web_dashboard/tabs/admin_auth.py`, `app.py` (`main()`), `web_app.py` (+2 endpoint: `POST /api/admin/login`, şifre sıfırlama), `tests/test_auth_gate.py` (yeni).
- Ölçüt: modal kapatılamıyor; giriş / misafir devam / şifremi unuttum akışları; `_env_kimlik` yalnız `DEBUG=1`; Docker rebuild + curl.
- `st.dialog(dismissible=False)` sürüm desteği yoksa CSS + ESC engeli, testte belgele.

## 2) NAV-IA-01 — Menü ağacı (plan §2.2, §2.3)
- Dosyalar: `web_dashboard/tabs/__init__.py` (`TabTanimi.ust_sayfa`, `ESKI_URL`), `app.py` sidebar, `tests/test_dashboard_nav.py`, `tests/test_app_menu_rol.py`.
- Ölçüt: 6 üst öğe; eski url yönlendirme testleri; `kimlik/yonetim/sistem` menüden kalktı; `GRUP_IS/GRUP_SISTEM` geriye dönük korunur; ortak `yenile()` yardımcısı (D-1).

## 3) NAV-IA-02 — Müşteri Yönetimi (plan §4)
- Dosyalar: yeni `web_dashboard/tabs/musteri_yonetimi.py`, `web_dashboard/tabs/admin_extras.py` (K-1: tier selectbox JSON'a bağlanır), `tests/test_musteri_yonetimi.py` (yeni).
- Ölçüt: 6 alt sekme (Kullanıcılar, Paket/Kredi, Giriş Etkinliği, Aramalar, Destek, Dışa Aktarma); tier seçimi doğru gidiyor (test).

## Kilit
`app.py` üç görevde de değişiyor → zincir sıralı olduğundan çakışma yok; kilit kilo'da kalır, roo onayda düşürür.

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]]


- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
