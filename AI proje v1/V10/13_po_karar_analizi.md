# PO Karar Analizi — Admin vs Müşteri Panel Metrikleri

> **Ürün Sahibi Karar Destek Belgesi**
> V10 — Admin Panel ve Müşteri Panel için metrik yönetim kararı analizi

Bağlantılar: [[01_sirket_master_ana_belgesi]] · [[12_kalite_metrikleri]] · [[project_state]] · [[TODO]]

---

## 1. Product Owner Stratejisi

### 1.1 İki Panel Modelinin Gerekçesi

Huginn Data Insights ürünü, kullanıcı grubuna göre ikiye ayrılmış bir panel yapısına sahiptir. Bu ayrım şu gerekçelere dayanmaktadır:

**Admin Panel (Yönetim Paneli) — Operasyonel Denetim:**
- Sistem yöneticileri, veri mühendisleri ve operasyon ekibi tarafından kullanılır.
- Veri kalitesinin sağlanması, hataların tespit edilmesi ve düzeltilmesi, kaynak yönetimi ve sistem performansının izlenmesi buradaki sorumluluklardır.
- `web_dashboard/tabs/admin_*.py` dosyalarındaki 19 admin sekmesi bu paneli oluşturur.
- Entity resolution hataları (yanlış bölme/birleştirme), mükerrer kayıtlar, eksik alanlar ve kaynak performans sorunları burada tespit edilir ve düzeltilir.

**Customer Panel (Müşteri Paneli) — İş Değeri Görüntüleme:**
- B2B müşteriler tarafından kullanılır.
- Müşterilerin firmaları araması, paketlerini gözden geçirmesi, kampanyalarını izlemesi sağlanır.
- `web_dashboard/tabs/ana_kontrol.py`, `web_dashboard/tabs/paketler.py` ve `web_dashboard/tabs/pazarlama.py` sekmelerini oluşturur.
- Müşterinin gördüğü verinin niteliği (doluluk, doğruluk, güncellik) doğrudan müşteri memnuniyetini etkiler.

### 1.2 Veri Akış Stratejisi

```
Kaynaklar → ETL → Company Master → Admin Panel (denetim/düzeltme) → Customer Panel (görüntüleme)
```

Admin Panel, verinin kalitesini garanti eder; Customer Panel, bu kalitenin müşteride nasıl hissettiğini gösterir. Bu iki panel arasındaki veri akışı, ürünün temel değer zinciridir.

### 1.3 Stratejik Öncelik Prensibi

> Admin Panel'de tespit edilen ve düzeltilen sorunlar, Customer Panel'deki müşteri deneyimini doğrudan iyileştirir. Dolayısıyla Admin Panel metrikleri öncelikli olarak geliştirilmeli; Customer Panel metrikleri ise müşteri algısını ölçmek için izlenmelidir.

---

## 2. 10 TEMEL GÖSTERGELER

Aşağıdaki tablo, V10 belge temeline dayanan 10 temel göstergesini, panel atamalarını ve kaynak dokümanlarını içerir:

| Gösterge | Açıklama | Panel | Admin Sekmesi | Müşteri Sekmesi | Kaynak Doküman |
|----------|----------|-------|---------------|-----------------|----------------|
| **Coverage** (Kapsam) | Ankara B2B şirketlerinin ne kadarı yakalandı | Customer Panel | admin_kpi.py, admin_musteriler.py | ana_kontrol.py | 01_sirket_master_ana_belgesi.md §16 |
| **Entity Accuracy** | Yanlış bölme/birleştirme oranı | Admin Panel | admin_quality.py, admin_search.py | — | 01_sirket_master_ana_belgesi.md §16 |
| **Duplicate Rate** | Mükerrer oranı | Admin Panel | admin_quality.py, admin_audit.py | — | 01_sirket_master_ana_belgesi.md §16 |
| **Field Completeness** | Alan doluluk oranı | Both | admin_quality.py, admin_kpi.py | ana_kontrol.py | 01_sirket_master_ana_belgesi.md §16 |
| **Freshness** (Güncellik) | Verinin ne kadar güncel olduğu | Admin Panel | admin_kpi.py, admin_realtime.py | — | 01_sirket_master_ana_belgesi.md §16 |
| **Source Reliability** | Kaynak performansı | Admin Panel | admin_kpi.py, admin_sistem.py | — | 01_sirket_master_ana_belgesi.md §16 |
| **Search Quality** | Arama başarısı | Customer Panel | admin_search.py, admin_api_analytics.py | ana_kontrol.py | 01_sirket_master_ana_belgesi.md §16 |
| **Profile Accuracy** | Profil doğruluğu | Customer Panel | admin_musteriler.py | ana_kontrol.py, paketler.py, pazarlama.py | 01_sirket_master_ana_belgesi.md §16 |
| **Evidence Coverage** | Önemli alanların kanıtla desteklenme oranı | Both | admin_quality.py, admin_kpi.py | ana_kontrol.py | 01_sirket_master_ana_belgesi.md §16 |
| **Data Quality Score** | Genel kalite skoru | Admin Panel | admin_kpi.py, admin_quality.py | — | 01_sirket_master_ana_belgesi.md §16, 12_kalite_metrikleri |

