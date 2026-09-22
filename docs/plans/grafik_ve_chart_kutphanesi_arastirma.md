# Grafik ve Chart Kutuphanesi Arastirmasi

**Tarih:** 2026-09-15
**Amac:** OSINT + AI Istihbarat Platformu icin ucretsiz grafik/chart kutuphanesi secimi
**Baglam:** AI proje v1/V10/03_mimari/osint_ai_visual_stack.md dokumanin sentezi

---

## Araştırma Kapsami

Aşağıdaki kütüphaneler üç gruba ayrilmistir:
- **Grup 1:** Standart/Yuksek Performansli Grafikler
- **Grup 2:** Ag Analizi ve Cografi Istihbarat (GEOINT)
- **Grup 3:** Arayüz, Widget ve AI Görselleştirme

Tum kütüphaneler ucretsiz ve açık kaynaklidir (MIT, Apache 2.0, BSD-3, MPL2).

---

## Grup 1: Standart/Yuksek Performansli Grafik Kütüphaneleri

### 1. Plotly (UI-CHART-01 — Onaylandı )
- **Lisans:** MIT
- **Render:** SVG + WebGL (scattergl, scatter3d)
- **Stars:** 18.6k | **Forks:** 2.8k
- **En İyi Kullanım:** KPI Dashboard, Risk Skorlari, Karşılaştırmali Analiz, AI Analiz Sonuçlari
- **Streamlit:** ✅ Native (st.plotly_chart) — Proje icinde zaten kullaniliyor
- **Zayıf Yanı:** Full bundle ~3.2MB (strict-mode ~430KB gz). 10k+ noktada SVG yavaşlar -> "render_mode="webgl" kullanilmal
- **Bundle:** ~870KB full, ~430KB strict-mode gz
- **Python:** İlk sinif vatandas — pip install plotly
- **Chart Types:** 40+ (statistical, 3D, contour, financial, geo, etc.)
- **Karar:** ✅ **PROJE İÇİN ONAYLI** — mevcut implementation (web_dashboard/charts.py) bu kütüphaneye dayanıyor

### 2. Apache ECharts
- **Lisans:** Apache 2.0
- **Render:** Canvas (SVG sec.)
- **Stars:** 66.3k | **Weekly Downloads:** 2.6M
- **En İyi Kullanım:** Sankey, Geo Maps (600+), Treemap, Calendar Heatmap, Sunburst, Timeline
- **Streamlit:** ⚠️ "streamlit-echarts" veya "streamlit-ech" gerekir
- **Zayıf Yanı:** Doc agırlıklı Cince, Streamlit entegrasyonu third-party
- **Performance:** 100k+ noktalar, "series.sampling: lttb" downsampling, tree-shakeable ~100KB gz
- **Bundle:** ~1.8MB full, ~520KB tree-shaken
- **Karar:** ⏳ **DEĞERLENDİRİLECEK** — Plotly'nin yapamadigi chart tipleri icin (Sankey, geo, heatmap)

### 3. Observable Plot
- **Lisans:** ISC
- **Render:** SVG (declarative)
- **Stars:** 10.4k
- **En İyi Kullanım:** Executive Dashboard, Kurumsal Raporlama, Araştırma Cıktıları
- **Zayıf Yanı:** Daha az etkileşimli, JavaScript tabanli, Streamlit entegrasyonu yok
- **Karar:** ⏳ **ILERI ÖLÇEK DEĞERLENDİRME**

### 4. Altair (Vega-Lite)
- **Lisans:** BSD-3
- **Render:** Vega-Lite -> SVG
- **Stars:** 10.4k
- **En İyi Kullanım:** Declarative Statistik Grafikler, Faceted Small-multiples
- **Zayıf Yanı:** Streamlit destegi zayıf, Verbose API
- **Karar:** ⏳ **ILERI ÖLÇEK DEĞERLENDİRME**

### 5. Bokeh
- **Lisans:** BSD-3
- **Render:** Canvas
- **Stars:** 20.4k
- **En İyi Kullanım:** Büyük Veri Dashboard (>1M noktalar), Datashader entegrasyonu
- **Zayıf Yanı:** API verbosity, Streamlit entegrasyonu Plotly kadar purusuz degil
- **Karar:** ⏳ **YALNIZCA 1M+ NOKTA SENARYOLARI**

