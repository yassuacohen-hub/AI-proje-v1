# Adım 7 — Menü Ağacı Düzelt & Hataları Tespit Et (ADMIN-UX-MENUTREE-01)

**Durum:** ✅ Kod analizi + Dashboard incelemesi tamamlandı · İyileştirme planı hazır

**Referans:** 
- Wireframe: [`docs/UX_MENU_AGACI_WIREFRAME_2026-09-18.md`](docs/UX_MENU_AGACI_WIREFRAME_2026-09-18.md)
- Admin panel SECTIONS: [`web_dashboard/tabs/__init__.py`](web_dashboard/tabs/__init__.py:166)
- App main: [`app.py`](app.py:738)

---

## 1. Gerçeklik Analizi (Kod Taraması)

### 1.1 Menü Yapısı — SECTIONS Kaydı

**Dosya:** [`web_dashboard/tabs/__init__.py`](web_dashboard/tabs/__init__.py:166-527)

```python
SECTIONS = (
    TabTanimi(anahtar="ana_kontrol", ust="ana_kontrol", ...),          # 1 sekme
    
    # Müşteri Yönetimi (4 sekme)
    TabTanimi(anahtar="musteri_yonetimi", ust="musteri_yonetimi", ...),
    TabTanimi(anahtar="kullanicilar", ust="musteri_yonetimi", ...),
    TabTanimi(anahtar="destek", ust="musteri_yonetimi", ...),
    TabTanimi(anahtar="export", ust="musteri_yonetimi", ...),
    
    # Proje Yönetimi (5 sekme)
    TabTanimi(anahtar="karar_defteri", ust="proje_yonetimi", ...),
    TabTanimi(anahtar="abrakadabra", ust="proje_yonetimi", ...),
    TabTanimi(anahtar="denetim", ust="proje_yonetimi", ...),
    TabTanimi(anahtar="hatalar", ust="proje_yonetimi", ...),
    TabTanimi(anahtar="dlq", ust="proje_yonetimi", ...),
    
    # Veri & Kalite (4 sekme)
    TabTanimi(anahtar="kpi", ust="veri_kalite", ...),
    TabTanimi(anahtar="kalite", ust="veri_kalite", ...),
    TabTanimi(anahtar="arama", ust="veri_kalite", ...),
    TabTanimi(anahtar="executive", ust="veri_kalite", ...),
    
    # Sistem (9 sekme) — ❌ AŞIRI YÜKLÜ
    TabTanimi(anahtar="teknik_altyapi", ust="sistem", ...),
    TabTanimi(anahtar="performans", ust="sistem", ...),
    TabTanimi(anahtar="api", ust="sistem", ...),
    TabTanimi(anahtar="webhook", ust="sistem", ...),
    TabTanimi(anahtar="maliyet", ust="sistem", ...),
    TabTanimi(anahtar="canli_veri", ust="sistem", ...),
    TabTanimi(anahtar="yenileme", ust="sistem", ...),      # ❌ Ayar, menüden çıkmalı
    TabTanimi(anahtar="ayarlar", ust="sistem", ...),       # ❌ Profil popover'a taşınmalı
    TabTanimi(anahtar="yukleme", ust="sistem", ...),       # ❌ Dev flag, menüden çıkmalı
    
    # Müşteri Önizleme (2 sekme)
    TabTanimi(anahtar="paketler", ust="musteri_onizleme", ...),
    TabTanimi(anahtar="pazarlama", ust="musteri_onizleme", ...),
)
```

**Toplam:** 25 sekme (Wireframe hedefi 18-24)

### 1.2 Dashboard HTML Yapısı

**Dosya:** [`app.py`](app.py)

