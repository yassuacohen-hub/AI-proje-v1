# ANKARA COMPANY MASTER
## Nihai Veri Şeması ve MVP Teknik Tasarım V1.0

Bağlantılar: [[README]] · [[01_v9_ile_karsilastirma]] · [[01_versiyon_6_baglam_dokumani]] · [[01_versiyon_7_baglam_dokumani]] · [[01_versiyon_8_baglam_dokumani]] · [[01_versiyon_9_baglam_dokumani]]

**Proje:** Ankara B2B Intelligence  
**Katman:** Company Universe / Company Master  
**Amaç:** Ankara'daki B2B şirket evrenini kapsamlı, tekilleştirilmiş, doğrulanabilir, güncellenebilir ve Market Brain + Customer Brain tarafından kullanılabilir hale getirmek.

## 1. Tasarım Felsefesi

Company Master yalnızca bir firma rehberi değildir. İlk MVP'de Ankara'daki şirketleri arama, filtreleme ve inceleme imkânı verir; altyapı ise ileride ticari istihbarat katmanlarını besleyecek şekilde tasarlanır.

Temel zincir:

```text
Company → Location → Industry/NACE → Product/Capability
        → Source → Evidence → Commercial Event
        → Commercial State → Need → Opportunity
```

## 2. Ana Kimlik Kararı

VKN Primary Key yapılmayacaktır.

```text
company_id = UUID (Primary Key)
VKN = benzersiz kimlik/doğrulama alanı
MERSİS = yardımcı kimlik alanı
```

Böylece VKN'si bulunmayan kaynaklar, farklı yazımlar ve gelecekte uluslararası şirketler desteklenebilir.

## 3. Ana Tablolar

### 3.1 `companies`

| Alan | Tip | Açıklama |
|---|---|---|
| company_id | UUID PK | Sistem içi benzersiz kimlik |
| legal_name | TEXT | Resmi unvan |
| trade_name | TEXT | Ticari unvan |
| company_type | ENUM | AŞ, Ltd vb. |
| tax_number | TEXT UNIQUE NULL | VKN |
| mersis_number | TEXT UNIQUE NULL | MERSİS |
| establishment_date | DATE NULL | Kuruluş tarihi |
| status | ENUM | active / inactive / unknown |
| status_confidence | NUMERIC(5,2) | Durum güveni |
| employee_count | INTEGER NULL | Doğrulanabiliyorsa |
| website_domain | TEXT NULL | Resmi domain |
| primary_phone | TEXT NULL | Ana telefon |
| primary_email | TEXT NULL | Kurumsal e-posta |
| description | TEXT NULL | Açıklama |
| data_quality_score | NUMERIC(5,2) | Veri kalitesi |
| entity_confidence | NUMERIC(5,2) | Eşleştirme güveni |
| first_seen_at | TIMESTAMP | İlk görülme |
| last_verified_at | TIMESTAMP | Son doğrulama |
| created_at | TIMESTAMP | Oluşturma |
| updated_at | TIMESTAMP | Güncelleme |

Eksik alanlar tahmin edilmez.

### 3.2 `company_names`

Aynı şirketin farklı kaynaklardaki adlarını tutar.

- `company_name_id` UUID PK
- `company_id` UUID FK
- `name` TEXT
- `name_type` ENUM
- `source_id` UUID FK
- `normalized_name` TEXT
- `valid_from` DATE
- `valid_to` DATE NULL
- `confidence` NUMERIC(5,2)

`name_type`: legal, trade, brand, source_variant, historical

### 3.3 `company_identifiers`

VKN, MERSİS ve diğer kimlikler.

- `identifier_id`
- `company_id`
- `identifier_type`
- `identifier_value`
- `source_id`
- `confidence`
- `verified_at`

### 3.4 `company_locations`

Bir şirketin birden fazla fiziksel lokasyonunu destekler.

- `location_id`
- `company_id`
- `location_type`
- `address_line`
- `district`
- `neighborhood`
- `city`
- `postal_code`
- `latitude`
- `longitude`
- `geocode_confidence`
- `osb_id`
- `is_primary`
- `source_id`
- `verified_at`

