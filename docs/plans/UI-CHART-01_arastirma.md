# UI-CHART-01 — Grafik/KPI Kart Kütüphanesi Araştırması (2026-09-15, roo)

**Amaç:** Muninn (8501) admin panelindeki `st.metric` kartlarını ve dağınık plotly çağrılarını
"havalı, modern" (sahip isteği) tek bir yardımcı modülle değiştirmek: gradient KPI kartı +
delta oku + sparkline, donut ve alan grafiği; koyu/açık tema uyumlu; responsive.

## Karşılaştırma

| Seçenek | Sürüm (kurulu) | Görsel kalite | Tema (koyu/açık) | Responsive | Ek bağımlılık | Karar |
|---|---|---|---|---|---|---|
| **Plotly (graph_objects)** | 7.0.0 ✅ | Yüksek — hover tooltip, donut, alan dolgusu, sparkline | `paper_bgcolor` şeffaf + token renkleri ile tam kontrol | `width="stretch"` | Yok | **SEÇİLDİ** |
| Altair | 6.2.2 ✅ | Yüksek — deklaratif, temiz | Tema nesnesi gerekir; Streamlit `theme="streamlit"` kısmen | Evet | Yok | Yedek (kullanılmadı) |
| streamlit-echarts | ❌ kurulu değil | Çok yüksek (animasyon) | JS tarafında tema | Evet | +1 paket (+ ECharts JS) | Red — bağımlılık maliyeti, `requirements-app.txt` şişer |
| streamlit-extras `metric_cards` | ❌ kurulu değil | Orta — yalnızca CSS kenarlık | CSS ile | Evet | +1 paket (geniş yüzey) | Red — aynı sonuç 20 satır HTML/CSS ile alınır |
| `st.metric` (mevcut) | 1.62.0 | Düşük — düz metin | Otomatik | Evet | Yok | Fallback olarak korunur |

**Gerekçe:** Plotly zaten `requirements-app.txt` içinde ve `admin_kpi.py` 4 yerde kullanıyor;
`src/company_master/ui/charts/__init__.py` de plotly tabanlı. Yeni bağımlılık **gerekmez**.
KPI kartı için grafik kütüphanesi değil, `st.markdown(unsafe_allow_html=True)` ile
`tokens.py` renklerine bağlı gradient kart yeterli; sparkline plotly ile 56px yükseklikte çizilir.

## Tema stratejisi

- Tema `st.get_option("theme.base")` → `"dark"`/`"light"`; `charts.tema_paleti()` bunu
  `src/company_master/ui/tokens.py` (`RENKLER` / `RENKLER_AYDINLIK`) jetonlarına eşler.
  Ham hex **yazılmaz**; SSOT korunur.
- Plotly figürleri: `paper_bgcolor`/`plot_bgcolor` = `rgba(0,0,0,0)`, yazı rengi `text`,
  grid `border` → kart arka planı ne olursa olsun uyumlu.
- Kategori renkleri: müşteri `metric-customer`, sistem `metric-system` (DASH-UX-01 sözleşmesi).

## Örnek görseller (referans)

1. Plotly donut (hole=0.6) + merkez toplam: https://plotly.com/python/pie-charts/#donut-chart
2. Plotly alan grafiği (`fill="tozeroy"`, spline): https://plotly.com/python/filled-area-plots/
3. Sparkline kartı deseni (eksensiz mini alan): https://plotly.com/python/line-charts/#sparklines-with-plotly-express

## API (web_dashboard/charts.py)

| Fonksiyon | Streamlit gerektirir mi | Açıklama |
|---|---|---|
| `sayi_formatla(deger)` | Hayır | `1234` → `"1.234"`, `None` → `"—"` |
| `delta_yonu(delta)` | Hayır | `"+12"`/`-3`/`0` → `yukari`/`asagi`/`duz` |
| `tema_paleti(tema)` | Hayır | token sözlüğünden renk paleti |
| `kpi_karti_html(...)` | Hayır | gradient kart HTML'i (XSS için `html.escape`) |
| `sparkline_fig / donut_fig / alan_grafigi_fig` | Hayır (plotly) | `go.Figure` üretir |
| `kpi_karti(...)`, `donut(...)`, `alan_grafigi(...)` | Evet | `st.*` sarmalayıcılar; plotly yoksa `st.metric`/`st.bar_chart`/`st.area_chart` fallback |

## Uygulama kapsamı

- `web_dashboard/tabs/ana_kontrol.py`: 8 `st.metric` → `kpi_karti`; webhook `st.bar_chart` → `donut`.
- `web_dashboard/tabs/admin_kpi.py`: `_render_kpi_card` imzası korunarak `kpi_karti`'ye delege;
  kaynak pie → `donut`; kalite trendi ve API trendi → `alan_grafigi`.
- Testler: `tests/test_charts.py` (Streamlit'siz saf yardımcılar + figür yapısı).
- Sabit px genişlik yok; yalnız yükseklik sabit (kart 56px sparkline, grafik 260–300px).

## Riskler / sonraki adım

- `unsafe_allow_html` yalnız `html.escape` ile temizlenmiş metin alır; kullanıcı girdisi kartlara gitmez.
- Sparkline için gerçek zaman serisi `/api/kpi` içinde yok; şimdilik yalnız veri varsa çizilir (parametre opsiyonel).
  Takip görevi: `/api/kpi/history` (son 7 gün) → sparkline besleme.