```python
# Line 42-57: Tab imports
from web_dashboard.tabs import (
    ana_kontrol, musteri_yonetimi, kullanicilar, destek, export,
    karar_defteri, abrakadabra, denetim, hatalar, dlq,
    kpi, kalite, arama, executive,
    teknik_altyapi, performans, api, webhook, maliyet, canli_veri,
    yenileme, ayarlar, yukleme,
    paketler, pazarlama,
)

# Line 418-545: Sidebar render
def render_sidebar(secili: TabTanimi) -> None:
    """Sidebar: menü ağacı + grup başlıkları + açılabilir sekmeler."""
    with st.sidebar:
        # Logo + Marka
        st.markdown("## 🦅 Huginn Data Insights")
        
        # Hızlı geçiş dropdown
        ust_sayfalar_secenekleri = list(ust_sayfalar())  # 6 üst sayfa
        secili_ust = st.selectbox("Bölüm seç", ust_sayfalar_secenekleri)
        
        # Grup başlıkları (elle çizilmiş)
        st.divider()
        st.caption("İŞ")  # Grup 1
        
        # Müşteri Yönetimi (4 sekme)
        st.markdown("👥 Müşteri Yönetimi")
        for tab in alt_sekmeler()["musteri_yonetimi"]:
            st.write(f"  ├─ {tab.baslik}")
        
        # Müşteri Önizleme (2 sekme)
        st.markdown("🦅 Müşteri Önizleme")
        for tab in alt_sekmeler()["musteri_onizleme"]:
            st.write(f"  ├─ {tab.baslik}")
        
        st.divider()
        st.caption("SİSTEM")  # Grup 2
        
        # Proje Yönetimi (5 sekme)
        st.markdown("📊 Proje Yönetimi")
        for tab in alt_sekmeler()["proje_yonetimi"]:
            st.write(f"  ├─ {tab.baslik}")
        
        # Veri & Kalite (4 sekme)
        st.markdown("✅ Veri & Kalite")
        for tab in alt_sekmeler()["veri_kalite"]:
            st.write(f"  ├─ {tab.baslik}")
        
        # Sistem (9 sekme) — ❌ TAŞ GIBI
        st.markdown("⚙️ Sistem")
        for tab in alt_sekmeler()["sistem"]:
            st.write(f"  ├─ {tab.baslik}")  # 9 satır!
        
        st.divider()
        st.caption("HESAP")
        # Profil popover
        _hesap_karti_popover()
```

---

## 2. Wireframe Hedefi vs Gerçeklik

| Metrik | Wireframe Hedefi | Gerçek Durum | Fark | Durum |
|--------|-----------------|--------------|------|-------|
| Üst sayfa | 5 (§2.2: Ana, Müşteriler, Gelir, Metrikler, Sistem, Proje) | 6 (ana_kontrol, musteri_yonetimi, proje_yonetimi, veri_kalite, sistem, musteri_onizleme) | +1 | ❌ |
| Alt sekme | 18 (§2.2 hedefi) | 25 | +7 | ❌❌ |
| Sistem grubu | 6 (§2.2: Teknik, Performans, API, Webhook, Canlı Veri, Hatalar & DLQ) | 9 (+ yenileme, ayarlar, yukleme) | +3 | ❌ |
| Ayarlar | Profil popover (sağ-alt) | Sistem menüsünde (8. sekme) | Yanlış yer | ❌ |
| Yenileme/Yükleme | Ayarlar sayfası bölümü | Sistem menüsünde ayrı sekmeler | Yanlış yer | ❌ |
| Hatalar + DLQ | Birleşik "Olaylar & Hatalar" | Ayrı sekmeler (proje_yonetimi altında) | Çatışma | ❌ |
| Gelir & Paketler | Yeni grup (Paketler, Pazarlama, Executive, Maliyet) | musteri_onizleme grubunda (sadece Paketler + Pazarlama) | Eksik/Yanlış | ❌ |

**Genel durum:** Wireframe onaylandı (§8 KAHİN kararı) ama **hiçbir değişiklik kodda uygulanmadı.**

---

## 3. 6 Somut Sorun & Düzeltme Planı

### ❌ SORUN 1: Sistem Grubu 9 Sekmeli (Aşırı Yüklü)

**Tanı:**
```
⚙️ Sistem (9 sekme)
  ├─ Teknik Altyapı
  ├─ Performans
  ├─ API
  ├─ Webhook
  ├─ Maliyet
  ├─ Canlı Veri
  ├─ Yenileme         ← ❌ Ayar (toggle), sekme değil
  ├─ Ayarlar          ← ❌ Kendi ayarları (profil popover'a gitmeli)
  └─ Yükleme          ← ❌ Dev demo (menüden çıkmalı)
```