`location_type`: headquarters, factory, branch, warehouse, office, workshop, unknown

### 3.5 `osbs`

Ankara OSB / sanayi bölgesi master tablosu.

- `osb_id`
- `name`
- `city`
- `district`
- `website`
- `osb_type`
- `status`
- `source_id`
- `verified_at`

Örnekler: OSTİM OSB, İvedik OSB, ASO 1. OSB, ASO 2-3 OSB, Başkent OSB, HAB OSB, Dökümcüler OSB, Anadolu OSB vb.

Liste sabit kabul edilmez; kaynaklarla doğrulanır.

### 3.6 `company_industries`

- `company_industry_id`
- `company_id`
- `nace_code`
- `nace_version`
- `nace_level`
- `is_primary`
- `source_id`
- `confidence`
- `verified_at`

NACE çoklu faaliyet destekleyecek şekilde modellenir.

### 3.7 `nace_codes`

- `nace_code` PK
- `version`
- `level`
- `parent_code`
- `title`
- `sector_group`
- `is_manufacturing`

MVP'de NACE C (İmalat) önceliklidir; model yalnızca C ile sınırlı değildir.

### 3.8 `company_products`

Şirketin ürettiği/sattığı/sunduğu ürün ve kabiliyetleri bağlar.

- `company_product_id`
- `company_id`
- `product_id`
- `relation_type`
- `evidence_id`
- `confidence`
- `first_seen_at`
- `last_seen_at`

`relation_type`: manufacturer, supplier, distributor, reseller, service_provider, integrator, unknown

### 3.9 `products`

- `product_id`
- `canonical_name`
- `category_id`
- `description`
- `product_status`

### 3.10 `product_categories`

Hiyerarşik ürün ağacı.

- `category_id`
- `parent_id`
- `name`
- `level`

Örnek:

```text
Makine
 ├─ CNC
 ├─ Pres
 ├─ Kompresör
 └─ Otomasyon
```

### 3.11 `company_contacts`

Öncelik kurumsal iletişim bilgileridir.

- `contact_id`
- `company_id`
- `contact_type`
- `value`
- `is_public`
- `source_id`
- `confidence`
- `verified_at`

`contact_type`: main_phone, sales_phone, general_email, sales_email, info_email, website, social_profile

### 3.12 `sources`

Verinin nereden geldiğini merkezi olarak takip eder.

- `source_id`
- `source_name`
- `source_type`
- `url`
- `authority_score`
- `collection_method`
- `legal_basis`
- `active`
- `created_at`

`source_type`: government, osb, chamber, company_website, public_registry, search_engine, manual, other

### 3.13 `source_records`

Ham kaynak kaydı korunur.

- `source_record_id`
- `source_id`
- `external_id`
- `raw_name`
- `raw_address`
- `raw_phone`
- `raw_email`
- `raw_website`
- `raw_tax_number`
- `raw_nace`
- `raw_payload` JSONB
- `collected_at`
- `content_hash`

Ham veri silinmez; yeniden işleme ve denetim için saklanır.

### 3.14 `entity_resolution`

- `resolution_id`
- `source_record_id`
- `company_id`
- `match_score`
- `match_method`
- `decision`
- `reviewed`
- `created_at`

`decision`: matched, possible_match, new_company, rejected

### 3.15 `evidence`

İleride Intelligence Engine'in temel kanıt katmanıdır.

- `evidence_id`
- `company_id`
- `source_id`
- `evidence_type`
- `title`
- `content_reference`
- `observed_at`
- `published_at`
- `freshness_score`
- `source_reliability`
- `independence_score`
- `evidence_strength`
- `raw_reference`

### 3.16 `company_events`

Company Master'dan Intelligence katmanına geçiş kapısıdır.

- `event_id`
- `company_id`
- `event_type`
- `event_date`
- `detection_date`
- `direction`
- `magnitude`
- `evidence_id`
- `confidence`
- `common_cause_id`

`direction`: positive, negative, mixed, stable, unknown

Negatif olay otomatik olarak kötü fırsat anlamına gelmez.

### 3.17 `company_state`

Algoritmik olarak türetilen güncel ticari durum.

