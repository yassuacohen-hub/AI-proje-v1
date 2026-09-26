# 🕵️‍♂️ Firma İstihbarat Dashboard: UI/UX & Mimari Rehberi

Bu rehber, **Streamlit** platformunda veri yoğunluğu yüksek, hızlı karar almayı destekleyen ve profesyonel bir SaaS ürünü hissiyatı veren **Firma İstihbarat Dashboard (Business Intelligence)** tasarımı için üretilmiş kapsamlı bir UX/UI mimari kılavuzudur.

---

## 🧭 1. Navigasyon ve Sayfa Düzeni (Navigation & Layout)

Firma istihbarat panellerinde kullanıcılar genellikle stres altında veya hızlı aksiyon alması gereken (kredi onay yöneticileri, risk analistleri vb.) profesyonellerdir. Bu nedenle arayüz **en fazla 2 tıkla** hedefe ulaştırmalıdır.

### 📊 Alternatif A: Sol Kenar Çubuğu (Sidebar) Menü Modeli (Önerilen)
Tüm analitik, filtreleme ve modül geçişlerini tek bir dikey çizgide toplayan, veri odaklı paneller için en standart ve kararlı yapıdır.
* **Küresel Kontroller (Sol Menü):** Firma adı arama, Vergi No (VKN) sorgulama ve "Yıl" seçimi gibi tüm dashboard'u baştan aşağı değiştirecek girdiler her zaman sol kenar çubuğunda (`st.sidebar`) yer almalıdır. Bu sayede kullanıcı sekmeler arasında gezinirken arattığı firma kaybolmaz.
* **UX Avantajı:** Geniş ekran modunda sağ taraftaki geniş analitik alanını tamamen grafiklere ve tablolara ayırma özgürlüğü sunur.

### 🗺️ Alternatif B: Üst Menü (Top Navigation) + Mega Filtre Modeli
Kullanıcının daha çok yatay akışta kalmasını sağlayan, özellikle yönetici (C-Level) sunumları ve geniş ekranlı monitörler için optimize edilmiş modern bir yaklaşımdır.
* **Yerleşim:** Sayfanın en üstünde şık bir navigasyon barı yer alır. Filtreler ise sayfa başında açılır-kapanır (`st.expander`) bir "Filtre Paneli" içinde gizlenir.
* **UX Avantajı:** Kullanıcıyı dikey bir sol menüyle sıkıştırmaz, içerik ekranın tamamına yayılır.

---

## 📦 2. Kaliteli Bir Dashboard İçin UX Bileşenleri & Linkleri

Streamlit'in standart bileşenlerinin (ham butonlar, düz listeler) yarattığı prototip algısını kırmak için aşağıdaki **özelleştirilmiş topluluk bileşenlerini (Custom Components)** entegre etmeniz şarttır:

### 🗂️ Navigasyon & Yapı Taşları
* **[Streamlit Option Menu](https://github.com/victoryhb/streamlit-option-menu "streamlit-option-menu"):** Bootstrap ikon desteğiyle sol menüde veya üst barda animasyonlu, pürüzsüz geçiş barları oluşturmak için en popüler kütüphanedir.
* **[Streamlit Antd Components](https://github.com/nicedouble/streamlit-antd-components "streamlit-antd-components"):** Ant Design kütüphanesini Streamlit'e taşır. Çok katmanlı açılır-kapanır menüler (nested menus), süreç takip adımları (`sac.steps`) ve ekmek kırıntıları (`sac.breadcrumbs`) için benzersizdir.

### 📊 Veri Yönetimi & Tablolar (Data Grids)
* **[Streamlit AgGrid](https://github.com/Pablocasas/streamlit-aggrid "streamlit-aggrid"):** Standart tabloları unutun. Hücre bazlı düzenleme (inline editing), Excel tarzı gelişmiş filtreleme, sıralama ve hücre içine buton/link gömme özellikleri sunan kurumsal seviyede bir tablodur.

### 🎨 Modern UI & Tasarım Sistemleri
* **[Streamlit Shadcn UI](https://github.com/gagan3012/streamlit-shadcn-ui "streamlit-shadcn-ui"):** Web dünyasının en popüler minimalist tasarım dili olan Shadcn UI elementlerini (modern modal pencereleri, badge'ler, avatar ikonları) uygulamanıza dahil eder.
* **[Streamlit Elements (Material UI)](https://github.com/okld/streamlit-elements "streamlit-elements"):** Kullanıcıların dashboard üzerindeki grafik ve analiz kartlarını sürükleyip bırakarak kendi panel düzenlerini oluşturmalarına (drag-and-drop grid) imkan tanır.

### 📉 İnteraktif Grafik & İlişki Ağları (Analytics)
* **[Plotly Python](https://plotly.com/python/ "Plotly Graphing Libraries"):** Streamlit ile yerleşik olarak kusursuz çalışan, veri analistlerinin fareyle üzerine gelip (hover) detay okuyabileceği grafikler için endüstri standardıdır.
* **[Streamlit ECharts](https://github.com/andfanilo/streamlit-echarts "streamlit-echarts"):** Çok daha estetik, akıcı animasyonlara sahip finansal göstergeler (gauge) ve ısı haritaları üretir.
* **Streamlit Network Graph Önerisi:** İstihbarat panellerinin kalbi olan holding yapıları ve gizli ortaklık zincirlerini görselleştirmek için harici ağ grafiği araçları kullanılmalıdır.

---

## ⚡ 3. Firma İstihbaratı İçin 5 Kritik UX Altın Kuralı

1. **Trafik Işığı Sistemi (Don't Make Me Think):** Şirket aratıldığı an ilk 3 saniyede risk durumu anlaşılmalıdır. Risk seviyesine göre ekranın üstündeki KPI kartları veya uyarı metinleri dinamik renk değiştirmelidir (Yeşil: Güvenli, Sarı: İzleme Listesi, Kırmızı: İcra/Kara Liste).
2. **Aşamalı İfşa (Progressive Disclosure):** Kullanıcıyı tek seferde tüm bilançolar ve davalarla boğmayın. En üstte özet kartlar, detaylar için ise yerleşik `st.tabs` kullanın. Bu hem gözü yormaz hem de sadece tıklanan sekmenin kodunu çalıştırarak hızı artırır.
3. **Form Kümelemesi (`st.form`):** Kullanıcı her harf yazdığında veya filtre değiştirdiğinde Streamlit'in baştan aşağı yenilenmesini (rerun) engellemek için arama/filtre alanlarını `with st.form():` içine alın. "Sorgula" butonuna basıldığında tek seferde çalışsın.
4. **Veri Tazeliği & Önbellek (`st.cache_data`):** İstihbarat verileri büyüktür. Sık değişmeyen şirket künye bilgilerini ve geçmiş finansalları önbelleğe alarak sorgu hızını milisaniyelere indirin.
5. **Dondurulmuş Başlıklar (Sticky Headers):** Uzun ticari sicil veya ihale tablolarında aşağı kaydırıldığında sütun isimlerinin görünür kalmasını sağlayarak veri okuma konforunu koruyun.

---

## 🛠️ 4. Hazır Prototip Kodu (Örnek Şablon)

Aşağıdaki kodu doğrudan `app.py` olarak kaydedip çalıştırarak modern navigasyon yapısına sahip kaliteli bir başlangıç mimarisi elde edebilirsiniz:

```python
import streamlit as st
from streamlit_option_menu import option_menu

# 1. Geniş Ekran ve Sayfa Ayarları
st.set_page_config(layout="wide", page_title="Firma İstihbarat Merkezi", page_icon="🕵️‍♂️")

# Custom CSS Enjeksiyonu ile Buton ve Kart Yuvarlama
st.markdown("""
    <style>
    .stButton>button { border-radius: 8px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.05); }
    div[data-testid="stMetric"] { background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_with_html=True)

# 2. Sol Menü Navigasyon Yönetimi (Alternatif A)
with st.sidebar:
    st.title("🕵️‍♂️ Risk Intelligence")
    
    with st.form("search_form"):
        target_company = st.text_input("🏢 Firma Adı veya VKN Giriniz", value="Örnek Holding A.Ş.")
        submit_btn = st.form_submit_button("🔍 İstihbarat Sorgula")
        
    st.divider()
    
    selected_module = option_menu(
        menu_title="Analiz Modülleri",
        options=["Genel Özet", "Finansal Analiz", "Hukuki Geçmiş"],
        icons=["building", "graph-up-arrow", "shield-slash"],
        menu_icon="cast",
        default_index=0,
        styles={
            "nav-link-selected": {"background-color": "#1E3A8A"}, # Kurumsal Lacivert
        }
    )

# 3. Dinamik İçerik Yönetimi
if target_company:
    st.title(f"🏢 {target_company} Analiz Raporu")
    
    if selected_module == "Genel Özet":
        # Trafik Işığı Sistemi ve KPI Kartları
        st.error("⚠️ DİKKAT: Firma hakkında son 30 günde 2 adet yeni icra takibi başlatılmıştır.")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Skoru", "C- (Yüksek Risk)", delta="-2 Kademe Drop", delta_color="inverse")
        col2.metric("Aktif Ticari Durum", "Tasfiye Halinde", delta="Kritik", delta_color="inverse")
        col3.metric("Yıllık Ciro (2025)", "145M TL", delta="+12% Büyüme")
        
    elif selected_module == "Finansal Analiz":
        st.subheader("📊 Finansal Sağlık & Bilanço Analizi")
        sub_tab1, sub_tab2 = st.tabs(["Bilanço & Gelir Tablosu", "Finansal Rasyolar"])
        with sub_tab1:
            st.caption("AgGrid veya Plotly grafik entegrasyon alanı")
            
    elif selected_module == "Hukuki Geçmiş":
        st.subheader("⚖️ Dava Dosyaları ve İhale Yasakları Açıklamaları")
```