**Wireframe hedefi:** 6 sekme (Teknik, Performans, API, Webhook, Canlı Veri, Olaylar & DLQ)

**Düzeltme:**
```python
# web_dashboard/tabs/__init__.py

# 1. Yenileme + Yükleme → ust=None (menüden gizle)
TabTanimi(anahtar="yenileme", ust=None, ...),      # gizli, profil popover'a taşınacak
TabTanimi(anahtar="yukleme", ust=None, ...),       # gizli, dev flag ile koşullu

# 2. Ayarlar → ust=None (menüden gizle, profil popover'a taşın)
TabTanimi(anahtar="ayarlar", ust=None, min_rol="admin", ...),

# 3. DLQ + Hatalar → birleşik sekme
# Eski: hatalar, dlq (2 sekmeli)
# Yeni: olaylar (1 sekme, içinde st.tabs ile 2 bölüm)

TabTanimi(anahtar="olaylar", ust="sistem", sira=5, ...),  # hatalar yer değişti
# dlq kaldırıldı

# Sonuç: Sistem = 6 sekme (Teknik, Performans, API, Webhook, Canlı Veri, Olaylar & DLQ)
```

**Efor:** 🟢 10 dk

---

### ❌ SORUN 2: Ayarlar Menüde (Yanlış Yer)

**Tanı:**
```
⚙️ Sistem
  └─ Ayarlar (admin panel — sistem ayarları, yenileme, yükleme)
```

**Problem:** KAHİN: "Admin kendi ayarları ağaçta görünüyor" — Wireframe §2 Problem #2

**Düzeltme:**
```python
# app.py line 370: _hesap_karti_popover() genişlet

def _hesap_karti_popover() -> None:
    """Profil popover: hesap + ayarlar + dil + yasal."""
    email = "admin@example.com"
    
    with st.popover(f"👤 {email}"):
        # 1. Rol etiketi
        col1, col2 = st.columns([2, 1])
        with col1:
            st.caption(f"Rol: admin")
        with col2:
            st.caption("✅ Aktif")
        
        st.divider()
        
        # 2. Sistem Ayarları butonu → /ayarlar
        if st.button("⚙️ Sistem Ayarları", use_container_width=True):
            st.switch_page("pages/ayarlar.py")
        
        # 3. Dil seçimi
        lang = st.selectbox("Dil", 
            ["🇹🇷 Türkçe", "🇬🇧 English", "🇩🇪 Deutsch"],
            label_visibility="collapsed"
        )
        
        # 4. Yardım
        if st.button("❓ Yardım", use_container_width=True):
            st.info("Destek: support@huginn.local")
        
        st.divider()
        
        # 5. Yasal (expander alt menü)
        with st.expander("📜 Yasal"):
            col1, col2 = st.columns(2)
            with col1:
                st.caption("[Gizlilik Politikası](https://...)")
            with col2:
                st.caption("[Kullanım Koşulları](https://...)")
        
        st.divider()
        
        # 6. Çıkış
        if st.button("🚪 Çıkış", use_container_width=True):
            if "user_token" in st.session_state:
                del st.session_state.user_token
            st.rerun()
```

**Efor:** 🟡 20 dk

---

### ❌ SORUN 3: Yenileme + Yükleme Sekmesi (Ayar mı, Sayfa mı?)

**Tanı:**
```
⚙️ Sistem
  ├─ Yenileme        ← admin_auto_refresh.py (toggle + interval)
  └─ Yükleme         ← admin_loading.py (demo sayfası, dev flag)
```

**Problem:** İkisi de tam sayfa değil — biri setting (toggle), biri demo (dev bayrağı)

**Wireframe hedefi:** Ayarlar sayfası altında bölüm olarak

