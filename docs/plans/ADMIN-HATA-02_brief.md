# ADMIN-HATA-02 — Admin sekmelerinde sessiz `except: pass` → loglu/görünür hata (kilo, P2)

Ortak kurallar: `docs/plans/GECE-ZINCIR-03_ortak_kurallar.md` (UTF-8, test, restart, commit YOK, rapor).

## Sorun
Admin sekmelerinde 16 adet sessiz `except Exception: pass` var; API/veri hatası kullanıcıya ve loga hiç düşmüyor, sekme "boş" görünüyor:
- `admin_kpi.py` L94-95, L106-107, L130-131, L198-199, L239-240, L277-278 (6)
- `admin_quality.py` L108-109, L136-137, L225-226 (3)
- `admin_performance.py` L34-35, L69-70, L198-199 (3)
- `ana_kontrol.py` L50-51, L70-71 (2)
- `admin_api_analytics.py` L56-57, L68-69 (2)

Muaf: `admin_dlq.py` L71-72 (`ValueError/TypeError` — bilinçli parse toleransı), `admin_loading.py` (demo).

## Amaç
Her sessiz blok ya `_LOG.warning("...: %s", exc)` ile loglanır ya da veri yükleme fonksiyonlarında `(veri, hata)` döner ve render'da `hata_kutusu` gösterilir. Kullanıcı hatayı görür, geliştirici logda bulur.

## Yapılacaklar
| # | İş | Not |
|---|----|-----|
| 1 | Her dosyaya `_LOG = logging.getLogger(__name__)` (yoksa) | Mevcut logger adı varsa onu kullan |
| 2 | `@st.cache_data` yükleme fonksiyonlarındaki `except Exception: pass` → `except Exception as exc: _LOG.warning("<fonksiyon> basarisiz: %s", exc)`; dönüş değeri **değişmez** (`{}`/`None`) | Cache'lenen fonksiyonun imzası/dönüş tipi sabit kalır — testler kırılmasın |
| 3 | Render içindeki (cache dışı) sessiz bloklar → `hata_kutusu("Veri yüklenemedi", exc, ipucu="API 8000 ayakta mı?")` | `company_master.ui.hata_kutusu` |
| 4 | Test: `tests/test_admin_sessiz_except.py` (YENİ) — AST ile 5 dosyada `ExceptHandler` gövdesi yalnız `Pass` olan blok sayısı **0**; muaf listesi (`admin_dlq.py`) açıkça yazılır | `ast.walk`, `isinstance(node.body[0], ast.Pass)` |
| 5 | Her dosya için 1 monkeypatch testi: yükleme fonksiyonu exception fırlatınca `caplog`'da WARNING var ve dönüş boş | Mevcut `tests/test_admin_performance.py`, `tests/test_admin_kpi*.py` vb. dosyalara ekle |

## Kilitli dosyalar
- `web_dashboard/tabs/admin_kpi.py`
- `web_dashboard/tabs/admin_quality.py`
- `web_dashboard/tabs/admin_performance.py`
- `web_dashboard/tabs/ana_kontrol.py`
- `web_dashboard/tabs/admin_api_analytics.py`
- `tests/test_admin_sessiz_except.py` (YENİ) + ilgili mevcut test dosyaları

## Kurallar
- Bu görev ADMIN-KPI-KART-01 ve KPI-HIST-01 ile aynı dosyalara dokunuyor → zincirde **onlardan sonra**; onların değişikliklerini geri alma.
- `st.error` yerine `hata_kutusu`; `print` YASAK.
- `web_dashboard/tabs/__init__.py` L619-623'teki sessiz blok **roo'nun** (ADMIN-NAV-HAZIR-01) — dokunma.

## Teslim
- `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id ADMIN-HATA-02 --ozet "..."`
- Rapor: `data/orchestrator/ADMIN-HATA-02_rapor_<tarih>_kilo.md`
- Kapsam dışı bulgu: `data/orchestrator/ADMIN-HATA-02_bulgular_<tarih>_kilo.md` (düzeltme YOK)
- `python scripts/streamlit_restart.py` + `python scripts/kodlama_denetim.py` temiz.

## Tahmin
~2 saat.