### 2.1 Gösterge Açıklama Detayları

**Coverage (Kapsam):**
- Admin: `admin_kpi.py` → "Toplam Firma" KPI kartı; `admin_musteriler.py` → firma listesi ve kalite görünümü
- Customer: `ana_kontrol.py` → "Toplam Firma" mavi metrik kartı — müşterinin veri setinin genişliğini gösterir

**Entity Accuracy:**
- Admin: `admin_quality.py` → Kalite skoru dağılımı ve entity confidence metrikleri; `admin_search.py` → arama sonuçlarının doğruluğu
- Customer panelinde doğrudan gösterilmez; düzeltme işlemi tamamen admin sorumluluğundadır

**Duplicate Rate:**
- Admin: `admin_quality.py` → kalite analizi kapsamında deduplikasyon; `admin_audit.py` → denetim kayıtları
- Mükerrer kayıtların tespiti ve birleştirme kararları burada yapılır

**Field Completeness (Alan Doluluk):**
- Admin: `admin_quality.py` → "Eksik Alan Analizi" tablosu ve grafik; `admin_kpi.py` → "Alan Bazlı Kalite Analizi" bölümü
- Customer: `ana_kontrol.py` → dolu alanların göstergeleri profil üzerinde müşteriye görünür

**Freshness (Güncellik):**
- Admin: `admin_kpi.py` → Kalite Skoru Trendi (7/30/90 gün); `admin_realtime.py` → canlı veri akisi ile son güncelleme takibi
- `12_kalite_metrikleri.md` §2.6 Veri Güncelliği metrikleri (0-8 puan) burada değerlendirilir

**Source Reliability (Kaynak Performansı):**
- Admin: `admin_kpi.py` → "Veri Kaynakları Durumu" bölümü; `admin_sistem.py` → sistem performans izleme
- Kaynakların sağlık durumu, başarı oranı ve güncelleme sıklığı admin tarafından yönetilir

**Search Quality:**
- Admin: `admin_search.py` → global arama ve filtreleme (kalite skoru aralığı, kaynak tipi filtre); `admin_api_analytics.py` → arama endpoint kullanım analitiği
- Customer: `ana_kontrol.py` → arama sonuçları ve kalite göstergeleri; müşteri arama deneyimi doğrudan bu metrikle ölçülür

**Profile Accuracy:**
- Admin: `admin_musteriler.py` → firma listesi ve kalite görünümü
- Customer: `ana_kontrol.py` → firma profili görüntüleme; `paketler.py` → paket atama doğruluğu; `pazarlama.py` → segment-firma eşleştirme doğruluğu

**Evidence Coverage:**
- Admin: `admin_quality.py` → kalite riski filtreleme ve iyileştirme önerileri; `admin_kpi.py` → kaynak sağlığı
- Customer: `ana_kontrol.py` → kanıt destekli profil bilgileri; müşteri kanıt kaynaklarını görebilir

**Data Quality Score:**
- Admin: `admin_kpi.py` → ana KPI kartları (genel kalite skoru); `admin_quality.py` → kalite skoru dağılımı, ortalama/medyan/min/max metrikler
- `12_kalite_metrikleri.md` genel skor formülü (Temel alanlar + Bonuslar - Ceza) burada uygulanır
- Customer panelinde direkt gösterilmez; sistem sağlığının göstergesidir

---

## 3. ADMIN PANEL METRİK HARİTASI