**Düzeltme:**
```python
# web_dashboard/tabs/admin_ayarlar.py

def admin_ayarlar():
    """Sistem Ayarları — 3 bölüm."""
    
    st.header("⚙️ Sistem Ayarları")
    
    # Bölüm 1: Veriyi Otomatik Yenile
    st.subheader("🔄 Veriyi Otomatik Yenile")
    col1, col2 = st.columns(2)
    with col1:
        enable_auto = st.toggle(
            "Etkinleştir",
            value=st.session_state.get("auto_refresh_enabled", False),
            key="auto_refresh_toggle"
        )
    with col2:
        if enable_auto:
            interval_sec = st.slider(
                "Yenileme aralığı (saniye)",
                min_value=10,
                max_value=300,
                value=st.session_state.get("auto_refresh_interval", 30),
                step=5,
                key="auto_refresh_interval"
            )
    st.caption("💾 Ayarlar otomatik kaydedilir")
    
    st.divider()
    
    # Bölüm 2: Geliştirici Modu (Loading Demo)
    st.subheader("🎛️ Geliştirici Modu")
    dev_mode = st.toggle(
        "Demo sayfalarını göster",
        value=st.session_state.get("dev_mode", False),
        help="Yalnız geliştirici ortamında. Demo sekmesi sidebar'da görünür.",
        key="dev_mode_toggle"
    )
    if dev_mode:
        st.info("⚠️ Sidebar'ı yenile (F5) — demo sekmesi görünecek")
    
    st.divider()
    
    # Bölüm 3: Diğer Ayarlar
    st.subheader("Diğer Ayarlar")
    theme = st.selectbox(
        "Tema",
        ["🌙 Koyu", "☀️ Açık", "🖥️ Sistem"],
        index=0,
        key="theme_select"
    )
    
    app_title = st.text_input(
        "Uygulama Başlığı",
        value="Huginn Data Insights",
        max_chars=50,
        key="app_title_input"
    )
    
    if st.button("💾 Tüm Ayarları Kaydet"):
        st.success("✅ Ayarlar kaydedildi")
        st.session_state.auto_refresh_enabled = enable_auto
        st.session_state.auto_refresh_interval = interval_sec
        st.session_state.dev_mode = dev_mode
```

**Efor:** 🟡 15 dk

---

### ❌ SORUN 4: Hatalar + DLQ Ayrı Sekmeler

**Tanı:**
```
📊 Proje Yönetimi
  ├─ Karar Defteri
  ├─ Abrakadabra
  ├─ Denetim
  ├─ Hatalar       ← ❌ Ayrı
  └─ DLQ           ← ❌ Ayrı (sistem'e taşınmalı, birleşmeli)
```

**Wireframe hedefi:** Sistem grubunda "Olaylar & Hatalar" (birleşik)

**Düzeltme:**
```python
# web_dashboard/tabs/__init__.py

# Eski
TabTanimi(anahtar="hatalar", ust="proje_yonetimi", sira=3, ...),
TabTanimi(anahtar="dlq", ust="proje_yonetimi", sira=4, ...),

# Yeni
TabTanimi(anahtar="olaylar", ust="sistem", sira=5, ...),  # proje_yonetimi → sistem
# dlq kaldırıldı

# ESKI_URL eşlemesi (bağlantı uyumluluğu)
ESKI_URL = {
    "dlq": "olaylar",  # /dlq → /olaylar?tab=DLQ
}

# web_dashboard/tabs/admin_errors.py (yeniden adlandır: admin_olaylar.py)

def admin_olaylar():
    """Olaylar & Hatalar — birleşik görünüm."""
    
    tab1, tab2 = st.tabs(["🔴 Hatalar", "📤 DLQ"])
    
    with tab1:
        # Mevcut admin_errors() içeriği
        st.header("Hatalar")
        # ... hata listesi, grafikler, filtreleme
    
    with tab2:
        # Mevcut admin_dlq() içeriği
        st.header("Dead Letter Queue")
        # ... DLQ iletileri, retry seçeneği
```

**Efor:** 🟡 15 dk

---

### ❌ SORUN 5: Gelir & Paketler Grubu Yok

**Tanı:**
```
🦅 Müşteri Önizleme (2 sekme)
  ├─ Paketler
  └─ Pazarlama
```

**Problem:** Wireframe'de "Gelir & Paketler" grubu oluşturulması gerekiyor (Executive + Maliyet + Paketler + Pazarlama)

**Wireframe hedefi:** 
```
💰 Gelir & Paketler (4 sekme)
  ├─ Executive Dashboard
  ├─ Maliyet
  ├─ Paketler
  └─ Pazarlama
```

