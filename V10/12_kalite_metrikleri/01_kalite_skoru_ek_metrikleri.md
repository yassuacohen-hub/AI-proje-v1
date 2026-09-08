# Kalite Skoru Ek Metrikleri — Gelecek Geliştirme Önerisi

> Bu belge, kalite skorunu zenginleştirmek için önerilen yeni metrikleri tanımlar.
> Henüz uygulanmamıştır; diğer ajanların görüşleri sonrası planlama aşamasına alınacaktır.
> Referans: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`

---

## 1. Mevcut Durum

Güncel kalite skoru formülü (2026-09-08 tarihli güncelleme):

| Alan | Puan | Açıklama |
|------|------|----------|
| Telefon | 15 | `primary_phone` veya `raw_phone` dolu |
| E-posta | 10 | `primary_email` veya `raw_email` dolu |
| Web sitesi | 10 | `website_domain` veya `raw_website` dolu |
| Adres | 10 | `adres` veya payload `adres` dolu |
| NACE | 15 | `nace_code` dolu |
| Vergi no | 10 | `vergi_no`/`tax_number` veya payload/raw dolu |
| OSB parsel | 5 | `osb_parsel` dolu |
| Sektör | 10 | payload `sektor` dolu |
| Kaynak bağlantısı | 5 | `source_record_id` dolu |
| Payload verisi | 5 | `raw_payload` içinde en az 1 alan dolu |
| **Ceza: vergi eksik** | -5 | Tüm vergi alanları boş |
| **Ceza: adres eksik** | -3 | Tüm adres alanları boş |
| **Ceza: web eksik** | -2 | Tüm web alanları boş |
| **Ceza: tüm iletişim boş** | -2 | Telefon, email, vergi tümü boş |

**Ortalama skor:** 63.94/100 (10,105 firma)

### Sınırlılıklar
- Vergi_no ve adres gibi kritik alanlar neredeyse boş (%0.4 ve %6.3)
- Web kazıma ile VKN bulunamadı (0/3,065 site)
- Harici API bağımlılığı olmadan skor artışı zor
- "Gerçek" firma aktivitesi ölçülmüyor

---

## 2. Önerilen Yeni Metrikler

### 2.1 İş İlanı Sayısı (0-8 puan)

**Amaç:** Firmanın aktif olup olmadığını, büyüklüğünü tahmin etmek.

**Veri Kaynağı:**
- Firma web sitesi / kariyer sayfası
- LinkedIn Jobs API
- İş ilanı platformları (Kariyer.net, Secret Ankara)

**Puanlama:**
| İlan Sayısı | Puan |
|-------------|------|
| 0 | 0 |
| 1-2 | 2 |
| 3-5 | 4 |
| 6-10 | 6 |
| 11-20 | 7 |
| 20+ | 8 |

**Güncelleme Sıklığı:** Aylık

---

### 2.2 Çalışan Sayısı Aralığı (0-7 puan)

**Amaç:** Firmanın büyüklüğünü ve kapasitesini ölçmek.

**Veri Kaynağı:**
- Web sitesi "Hakkımızda" / "Kurumsal" sayfası
- LinkedIn şirket sayfası
- GİB / MERSİS API (gelecek)

**Puanlama:**
| Çalışan Aralığı | Puan |
|-----------------|------|
| Belirsiz / 0 | 0 |
| 1-10 | 2 |
| 11-50 | 3 |
| 51-200 | 4 |
| 201-500 | 5 |
| 501-1000 | 6 |
| 1000+ | 7 |

**Güncelleme Sıklığı:** 3 ayda bir

---

### 2.3 Sosyal Medya Varlığı (0-5 puan)

**Amaç:** Firmanın dijital varlığını ve etkileşim düzeyini ölçmek.

**Veri Kaynağı:**
- `raw_payload` `sosyal_medya` alanı (8,313 kayıt mevcut)
- Ek scrape: LinkedIn, Instagram, Twitter/X

**Puanlama:**
| Platform Sayısı | Puan |
|-----------------|------|
| Yok | 0 |
| 1 platform | 2 |
| 2-3 platform | 3 |
| 4+ platform | 5 |

**Güncelleme Sıklığı:** Aylık

---

### 2.4 E-posta Domain Geçerliliği (0-3 puan)

**Amaç:** E-posta adreslerinin gerçek ve iletilebilir olup olmadığını kontrol etmek.

**Veri Kaynağı:**
- DNS MX kaydı sorgusu
- SMTP bağlantı testi (catch-all tespiti)

**Puanlama:**
| Durum | Puan |
|-------|------|
| Geçersiz domain / MX yok | 0 |
| MX kaydı var, catch-all bilinmiyor | 2 |
| MX kaydı var, deliverable | 3 |

**Güncelleme Sıklığı:** 6 ayda bir

---

### 2.5 Telefon Formatı Geçerliliği (0-2 puan)

**Amaç:** Telefon numaralarının Türkiye formatında ve tutarlı olup olmadığını kontrol etmek.

**Veri Kaynağı:**
- Regex validasyon: `^(\+90|0)?\s*([3579][0-9]{2})[-\s]?([0-9]{3})[-\s]?([0-9]{2})[-\s]?([0-9]{2})$`

**Puanlama:**
| Durum | Puan |
|-------|------|
| Geçersiz format | 0 |
| Eski format (03XX XXX XXXX) | 1 |
| Yeni format (0XXX XXX XX XX) | 2 |

**Güncelleme Sıklığı:** Her normalize işleminde

---

### 2.6 Veri Güncelliği (0-8 puan)

**Amaç:** Firma verisinin ne kadar güncel olduğunu ölçmek.

**Veri Kaynağı:**
- `companies.last_verified_at`
- `source_records.collected_at`
- Scrape zaman damgası

**Puanlama:**
| Son Güncelleme | Puan |
|----------------|------|
| > 1 yıl | 0 |
| 6-12 ay | 2 |
| 3-6 ay | 4 |
| 1-3 ay | 6 |
| < 1 ay | 8 |

**Güncelleme Sıklığı:** Otomatik (her scrape sonrası)

---

### 2.7 Kaynak Çeşitliliği (0-5 puan)

**Amaç:** Firmanın birden fazla bağımsız kaynaktan doğrulanıp doğrulanmadığını ölçmek.

**Veri Kaynağı:**
- `companies` → `source_records` → `sources` JOIN

**Puanlama:**
| Benzersiz Kaynak Sayısı | Puan |
|-------------------------|------|
| 1 | 0 |
| 2 | 2 |
| 3-4 | 4 |
| 5+ | 5 |

**Güncelleme Sıklığı:** Her normalize işleminde

---

## 3. Toplam Potansiyel Puan Dağılımı

| Kategori | Mevcut | Önerilen |
|----------|--------|----------|
| Temel alanlar | 85 | 85 |
| Bonuslar | 10 | 40 |
| Ceza | -27 | -12 |
| **Max** | **100** | **113** |

> Not: Yeni max 113 puan olduğu için ölçekleme yapılabilir.
> Alternatif: Mevcut alan ağırlıklarını %80 oranında düşürerek yer açmak.

---

## 4. Geliştirme Önceliği

| Öncelik | Metrik | Teknik Zorluk | Etki |
|---------|--------|---------------|------|
| P0 | Veri güncelliği | Düşük | Orta |
| P1 | Sosyal medya | Düşük | Düşük |
| P1 | Telefon formatı | Düşük | Düşük |
| P2 | İş ilanı sayısı | Orta | Yüksek |
| P2 | Çalışan sayısı | Orta | Yüksek |
| P3 | E-posta domain | Yüksek | Düşük |
| P3 | Kaynak çeşitliliği | Düşük | Düşük |

---

## 5. Uygulama Planı

### Faz 1: Hazırlık
- [ ] Şema değişiklikleri: `companies` tablosuna yeni alanlar ekle
  - `job_postings_count INTEGER`
  - `employee_count_estimate INTEGER`
  - `social_media_count INTEGER`
  - `email_valid BOOLEAN`
  - `phone_valid BOOLEAN`
  - `source_diversity_score INTEGER`
- [ ] Yeni migration dosyası oluştur
- [ ] Test verisiyle simülasyon yap

### Faz 2: Veri Toplama
- [ ] İş ilanı scraper'ı geliştir
- [ ] LinkedIn API entegrasyonu
- [ ] Sosyal medya linki extractor
- [ ] DNS lookup servisi
- [ ] Telefon format normalizer

### Faz 3: Kalite Skoru Entegrasyonu
- [ ] `recalc_quality_scores.py`'yi güncelle
- [ ] A/B test: eski vs yeni formül
- [ ] Dashboard'da yeni metriklere yer aç

### Faz 4: Gözleme ve İyileştirme
- [ ] Ajanların görüşlerini topla
- [ ] Puanlama ayarlamaları yap
- [ ] CHANGELOG ve belgeleri güncelle

---

## 6. Ajan Görüşleri

> Bu bölümü dolduracak ajanlar:
> - [ ] Koordinatör
> - [ ] Geliştirici
> - [ ] Mimar
> - [ ] Kalite
> - [ ] Araştırmacı
> - [ ] Web Kazıma
> - [ ] Backend
> - [ ] Frontend

---

*Son güncelleme: 2026-09-08*
