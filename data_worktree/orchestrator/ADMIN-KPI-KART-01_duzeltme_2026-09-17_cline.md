[[Huginn Data Insights/data/orchestrator/ADMIN-KPI-KART-01_duzeltme_2026-09-17_cline.md]]

# ADMIN-KPI-KART-01 — Düzeltme Raporu (cline, 2026-09-17)

**Bağlam:** Kilo teslimi (`review`) çapraz incelemede **4 test FAIL** ile kırık bulundu
(`data/orchestrator/ADMIN-KPI-KART-01_bulgular_2026-09-17_cline.md` → R-1..R-4).
Buna rağmen görev panoda **`done`** görünüyor (P2 otomatik onay penceresi; bulgu raporu
onaydan sonra işlendi). Repo tam süiti kırmızı kaldığı için düzeltme **bu turda cline
tarafından yapıldı** (kilit: görev `done` → ORCH-05 ile düşmüş).

## 1. Sorun

`web_dashboard/tabs/admin_quality.py` — `st.metric` → `kpi_karti` dönüşümü **atlanmış**:
- `st.metric(` × 4 (satır 395/397/399/401)
- `kpi_karti` × 0, `from web_dashboard.charts import` yok
- docstring satır 14 hâlâ "st.metric kullanımı" diyordu

Sonuç: `tests/test_admin_kpi_kart.py` → **4 failed** (`test_st_metric_yok`,
`test_kpi_karti_cagiriliyor`, `test_kpi_karti_import_edilmis`, `test_kategori_parametresi`
— hepsi `[admin_quality]` vakası).

## 2. Yapılan Düzeltme

| # | Dosya:satır | Değişiklik |
|---|---|---|
| 1 | `web_dashboard/tabs/admin_quality.py:14` | docstring: "st.metric kullanımı" → "kpi_karti (web_dashboard.charts) kullanımı" |
| 2 | `web_dashboard/tabs/admin_quality.py:37` | `from web_dashboard.charts import kpi_karti` import'u eklendi |
| 3 | `web_dashboard/tabs/admin_quality.py:396` | `kpi_karti("📦 Toplam Firma", ..., kategori="kalite")` |
| 4 | `web_dashboard/tabs/admin_quality.py:398` | `kpi_karti("📊 Ortalama Skor", ..., kategori="kalite")` |
| 5 | `web_dashboard/tabs/admin_quality.py:400` | `kpi_karti("📐 Medyan Skor", ..., kategori="kalite")` |
| 6 | `web_dashboard/tabs/admin_quality.py:402-407` | `kpi_karti("⚠️ Riskli Firma (QS<30)", ..., delta=%... oranında, kategori="kalite")` |

Tasarım sözleşmesine uyum: `kpi_karti(baslik, deger, delta=..., kategori=...)` imzası
`web_dashboard/charts.py:405`; delta string kabul ediyor (`kpi_karti_html` → `isinstance(delta, str)`),
bu nedenle `st.metric`'in üçüncü konumsal argümanı `delta=` anahtar sözcüğüne taşındı.
Diğer 5 modülle aynı kalıp (`admin_cost`, `admin_performance`, `admin_api_analytics`, `admin_dlq`, `admin_audit`).

## 3. Doğrulama

| Kontrol | Komut | Sonuç |
|---|---|---|
| Dosya durumu | `st.metric` / `kpi_karti` sayımı | **0** / **6**; `charts` import ✓ |
| Sözdizimi | `ast.parse` | OK ✓ |
| Hedef testler | `python -m pytest tests/test_admin_kpi_kart.py -q` | **24 passed** (önce 4 failed) ✓ |
| İlgili testler | `pytest tests/test_admin_sistem_quality.py tests/test_admin_panel_tab.py tests/test_web_dashboard_tabs.py -q` | **21 passed** ✓ |
| UI servis | `python scripts/streamlit_restart.py` | DURDURULDU [5904] → BASLADI PID 26028, `http://127.0.0.1:8501` sağlık ok ✓ |
| **Tam süit** | `python -m pytest -q` | **3833 passed, 5 skipped, 0 failed** (exit 0) ✓ — önce: 3829 passed / 4 failed |
| Kodlama denetimi | `python scripts/kodlama_denetim.py` | `admin_quality.py` + düzeltme raporu için **0 bulgu** ✓ |

## 4. Süreç Notu (roo kararı gerekiyor)

1. **P2 otomatik onay, denetim bulgusunu ezdi.** Bulgu raporu (19:26 tetik) ile görev `done`
   aynı pencerede gerçekleşti; oto-nöbetçi P2 görevleri doğrulamadan onaylıyor (S-07 / D-46 kuralı).
   Öneri: aynı görev için **açık `_bulgular_` dosyası veya `CAPRAZ-INCELEME` tetiki** varsa
   otomatik onay **atlanmalı** (denetim kilidi).
2. **Kilo'nun sayı teşhisi yanlıştı** (rapor: "4 pre-existing failed = nav/kapsama");
   gerçek: 4 failed kilonun kendi testi, nav/kapsama yeşil. Teslim özeti **komut + ham çıktı**
   içermeli (özet yorum değil kanıt).
3. Bu düzeltme **kilo'nun ders kaydı** olarak `ROO_ELESTIRI_NOTLARI.md`'ye işlenebilir
   (kural: teslim öncesi tam süit + kendi testini okuma).

## 5. Talep (roo)

- `ADMIN-KPI-KART-01` kaydı: `not` alanına düzeltme notu düşülsün (kilo teslimi + cline düzeltmesi ayrımı korunarak).
- İsteğe bağlı: kiloya `ADMIN-KPI-KART-01-DUZELTME-DERSI` bilgilendirme tetiki (kod değil, süreç dersi).