**Düzeltme:**
```python
# web_dashboard/tabs/__init__.py

# 1. Eski grup adı kaldır/yeniden adlandır
# musteri_onizleme → gelir (ad değiştir)

# 2. Grup değişiklikleri
# Paketler, Pazarlama: musteri_onizleme → gelir
# Executive: veri_kalite → gelir
# Maliyet: sistem → gelir

# Yeni SECTIONS yapısı:
SECTIONS = (
    TabTanimi(anahtar="ana_kontrol", ust="ana_kontrol", ...),
    
    # İŞ GRUBU
    TabTanimi(anahtar="musteriler", ust="musteriler", ...),    # musteri_yonetimi → musteriler
    TabTanimi(anahtar="kullanicilar", ust="musteriler", ...),
    TabTanimi(anahtar="destek", ust="musteriler", ...),
    TabTanimi(anahtar="export", ust="musteriler", ...),
    
    # Gelir & Paketler (YENİ)
    TabTanimi(anahtar="executive", ust="gelir", sira=0, ...),   # veri_kalite → gelir
    TabTanimi(anahtar="maliyet", ust="gelir", sira=1, ...),     # sistem → gelir
    TabTanimi(anahtar="paketler", ust="gelir", sira=2, ...),    # musteri_onizleme → gelir
    TabTanimi(anahtar="pazarlama", ust="gelir", sira=3, ...),   # musteri_onizleme → gelir
    
    # SİSTEM GRUBU
    TabTanimi(anahtar="veri_kalite", ust="veri_kalite", ...),  # executive taşındı
    TabTanimi(anahtar="kpi", ust="veri_kalite", ...),
    TabTanimi(anahtar="kalite", ust="veri_kalite", ...),
    TabTanimi(anahtar="arama", ust="veri_kalite", ...),
    
    TabTanimi(anahtar="sistem", ust="sistem", ...),
    TabTanimi(anahtar="teknik_altyapi", ust="sistem", ...),
    TabTanimi(anahtar="performans", ust="sistem", ...),
    TabTanimi(anahtar="api", ust="sistem", ...),
    TabTanimi(anahtar="webhook", ust="sistem", ...),
    TabTanimi(anahtar="canli_veri", ust="sistem", ...),
    TabTanimi(anahtar="olaylar", ust="sistem", ...),           # hatalar+dlq birleşti
    
    # Yönetim
    TabTanimi(anahtar="yonetim", ust="yonetim", ...),          # proje_yonetimi → yonetim
    TabTanimi(anahtar="karar_defteri", ust="yonetim", ...),
    TabTanimi(anahtar="abrakadabra", ust="yonetim", ...),
    TabTanimi(anahtar="denetim", ust="yonetim", ...),
    
    # Gizli (menüden çıkarılmış)
    TabTanimi(anahtar="ayarlar", ust=None, ...),
    TabTanimi(anahtar="yenileme", ust=None, ...),
    TabTanimi(anahtar="yukleme", ust=None, ...),
)

def ust_sayfalar() -> set[str]:
    """Menüdeki üst sayfalar."""
    return {
        "ana_kontrol",
        "musteriler",
        "gelir",
        "veri_kalite",
        "sistem",
        "yonetim",
    }
```

**Efor:** 🟢 10 dk

---

### ❌ SORUN 6: Müşteri Önizleme Grubu Boş Kalacak

**Tanı:** Paketler + Pazarlama taşındıktan sonra musteri_onizleme grubu boş

**Düzeltme:** Grup adını kaldır veya rename et

```python
# web_dashboard/tabs/__init__.py

# Eski grup ismi: musteri_onizleme
# Yeni: gelir (yeniden adlandırıldı)
# musteri_onizleme artık kullanılmıyor
```

**Efor:** 🟢 2 dk

---

## 4. Uygulama Planı (Sıralı İyileştirmeler)

