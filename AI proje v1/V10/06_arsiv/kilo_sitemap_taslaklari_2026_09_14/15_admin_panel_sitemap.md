# Admin Paneli Menü Ağaçı (Sitemap) — V10

Bağlantılar: [[14_po_panel_haritasi]] · [[13_po_karar_analizi]] · [[01_sirket_master_ana_belgesi]] · data/orchestrator/task_board.json · CHANGELOG → [[CHANGELOG]]

> **Amac:** Mevcut 20 admin sekmesi + 3 müşteri sekmesini, kullanıcı rolleri ve iş akışına göre hiyerarşik bir menü yapısına dönüştürmek.
> **Tarih:** 2026-09-14
> **Durum:** Taslak — PO ve mimari onayı bekleniyor.

---

## 1. Mevcut Panel Bileşenleri Envanteri

### Admin Paneli (20 sekme)

| # | Dosya | Açıklama |
|---|-------|----------|
| 1 | admin_kpi.py | KPI Kartları — Müşteri, API, Sinyal, Sistem Sağlığı (P7-25) |
| 2 | admin_panel.py | Karar Defteri + Kullanıcı Ayarları (P7-46) |
| 3 | admin_musteriler.py | Müşteri Listesi, Filtre, Kalite Bildirimleri |
| 4 | admin_quality.py | Veri Kalitesi — Kaynak, Alan, Sığlık Kalitesi Raporu |
| 5 | admin_cost.py | AI Maliyet Dashboardu — Provider bazlı maliyet, anomali (P7-27) |
| 6 | admin_performance.py | Sistem Performansı — Latency, Cache, Slow Query (P7-33) |
| 7 | admin_webhook_monitor.py | Webhook Sağlığı — Endpoint health, olay, DLQ |
| 8 | admin_dlq.py | Dead Letter Queue — Hatalı mesajlar, yeniden deneme |
| 9 | admin_errors.py | Hata Sayfaları — 404, 500, Bağlantı Hatası (P7-43) |
| 10 | admin_loading.py | Loading UX — Skeleton, Progress, Async Durumu (P7-42) |
| 11 | admin_realtime.py | Canlı Veri Akışı — SSE Admin Sekmesi (P7-45) |
| 12 | admin_api_analytics.py | API Analitiği — Kullanım, Rate Limit, Tier (P7-32) |
| 13 | admin_audit.py | Denetim Logu — Karar, Kullanıcı, Veri Kayıtları |
| 14 | admin_auth.py | Kimlik Doğrulama — Yetki, Rol, Token Yönetimi |
| 15 | admin_extras.py | API Yönetimi + Kullanıcı Yönetimi (ekranlar) |
| 16 | admin_yonetim.py | Yönetim — API/Kullanici/Export/Araç/Yenileme |
| 17 | admin_sistem.py | Sistem — Webhook, DLQ, Performans, Maliyet, API |
| 18 | admin_auto_refresh.py | Otomatik Yenileme Ayarları |
| 19 | admin_search.py | Global Arama — Firma, Kaynak, Sorgu |
| 20 | admin_export.py | Veri Exportu — CSV, Excel, PDF Raporlama |

### Müşteri Paneli (3 sekme)

| # | Dosya | Açıklama |
|---|-------|----------|
| 1 | ana_kontrol.py | Ana Dashboard — Müşteri + Sistem metrikleri (K4 renk) |
| 2 | paketler.py | Paketler — Subscription, Fiyat, Upgrade |
| 3 | pazarlama.py | Pazarlama — Kampanyalar, Fırsatlar, Kampanya Durum |

---

=
## 2. Menü Ağaçı (Sitemap) — V10 Önerisi

### 🏠 [ALL] Ana Sayfa / Dashboard

> İlk açık ekran. KPI özeti + sistem sağlığı + hızlı eylem.

🏠 Ana Sayfa
├── 📊 KPI Özeti (admin_kpi)
│   ├── Toplam Firma / Aktif Kullanıcı / API / Sinyal
│   ├── Kalite Skoru Trendi
│   ├── Alan Doluluk Analizi
│   └── Kaynak Sağlığı Grafikleri
├── ⚡ Sistem Sağlığı (admin_performance)
│   ├── Query Latency
│   ├── Cache Hit Oranı
│   └── Prometheus / OTel Bağlantısı
├── 🔴 Hata Bildirimleri (admin_errors)
│   ├── Son 404 / 500 Hataları
│   └── Bağlantı Hatası Logu
└── 🔄 Canlı Durum (admin_realtime)
    ├── SSE Stream
    └── Son Olaylar

