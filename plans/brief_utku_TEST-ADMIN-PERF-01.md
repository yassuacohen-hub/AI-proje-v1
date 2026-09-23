# TEST-ADMIN-PERF-01 — admin_performance KPI dili tek'lensin

## Görev Özeti
`tests/test_admin_performance.py` 3 test `patch.object(admin_performance, "kpi_karti")`
yapıyor ama `web_dashboard/tabs/admin_performance.py` `kpi_karti` import etmiyor;
hâlâ `company_master.ui.MetricCard` kullanıyor. Testler `AttributeError` ile kırık.

## Kök Neden (doğrulandı)
`web_dashboard/tabs/admin_performance.py:25` → `from company_master.ui import MetricCard`
Diğer 12 admin sekmesi `from web_dashboard.charts import kpi_karti` kullanıyor (UI-CHART-01).
Bu dosya geçişten atlanmış.

## Çıktı
- `web_dashboard/tabs/admin_performance.py`: `MetricCard` → `kpi_karti` (UI-CHART-01 kalıbı)
- Kart çağrıları `kpi_karti(baslik, deger, ikon=..., kategori=...)` imzasına uysun
- `st.metric` eklenmeyecek (D: tek KPI dili, `tests/test_admin_sekme_durum.py` bunu kolluyor)

## Kabul Kriteri
```
set PYTHONIOENCODING=utf-8 && python -m pytest tests/test_admin_performance.py -q
# 3 failed -> 0 failed

set PYTHONIOENCODING=utf-8 && python -m pytest tests/test_admin_sekme_durum.py tests/test_admin_kpi_kart.py -q
# yesil kalmali (regresyon yok)
```

## Kurallar
- D-86: her komut `set PYTHONIOENCODING=utf-8 &&` ile
- D-66: kanıtsız kapanış yok — teslimde pytest çıktısını yapıştır
- Testi değiştirerek geçirme yasak; kaynak düzelecek

## Süre Tahmini
2 saat

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
