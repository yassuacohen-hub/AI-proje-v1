# KPI-HIST-01 — `/api/kpi/history` + gerçek sparkline (kilo, P2)

> Ortak kurallar: `docs/plans/GECE-ZINCIR-03_ortak_kurallar.md`. Zincir halkası 3/4.
> Kaynak: `docs/ROO_ELESTIRI_NOTLARI.md` D-14 (KPI sparkline tek noktalı; tarihçe uç noktası yok).

## Kapsam
- `web_app.py` (kilo kilidi zaten var), `web_dashboard/tabs/ana_kontrol.py`, `tests/test_api_kpi_history.py` (yeni), `tests/test_ana_kontrol*.py`.
- DOKUNMA: `web_dashboard/tabs/__init__.py`, `app.py`.

## İş
1. **Uç nokta:** `GET /api/kpi/history?days=7` (`require_api_key`, `@admin_cache(ttl=300)`, `days` 1–30 sınırı). Yanıt:
   `{"days": 7, "series": {"login": [..7 int..], "search": [..], "yeni_firma": [..]}, "labels": ["2026-09-11", ...]}`
   Kaynak tablolar: `login_events` ve `search_events` (DATA-LOG-01, `ts` kolonu) günlük sayım; `yeni_firma` = `companies.created_at` günlük sayım (kolon yoksa sıfır dizi + `"eksik": ["yeni_firma"]`). SQLite/PostgreSQL uyumlu: `substr(ts,1,10)` yerine `date(ts)` her iki motorda çalışır; `CASE WHEN` tercih, `FILTER` yok.
2. **Ana kontrol kartları:** `ana_kontrol.py` `load_kpi_history()` (`@st.cache_data(ttl=300)`) → `kpi_karti(..., sparkline=series[...])`. En az 3 kart gerçek seri alır: Aktif Kullanıcı (login), Sinyal/Arama (search), Toplam Firma (yeni_firma kümülatif). API hata verirse sparkline boş → kart eskisi gibi çizilir (geriye uyum).
3. Testler: uç nokta 200 + şekil (7 eleman), `days` sınırı (0 → 422 veya 1'e kırp; 31 → 30'a kırp), API key yokken 401; `load_kpi_history` hata → `{}`.

## Teslim kriteri
- Tam süit yeşil; `kodlama_denetim` temiz; `streamlit_restart.py`; Docker API varsa `docker compose up -d --build api` + `curl` doğrulama (yoksa rapora "docker yok" yaz).
- Rapor: `data/orchestrator/KPI-HIST-01_rapor_<tarih>_kilo.md`.