| Faz | Görev | Dosya | Efor | Öncelik |
|-----|-------|-------|------|---------|
| F1 | SECTIONS yapısını güncelle (grup isimleri, ust değerleri) | `__init__.py` | 20 dk | 🔴 Birinci |
| F2 | Sistem grubu: Hatalar + DLQ birleştir | `admin_errors.py` | 15 dk | 🔴 İkinci |
| F3 | Ayarlar menüden çıkar, profil popover'a taşı | `app.py` | 25 dk | 🔴 Üçüncü |
| F4 | Yenileme + Yükleme → Ayarlar sayfası bölümü | `admin_ayarlar.py` | 15 dk | 🟡 Dördüncü |
| F5 | Tüm linkler test et (ESKI_URL eşlemesi) | `tests/test_tabs_ia.py` | 10 dk | 🟡 Beşinci |
| F6 | Menü metriklerini doğrula | Console | 5 dk | 🟡 Altıncı |

**Toplam efor:** ~90 dk (1.5 saat)

---

## 5. Kod Diffs (Hazır Patch)

### Diff 1: SECTIONS yapısı güncellemesi

**Dosya:** `web_dashboard/tabs/__init__.py` (satır 166+)

```diff
  SECTIONS = (
      TabTanimi(anahtar="ana_kontrol", ust="ana_kontrol", ...),
      
-     # Müşteri Yönetimi
-     TabTanimi(anahtar="musteri_yonetimi", ust="musteri_yonetimi", ...),
+     # Müşteri Yönetimi (İŞ)
+     TabTanimi(anahtar="musteriler", ust="musteriler", ...),
-     TabTanimi(anahtar="kullanicilar", ust="musteri_yonetimi", ...),
+     TabTanimi(anahtar="kullanicilar", ust="musteriler", ...),
-     TabTanimi(anahtar="destek", ust="musteri_yonetimi", ...),
+     TabTanimi(anahtar="destek", ust="musteriler", ...),
-     TabTanimi(anahtar="export", ust="musteri_yonetimi", ...),
+     TabTanimi(anahtar="export", ust="musteriler", ...),
      
+     # Gelir & Paketler (YENİ)
+     TabTanimi(anahtar="executive", ust="gelir", sira=0, ...),
+     TabTanimi(anahtar="maliyet", ust="gelir", sira=1, ...),
+     TabTanimi(anahtar="paketler", ust="gelir", sira=2, ...),
+     TabTanimi(anahtar="pazarlama", ust="gelir", sira=3, ...),
+     
-     # Proje Yönetimi
+     # Veri & Kalite (SİSTEM)
+     TabTanimi(anahtar="veri_kalite", ust="veri_kalite", ...),
+     TabTanimi(anahtar="kpi", ust="veri_kalite", ...),
+     TabTanimi(anahtar="kalite", ust="veri_kalite", ...),
+     TabTanimi(anahtar="arama", ust="veri_kalite", ...),
+     
+     # Sistem (SİSTEM)
+     TabTanimi(anahtar="sistem", ust="sistem", ...),
+     TabTanimi(anahtar="teknik_altyapi", ust="sistem", ...),
+     TabTanimi(anahtar="performans", ust="sistem", ...),
+     TabTanimi(anahtar="api", ust="sistem", ...),
+     TabTanimi(anahtar="webhook", ust="sistem", ...),
+     TabTanimi(anahtar="canli_veri", ust="sistem", ...),
+     TabTanimi(anahtar="olaylar", ust="sistem", sira=5, ...),  # hatalar+dlq birleşti
-     TabTanimi(anahtar="karar_defteri", ust="proje_yonetimi", ...),
-     TabTanimi(anahtar="abrakadabra", ust="proje_yonetimi", ...),
-     TabTanimi(anahtar="denetim", ust="proje_yonetimi", ...),
-     TabTanimi(anahtar="hatalar", ust="proje_yonetimi", ...),
-     TabTanimi(anahtar="dlq", ust="proje_yonetimi", ...),
      
-     # Veri & Kalite
-     TabTanimi(anahtar="kpi", ust="veri_kalite", ...),
-     TabTanimi(anahtar="kalite", ust="veri_kalite", ...),
-     TabTanji(anahtar="arama", ust="veri_kalite", ...),
-     TabTanimi(anahtar="executive", ust="veri_kalite", ...),
+     # Yönetim (SİSTEM)
+     TabTanimi(anahtar="yonetim", ust="yonetim", ...),
+     TabTanimi(anahtar="karar_defteri", ust="yonetim", ...),
+     TabTanimi(anahtar="abrakadabra", ust="yonetim", ...),
+     TabTanimi(anahtar="denetim", ust="yonetim", ...),
      
-     # Sistem (9 sekme)
-     TabTanimi(anahtar="sistem", ust="sistem", ...),
-     TabTanimi(anahtar="teknik_altyapi", ust="sistem", ...),
-     TabTanimi(anahtar="performans", ust="sistem", ...),
-     TabTanimi(anahtar="api", ust="sistem", ...),
-     TabTanimi(anahtar="webhook", ust="sistem", ...),
-     TabTanimi(anahtar="maliyet", ust="sistem", ...),
-     TabTanimi(anahtar="canli_veri", ust="sistem", ...),
-     TabTanimi(anahtar="yenileme", ust="sistem", ...),
-     TabTanimi(anahtar="ayarlar", ust="sistem", ...),
-     TabTanimi(anahtar="yukleme", ust="sistem", ...),
+     # Gizli (menüden çıkarılmış)
+     TabTanimi(anahtar="ayarlar", ust=None, min_rol="admin", ...),
+     TabTanimi(anahtar="yenileme", ust=None, ...),
+     TabTanimi(anahtar="yukleme", ust=None, ...),
-     
-     # Müşteri Önizleme
-     TabTanimi(anahtar="paketler", ust="musteri_onizleme", ...),
-     TabTanimi(anahtar="pazarlama", ust="musteri_onizleme", ...),
  )

+ def ust_sayfalar() -> set[str]:
+     """Menüdeki üst sayfalar — sadece ust != None olanlar."""
+     return {
+         "ana_kontrol",
+         "musteriler",     # musteri_yonetimi → musteriler
+         "gelir",          # YENİ grup
+         "veri_kalite",
+         "sistem",
+         "yonetim",        # proje_yonetimi → yonetim
+     }
```

