# UI-CHART-01 Hibrit Geçiş Planı
Hazırlayan: kilo · Tarih: 2026-09-16 · Durum: taslak (roo sentezi bekliyor)

## BÖLÜM 1 — Durum

Mevcut grafik kütüphanesi durumu:
- **Plotly** (onaylı): `web_dashboard/charts.py` — `sparkline_fig`, `donut_fig`, `alan_grafigi_fig` fonksiyonları mevcut. `st.line`, `st.bar`, `st.pie` fallback'ler aktif.
- **Altair**: Yüklü değil, bağımlılık yok.
- **streamlit-echarts**: Yüklü değil, onaysız.
- **streamlit-extras metric_cards**: Yüklü değil.

Kullanılabilir: Plotly (onaylı) + `st.*_chart` fallback'leri.

## BÖLÜM 2 — Hibrit Strateji

| Senerio | Kütüphane | Durum |
|---|---|---|
| KPI kartları (delta ok + sparkline) | Plotly `sparkline_fig` | ✅ Mevcut |
| Donut grafikler | Plotly `donut_fig` | ✅ Mevcut |
| Alan grafikleri | Plotly `alan_grafigi_fig` | ✅ Mevcut |
| Gradient KPI kartları | Plotly + CSS gradient | ✅ Planlanmış |
| Hover tooltips | Plotly hover | ✅ Mevcut |
| ECharts ( dinamik ) | streamlit-echarts | ⏳ Onay bekliyor |
| Cython/Deck.gl 3D | native Streamlit | ⏳ İleri aşama |

## BÖLÜM 3 — Tema

- Tema paleti: `tema_paleti()` fonksiyonu → token'lardan gelir
- Koyu/açık: `st.get_option('theme.base')` ile otomatik
- Responsive: `use_container_width=True`, sabit px yok

## BÖLÜM 4 — İletişim Protokolü

- ECharts onaysız kütüphanedir — roo onayı olmadan kod yazılmaz
- sessizlik onay değildir
- decision_log.jsonl kilo→roo haberleşme kanalı değildir
- Kilo `decision_log.jsonl`'e yazamaz
- Kilo `test_web_dashboard_tabs.py` testi dışında farklı bir dosyaya dokunmadı
