# ADMIN-MUSTERI-02 — Müşteri Yönetimi: placeholder alt sekmeleri gerçek içerikle doldur (kilo, P2)

Ortak kurallar: `docs/plans/GECE-ZINCIR-03_ortak_kurallar.md` (UTF-8, test, restart, commit YOK, rapor).

## Sorun
`web_dashboard/tabs/musteri_yonetimi.py` içinde iki alt sekme boş/yarım:
- `_kullanicilar_onay()` (L63-64) → `st.info("Kullanıcılar & Onay — placeholder")`. Oysa `admin_extras.render_user_management(token)` (bekleyen onaylar + kredi formu) hazır ve test edilmiş (`tests/test_admin_extras_kullanici.py`).
- `_paket_kredi()` (L67-78) yalnız `/api/admin/categories` sayısını gösteriyor; `except Exception: data = None` sessiz. Paket listesi `paketler.load_paketler()` ile mevcut.

## Amaç
Müşteri Yönetimi üst sayfasının 6 alt sekmesinin tamamı gerçek veri göstersin; sessiz except kalmasın.

## Yapılacaklar
| # | İş | Not |
|---|----|-----|
| 1 | `_kullanicilar_onay()` → `st.session_state.get("admin_token")` al; token yoksa `bos_durum("Giriş gerekli", aksiyon="Kimlik sekmesinden giriş yapın")`; varsa `admin_extras.render_user_management(token)` çağır | Tembel import (`from web_dashboard.tabs.admin_extras import render_user_management`) |
| 2 | `_paket_kredi()` → `api_cagir(get_api, "/api/admin/categories")` ile kategori sayısı `kpi_karti`; altına `paketler.load_paketler()` sonucu `_render_paket_tablosu` (demo rozeti korunur) | `company_master.ui.api_cagir` / `hata_kutusu`; `except: data=None` KALDIR |
| 3 | `tests/test_musteri_yonetimi.py`: (a) token yokken `bos_durum` çağrılır, `render_user_management` çağrılmaz; (b) token varken çağrılır; (c) `_paket_kredi` API hatasında `hata_kutusu` çizilir, exception fırlamaz | monkeypatch; mevcut testler kırılmasın |
| 4 | Modül docstring'inde "placeholder" ifadesi kalmasın | grep `placeholder` musteri_yonetimi.py → 0 |

## Kilitli dosyalar
- `web_dashboard/tabs/musteri_yonetimi.py`
- `tests/test_musteri_yonetimi.py`

## Kurallar
- `admin_extras.py`, `paketler.py` **DEĞİŞMEZ** (yalnız import).
- `web_dashboard/tabs/__init__.py` yasak (roo).
- UI-MIMARI-02 aynı dosyaya dokunuyor → bu görev zincirde ondan **sonra** gelir; UI-MIMARI-02'de yaptığın temizliği geri alma.

## Teslim
- `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id ADMIN-MUSTERI-02 --ozet "..."`
- Rapor: `data/orchestrator/ADMIN-MUSTERI-02_rapor_<tarih>_kilo.md`
- Kapsam dışı bulgu: `data/orchestrator/ADMIN-MUSTERI-02_bulgular_<tarih>_kilo.md` (düzeltme YOK)
- `python scripts/streamlit_restart.py` + `python scripts/kodlama_denetim.py` temiz.

## Tahmin
~1.5 saat.


---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]]


- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]