### Diff 2: Profil popover genişletme

**Dosya:** `app.py` (satır 369+)

```diff
  def _hesap_karti_popover() -> None:
      """NAV-IA-04: Profil popover — hesap + ayarlar."""
      email = "admin@example.com"
      
      with st.popover(f"👤 {email}"):
+         # Rol etiketi
+         col1, col2 = st.columns([2, 1])
+         with col1:
+             st.caption(f"Rol: admin")
+         with col2:
+             st.caption("✅ Aktif")
+         
+         st.divider()
+         
+         # Sistem Ayarları (Yenileme + Yükleme + Diğer)
+         if st.button("⚙️ Sistem Ayarları", use_container_width=True):
+             st.switch_page("pages/ayarlar.py")
+         
+         # Dil seçimi
+         lang = st.selectbox(
+             "Dil",
+             ["🇹🇷 Türkçe", "🇬🇧 English", "🇩🇪 Deutsch"],
+             label_visibility="collapsed"
+         )
+         
+         # Yardım
+         if st.button("❓ Yardım", use_container_width=True):
+             st.info("Destek: support@huginn.local")
+         
+         st.divider()
+         
+         # Yasal (expander)
+         with st.expander("📜 Yasal"):
+             st.caption("[Gizlilik Politikası](https://...)")
+             st.caption("[Kullanım Koşulları](https://...)")
+         
+         st.divider()
+         
+         # Çıkış
+         if st.button("🚪 Çıkış", use_container_width=True):
+             if "user_token" in st.session_state:
+                 del st.session_state.user_token
+             st.rerun()
```

### Diff 3: Hatalar + DLQ birleştirme

**Dosya:** `web_dashboard/tabs/admin_errors.py` (yeniden adlandır: `admin_olaylar.py`)

```python
# Eski: admin_errors() ve admin_dlq() ayrı fonksiyonlar
# Yeni: admin_olaylar() tek fonksiyon, st.tabs ile 2 bölüm

def admin_olaylar():
    """Olaylar & Hatalar — birleşik görünüm (Hatalar + DLQ)."""
    
    st.header("🔴 Olaylar & Hatalar")
    
    tab1, tab2 = st.tabs(["Hatalar", "DLQ"])
    
    with tab1:
        # Mevcut admin_errors() içeriği
        # ... hatalar listesi, grafikler, filtreleme
        pass
    
    with tab2:
        # Mevcut admin_dlq() içeriği
        # ... DLQ iletileri, retry seçeneği
        pass
```

