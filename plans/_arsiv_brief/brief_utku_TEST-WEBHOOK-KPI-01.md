# TEST-WEBHOOK-KPI-01 — webhook_monitor metrik testi kırık

## Görev Özeti
`tests/test_webhook_monitor_tab.py::test_render_webhook_monitor_tab_renders_metrics`
`assert metric.called` → False. Test `st.metric` mock'luyor ama kaynak
`web_dashboard/tabs/webhook_monitor.py` UI-CHART-01 geçişiyle `kpi_karti`'ye taşınmış.

## Kök Neden (doğrulandı)
`webhook_monitor.py:26` → `from web_dashboard.charts import kpi_karti  # UI-CHART-01`
Kaynak doğru, **test eski**. `st.metric` artık çağrılmıyor, çağrılmamalı da.

## Çıktı
- `tests/test_webhook_monitor_tab.py`: mock hedefi `st.metric` → `webhook_monitor.kpi_karti`
- Assert, çizilen kart sayısını/başlıklarını doğrulasın (sadece `.called` değil)
- Kaynağa dokunma — kaynak zaten kuralı sağlıyor

## Kabul Kriteri
```
set PYTHONIOENCODING=utf-8 && python -m pytest tests/test_webhook_monitor_tab.py -q
# 1 failed -> 0 failed
```

## Kurallar
- D-86: `set PYTHONIOENCODING=utf-8 &&`
- D-66: teslimde pytest çıktısı zorunlu
- Test'i silerek/skip'leyerek geçirmek yasak; assert anlamlı kalacak

## Süre Tahmini
1 saat

## Ilgili Nodlar
- [[Huginn Data Insights/AGENTS]]