- `company_id`
- `growth_state`
- `investment_state`
- `hiring_state`
- `capacity_state`
- `export_state`
- `financial_pressure_state`
- `overall_commercial_state`
- `state_confidence`
- `calculated_at`

### 3.18 `commercial_signals`

- `signal_id`
- `company_id`
- `signal_type`
- `signal_value`
- `direction`
- `strength`
- `recency`
- `independence`
- `causal_relevance`
- `evidence_strength`
- `baseline_delta`
- `detected_at`

### 3.19 `momentum_snapshot`

- `company_id`
- `momentum_score`
- `velocity`
- `acceleration`
- `signal_independence`
- `contradiction_penalty`
- `baseline_change`
- `calculated_at`

Momentum yalnızca sinyal sayısı değildir.

## 4. Veri Kalitesi

Temel boyutlar:

```text
Accuracy
Completeness
Freshness
Consistency
Uniqueness
Source Reliability
Entity Confidence
```

Genel skor bu boyutların fonksiyonudur. Başlangıç ağırlıkları benchmark ile daha sonra kalibre edilir.

Her kritik alan için:

```text
first_seen_at
last_seen_at
verified_at
```

tutulur.

## 5. Çelişki Yönetimi

Kaynaklar farklı bilgi verirse çelişki silinmez.

```text
Kaynaklar
 ↓
Güvenilirlik
 ↓
Güncellik
 ↓
Kanıt gücü
 ↓
Güncel durum
```

Gerekirse kullanıcıya:

> Aktif — Orta güven

gibi gösterilir.

## 6. UNKNOWN Prensibi

Sistem aşağıdakileri kanıt yoksa uydurmaz:

- bütçe
- satın alma kararı
- karar verici
- karar bölgesi
- satın alma tarihi
- rakip
- mevcut tedarikçi
- satın alma gerçekleşti mi

`Unknown`, veri kalitesi hatası olarak otomatik cezalandırılmaz.

## 7. Entity Resolution

Örnek:

```text
ABC MAKİNA SAN. VE TİC. LTD. ŞTİ.
ABC Makina
ABC MAKINA SAN TIC LTD
ABC Makina Ltd.
```

tek `company_id` altında birleştirilebilir.

Önerilen başlangıç eşikleri:

```text
95–100 → otomatik eşleştir
85–94  → güçlü aday
70–84  → ikinci kontrol
<70    → eşleştirme yapma
```

Eşikler gerçek veri benchmark'ı ile yeniden ayarlanır.

## 8. ETL Mimarisi

```text
SOURCE
  ↓
RAW INGESTION
  ↓
NORMALIZATION
  ↓
VALIDATION
  ↓
ENTITY RESOLUTION
  ↓
COMPANY MASTER
  ↓
ENRICHMENT
  ↓
DATA QUALITY
  ↓
SEARCH INDEX
  ↓
INTELLIGENCE LAYER
```

Ham veri ile temizlenmiş veri ayrıdır.

## 9. Veri Toplama Önceliği

Ankara için:

1. OSB'ler
2. OSTİM
3. İvedik
4. ASO OSB'leri
5. diğer sanayi bölgeleri
6. oda/kuruluş kaynakları
7. kamuya açık şirket kayıtları
8. şirketlerin resmi web siteleri

Amaç önceden belirlenmiş sayıya ulaşmak değil, **mümkün olan en kapsamlı ve doğrulanabilir Ankara B2B Company Universe** oluşturmaktır.

## 10. MVP Öncelikleri

### P0 — Zorunlu

- company_id
- unvan
- VKN varsa
- il / ilçe
- adres
- web sitesi
- telefon
- sektör
- NACE varsa
- kaynak
- son doğrulama
- entity confidence
- data quality

### P1 — Çok Değerli

- OSB
- ürünler
- üretici/satıcı ilişkisi
- lokasyon türü
- alternatif şirket isimleri

### P2 — Intelligence Hazırlığı

- evidence
- events
- commercial signals
- company state
- momentum

## 11. Arama

İlk MVP için:

**PostgreSQL + Full Text Search**

yeterlidir.

Gerekirse daha sonra:

