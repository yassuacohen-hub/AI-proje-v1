# Web Kazıma Kaynak Araştırması ve Scraping Stratejisi

Bağlantılar: [[00-Home]] · [[01_veri_kaynagi_envanteri]] · [[02_ankara_osb_ekosistemi_arastirma_notu]] · [[03_osb_masa_basi_analizi]] · [[10_ankara_osb_sentez]] · [[10_mvp_kapsam]] · [[project_state]] · [[CHANGELOG]]

Bu belge, Ankara B2B Company Master V1.0 projesi için web kazıma yapılabilecek TÜM kaynakları araştırır, önceliklendirir, scraping stratejisi sunar ve çapraz kaynak eşleştirme planını içerir.

**Tarih:** 2026-09-01
**Analist:** Araştırmacı Ajan (orquestratör desteğiyle)
**Karar referansı:** [[10_ankara_osb_sentez]] Karar 7 (yeni, 2026-09-01)

---

## 1. Kaynak Sınıflandırması (12 Kaynak)

### A. RESMİ / KAMU KAYNAKLARI (Yüksek güvenilirlik)

#### A1. MERSİS — Merkezi Sicil Kayıt Sistemi
- **URL:** https://mersis.gtb.gov.tr
- **Erişim:** Kamuya açık arama (Captcha olabilir)
- **Veri:** Şirket unvanı, MERSİS no, vergi no, adres, NACE, tescil tarihi, sermaye
- **KVKK riski:** Düşük (şirket bilgisi, kişi bilgisi yok)
- **Scraping yöntemi:** API varsa (https://mersisapi.gtb.gov.tr) tercih et; yoksa Selenium + manuel Captcha
- **Rate limit:** 1 istek / 5 saniye (resmi site, yavaş olabilir)
- **Öncelik:** ⭐⭐⭐⭐⭐ (her firma için MERSİS no zorunlu olmalı)
- **Beklenen eşleşme anahtarı:** vergi_no veya unvan

#### A2. GİB — Gelir İdaresi Başkanlığı (Vergi Levhası Sorgu)
- **URL:** https://www.gib.gov.tr
- **Erişim:** e-Vergi Levhası Sorgu (anonim)
- **Veri:** Vergi no, unvan, adres, VD müdürlüğü
- **KVKK riski:** Çok düşük (anonim sorgu)
- **Scraping yöntemi:** Form-based POST request
- **Öncelik:** ⭐⭐⭐⭐

#### A3. Ticaret Sicil Gazetesi
- **URL:** https://www.ticaretsicil.gov.tr
- **Erişim:** Gazete arşivi kamuya açık
- **Veri:** Şirket kuruluş, birleşme, tasfiye ilanları
- **Scraping yöntemi:** PDF parse
- **Öncelik:** ⭐⭐ (geçmişe dönük)

#### A4. TOBB — Türkiye Odalar ve Borsalar Birliği
- **URL:** https://www.tobb.org.tr
- **Alt:** https://sanayi.tobb.org.tr
- **Erişim:** Sorgulama formu kamuya açık
- **Veri:** Oda üyesi firma bilgileri, sicil no, NACE
- **Öncelik:** ⭐⭐⭐⭐

#### A5. Sanayi ve Teknoloji Bakanlığı — OSB Bilgi Sistemi
- **URL:** https://www.sanayi.gov.tr
- **Alt:** OSB İstatistik Modülü
- **Veri:** 304 OSB, parsel sayıları, istihdam, sektör
- **Öncelik:** ⭐⭐⭐⭐ (kendi OSB envanterimiz için)

#### A6. SGK — Sosyal Güvenlik Kurumu
- **URL:** https://www.sgk.gov.tr
- **Veri:** Çalışan sayısı (4a/4b/4c), sektör
- **Erişim:** Kısıtlı, anonim sorgu yok
- **Öncelik:** ⭐ (erişim zor, bireysel başvuru gerekir)

### B. MESLEK KURULUŞLARI / ODALAR (Yüksek güvenilirlik)

#### B1. ASO — Ankara Sanayi Odası Üye Rehberi
- **URL:** https://www.aso.org.tr/firmarehberi/
- **Erişim:** Kamuya açık (giriş gerektirmez)
- **Veri:** Üye firma, vergi no, adres, telefon, email, web sitesi, NACE, meslek grubu
- **KVKK riski:** Orta (yetkili kişi adı olabilir)
- **Scraping yöntemi:** AJAX API (muhtemelen GET /api/firmalar?page=N)
- **Sayfa başına:** ~20-50 firma
- **Rate limit:** 1 istek / 2 saniye
- **Öncelik:** ⭐⭐⭐⭐⭐ (MVP ana kaynak, ASO 1 OSB alternatifi)
- **Beklenen eşleşme:** vergi_no, unvan, telefon
- **Kod örneği:**

```python
import requests
import time

BASE = "https://www.aso.org.tr/firmarehberi/"
HEADERS = {"User-Agent": "AnkaraB2B-Bot/1.0 (research@example.com)"}

def aso_sorgula(q: str, sayfa: int = 1) -> list[dict]:
    """ASO firmarehberi sorgu (form veya API)."""
    resp = requests.get(
        f"{BASE}/arama",
        params={"q": q, "page": sayfa},
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    # JSON dönüyorsa doğrudan parse; HTML ise BS4 ile parse
    return resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text
```

#### B2. ATO — Ankara Ticaret Odası
- **URL:** https://www.atonet.org.tr
- **Veri:** Hizmet sektörü firmaları (ASO sanayi odaklı, ATO hizmet)
- **Öncelik:** ⭐⭐⭐ (Faz 2+)

#### B3. OSB Üst Kuruluşu (OSBÜK)
- **URL:** https://www.osbuk.org.tr
- **Veri:** Tüm OSB listesi, parsel/envanter
- **Öncelik:** ⭐⭐⭐

### C. TEKNOPARK / KULUÇKA MERKEZLERİ (Yüksek teknoloji sinyali)

#### C1. ODTÜ TEKNOKENT
- **URL:** https://www.odtuteknokent.com.tr
- **Veri:** 400+ firma, teknoloji alanı, kuruluş yılı
- **Erişim:** Kamuya açık şirket listesi
- **Öncelik:** ⭐⭐⭐⭐ (Ankara için kritik)

#### C2. Hacettepe TEKNOKENT
- **URL:** https://www.hacettepeteknokent.com.tr
- **Veri:** Sağlık/biyoteknoloji firmaları
- **Öncelik:** ⭐⭐⭐

#### C3. ASO TEKNOKENT
- **URL:** https://www.asoteknopark.com
- **Öncelik:** ⭐⭐⭐

#### C4. Bilkent CYBERPARK
- **URL:** https://www.cyberpark.com.tr
- **Veri:** Bilişim firmaları
- **Öncelik:** ⭐⭐⭐

### D. AÇIK TİCARİ REHBERLER (Orta güvenilirlik, hızlı kazanım)

#### D1. firmarehberim.com
- **Erişim:** Açık
- **Veri:** Kategori bazlı firma listesi, telefon, adres
- **Öncelik:** ⭐⭐ (güvenilirlik düşük, çapraz doğrulama için kullan)

#### D2. rehbersanayi.com
- **Erişim:** Açık
- **Veri:** Sanayi firmaları
- **Öncelik:** ⭐⭐

#### D3. sahibinden.com (Kurumsal Üye İlanları)
- **Erişim:** Kısmen açık
- **Veri:** Kurumsal üye bilgileri
- **Öncelik:** ⭐ (Kullanıcı sözleşmesi sıkı)

#### D4. LinkedIn (Üye arama / Şirket sayfaları)
- **Erişim:** API kısıtlı, scraping TOS'a aykırı
- **Veri:** Çalışan sayısı, sektör, lokasyon
- **Öncelik:** ⭐ (riskli)

#### D5. Facebook Business Pages
- **API:** Graph API ile sınırlı erişim
- **Veri:** Kategori, lokasyon, açıklama
- **Öncelik:** ⭐⭐ (API token gerekir)

### E. KAMU AÇIK VERİ PORTALLARI (En güvenilir)

#### E1. data.gov.tr
- **URL:** https://data.gov.tr
- **Veri:** KOSGEB, TÜİK, Bakanlık veri setleri
- **Öncelik:** ⭐⭐⭐⭐⭐ (toplu veri indirme)

#### E2. TÜİK — Sanayi ve Hizmet İstatistikleri
- **URL:** https://www.tuik.gov.tr
- **Veri:** Sektörel istatistik, bölgesel dağılım
- **Öncelik:** ⭐⭐⭐⭐ (istatistik çaprazlama)

#### E3. KOSGEB Veritabanı
- **Erişim:** Açık (e-devlet üzerinden)
- **Veri:** Kobİ destek alan firmalar
- **Öncelik:** ⭐⭐⭐

#### E4. e-Devlet Kapısı
- **URL:** https://www.turkiye.gov.tr
- **Veri:** Resmi belge sorgulama
- **Erişim:** Bireysel (otomasyon zor)
- **Öncelik:** ⭐ (erişim kısıtlı)

---

## 2. Öncelik Matrisi

| Öncelik | Kaynak | Erişim | Veri Hacmi | KVKK Risk | Zorluk |
|---|---|---|---|---|---|
| 1 (MVP) | OSTİM | Açık | 6.500+ | Düşük | Kolay |
| 2 (MVP) | ASO firmarehberi | Açık | 5.000+ | Orta | Orta |
| 3 | ODTÜ TEKNOKENT | Açık | 400+ | Düşük | Kolay |
| 4 | MERSİS | Captcha | 100K+ | Çok düşük | Zor |
| 5 | TOBB | Açık | 50K+ | Düşük | Orta |
| 6 | data.gov.tr | Açık | Değişken | Çok düşük | Kolay (CSV indirme) |
| 7 | GİB | Açık | 100K+ | Düşük | Orta |
| 8 | OSBÜK | Açık | 304 OSB | Düşük | Kolay |
| 9 | TÜİK | Açık | İstatistik | Çok düşük | Orta |
| 10 | Sanayi Bakanlığı | Açık | OSB envanteri | Düşük | Kolay |
| 11 | firmarehberim.com | Açık | 50K+ | Orta | Kolay |
| 12 | LinkedIn/Facebook | API/Token | Değişken | Yüksek | Zor |

---

## 3. Cross-Source Eşleştirme (Entity Resolution) Planı

### 3.1 Birincil Anahtarlar
- `vergi_no` (MERSİS, GİB, ASO, OSTİM) — en güvenilir
- `mersis_no` (MERSİS'den)
- `unvan_normalized` (tüm kaynaklar) — fuzzy match gerekli

### 3.2 Eşleştirme Stratejisi
- **Aşama 1:** vergi_no üzerinden deterministik eşleştirme
- **Aşama 2:** unvan + ilçe üzerinden fuzzy eşleştirme (Levenshtein, Jaro-Winkler)
- **Aşama 3:** telefon + adres üzerinden doğrulama

### 3.3 Veri Birleştirme Politikası
- Aynı firma birden fazla kaynakta varsa:
  - MERSİS = kaynak (yetki no, tescil)
  - ASO = meslek grubu, NACE
  - OSTİM = sektör detayı
  - OSB websitesi = telefon, email, web_sitesi, sosyal_medya
  - ODTÜ TEKNOKENT = teknoloji alanı, patent
- Conflict varsa: kaynak güvenilirliği sırasına göre seç (MERSİS > ASO > OSB > diğer)

---

## 4. KVKK Ayrıcalık Politikası (Yeni — 2026-09-01)

### 4.1 Hassasiyet Seviyeleri

| Seviye | Tanım | Erişim | Örnek |
|---|---|---|---|
| **PUBLIC** | Herkes görebilir, anonim | API açık | Vergi no, adres, telefon, web sitesi, NACE |
| **SEMI_PUBLIC** | Kurumsal iletişim | API açık + log | info@, sabit telefon, meslek grubu |
| **RESTRICTED** | KVKK kapsamında | Yetkili kullanıcı + log | Şahıs adı, özel GSM, kişisel email |
| **PROHIBITED** | Yasak | Hiçbir koşulda | TC kimlik, sağlık verisi, özel nitelikli |

### 4.2 Yeni Şema Alanları (Öneri)

```sql
-- Her iletişim alanı için hassasiyet
ALTER TABLE companies ADD COLUMN telefon_hassasiyet TEXT DEFAULT 'PUBLIC' 
    CHECK(telefon_hassasiyet IN ('PUBLIC', 'SEMI_PUBLIC', 'RESTRICTED', 'PROHIBITED'));
ALTER TABLE companies ADD COLUMN email_hassasiyet TEXT DEFAULT 'SEMI_PUBLIC';
ALTER TABLE companies ADD COLUMN yetkili_hassasiyet TEXT DEFAULT 'RESTRICTED';

-- Erişim log tablosu
CREATE TABLE access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    company_id INTEGER,
    field_accessed TEXT,
    sensitivity_level TEXT,
    access_timestamp TEXT DEFAULT (datetime('now')),
    purpose TEXT
);
```

### 4.3 Erişim Kontrol Mantığı
- PUBLIC: API'den direkt döner
- SEMI_PUBLIC: API'den döner, access_log'a yazılır
- RESTRICTED: Yetki kontrolü + access_log + purpose zorunlu
- PROHIBITED: Asla döndürülmez

### 4.4 "Ayrıcalık Tanınsın" Yorumu (Product Owner)
- "KVKK içeren veriler olursa ayrıcalık tanınsın" = RESTRICTED seviyedeki alanlar:
  - Default olarak maskelenir (Ahmet B****, 0532***1234)
  - Yetkili kullanıcı + açıklama ile erişilebilir
  - Tüm erişim loglanır
- "Ne kadar çok bilgi o kadar iyi" = PUBLIC + SEMI_PUBLIC toplanır
- "Halka açık paylaşımlar olabilir" = e-Devlet, OSB websitesi, sosyal medya

---

## 5. Scraping Pipeline Genel Akış

```
Kaynak (OSB/ASO/MERSİS)
    ↓ requests/Selenium
HTML/JSON
    ↓ BeautifulSoup/lxml
Ham kayıt dict
    ↓ Normalizer (Türkçe karakter, telefon formatı, unvan std)
Normalized dict
    ↓ KVKK Filter (hassasiyet etiketi)
Etiketli kayıt
    ↓ Entity Resolver (vergi_no birincil, unvan fuzzy)
Eşleşen firma güncelleme veya yeni kayıt
    ↓ SQLite/PostgreSQL
companies tablosu
```

---

## 6. Faz Planı (Web Kazıma)

### Faz 1A — MVP (Hafta 1-2)
- ✅ OSTİM scraping (zaten scraper hazır)
- 🔄 ASO firmarehberi scraper
- 🔄 ODTÜ TEKNOKENT scraper
- 🔄 Cross-source eşleştirme (vergi_no anahtar)

### Faz 1B — Genişletme (Hafta 3-4)
- 🔄 GİB vergi levhası sorgu
- 🔄 TOBB üye sorgulama
- 🔄 data.gov.tr toplu veri indirme
- 🔄 ASO 1 OSB / İvedik OSB (talep sonrası)

### Faz 2 — Kalite (Hafta 5+)
- 🔄 MERSİS API (Captcha çözümü)
- 🔄 Sanayi Bakanlığı OSB envanteri
- 🔄 KOSGEB veritabanı
- 🔄 LinkedIn/Facebook (API token)

---

## 7. Yasal/Etik Notlar

- **Robots.txt:** Her kaynak için scraping öncesi kontrol
- **Rate limit:** 1-3 saniye arası (kaynağa göre)
- **User-Agent:** `AnkaraB2B-Bot/1.0 (research@example.com)`
- **Veri paylaşımı:** Üçüncü partiye satış YOK; sadece analiz/ürün geliştirme
- **KVKK:** RESTRICTED alanlar loglanır, amacı belirtilir
- **Opt-out:** Firmalar talep ederse verileri silinir veya maskelenir

---

## 8. Önerilen Hemen Sonraki Adımlar

| # | Adım | Sorumlu | Süre |
|---|---|---|---|
| 1 | ASO firmarehberi scraper oluştur | Geliştirici Ajan | 1-2 saat |
| 2 | ODTÜ TEKNOKENT scraper oluştur | Geliştirici Ajan | 1 saat |
| 3 | KVKK hassasiyet şemasını companies.sql'e ekle | Mimar Ajan | 30 dk |
| 4 | Entity resolution modülü (fuzzy match) | Geliştirici Ajan | 2 saat |
| 5 | data.gov.tr toplu veri taraması | Araştırmacı Ajan | 1 saat |
| 6 | Pilot: 50 firma için cross-source merge | Kalite Ajan | 1 saat |

---

## İlgili Wiki Sayfaları

- [[01_veri_kaynagi_envanteri]] — Mevcut kaynak envanteri
- [[02_ankara_osb_ekosistemi_arastirma_notu]] — OSB araştırma
- [[03_osb_masa_basi_analizi]] — 3 OSB masa başı
- [[05_acik_veri_ve_kazina_politikasi]] — Açık veri politikası (yeni)
- [[10_ankara_osb_sentez]] — Sentez kararları
- [[10_mvp_kapsam]] — MVP kapsam
- [[01_sirket_master_ana_belgesi]] — Ana şema