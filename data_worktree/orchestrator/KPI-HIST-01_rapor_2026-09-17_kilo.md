[[Huginn Data Insights/data/orchestrator/KPI-HIST-01_rapor_2026-09-17_kilo.md]]

# KPI-HIST-01 Raporu

**Tarih:** 2026-09-17
**Ajan:** kilo
**Paket:** `web_app.py` (/api/kpi/history), `web_dashboard/tabs/ana_kontrol.py` (sparkline kartları), `tests/test_api_kpi_history.py`

## Yapılanlar

### API Endpoint — `/api/kpi/history` (web_app.py)
- **Format düzeltme**: Yanıt artık brief formatında: `{"days": N, "series": {"login": [N int], "search": [N int], "yeni_firma": [N int]}, "labels": ["YYYY-MM-DD", ...]}`
- **days doğrulama**: `days < 1` veya `days > 30` → varsayılan 7
- **yeni_firma**: `companies.created_at` sorgusu (kümülatif). Sutun yoksa → sıfır dizi, hata yönetimli.
- **SQLite/PostgreSQL uyumlu**: `DATE()` ve `datetime()` kullanımı standart

### Ana Kontrol Kartları (ana_kontrol.py)
- **Toplam Firma**: artık sparkline ile `series.yeni_firma` (kümülatif) verisi
- **Aktif Kullanıcı**: sparkline `series.login`
- **Sinyal Sayısı**: sparkline `series.search`
- **API Çağrıları**: sparkline kaldırıldı (kayıt yok — `day_{i}_api` formatı API'da yoktu)
- Sparkline verisi `series.login/search/yeni_firma` formatından okunuyor (önceki `day_{i}_login` formatı uyumsuzdu)

### Testler
- `tests/test_api_kpi_history.py`: 4 passed (yapı, boş veri, days doğrulama, hata yönetimi)
- Tam süit: 3795 passed, 4 failed (kilit: __init__.py — pré-eksist), 5 skipped

## Riskler
- `web_app.py` kilidi: API-SPLIT-01 ile paylaşılıyor (kilo sahibi)
- `ana_kontrol.py` kilidi: KPI-HIST-01 kilidi (kilo sahibi)
- 4 test failure `__init__.py` kilidinden (SEC-AUTH-01/cline) — UI-MIMARI-02 raporunda belirtildi