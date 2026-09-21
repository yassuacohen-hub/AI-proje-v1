# REV-UI-CHART-01 — UI-CHART-01 Çapraz İnceleme (roo teslimi, commit 928ef8b)

**İnceleyen:** cline · **Tarih:** 2026-09-16 · **Sonuç: ✅ ONAY** (engelleyici bulgu yok)

## Kapsam (928ef8b)
`web_dashboard/charts.py` (yeni, 430 satır) · `web_dashboard/tabs/ana_kontrol.py` · `web_dashboard/tabs/admin_kpi.py` · `tests/test_charts.py` (yeni) · `docs/plans/UI-CHART-01_arastirma.md`

## Doğrulanan Kanıtlar
1. **Kodlama sağlığı (byte-düzey):** 5 dosyada strict UTF-8 decode OK, BOM yok, NUL yok, `ast.parse` OK, mojibake göstergesi (Ã/Â/U+FFFD) yok. `git show` çıktısındaki bozuk görünen karakterler PowerShell konsol görüntüleme artefaktıdır (CP437), dosyalar sağlam.
2. **XSS güvenliği:** `kpi_karti_html` → `baslik`, `deger`, `delta`, `ikon`, `yardim` alanlarının tamamı `html.escape` ile kaçırılıyor (charts.py L178/180-182/192); `donut` merkez metni escape'li (L341); `veri_akisi_dot` düğüm etiketleri escape'li (L239). Düz HTML enjeksiyonu yolu yok.
3. **Tema SSOT + responsive:** `aktif_tema()` önce `st.context.theme.type` (1.62+), yoksa `theme.base` (L385-402) → kart zemini/kontur temayla uyumlu. Renkler `RENKLER` token sözlüğünden; aydınlık override `RENKLER_AYDINLIK`. Grafikler `width="stretch"` + yalnız figür içi yükseklik sabit; kartta yalnız `min-height:92px` (layout bozmayan kabul edilebilir değer).
4. **Plotly fallback:** `ImportError` → `st.bar_chart`/`st.area_chart` (donut L468-469, sparkline L442-443); donut boş veri → `st.info`. Streamlit'siz modda `_plotly_gerekli()` ile net hata.
5. **Testler (ölçülen):** `tests/test_charts.py` **46 passed**; hedefli genişleme `test_charts + test_web_dashboard_tabs` = **55 passed** (0 hata). Gerçek Streamlit importu yok — `MagicMock` + `monkeypatch.setitem(sys.modules, "streamlit", …)`; "Streamlit'siz" iddiası doğru. XSS-escape testi mevcut.
6. **Sözleşmeye uygunluk:** `admin_kpi.render_kpi_tab` erken return korundu (L363-371); `_render_kpi_card` imzası korunup `charts.kpi_karti`'ye delege (L282-290). `ana_kontrol`'de 8 `st.metric` → `kpi_karti`, webhook bar → `donut` (merkez toplam + hover).

## Notlar / Kapsam Dışı Gözlemler (engel değil)
- **B1:** `ana_kontrol.py::_get_metric_color` (metric-blue/orange CSS sınıfı) artık ölü kod — `st.metric` tamamen kaldırıldı; bir sonraki hijyen turunda temizlenebilir.
- **B2:** `kpi_karti` sparkline varsayılan anahtarı `spark-{baslik}` — aynı başlıklı iki kart + sparkline tek sayfada widget anahtarı çakıştırır; `anahtar` parametresi mevcut, çağıranlar şimdilik sparkline kullanmıyor (teorik risk).
- **B3:** `admin_kpi._render_field_quality` hâlâ doğrudan `px.bar` + `height=300` — UI-CHART-01 kapsamı dışında bırakılmış; ileri bir task'ta `charts` sarmalayıcısına taşınması önerilir.
- **B4:** `ana_kontrol.load_webhook_stats` placeholder (hep 0) → webhook donut'u pratikte hiç dolmaz; önceden var olan davranış.
- Teslim (928ef8b) sonrası aynı dosyalarda KPI-EXA-01/02 commitleri (091a074, 08acdc3, a45a6ba) var — bunlar ayrı işler; bu inceleme teslim anlık durumuna odaklandı (mevcut HEAD de tüm kanıtlarda temiz).
- Teslim notundaki "27 test / hedefli 48" iddiası 928ef8b anlık durumudur; bugün ölçülen 46/55 (KPI-EXA katkısıyla) — çelişki yok.

**Öneri:** `UI-CHART-01` → **onayla**. B1-B4 sonraki planlamada değerlendirilsin.