Aşağıdaki harita, her admin_* sekmesinin hangi metrikleri gösterdiğini veya hangi göstergelerle ilişkili olduğunu belirtir:

### 3.1 Temel Veri ve Denetim Sekmeleri

| Admin Sekme | Dosya | İlişkili Gösterge | Metrik Detayları |
|-------------|-------|---------------------|-------------------|
| **Veri Kalitesi Özeti** | `admin_quality.py` | Entity Accuracy, Duplicate Rate, Field Completeness, Evidence Coverage, Data Quality Score | Kalite skoru dağılımı (bucket bazlı), eksik alan analizi, iyileştirme önerileri, kalite riski filtreleme (QS<30), medyan/ortalama/min/max metrikler |
| **Admin Dashboard KPI** | `admin_kpi.py` | Coverage, Field Completeness, Freshness, Source Reliability, Evidence Coverage, Data Quality Score | Toplam firma, kalite skoru trendi (7/30/90 gün), alan bazlı kalite (doluluk %), kaynak sağlığı (pie chart), API kullanım trendi, AI maliyet KPI |
| **Admin Denetim** | `admin_audit.py` | Duplicate Rate, Entity Accuracy | Decision Log, dosya kilidi durumu, handoff logu, görev durumu özeti, trigger logu — denetim ve uyum takibi |
| **Karar Defteri** | `admin_panel.py` | Entity Accuracy (review decisions) | Decision Log kayıtları — entity resolution kararları ve onay geçmişi |

### 3.2 Sistem ve Altyapı Sekmeleri

| Admin Sekme | Dosya | İlişkili Gösterge | Metrik Detayları |
|-------------|-------|---------------------|-------------------|
| **Sistem** | `admin_sistem.py` | Source Reliability, Data Quality Score | Webhook DLQ, performans, API analitiği, maliyet dashboard — sistem sağlığı ve kaynak performansı |
| **Sistem Performansı** | `admin_performance.py` | Data Quality Score, Source Reliability | Query latency, cache hit ratio, slow queries, Prometheus metrikleri, OpenTelemetry trace linking |
| **AI Maliyet Dashboard** | `admin_cost.py` | Data Quality Score | Provider bazlı maliyet analizi, anomali tespiti, latency vs maliyet, verimlilik heatmap |
| **Canlı Veri Akisi** | `admin_realtime.py` | Freshness, Data Quality Score | SSE ile gerçek zamanlı KPI (toplam firma, sinyal, API çağrı, sistem sağlığı), 24 saat trend |
| **Webhook DLQ** | `admin_dlq.py` | Data Quality Score | DLQ istatistikleri, hata türleri, retry işlemleri — veri akışı tutarlılığı takibi |

### 3.3 Arama ve Yönetim Sekmeleri

| Admin Sekme | Dosya | İlişkili Gösterge | Metrik Detayları |
|-------------|-------|---------------------|-------------------|
| **Global Arama** | `admin_search.py` | Entity Accuracy, Search Quality | Firma arama (isim, VKN, telefon, email, NACE), kalite skoru filtreleme, kaynak tipi filtreleme |
| **API Analitiği** | `admin_api_analytics.py` | Search Quality, Source Reliability | Endpoint kullanım istatistikleri, tier bazlı kullanım, rate-limit yapılandırması, sistem metrikleri |
| **Yönetim** | `admin_yonetim.py` | Entity Accuracy, Field Completeness | API/kullanıcı yönetimi, arama, export, otomatik yenileme — tüm idari işlemler |
| **Müşteriler** | `admin_musteriler.py` | Coverage, Profile Accuracy | Firma listesi, kalite skoru filtreleme, kaynak filtreleme — müşteri görünümü admin denetimi için |
| **Veri Export** | `admin_export.py` | Coverage, Field Completeness, Data Quality Score | KPI metrikleri, firma verileri, audit log, görev panosu export (CSV/Excel) |

### 3.4 Destek Sekmeleri

