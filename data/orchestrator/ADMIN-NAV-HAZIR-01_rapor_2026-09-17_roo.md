# ADMIN-NAV-HAZIR-01 — Navigasyon SSOT Temizligi (roo)

- **Tarih:** 2026-09-17
- **Ajan:** roo (orkestrator, kendi gorevi)
- **Brif:** `docs/plans/ADMIN-NAV-HAZIR-01_brief.md`
- **Kapsam:** `web_dashboard/tabs/__init__.py`, `tests/test_admin_sekme_durum.py`

## 1. Bulgular (teslim oncesi durum)

| # | Bulgu | Yer | Etki |
|---|-------|-----|------|
| B1 | `veri_kalite` bolumu `hazir=False`, `bekleyen_gorev="NAV-IA-01"` | `__init__.py` SECTIONS | NAV-IA-01 bitmis olmasina ragmen UI'da "hazirlaniyor" placeholder cikiyordu |
| B2 | `musteri_onizleme` bolumu `hazir=False`, `bekleyen_gorev="NAV-IA-02"` | `__init__.py` SECTIONS | Ayni sekilde bayat placeholder |
| B3 | `veri_kalite` TabTanimi blogu 0 bosluk girintili (digerleri 4) | `__init__.py` SECTIONS | Okunabilirlik/bicim bozuklugu |
| B4 | `except Exception: pass` (sessiz yutma) | `tab_url_getir()` | Hata gorunmezligi; proje kuralina aykiri |

## 2. Yapilan Degisiklikler

| Dosya | Degisiklik |
|-------|-----------|
| `web_dashboard/tabs/__init__.py` | `veri_kalite` → `hazir=True`, `bekleyen_gorev` alani kaldirildi, girinti 4 bosluga duzeltildi |
| `web_dashboard/tabs/__init__.py` | `musteri_onizleme` → `hazir=True`, `bekleyen_gorev` alani kaldirildi |
| `web_dashboard/tabs/__init__.py` | `import logging` + `_LOG = logging.getLogger(__name__)` eklendi |
| `web_dashboard/tabs/__init__.py` | `tab_url_getir()` sessiz except → `except Exception as exc:  # noqa: BLE001` + `_LOG.debug("session_state yok: %s", exc)` |
| `tests/test_admin_sekme_durum.py` | Yeni regresyon testi: `test_tabs_init_bekleyen_gorev_panoda_done` + `_pano_gorevleri()` / `_bitmis_gorev_kumesi()` yardimcilari |

## 3. Regresyon Testi Tasarimi

- Pano kaynagi: `data/orchestrator/task_board.json` (gercek dosya adi; `pano.json` yok).
- Pano `done`/`review` gorevleri toplanir; **pano okunamazsa** sabit `BITMIS_GOREVLER = {"NAV-IA-01", "NAV-IA-02"}` kullanilir.
- `pytest.skip` **kullanilmaz** — brif geregi test her ortamda kanit uretir (CI'da pano dosyasi olmasa bile calisir).
- Dogrulama: `SECTIONS` icindeki hicbir `bekleyen_gorev`, bitmis gorev kumesinde olmamali.

## 4. Dogrulama

| Kontrol | Sonuc |
|---------|-------|
| `pytest tests/test_admin_sekme_durum.py -q -rs` | **71 passed**, skip yok |
| `pytest tests/test_admin_sekme_durum.py tests/test_sayfa_iskeleti.py -v` (duzeltme oncesi) | 161 passed, 1 skipped → skip kaldirildi |
| `python scripts/kodlama_denetim.py` | Degistirilen iki dosya icin **uyari yok** (cikti yalnizca GIT-HIJYEN-01 backlog'undaki eski dosyalari listeliyor) |
| `python scripts/streamlit_restart.py` | Basarili — PID 24552, `http://127.0.0.1:8501` saglik ok |

## 5. Notlar / Kalan

- `render_fonksiyonu()` (L668-671) icinde de bir `except Exception: pass` var; brif kapsaminda **degildi**, dokunulmadi. Lazy import hatasini yutuyor → ayri gorev onerisi (**ADMIN-NAV-HAZIR-02**).
- `web_dashboard/tabs/admin_auth.py` icinde 2 sessiz except (L47-49, L121-123) tespit edildi → ayni takip gorevine dahil edilebilir.
- **Commit YOK** (sahip karari: commit sabah toplu atilacak).


---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]


- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]
