# ADMIN-KPI-KART-01 — Admin sekmelerinde `st.metric` → `kpi_karti` (kilo, P2)

Ortak kurallar: `docs/plans/GECE-ZINCIR-03_ortak_kurallar.md` (UTF-8, test, restart, commit YOK, rapor).

## Amaç
Admin panelindeki ~31 ham `st.metric` çağrısını tek görsel dile (`web_dashboard/charts.py::kpi_karti`) taşımak. `admin_kpi.py` zaten bu yolu kullanıyor; referans o. `admin_executive.py` ve `admin_search.py` de aynı kalıba geçirildi (roo, 2026-09-17) — ikisi de örnek olarak incelenebilir.

## Kapsam (kilitli dosyalar)
| Dosya | st.metric | Kategori önerisi |
|---|---|---|
| `web_dashboard/tabs/admin_cost.py` | 4 (L520-541) | `maliyet` / `uyari` |
| `web_dashboard/tabs/admin_quality.py` | 4 (L395-401) | `kalite` |
| `web_dashboard/tabs/admin_performance.py` | ~10 (L115-186; biri döngüde `st.metric(k, v)`) | `sistem` |
| ~~`web_dashboard/tabs/admin_executive.py`~~ | ✅ roo bitirdi (ADMIN-EXEC-01) | **DOKUNMA** |
| `web_dashboard/tabs/admin_api_analytics.py` | 8 (L117-193) | `sistem` |
| `web_dashboard/tabs/admin_dlq.py` | 6 (L100-132) | `uyari` / `sistem` |
| `web_dashboard/tabs/admin_audit.py` | 5 (L168-176) | `guvenlik` |
| ~~`web_dashboard/tabs/admin_search.py`~~ | ✅ roo bitirdi (ADMIN-SEARCH-01) | **DOKUNMA** |
| `tests/test_admin_dlq_tab.py`, `tests/test_web_dashboard_tabs.py` | `admin_dlq.st.metric` monkeypatch → `kpi_karti` monkeypatch'e çevir |
| `tests/test_admin_kpi_kart.py` (YENİ) | her sekmede `st.metric` çağrısı kalmadığını AST/regex ile doğrula |

## Kurallar
1. `kpi_karti` imzası DEĞİŞMEZ (`charts.py` senin UI-MIMARI-02 kilidinde ama imza sözleşmesi ana_kontrol/admin_kpi tarafından kullanılıyor). Eksik parametre gerekirse yeni **opsiyonel** kwarg ekle, mevcut çağrıları kırma.
2. `delta` varsa aynen aktar; `help=` → `yardim=`; sayı formatı `sayi_formatla` üzerinden (ondalik/birim).
3. `kategori` yoksa `KATEGORI_RENK` anahtarlarından seç; yeni kategori eklemek yasak (token sistemi).
4. Döngü içindeki metrik (`admin_performance`) `st.columns` + `kpi_karti` ile; kolon sayısı ≤ 4.
5. Test: her sekmenin `render_*` fonksiyonu `streamlit` mock ile çağrılınca hata vermemeli; toplam test sayısı düşmemeli.
6. `python scripts/kodlama_denetim.py` temiz; `python scripts/streamlit_restart.py` çalıştır.
7. `admin_executive.py` ve `admin_search.py` roo tarafından tamamlandı (2026-09-17); bu iki dosyaya ve `tests/test_admin_executive.py` / `tests/test_admin_search.py` testlerine DOKUNMA. `tests/test_admin_kpi_kart.py` AST kontrolüne dahil edebilirsin (zaten `st.metric` içermiyorlar).

## Teslim
- `python scripts/gorev_kutusu.py teslim --ajan kilo --task-id ADMIN-KPI-KART-01`
- Rapor: `data/orchestrator/ADMIN-KPI-KART-01_rapor_<tarih>_kilo.md` (sekme başına önce/sonra sayım tablosu).
- Kapsam dışı bulgu → `data/orchestrator/ADMIN-KPI-KART-01_bulgular_<tarih>_kilo.md` (düzeltme YOK).

## Tahmin
~2,5 saat. Öncelik sırası: dlq → performance → api_analytics → cost → quality → audit.