| Admin Sekme | Dosya | Açıklama |
|-------------|-------|----------|
| **Admin Girişi** | `admin_auth.py` | Admin giriş ekranı, JWT token yönetimi |
| **Loading States** | `admin_loading.py` | Progress bar, skeleton loader, timeout ayarları |
| **Auto Refresh** | `admin_auto_refresh.py` | Otomatik yenileme aralığı (15-600s) ayarlama |
| **Hata Yönetimi** | `admin_errors.py` | 404/500 hata sayfaları, hata raporlama, istatistikler |
| **Kullanıcı Ayarları** | `admin_panel.py` (ayarlar) | Sema odaklı form üretimi, doğrulama, kalıcı kayıt |

---

## 4. MÜŞTERİ PANEL METRİK HARİTASI

Aşağıdaki harita, her müşteri sekmesinin hangi metrikleri gösterdiğini belirtir:

### 4.1 Ana Kontrol

| Müşteri Sekme | Dosya | İlişkili Gösterge | Metrik Detayları |
|---------------|-------|---------------------|-------------------|
| **Ana Kontrol** | `ana_kontrol.py` | Coverage, Search Quality, Profile Accuracy, Evidence Coverage | **Mavi Kartlar (Müşteri):** Toplam Firma, Aktif Kullanıcı, Sinyal Sayısı, API Çağrıları (24h) · **Turuncu Kartlar (Sistem):** Sistem Durumu, DLQ, Cache Hit Oranı, Query Latency · Anlık uyarılar, webhook akışı grafiği |

### 4.2 Paketler

| Müşteri Sekme | Dosya | İlişkili Gösterge | Metrik Detayları |
|---------------|-------|---------------------|-------------------|
| **Paketler** | `paketler.py` | Profile Accuracy | Paketler kataloğu, fiyatlar, özellikler, çapraz satış önerileri — firmanın profil doğruluğu ve paket uyumu müşteri tarafından değerlendirilir |

### 4.3 Pazarlama

| Müşteri Sekme | Dosya | İlişkili Gösterge | Metrik Detayları |
|---------------|-------|---------------------|-------------------|
| **Pazarlama** | `pazarlama.py` | Profile Accuracy, Evidence Coverage | Kampanya listesi, performans özeti (CTR, dönüşüm oranı, bütçe), segmentler, segment-kampanya kapsaması — segment-firma eşleştirme doğruluğu; Profil doğruluğu ve Evidence Coverage etkilenir |

---

## 5. V10 UYGULAMA ÖNCELİKLERİ

### 5.1 Admin Panel Öncelikleri

| Öncelik | Gösterge | Sekme | Açıklama | Neden |
|---------|----------|-------|----------|-------|
| **P0** | Data Quality Score | `admin_kpi.py`, `admin_quality.py` | Genel kalite skoru KPI kartları ve dağılımı | Sistem sağlığının temel göstergesidir; tüm diğer metriklerin temelidir |
| **P0** | Field Completeness | `admin_quality.py` | Eksik alan analizi ve iyileştirme önerileri | Kritik alanların doluluğu veri kalitesinin en hızlı iyileştirilebilecek faktörüdür |
| **P0** | Freshness | `admin_kpi.py` | Kalite skoru trendi (7/30/90 gün) | Güncellik, verinin geçerliliğini doğrudan etkiler |
| **P1** | Source Reliability | `admin_kpi.py` | Kaynak sağlığı durumu | Kaynak yönetimi uzun vadeli kalite için kritiktir |
| **P1** | Entity Accuracy | `admin_quality.py`, `admin_search.py` | Entity confidence ve çözümleme kalitesi | Yanlış birleştirme/bölme tutarlı veriyi olumsuz etkiler |
| **P1** | Coverage | `admin_kpi.py`, `admin_musteriler.py` | Toplam firma sayısı ve kapsam büyümesi | Kapsam, ürün değerinin temel ölçüsüdür |
| **P2** | Duplicate Rate | `admin_quality.py`, `admin_audit.py` | Deduplikasyon ve denetim | Mükerrer kayıtlar veri güvenilirliğini azaltır |
| **P2** | Evidence Coverage | `admin_quality.py`, `admin_kpi.py` | Kanıt kapsam analizi | Intelligence katmanı için ön hazırlık |
| **P2** | Search Quality | `admin_search.py`, `admin_api_analytics.py` | Arama kalitesi ve endpoint kullanımı | Arama başarısı kullanıcı deneyimini etkiler |
| **P3** | Profile Accuracy | `admin_musteriler.py` | Profil doğruluğu denetimi | Müşteri görünümü doğrulama |

