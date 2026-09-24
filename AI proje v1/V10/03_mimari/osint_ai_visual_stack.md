# SaaS OSINT + AI İstihbarat Platformu Nihai Mimari & Görselleştirme Stack'i

Bu doküman, Streamlit sınırlarına takılmayan, modern, kurumsal ve **AbyssTracker** seviyesinde premium görünüme sahip bir **OSINT + AI + Siber İstihbarat Platformu** için önerilen katmanlı mimari ve kütüphane rehberidir. Listelenen tüm araçlar açık kaynaklı veya ücretsiz kullanım katmanına sahiptir.

---

## 🎨 1. Grafik Motorları (Ana Katman)

### 🌟 Apache ECharts (En Güçlü Tercih)
* **Kısa Tanım:** Yüksek performanslı, zengin grafik türlerine sahip ve özelleştirilebilir açık kaynaklı JavaScript grafik kütüphanesidir.
* **En İyi Kullanım Alanları:** Threat Timeline, Attack Chain, Sankey, Force Graph, Entity Relationship, Heatmap.
* **Kurulum (Streamlit):** `pip install streamlit-echarts`
* **Kaynaklar:** [GitHub - streamlit-echarts](https://github.com/andfanilo/streamlit-echarts "Streamlit ECharts GitHub"), [Resmi Web Sitesi](https://echarts.apache.org "Apache ECharts Official")

### 📊 Plotly
* **Kısa Tanım:** Veri bilimi ve analitik için dünya standardı olan, etkileşimli ve Python ile yerel olarak harika çalışan grafik kütüphanesidir.
* **En İyi Kullanım Alanları:** AI Analiz Sonuçları, Risk Skorları, KPI Dashboard, Karşılaştırmalı Analiz.
* **Kurulum:** `pip install plotly`
* **Kaynaklar:** [Plotly Python Dokümantasyonu](https://plotly.com/python/ "Plotly Python Reference"), [GitHub - Plotly](https://github.com/plotly/plotly.py "Plotly GitHub")

### 📈 Observable Plot
* **Kısa Tanım:** Hızlı, esnek ve açıklayıcı (declarative) grafikler üretmek için optimize edilmiş modern bir veri görselleştirme motorudur.
* **En İyi Kullanım Alanları:** Kurumsal raporlar, araştırma çıktıları, Executive (Yönetici) dashboard'ları.
* **Kaynaklar:** [Resmi Web Sitesi](https://observablehq.com/plot "Observable Plot Official"), [GitHub - Observable Plot](https://github.com/observablehq/plot "Observable Plot GitHub")

---

## 🌍 2. Harita ve Coğrafi İstihbarat (GEOINT)

### 🌟 deck.gl (Büyük Veri İçin En İyisi)
* **Kısa Tanım:** WebGL2 destekli, milyonlarca veri noktasını tarayıcıda donanım ivmesiyle (GPU) akıcı şekilde işleyebilen harita katman kütüphanesidir.
* **En İyi Kullanım Alanları:** IP dağılımları, Botnet haritaları, Darkweb lokasyonları, Küresel tehdit yoğunlukları.
* **Kaynaklar:** [Resmi Web Sitesi](https://deck.gl "deck.gl Official"), [GitHub - deck.gl](https://github.com/visgl/deck.gl "deck.gl GitHub")

### 🗺️ Kepler.gl
* **Kısa Tanım:** Uber tarafından geliştirilen, büyük ölçekli coğrafi veri setlerini kod yazmadan veya minimum kodla görselleştirmeyi sağlayan güçlü bir geospatial analiz aracıdır.
* **En İyi Kullanım Alanları:** Tehdit ısı haritaları, Cluster (kümeleme) haritaları, animasyonlu zaman çizgileri.
* **Kaynaklar:** [Resmi Web Sitesi](https://kepler.gl "Kepler.gl Official"), [GitHub - Kepler.gl](https://github.com/keplergl/kepler.gl "Kepler.gl GitHub")

### 🗺️ MapLibre
* **Kısa Tanım:** Mapbox'ın açık kaynaklı kalması için topluluk tarafından çatallanan (fork), tamamen ücretsiz ve yüksek performanslı bir harita render motorudur.
* **En İyi Kullanım Alanları:** Özelleştirilmiş altlık haritalar (Vector Tiles), tamamen ücretsiz harita altyapıları.
* **Kaynaklar:** [Resmi Web Sitesi](https://maplibre.org "MapLibre Official"), [GitHub - MapLibre GL JS](https://github.com/maplibre/maplibre-gl-js "MapLibre GitHub")

---

## 🕸️ 3. Ağ ve İlişki Analizi (Link Analysis)

### 🌟 Cytoscape.js (OSINT İçin Kritik)
* **Kısa Tanım:** Akademik ve ticari ağ analizlerinde kullanılan, grafik teorisi analizleri yapabilen tam donanımlı ilişki ağ görselleştirme kütüphanesidir.
* **En İyi Kullanım Alanları:** Kişi ilişkileri, domain-IP ilişkileri, Telegram/Sosyal medya ağları, finansal takip/kripto para transfer ağları.
* **Kaynaklar:** [Resmi Web Sitesi](https://js.cytoscape.org "Cytoscape.js Official"), [GitHub - Cytoscape.js](https://github.com/cytoscape/cytoscape.js "Cytoscape.js GitHub")

### ⚡ Sigma.js
* **Kısa Tanım:** WebGL tabanlı yapısıyla 100.000+ üzeri düğümü (node) ve bağı tarayıcıda kasmadan gösterebilen devasa ağ odaklı kütüphanedir.
* **En İyi Kullanım Alanları:** Çok büyük botnet ağları, geniş çaplı sızıntı (data leak) veri analizleri.
* **Kaynaklar:** [Resmi Web Sitesi](https://www.sigmajs.org "Sigma.js Official"), [GitHub - Sigma.js](https://github.com/jacomyal/sigma.js "Sigma.js GitHub")

### 🔗 Vis Network
* **Kısa Tanım:** Kullanımı son derece kolay, dinamik, tıklama ve sürüklemelere hızlı tepki veren esnek bir ağ haritalama aracıdır.
* **En İyi Kullanım Alanları:** Maltego benzeri sürükle-bırak görünümler, hızlı prototipleme.
* **Kaynaklar:** [Resmi Web Sitesi](https://visjs.github.io/vis-network/ "Vis Network Official"), [GitHub - Vis Network](https://github.com/visjs/vis-network "Vis Network GitHub")

---

## 📊 4. Veri Tabloları

### 🌟 AG Grid
* **Kısa Tanım:** Filtreleme, gruplama, pivot, excel'e aktarma ve satır sabitleme gibi kurumsal tüm ihtiyaçları karşılayan dünyanın en gelişmiş veri tablosudur.
* **Kurulum (Streamlit):** `pip install streamlit-aggrid`
* **Kaynaklar:** [GitHub - streamlit-aggrid](https://github.com/marlanidon/streamlit-aggrid "Streamlit AG Grid GitHub"), [AG Grid Resmi Sitesi](https://www.ag-grid.com "AG Grid Official")

---

## 🎯 5. KPI Kartları ve Modern Widgetlar

### 🌟 Shadcn UI
* **Kısa Tanım:** Doğrudan koda kopyalanarak özelleştirilebilen, Radix Primitives ve Tailwind CSS tabanlı, son yılların en popüler modern arayüz bileşen setidir.
* **Kurulum (Streamlit):** `pip install streamlit-shadcn-ui`
* **Kaynaklar:** [GitHub - streamlit-shadcn-ui](https://github.com/victoryhb/streamlit-shadcn-ui "Streamlit Shadcn UI GitHub"), [Shadcn UI Resmi Sitesi](https://ui.shadcn.com "Shadcn UI Official")

---

## 📈 6. Animasyonlu Dashboard

### 🌟 Framer Motion
* **Kısa Tanım:** React tabanlı projelerde (Streamlit özel bileşenleri yazarken) premium hissiyat yaratan akıcı ve deklaratif animasyon kütüphanesidir.
* **En İyi Kullanım Alanları:** Sayfa geçişleri, hover (üzerine gelme) efektleri, siber panellerde veri yüklenme animasyonları.
* **Kaynaklar:** [Resmi Web Sitesi](https://www.framer.com/motion/ "Framer Motion Official"), [GitHub - Framer Motion](https://github.com/framer/motion "Framer Motion GitHub")

---

## 🤖 7. AI Sonuç Görselleştirme

### 🌟 React Flow
* **Kısa Tanım:** Node tabanlı editörler ve interaktif iş akış şemaları oluşturmak için geliştirilmiş lider React kütüphanesidir.
* **En İyi Kullanım Alanları:** AI Workflow, Agent Graph yapıları, LLM Chain ve karar ağaçları görselleştirmesi.
* **Kaynaklar:** [Resmi Web Sitesi](https://reactflow.dev "React Flow Official"), [GitHub - React Flow](https://github.com/xyflow/xyflow "React Flow GitHub")

### 🧜‍♀️ Mermaid
* **Kısa Tanım:** Markdown benzeri basit bir metin tabanlı kodlama ile dinamik diyagramlar ve akış şemaları üreten JavaScript aracıdır. LLM'lerin doğrudan çıktı üretmesi için mükemmeldir.
* **En İyi Kullanım Alanları:** AI tarafından anlık oluşturulan akış şemaları, basit ajan mimarileri.
* **Kaynaklar:** [Resmi Web Sitesi](https://mermaid.js.org "Mermaid.js Official"), [GitHub - Mermaid](https://github.com/mermaid-js/mermaid "Mermaid GitHub")

---

## 🔥 Siber İstihbarat İçin Önerilen Nihai Entegrasyon Matrisi

| Katman | Seçilen Teknoloji | OSINT Rolü | Lisans Durumu |
| :--- | :--- | :--- | :--- |
| **Grafik Motoru** | `Apache ECharts` | Threat Timeline & Attack Chain analizi | Ücretsiz / Açık Kaynak |
| **Coğrafi Konum** | `deck.gl` | Global IP ve Botnet Dağılım Haritası (GPU Hızlı) | Ücretsiz / Açık Kaynak |
| **İlişki Ağları** | `Cytoscape.js` | Maltego Tarzı Profil, Domain ve Örgüt İlişkileri | Ücretsiz / Açık Kaynak |
| **Veri Analitiği** | `AG Grid` | Sızıntı Verileri, Log Arama ve Gelişmiş Filtreleme | Ücretsiz (Community) |
| **Arayüz (UI)** | `Shadcn UI` | Modern, Karanlık Tema Odaklı SaaS Görünümü | Ücretsiz / Açık Kaynak |
| **AI Görselleştirme**| `React Flow` | Multi-Agent Yapıları ve AI Karar Mekizmaları | Ücretsiz (MIT) |
| **Animasyon** | `Framer Motion` | Premium Geçişler ve Canlı Tehdit Akışları | Ücretsiz / Açık Kaynak |