👥 [ADMIN] Müşteri ve Kullanıcı Yönetimi

> Kimler var, ne yapabiliyor, hangi firmalara ait?

👥 Müşteri & Kullanıcı Yönetimi
├── 👥 Müşteri Listesi (admin_musteriler)
│   ├── Firma Arama ve Filtreleme
│   ├── Kalite Skoru Sliders
│   ├── Kaynak Bazlı Filtreleme
│   └── Firma Detay / Profil
├── 🔑 Kullanıcı Yönetimi (admin_extras → render_user_management)
│   ├── Kullanıcı Listesi (Rol, Durum, E-posta)
│   ├── Yeni Kullanıcı Davet Et
│   └── & Şifre Sıfırlama
└── 📋 Karar Defteri (admin_panel → render_decision_tab)
    ├── Son 50 Karar Kaydı
    ├── Karar Veren / Etiketler
    └── Detay Görüntüleme

===

📊 [ALL] Veri ve Kalite Yönetimi

> Veri bizim ürünümüz. Kalite = güven.

📊 Veri & Kalite Yönetimi
├── 🎯 Kalite Skoru Panosu (admin_quality)
│   ├── Genel Kalite Skoru
│   ├── Kaynak Bazlı Kalite
│   └── Alan Bazlı Doluluk
├── 🔗 Kaynak Yönetimi (admin_quality)
│   ├── Kaynak Listesi ve Durum
│   └── Kaynak Bazlı Performans
├── 📡 Canlı Veri Akışı (admin_realtime)
│   ├── SSE Endpoint Durumu
│   └── Son Veri Akışı
└── 📤 Veri Exportu (admin_export)
    ├── CSV / Excel / PDF
    └── Raporlama Şablonları

🔧 [ADMIN] Sistem ve Altyapı

> Platformun omurgası. Altyapı sorunları burada tespit edilir.

💰 Maliyet Dashboardu (admin_cost)
├── Provider Bazlı Maliyet (9Router)
├── Günlük/Aylık Tahmini
├── Anomali Tetikleyicileri
└── Token Kullanımı
⚙️ Performans (admin_performance)
├── Response Time Trendi
├── Cache İstatistikleri
└── Slow Query Logu
📡 API Analitiği (admin_api_analytics)
├── Endpoint Kullanım İstatistikleri
├── Tier Bazlı Dağılım
└── Rate Limit Durumu
📨 Webhook Monitoru (webhook_monitor)
├── Endpoint Health Check
├── Olay İstatistikleri
└── DLQ Kayıtları
🗑️ Dead Letter Queue (admin_dlq)
├── Hatalı Mesajlar
├── Yeniden Deneme Geçmişi
└── Retry/backoff Kontrolü
🔄 Otomatik Yenileme (admin_auto_refresh)
└── Yenileme Aralığı Ayarları
🔍 Global Arama (admin_search)
├── Firma Arama
├── Kaynak Arama
└── Sorgu Geliştirme

===

### System Admin İçin Optimal Akış
1. 🏠 Ana Sayfa → Sistem Sağlığı kontrolü
2. 🔧 Sistem
3. 📊 Veri
4. 🛡️ Güvenlik
5. 👥 Müşteri Yönetimi → Kullanıcı/Rol güncellemeleri

### Operations Manager İçin Optimal Akış
1. 🏠 Ana Sayfa → KPI Özeti
2. 👥 Müşteri Yönetimi → Müşteri Listesi, Filtreleme
3. 📊 Veri
4. 📡 Canlı Veri → Gerçek Zamanlı Durum
5. 📤 Export → Raporlama

### Data Engineer İçin Optimal Akış
1. 📊 Veri
2. 🔧 Sistem → API Analitiği, Performans
3. 📡 Canlı Veri → SSE Durumu
4. 📤 Export → Veri Exportu
5. 🔍 Arama → Firma/Kayıt Araştırma

### Product Owner İçin Optimal Akış
1. 🏠 Ana Sayfa → Genel Bakış
2. 📊 KPI Özeti → İş Metrikleri
3. 👥 Müşteri Yönetimi → Müşteri Ve Kullanıcı Durumu
4. 📋 Karar Defteri → Onay Bekleyen Kararlar
5. 🛡️ Denetim → Karar Geçmişi

### Developer İçin Optimal Akış
1. 🔧 Sistem → API Analitiği, Performans
2. 🛡️ Güvenlik → Auth, Denetim Logu
3. 📡 Canlı Veri → SSE Debug
4. 🔍 Arama → Hızlı Kayıt Bulma
5. 📨 Webhook → Hata Debugleme