**Meilisearch veya Elasticsearch**

eklenir.

İlk günden Elasticsearch zorunlu değildir.

## 12. API

Önerilen temel endpointler:

```text
GET /companies
GET /companies/{company_id}
GET /companies/{company_id}/locations
GET /companies/{company_id}/industries
GET /companies/{company_id}/products
GET /companies/{company_id}/sources
GET /companies/{company_id}/events
GET /companies/{company_id}/signals

GET /search/companies
GET /filters/sectors
GET /filters/osbs
GET /filters/nace
```

## 13. Current Value + Evidence History

Güncel değer ile tarihsel kanıt ayrılmalıdır.

Örneğin:

```text
companies.website_domain
```

güncel domaini tutar.

`source_records` ve `evidence` geçmişte ne görüldüğünü korur.

Böylece:

> Bu şirketin web sitesi ne zaman değişti?

gibi sorular cevaplanabilir.

## 14. Firma Profilinin MVP Görünümü

```text
ABC MAKİNA SAN. VE TİC. LTD. ŞTİ.

Sektör: Makine İmalatı
NACE: 28.xx
Lokasyon: OSTİM / Yenimahalle / Ankara

Web: ...
Telefon: ...

Ürünler:
• CNC
• Özel Makine
• Otomasyon

Durum: Aktif
Veri Güveni: Yüksek

Kaynaklar:
• OSB
• Şirket Web Sitesi
• diğer doğrulanmış kaynaklar
```

## 15. Sonraki Intelligence Profili

```text
TİCARİ DURUM

Büyüme      ↑
Yatırım     ↑
İşe Alım    ↑
Kapasite    ↑

Momentum: 78
Kanıt Gücü: 84

Son Değişimler:
• Yeni tesis sinyali
• Teknik personel işe alımı
• Yeni ürün duyurusu
```

## 16. Başarı KPI'ları

Firma sayısı tek KPI değildir.

- **Coverage:** Ankara B2B şirketlerinin ne kadarı yakalandı?
- **Entity Accuracy:** Yanlış bölme/birleştirme oranı
- **Duplicate Rate:** Mükerrer oranı
- **Field Completeness:** Alan doluluk oranı
- **Freshness:** Güncellik
- **Source Reliability:** Kaynak performansı
- **Search Quality:** Arama başarısı
- **Profile Accuracy:** Profil doğruluğu
- **Evidence Coverage:** Önemli alanların kanıtla desteklenme oranı

## 17. Mimari Sınır

Company Master tek başına şunları yapmaz:

- satın alma tahmini
- bütçe tahmini
- fırsat skoru
- müşteri ürün uyumu
- karar verici tahmini
- satış kazanma tahmini

Bunlar ileride ilgili Intelligence Engine'lerinin sorumluluğudur.

## 18. Nihai Büyük Resim

```text
                 ANKARA COMPANY UNIVERSE
                          │
                          ▼
                  ┌───────────────┐
                  │ Company Master│
                  └───────┬───────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   Locations          Industries        Products
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
                  Evidence & Sources
                          │
                          ▼
                   Data Quality
                          │
                          ▼
                 Commercial Events
                          │
                          ▼
                 Commercial Signals
                          │
                          ▼
                  Market Brain
                          │
                          ▼
                  Customer Brain
                          │
                          ▼
                 Opportunity Engine
                          │
                          ▼
                  Decision Engine
                          │
                          ▼
                  Portfolio Engine
                          │
                          ▼
                   Learning Engine
```

## ANA PRENSİP

> **Önce şirketi doğru tanı. Sonra şirketin değişimini anla. Sonra ihtiyacı çıkar. Sonra müşterinin ürünüyle eşleştir. Sonra aksiyon öner. Sonra gerçek sonucu öğren.**

**Bu belge Company Master V1.0 için temel teknik şartnamedir.**

---
**Sonraki teknik adım:** Ankara veri kaynaklarının kesin envanterini çıkarıp her kaynak için `source → alanlar → erişim yöntemi → güncelleme sıklığı → yasal durum → güven skoru` matrisi oluşturmak; ardından PostgreSQL şemasını gerçek SQL migration olarak üretmek.