**Grup 1 Karar Matrisi:**
| Senaryo | İlk Tercih | Alternatif |
|---------|-----------|------------|
| KPI Card / Trend / Donut | **Plotly** ✅ | — |
| Sankey / Heatmap / Geo | **ECharts** | Plotly (limited) |
| Executive Report | **Observable Plot** | Plotly |
| 100k+ Nokta | **ECharts** | Bokeh+Datashader |
| Scientific/Statistical | **Plotly** | Altair |

---

## Grup 2: Ag Analizi ve Cografi Istihbarat (GEOINT)

### 1. Cytoscape.js (OSINT İçin Kritik)
- **Lisans:** MIT
- **Render:** SVG/Canvas
- **En İyi Kullanım:** Kisi İlişkileri, Domain-IP İlişkileri, Telegram/Sosyal Medya Aglari, Finansal Takip/Kripto Transfer Aglari
- **Streamlit:** ⚠️ "streamlit-cytoscape" (omegahh) veya custom component gerekir
- **Özellikler:** Force-directed (fcose), Hierarchical (klay), CoSE, Circle, Grid layoutlari; PNG/SVG export; Dynamic legend; Streamlit theme entegrasyonu
- **Karar:** 🔴 **ACIL DEĞERLENDİRME** — OSINT link analizi icin olmazsa olmaz

### 2. deck.gl (Büyük Veri İçin En İyisi)
- **Lisans:** MIT
- **Render:** WebGL2 (GPU hızlandırmalı)
- **En İyi Kullanım:** IP Dagilimlari, Botnet Haritaları, Darkweb Lokasyonları, Küresel Tehdit Yoğunlukları
- **Streamlit:** ❌ Custom Streamlit component gerekir (direct WebGL integration)
- **Zayıf Yanı:** Harita degil, ancak katmanlar; MapLibre veya benzeri basemap gerekli; Karmaşik GPU pipeline
- **Bundle:** Moduler ama GPU framework
- **Karar:** 🟡 **BÜYÜK VERİ COĞRAFİ SENARYOLAR İÇİN** — IP dagılımı >1000 nokta oldugunda

### 3. Sigma.js
- **Lisans:** MIT
- **Render:** WebGL
- **En İyi Kullanım:** 100.000+ dugumlu ag görselleştirme (botnet aglari, data leak analizi)
- **Zayıf Yanı:** Özel API, öğrenme egrisi
- **Karar:** ⏳ **ÇOK BÜYÜK AG SENARYOLARI**

### 4. Kepler.gl
- **Lisans:** MIT
- **Render:** WebGL
- **En İyi Kullanım:** Tehdit Isi Haritaları, Cluster Haritaları, Animasyonlu Zaman Cizgileri
- **Zayıf Yanı:** Kod gerektirir (minimum kod ama Python wrapper yok)
- **Karar:** ⏳ **GEO ANALİZ SENERENARYOLARI**

### 5. MapLibre
- **Lisans:** MPL2 (dosya değişikliği zorunlu)
- **Render:** WebGL
- **En İyi Kullanım:** Ozelleştirilmis altlık haritalar (Vector Tiles), tamamen ucretsiz harita altyapısı
- **Karar:** ⏳ **HARITA ALTYAPISI İÇİN** (deck.gl ile birlikte)

### 6. Vis Network
- **Lisans:** MIT
- **Render:** SVG
- **En İyi Kullanım:** Surukle-bırak prototipleme, Maltego benzeri gorunimler
- **Zayıf Yanı:** Scale sinirlı (1000+ node yavaşlar)
- **Karar:** ⏳ **HIZLI PROTOTİP İÇİN**

**Grup 2 Karar Matrisi:**
| Senaryo | İlk Tercih | Alternatif |
|---------|-----------|------------|
| Domain-IP İlişkileri | **Cytoscape.js** | Vis Network |
| Global IP Dagılımı (>1000) | **deck.gl** + MapLibre | Kepler.gl |
| Botnet Ag Grafiği | **Cytoscape.js** / Sigma.js | — |
| Tehdit Isi Haritasi | **Kepler.gl** | deck.gl |
| Hızlı Prototip | **Vis Network** | Cytoscape.js |

---

## Grup 3: Arayüz, Widget ve AI Görselleştirme