---

🏢 Müşteri Paneli (B2B)
🏠 Ana Kontrol (ana_kontrol)
Müşteri Metrikleri (Mavi Kartlar)
Sistem Metrikleri (Turuncu Kartlar)
Hızlı Eylem Butonları
📦 Paketler (paketler)
Aktif Paket Bilgisi
Fiyat ve Tier Karşılaştırma
Upgrade / Downgrade
Ödeme Geçmişi
📢 Pazarlama (pazarlama)
Aktif Kampanyalar
Segment Önerileri
Fırsatlar ve Kampanya Durumları

===

5. İsim Önerileri (Naming Map)

| Mevcut Dosya | Teknik İsim | Ekranda Gösterilecek İsim |
|---|---|---|
| admin_kpi.py | admin_kpi | 📊 KPI Özeti |
| admin_panel.py | admin_panel | ⚙️ Ayarlar |
| admin_musteriler.py | admin_musteriler | 👥 Müşteriler |
| admin_quality.py | admin_quality | 🎯 Veri Kalitesi |
| admin_cost.py | admin_cost | 💰 Maliyet |
| admin_performance.py | admin_performance | ⚡ Performans |
| webhook_monitor.py | webhook_monitor | 📨 Webhook |
| admin_dlq.py | admin_dlq | 🗑️ DLQ |
| admin_errors.py | admin_errors | ❌ Hata Yönetimi |
| admin_loading.py | admin_loading | ⏳ Loading |
| admin_realtime.py | admin_realtime | 🔴 Canlı Veri |
| admin_api_analytics.py | admin_api_analytics | 📡 API Analitiği |
| admin_audit.py | admin_audit | 🛡️ Denetim |
| admin_auth.py | admin_auth | 🔐 Güvenlik |
| admin_extras.py | admin_extras | 🔧 Ekranlar |
| admin_yonetim.py | admin_yonetim | 🛠️ Yönetim |
| admin_sistem.py | admin_sistem | 🔧 Sistem |
| admin_auto_refresh.py | admin_auto_refresh | 🔄 Yenileme |
| admin_search.py | admin_search | 🔍 Arama |
| admin_export.py | admin_export | 📤 Export |
| ana_kontrol.py | ana_kontrol | 🏠 Ana Kontrol |
| paketler.py | paketler | 📦 Paketler |
| pazarlama.py | pazarlama | 📢 Pazarlama |

6. İlerleyen İş Akışı Bağlantıları

| Gereksinim | İlgili Görev | Açıklama |
|---|---|---|
| MFA zorunluluğu | PO-BACK-07 (Feature Flags) | Admin auth sekmesine MFA flag ekleme |
| SLA takibi | PO-BACK-11 (Source Reliability) | Kaynak bazlı SLA dashboardu |
| Hata raporlama | PO-BACK-06 (Destek Merkezi) | Hata → ticket pipeline |
| Kampanya durum makinesi | PO-BACK-03 | Admin panelinde kampanya sekmesi |
| Paket fiyat kataloğu | PO-BACK-04 | Müşteri panelinde fiyat tablosu |
| Tazelik etiketi | PO-BACK-05 | Her sekmede Son güncelleme |
| Coverage analytics | PO-BACK-10 | Admin + Müşteri panelinde |
| Duplicate rate | PO-BACK-09 | Admin dedup dashboardu |

7. Tasarım Prensipleri

1. **Öncelik sıralaması:** En sık kullanılan ekranlar ilk 2 sekmeye yerleştirilir.
2. **Rol bazlı görünürlük:** Yetki olmayan ekranlar gizlenir (not stubbed).
3. **Renk kodlaması:** Mavi = Müşteri, Turuncu = Sistem (K4 kuralı).
4. **Boş durum:** \" Veri gelince X burada "görünecek\ mesajı (admin_kpi).
5. **Düzenleme:** Cache TTL = 30sn (vurgulanmamış), 60sn (vurgulanmış).
6. **Tasarım:** @st.cache_data(ttl=) dekoratörü tüm veri yükleme fonksiyonlarında zorunlu.
7. **Dışa aktarma:** Export ekranı tüm görüntülenen veriyi desteklemelidir.
8. **Yenileme:** Her ekranında \" "Yenile\ butonu ve otomatik yenileme seçeneği.

*Son güncelleme: 2026-09-14*
*Doküman: V10/15_admin_panel_sitemap.md*