### 5.2 Customer Panel Öncelikleri

| Öncelik | Gösterge | Sekme | Açıklama | Neden |
|---------|----------|-------|----------|-------|
| **P0** | Coverage | `ana_kontrol.py` | Toplam Firma metrik kartı | Müşterinin veri setinin kapsamını bilmesi temel beklentisidir |
| **P0** | Search Quality | `ana_kontrol.py` | Arama sonuçları ve kalite göstergeleri | Arama başarısı müşteri memnuniyetinin belirleyicisidir |
| **P0** | Profile Accuracy | `ana_kontrol.py` | Firma profili doğruluğu | Müşterinin gördüğü verinin doğruluğu güveni doğrudan etkiler |
| **P1** | Field Completeness | `ana_kontrol.py` | Dolu alan göstergeleri | Eksik profiler müşteri güvenini azaltır |
| **P1** | Search Quality | `admin_search.py` (admin desteği) | Kalite skoru aralığı filtrelemesi | Müşteri arama deneyimini zenginleştirir |
| **P2** | Evidence Coverage | `ana_kontrol.py` | Kanıt destekli bilgiler | Profil güveni artırma için ikincil öncelik |
| **P2** | Profile Accuracy | `paketler.py`, `pazarlama.py` | Paket/segment uyumlu profiller | Çapraz satış ve pazarlama doğruluğu |

---

## 6. KARAR NOTLARI (Decision Log)

> Bu bölüm, gelecekteki Ürün Sahibi kararlarının kaydedildiği karar defteridir. Her karar tarih, karar, gerekçe ve etiket formatında kaydedilmelidir.

### Karar Kayıt Formatı

```
Tarih: [YYYY-MM-DD]
Karar: [Karar Özeti]
Gerekçe: [Neden bu karar alındı]
Etiketler: [karar-kategorisi, ilgili-göstergeler, ilgili-panel]
Durum: [active | superseded | reversed]
```

### Giriş Kararları (V10 Başlangıç)

| Tarih | Karar | Gerekçe | Etiketler | Durum |
|-------|-------|---------|-----------|-------|
| 2026-09-14 | Admin ve Customer panel ayrımı kesinleştirildi | İki farklı kullanıcı grubunun ihtiyaçları farklıdır; admin operasyonel denetim, müşteri iş değeridir | admin-vs-customer, strategy, both | active |
| 2026-09-14 | 10 temel gösterge V10 metrik çerçevesi olarak belirlendi | V10 belge temeline dayalı; 01_sirket_master_ana_belgesi.md §16 ve 12_kalite_metrikleri kaynaklı | kpi, v10, indicators | active |
| 2026-09-14 | Coverage ve Search Quality Customer Panel'e tahsis edildi | Müşterilerin veri kapsamını ve arama deneyimini doğrudan etkiler | coverage, search-quality, customer-panel | active |
| 2026-09-14 | Entity Accuracy, Duplicate Rate, Freshness, Source Reliability, Data Quality Score Admin Panel'e tahsis edildi | Bu göstergeler teknik denetim ve düzeltme gerektirir; müşteri arayüzünden yönetilmez | entity-accuracy, duplicate-rate, freshness, source-reliability, data-quality-score, admin-panel | active |
| 2026-09-14 | Field Completeness ve Evidence Coverage Both Panel'e tahsis edildi | Admin izler, müşteri yararlanır; ikisi için de ortak sorumluluk vardır | field-completeness, evidence-coverage, both | active |
| 2026-09-14 | Profile Accuracy Customer Panel'e tahsis edildi | Profil doğruluğu müşteri doğrudan görür ve güvenini etkiler | profile-accuracy, customer-panel | active |
| 2026-09-14 | Admin Panel P0 öncelikleri belirlendi | Data Quality Score, Field Completeness ve Freshness temel kalite gösterge leridir; bunlar olmadan diğer metrikler anlamlıdır | p0, admin-panel, quality | active |
| 2026-09-14 | Customer Panel P0 öncelikleri belirlendi | Coverage, Search Quality ve Profile Accuracy müşteri deneyiminin temel taşlarıdır | p0, customer-panel, experience | active |

---

*Son güncelleme: 2026-09-14 · Versiyon: V10 · Ürün: Huginn Data Insights*

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/ADMIN_DASHBOARD_HUB]]