### 1. AG Grid
- **Lisans:** MIT (Community)
- **Tür:** Veri Tablosu
- **En İyi Kullanım:** Sızıntı Verileri, Log Arama, Gelişmiş Filtreleme, Excel Aktarma
- **Streamlit:** ✅ "streamlit-aggrid"
- **Zayıf Yanı:** 200MB+ veri yavaşlar, Community versiyon Bazı özellikler eksik
- **Karar:** 🟡 **SIZINTI/LOG SENARYOLARI İÇİN**

### 2. Shadcn UI
- **Lisans:** MIT
- **Tür:** UI Bileşen Seti (Chart KÜTÜPHANESİ DEĞİL)
- **En İyi Kullanım:** Modern Karanlık Tema, SaaS Gorunumu, Premium Arayüz
- **Streamlit:** ✅ "streamlit-shadcn-ui" v1.4.0 (V2, Tailwind CSS 4, React 19)
- **Özellikler:** "line_chart", "area_chart", "bar_chart", "pie_chart", "radar_chart" (shadcn Charts component!)
- **Önemli Not:** Shadcn UI aslında Chart component de içeriyor (shadcn/ui Charts). Native tooltips ve legends ile light/dark palette. AMA bunlar temel chartlar — KPI cards ve sparklines icin yeterli, ileri düzey grafikler icin Plotly gerekir
- **Karar:** 🟡 **UI KATMANI İÇİN** — chart kütüphanesi degil ama premium UI sağlar

### 3. React Flow
- **Lisans:** MIT
- **Tür:** Node Editor / Flow Diagram
- **En İyi Kullanım:** AI Workflow, Agent Graph Yapıları, LLM Chain ve Karar Agaclari
- **Streamlit:** ❌ Custom component gerekir
- **Karar:** ⏳ **AI WORKFLOW GÖRSELLEŞTİRME İÇİN**

### 4. Mermaid
- **Lisans:** MIT
- **Tür:** Metin tabanli Diagram
- **En İyi Kullanım:** AI tarafindan anlık olusturulmus akış şemalari, basit aj mimarileri
- **Streamlit:** ⚠️ "streamlit-mermaid" veya HTML embed
- **Karar:** ✅ **AI OLUŞTURMUŞ DIAGRAMLAR İÇIN** — LLM dogrudan Mermaid syntax üretebilir

### 5. Framer Motion
- **Lisans:** MIT
- **Tür:** Animasyon
- **En İyi Kullanım:** Sayfa gecişleri, hover efektleri, siber panellerde veri yüklenme animasyonlari
- **Streamlit:** ❌ React component icinde
- **Karar:** ⏳ **PREMIUM UI ANIMASYON İÇİN** (Faz 3+)

**Grup 3 Karar Matrisi:**
| Senaryo | İlk Tercih | Alternatif |
|---------|-----------|------------|
| Data Table (Sızıntı/Log) | **AG Grid** | st.dataframe |
| Premium UI/Theme | **Shadcn UI** | Custom CSS |
| AI Workflow Diagram | **React Flow** | Mermaid |
| AI Anlık Diagram | **Mermaid** | React Flow |
| Animasyon | **Framer Motion** | CSS |

---

## UI-CHART-01 Cross-Check Sonucu

### Onaylanan ()
- **Plotly** → UI-CHART-01 kararı dogrulanmis. MIT lisans, Streamlit native, 40+ chart type, Python-first. Proje icinde "web_dashboard/charts.py" ile mevcut.
- **Mermaid** → AI tarafindan üretilen diagramlar icin dogru secim.

### Senaryo Bagli (⏳)
- **Apache ECharts** → Plotly'nin yapamadigi Sankey/geo/heatmap icin ek kütüphane olarak degerlendirilebilir. Ancak "streamlit-echarts" sidebar cakisma sorunu cozuldunce olabilir. UI-CHART-01 research'de red edilmişti.
- **Cytoscape.js** → OSINT link analizi icin kritik. "streamlit-cytoscape" componenti mevcut ve MIT lisansli. Önerilen: "src/company_master/ui/charts/__init__.py" uzerine entegre edilmeli.
- **deck.gl** → Büyük veri cografi (>1000 nokta) senaryolar icin. Deck.gl + MapLibre cifti guçlu.
- **AG Grid** → Sızıntı verileri icin "streamlit-aggrid" ile entegre edilebilir.
- **Shadcn UI** → UI katmani icin dogru, ancak chart kütüphanesi degil. "streamlit-shadcn-ui" v1.4.0 şimdi Charts component de sunuyor (line, area, bar, pie, radar, radial).