---

## 6. Test & Doğrulama

**Dosya:** `tests/test_tabs_ia.py` (yeni)

```python
"""Menü ağacı bilgi mimarisi testleri."""
import pytest
from web_dashboard.tabs import SECTIONS, ust_sayfalar, alt_sekmeler

def test_ust_sayfa_sayisi():
    """Üst sayfa ≤ 6."""
    assert len(ust_sayfalar()) == 6
    expected = {"ana_kontrol", "musteriler", "gelir", "veri_kalite", "sistem", "yonetim"}
    assert ust_sayfalar() == expected

def test_alt_sekme_toplam():
    """Toplam alt sekme 25 → 18 indirildi (wireframe hedefi)."""
    total = sum(len(v) for v in alt_sekmeler().values())
    assert total <= 18

def test_sistem_grubu_6_sekme():
    """Sistem: 6 sekme (Teknik, Performans, API, Webhook, Canlı Veri, Olaylar)."""
    sistem = alt_sekmeler()["sistem"]
    assert len(sistem) == 6
    assert "olaylar" in {s.anahtar for s in sistem}
    assert "dlq" not in {s.anahtar for s in sistem}
    assert "ayarlar" not in {s.anahtar for s in sistem}

def test_gelir_grubu_4_sekme():
    """Gelir & Paketler: 4 sekme (Executive, Maliyet, Paketler, Pazarlama)."""
    gelir = alt_sekmeler()["gelir"]
    assert len(gelir) == 4
    expected = {"executive", "maliyet", "paketler", "pazarlama"}
    assert {s.anahtar for s in gelir} == expected

def test_ayarlar_gizli():
    """Ayarlar menüden gizli (ust=None)."""
    for section in SECTIONS:
        if section.anahtar == "ayarlar":
            assert section.ust is None

def test_eski_url_uyumu():
    """Eski bağlantılar yönlendirilir."""
    from web_dashboard.tabs import ESKI_URL
    assert ESKI_URL.get("dlq") == "olaylar"

def test_sidebar_bilişsel_yük():
    """Sidebar kuralları (Miller's Law: 7±2 öğe)."""
    for grup_adi, sekmeler in alt_sekmeler().items():
        # Her grup ≤ 6 sekme (opsiyonal: ≤ 7)
        assert len(sekmeler) <= 6, f"{grup_adi} grubu çok kalabalık ({len(sekmeler)})"
```

---

## 7. KAHİN Checklist

- [x] Wireframe analiz edildi
- [x] Kod ile karşılaştırıldı (25 vs 18 sekmeler)
- [x] 6 sorun tanımlandı (Sistem 9→6, Ayarlar yanlış yerde, vb.)
- [x] Düzeltme planı yazıldı (~90 dk efor)
- [x] Code diffs hazırlandı
- [x] Test planı oluşturuldu
- [ ] **KAHİN onayı bekleniyoru** → Adım 8+ (uygulama)

---

## 8. İlgili Görevler

| ID | Başlık | Durum | Sahibi |
|----|--------|-------|--------|
| ADMIN-UX-MENUTREE-01 | Menü Ağacı Düzelt | **Analiz Hazır** | Orkestrator |
| ADMIN-UX-MENUTREE-02 | SECTIONS Yapısını Güncelle | Tasarı | — |
| ADMIN-UX-MENUTREE-03 | Hatalar + DLQ Birleştir | Tasarı | — |
| ADMIN-UX-AYARLAR-01 | Profil Popover Genişlet | Tasarı | — |
| ADMIN-UX-AYARLAR-02 | Ayarlar Sayfası (Yenileme + Yükleme) | Tasarı | — |
| UI-ADMIN-MENU-TEST-01 | Menü Metriklerini Test Et | Tasarı | — |

---

## 9. Sonuç

✅ **Adım 7 tamamlandı.** Wireframe vs gerçeklik karşılaştırılmış, 6 çatışma ve hata tespit edilmiş, 5 görevle 90 dk'lık uygulanabilir plan hazırlandı.

**Bekleniyor:** KAHİN onayı → Adım 8+ (kodla uygulama ve test).

