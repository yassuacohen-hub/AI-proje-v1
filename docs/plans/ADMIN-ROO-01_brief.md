# ADMIN-ROO-01 — Admin sekmeleri hata/boş-durum standardı + canlı/pazarlama/paketler kpi_karti (roo, P1, ceza görevi)

Sahip emri (2026-09-17): "kendine de ceza görevi olarak ≥5 saatlik admin paneli görevi koy; kritik işler olsun; çakışma yaşanmasın; commit yarın."

## Hedef
Admin sekmelerinde API/DB hatası ve boş veri durumlarını tek bileşenle (`src/company_master/ui/components/durum.py`) standartlaştırmak; ham `st.metric` kalan roo-kapsamındaki sekmeleri `kpi_karti`'ya taşımak; `admin_realtime` DB sorgusunu SQLAlchemy 2 uyumlu hale getirmek.

## Kapsam (roo kilitleri — kilo/cline dosyalarına dokunulmaz)
| Aşama | Dosya | İş |
|---|---|---|
| A | `src/company_master/ui/components/durum.py` (YENİ), `src/company_master/ui/__init__.py` | `hata_kutusu(baslik, hata, ipucu=None)`, `bos_durum(mesaj, ikon="📭", aksiyon=None)`, `yukleniyor(mesaj)`; `api_cagir(fn, *, baslik)` sarmalayıcı (try/except → hata_kutusu, None döner) |
| A | `tests/test_ui_durum.py` (YENİ) | bileşen çıktıları + `api_cagir` hata/başarı yolları |
| B | `web_dashboard/tabs/admin_realtime.py` | `load_kpi_from_db` → `text()`; 5 `st.metric` → `kpi_karti`; SSE hatası → `hata_kutusu`; boş veri → `bos_durum` |
| B | `tests/test_admin_realtime_tab.py` (YENİ) | SSE başarısız + DB fallback; text() kullanımı; render hata vermiyor |
| C | `admin_sistem`, `admin_musteriler`, `admin_yonetim`, `admin_extras`, `admin_destek`, `admin_export`, `admin_loading`, `teknik_altyapi`, `proje_yonetimi` | çıplak `requests.get` / `except Exception: pass` kalıpları → `api_cagir` + `hata_kutusu`; boş listeler → `bos_durum` |
| D | `pazarlama.py`, `paketler.py` | `st.metric` → `kpi_karti` (varsa) |
| E | `tests/test_admin_sekme_durum.py` (YENİ) | her kapsam sekmesi: API hatasında exception fırlatmıyor; `except: pass` kalıbı yok (regex) |

## Yasaklar
- `tabs/__init__.py`, `charts.py`, `ana_kontrol.py`, `musteri_yonetimi.py`, `admin_panel.py`, `admin_auto_refresh.py`, `web_app.py`, `admin_auth.py` (kilo/cline kilitleri).
- `kpi_karti` imzası değişmez; yeni kategori eklenmez.
- Commit YOK; sabah sahip/roo kontrol edip commitler.

## Bulgu notları (düzeltme kapsam dışı — rapora yazılır)
- `admin_auth.py::_env_kimlik` DEBUG=1 dalında `return` eksik → `None` unpack riski (cline SEC-AUTH-01'e not).
- `admin_auth.py::render_admin_cikis` `use_container_width=True` eski API.

## Teslim
- `python scripts/streamlit_restart.py`; `python -m pytest tests/test_ui_durum.py tests/test_admin_realtime_tab.py tests/test_admin_sekme_durum.py tests/test_web_dashboard_tabs.py -q`; `python scripts/kodlama_denetim.py`.
- Rapor: `data/orchestrator/ADMIN-ROO-01_rapor_2026-09-17_roo.md`.
- Pano: `review` (sahip sabah onaylar).

## Tahmin
A 1s · B 1.5s · C 2s · D 0.5s · E 0.5s ≈ 5.5 saat.