### Reddedilen ()
- **Observable Plot** → JavaScript, Streamlit entegrasyonu yok
- **Altair** → Streamlit destegi zayıf
- **Bokeh** → Sadece 1M+ noktalar icin
- **Sigma.js** → Sadece 100k+ node icin (Cytoscape.js yeterli çoğu senaryoda)
- **Vis Network** → Prototip icin iyi ama ölçek sinirlı
- **React Flow** → AI workflow icin iyi ama cok özel (Faz 3+)
- **Framer Motion** → Animasyon (Faz 3+)

---

## Lisans Ozeti

| Kütüphane | Lisans | Ticari Kullanım | Not |
|-----------|--------|------------------|-----|
| Plotly | MIT | ✅ Serbest | — |
| Apache ECharts | Apache 2.0 | ✅ Serbest | — |
| Cytoscape.js | MIT | ✅ Serbest | — |
| deck.gl | MIT | ✅ Serbest | — |
| Kepler.gl | MIT | ✅ Serbest | — |
| MapLibre | MPL2 | ✅ Serbest | Dosya değişikliği zorunlu |
| AG Grid | MIT (Community) | ✅ Serbest | Community Bazı özellikler eksik |
| Shadcn UI | MIT | ✅ Serbest | — |
| React Flow | MIT | ✅ Serbest | — |
| Mermaid | MIT | ✅ Serbest | — |
| Framer Motion | MIT | ✅ Serbest | — |
| Sigma.js | MIT | ✅ Serbest | — |
| Vis Network | MIT | ✅ Serbest | — |
| Observable Plot | ISC | ✅ Serbest | — |
| Altair | BSD-3 | ✅ Serbest | — |
| Bokeh | BSD-3 | ✅ Serbest | — |

**Sonuc:** Tum kütüphaneler ucretsiz ve ticari kullanım icin uygun. Lisans riski yok.

---

## Entegrasyon Plani (Aşamali)

### AŞAMA 1 (Şimdiki Sprint — UI-CHART-01 devam)
- [x] **Plotly** → KPI kartları, trend grafiği, donut, sparkline (web_dashboard/charts.py)
- [ ] "bar_grafigi" fonksiyonu ekle (alan doluluk icin)
- [ ] "_render_field_quality"/i "bar_grafigi" ile degistir

### AŞAMA 2 (Önümüzdeki Sprint)
- [ ] **Cytoscape.js** → İlişki ag görselleştirme (domain-IP, kisi ilişkileri)
- [ ] "streamlit-cytoscape" entegrasyonu veya custom component
- [ ] "src/company_master/ui/charts/__init__.py" güncellemesi

### AŞAMA 3 (Planlanacak)
- [ ] **Apache ECharts** → Sankey (attack chain), geo haritalar, heatmap
- [ ] **deck.gl** → Global IP/botnet dagılımı (WebGL) + MapLibre
- [ ] **AG Grid** → İleri düzey veri tablosu (sızıntı verileri, log arama)
- [ ] **Shadcn UI** → Premium UI bileşenleri (KPI cards, formlar, overlays)

### AŞAMA 4 (Faz 3+)
- [ ] **React Flow** → Multi-agent yapıları görselleştirme
- [ ] **Mermaid** → AI tarafindan anlık flowchart üretimi
- [ ] **Framer Motion** → Animasyonlar

---

## MVP Önerisi (Roo'a soru)

MVP kapsaminda su sorularin karari gerekir:
1. Cytoscape.js MVP'de mi olmalı? (OSINT link analizi MVP'de kritik mi?)
2. ECharts vs Plotly sınırı nerede? (MVP icin Plotly yeterli mi, yoksa ECharts da gerekli mi?)
3. deck.gl — MVP'de cografi vizasyon gerekli mi?
4. Shadcn UI — Premium UI MVP'de mi yoksa sadece Plotly tema iyileştirmesi mi yeterli?

Bu sorularin cevaplanmasi Roo/Plan agent görüşüyle çözülmelidir.
