# ANKARA B2B INTELLIGENCE — MASTER CONTEXT V8 FINAL

Bağlantılar: [[README]] · [[01_sirket_master_ana_belgesi]] · [[01_v9_ile_karsilastirma]] · [[01_versiyon_6_baglam_dokumani]] · [[01_versiyon_7_baglam_dokumani]] · [[01_versiyon_9_baglam_dokumani]]

---

## V8 FÜZYON: V6 Test Edilmiş Prensipler + V7 Somut Altyapı + Simülasyon Düzeltmeleri + 8 Doküman Tutarlılık Düzeltmesi


---

## 0. FÜZYON MANIFESTOSU: Neden V8 Final?

Date:**

**Status:** Birleşik Tasarım — 100×100×100 Simülasyon Testinden Geçmiş + 8 Doküman Tutarlılık Düzeltmesi Uygulanmış

**Core Principle:**

> Do not pretend to know what the data cannot prove. Preserve uncertainty and make the strongest evidence-backed commercial inference possible.

**V6** = Beyin. Pek çok adversarial testten geçmiş, belirsizliği koruyan, kanıt-odaklı, öğrenen bir zeka mimarisi. Ama soyut; somut veri pipeline'ı, monetizasyon ve saha operasyonu eksik.

**V7** = Gövde. PostgreSQL + ChromaDB + Neo4j + Redis altyapısı, TOPSIS matematiği, monetizasyon, WhatsApp/OCR saha köprüleri, Türkiye özgü entegrasyonlar. Ama öğrenme, portföy optimizasyonu, karar motoru ve test çerçevesi eksik.

**V8** = Beyin + Gövde + Sinir Sistemi + Hata Düzeltmeleri. V6'nın test edilmiş prensipleri korunur; V7'nin somut teknolojileri bu prensiplere hizmet edecek şekilde konumlandırılır. **100×100×100 simülasyonu sonrası 5 kritik bulgu tespit edilmiş ve düzeltilmiştir.**

**V8 Final** = V8 + 8 Doküman Tutarlılık Düzeltmesi (Shadow Model detaylandırma, Anonim Profil akışı, DEPRIORITIZE seviyelendirme, Safety Net clamp/normalize, Kalibrasyon cold-start stratejisi, Portfolio Score fit tekrarı giderme, Global Deduplication SQL default, Decision Matrix need aralığı standartizasyonu).

---

## 0.1. 100×100×100 SİMÜLASYON SONUÇLARI

**Senaryo:** 100 Firma × 100 Ürün × 100 Kullanıcı, 646 sinyal, 10,000 potansiyel eşleşme.

---

### Tespit Edilen 5 Kritik Bulgu

|

---

# | Bulgu

Risk
| Düzeltme  |   | --- | ------- |------
| ---------- |   | **1**  | **Yüksek skorlu fırsatlar daha başarılı değil** (WON ort: 0.598 vs Hatalı ort: 0.610)  | TOPSIS skorları satış başarısını öngörmüyor
| Learning Engine kalibrasyonu + Ensemble skorlama  |   | **2**  | **Hata oranı %48.2** (NO_RESPONSE 22%, LOST 22%, WRONG_TIMING 15%)  | Sistem kendini kalibre etmiyor
| Outcome Ledger + Feedback Engine + Shadow Model  |   | **3**  | **Fit skoru yanıltıcı** (Başkent Egzoz Helikopter Parçası fit: 0.319, skor: 0.793)  | Fit ağırlığı düşük, bonuslar baskın
| Fit ağırlığı %20→%35, bonuslar sınırlı  |   | **4**  | **Aynı firma-ürün tekrarı** (Global deduplication yok)  | Birden fazla kullanıcı aynı fırsatı görüyor
| Global deduplication + rezervasyon sistemi  |   | **5**  | **Düşük need ile CONTACT_NOW** (need_prob 0.15 olanlar şimdi ara)  | Gate'ler gevşek | Need < 0.25 → max INVESTIGATE |

---

### Simülasyon Metrikleri (Düzeltme Öncesi vs Sonrası)


| Metrik  | Önceki (A Seçenekleri)  | Sonra (B Seçenekleri + Düzeltmeler)  |  |--------
| ---------------------- | ----------------------------------- |   | CONTACT_NOW  | 0
| **92**  |   | INVESTIGATE  | 911  | **118**
|   | MONITOR  | 0  | **42**  |
| Kullanıcı başına ort.  | 9.1  | **3.0**  |  | Portfolio skor çeşitliliği
| Hepsi 0.852  | **0.76 - 0.83**  |   | Firma başına max contact  | 15 | **3** (limitli) |

---

## 0.2. DOKÜMAN TUTARLILIK DÜZELTMELERİ (V8 Final'e Özel)

|

---

# | Bulgu

Konum
| Düzeltme  |   | --- | ------- |-------
| ---------- |   | **D1**  | Shadow Model detayı eksik  | Bölüm 7.2, 7.3
| Güvenlik Valfi + A/B Test Motoru olarak detaylandırıldı (Bölüm 7.2.1, 7.3.1)  |   | **D2**  | Anonim Profil / CONTACT_NOW çelişkisi  | Bölüm 10.1 vs 10.4
| 2 Aşamalı Akış: Keşfet (Anonim) → Kimliği Aç (Açık) (Bölüm 10.4)  |   | **D3**  | DEPRIORITIZE tetikleyicisi net değil  | Bölüm 5.1 vs 10.2
| 2 Seviyeli DEPRIORITIZE + eşik standartizasyonu (Bölüm 5.1.1)  |   | **D4**  | Safety Net negatif skor  | Bölüm 4.2
| Clamp + normalize: Safety skoru 0-1 aralığında (Bölüm 4.2.1)  |   | **D5**  | Kalibrasyon cold-start  | Bölüm 7.3 vs 16
| Faz 1'de statik ağırlıklar, Faz 2'de Shadow Model, Faz 3'de otomatik kalibrasyon (Bölüm 7.3.1)  |   | **D6**  | Portfolio Score fit tekrarı  | Bölüm 6.1
| Portfolio'daki FIT_SCORE kaldırıldı, Ensemble skoru yeterli (Bölüm 6.1)  |   | **D7**  | Global Deduplication SQL eksik  | Bölüm 9.2
| expires_at default değeri eklendi (Bölüm 9.2)  |   | **D8**  | Decision Matrix need aralığı boş  | Bölüm 4.1 vs 5.1 | 0.25-0.40 aralığı INVESTIGATE olarak tanımlandı (Bölüm 5.1) |

---

## 1. BİRLEŞİK MİMARİ: 6+1 KATMAN

V6'nın orijinal 6 katmanı korunur. V7 teknolojileri her katmana entegre edilir. **Simülasyon bulguları ve tutarlılık düzeltmeleri katmanlara yansıtılır.**
```
┌─────────────────────────────────────────────────────────────┐ │

KATMAN 6: LEARNING ENGINE (Kalibre Edilmiş + Shadow Model)

│ │

(Prediction Ledger → Outcome Ledger → Shadow Model)

│ │

V8 Final: Güvenlik Valfi + A/B Test + Cold-Start Stratejisi│ ├─────────────────────────────────────────────────────────────┤ │

KATMAN 5: PORTFOLIO ENGINE (Deduplicated)

│ │

(10,000 match → 20 priority + kıt kaynak)

│ │

V8 Final: Global deduplication, rezervasyon, Ensemble skoru │ ├─────────────────────────────────────────────────────────────┤ │

KATMAN 4: DECISION ENGINE (Need Kısıtlı + 2 Seviyeli DEP)

│ │

(contact / monitor / investigate / wait / deprioritize)

│ │

V8 Final: Need < 0.25 → CONTACT_NOW yasak, saatlik limit

│ ├─────────────────────────────────────────────────────────────┤ │

KATMAN 3: OPPORTUNITY ENGINE (Ensemble + Safety Clamp)

│ │

(Need → Fit → Evidence → Timing gates)

│ │

V8 Final: 3 Model Ensemble (TOPSIS + Learning + Safety Net) │ ├─────────────────────────────────────────────────────────────┤ │

KATMAN 2: CUSTOMER BRAIN (Kategori-spesifik)

│ │

(Bu müşteri için hangileri gerçekten satılabilir?)

│ │

V8 Final: NACE kuralı + ChromaDB + insan onayı (hibrit fit)│ ├─────────────────────────────────────────────────────────────┤ │

KATMAN 1: MARKET BRAIN

│ │

(Piyasada ne oluyor?)

│ │

V7: GİB e-fatura, OSB dizin, EKAP, LinkedIn, ERP telemetry│ ├─────────────────────────────────────────────────────────────┤ │

KATMAN 0: EVIDENCE & DATA QUALITY LAYER

│ │

(9 boyutlu kanıt katmanı + Pydantic + Quarantine)

│ │

V7: Validation Gate, quarantine_firms, source reliability

│ └─────────────────────────────────────────────────────────────┘
```
---

## 2. KATMAN 1: MARKET BRAIN — Piyasada Ne Oluyor?

**V6 Prensibi:** Observes investments, hiring, expansion, contraction, exports, projects, procurement signals, financing, restructuring, contracts, public announcements.

**V7 Somutlaştırması:**

---

### 2.1 Veri Kaynakları (MVP → Scale)


| Öncelik  | Kaynak  | VKN/Domain Köprüsü  | V6 Signal Tipi  | V7 Teknoloji
|   | --------- | -------- | ------------------- |----------------
| -------------- |   | **MVP-1**  | GİB E-Fatura Açık Liste  | VKN
| Ticari varlık sinyali  | PostgreSQL master anchor  |   | **MVP-1**  | OSTİM / İvedik / ASO Web Dizin
| Domain/Telefon  | Fiziki operasyon sinyali  | Web scraper + Pydantic gate  |  | **MVP-1**
| ASO / ATO Üye Listeleri  | VKN  | İkincil doğrulama  | Fallback bridge  |
| **MVP-2**  | EKAP Kamu İhaleleri  | VKN  | Procurement signal  | tenders_history uydu tablosu
|   | **MVP-2**  | LinkedIn (açık veri)  | Domain + Şehir fuzzy  | Hiring / tech intent
| company_social_metrics uydu tablosu  |   | **MVP-3**  | Dış Ticaret / GTİP  | GTİP + NACE
| Import substitution  | ChromaDB capability matching  |   | **Scale**  | ERP/MES Telemetry (opsiyonel)
| VKN + API key  | Real-time idle capacity  | mTLS/OAuth2 gateway  |  | **Scale**
| TOBB Kapasite Raporu OCR  | VKN  | Makine envanteri  | OCR parser + Pydantic gate  |
| **Scale**  | WhatsApp Voice-to-Intent  | Domain/Telefon  | Acil ihtiyaç sinyali  | Speech-to-Text → ChromaDB query |

**V6 ↔ V8 Final Kuralı:** V6'nın Do not make the product dependent on private CRM/ERP data prensibi korunur. ERP/MES entegrasyonu **Scale aşamasında opsiyoneldir**. MVP'de ürün, yasal olarak erişilebilen kamu/OSB verileriyle çalışır.

---

### 2.2 Signal & Momentum System (V6 Konsept + V7 Vektörleştirme)

V6'nın 9 sinyal kavramı V7 teknolojileriyle desteklenir:
| V6 Kavramı  | V8 Final Implementasyonu  |   | ------------ |-------------------
|   | Signal Cluster  | ChromaDB'de benzer sinyallerin vektör kümesi  |  | Signal Velocity
| Redis time-series: son 30 gündeki sinyal değişimi  |   | Signal Acceleration  | PostgreSQL window function: velocity'nin velocity'si  |
| Signal Independence  | Neo4j graph: aynı kaynaktan mı geliyor? (common cause detection)  |   | Common Cause Detection  | Neo4j relationship type: CAUSED_BY_SAME_INCENTIVE
|   | Signal Contradiction  | ChromaDB contradiction vector: pozitif + negatif sinyal aynı firmada  |  | Missing Signal
| Prediction Ledger'da Expected Signal Not Observed kaydı  |   | Company Baseline  | PostgreSQL: firmanın kendi geçmişiyle karşılaştırma  | | Sector Baseline | PostgreSQL: sektör ortalaması window function |

**Kural:** Copied articles do not count as independent evidence. ChromaDB'de aynı source_domain'e sahip vektörler independence=0.5 olarak işaretlenir.

---

## 3. KATMAN 2: CUSTOMER BRAIN — Bu Müşteri İçin Hangileri Gerçekten Satılabilir?

**V6 Prensibi:** Evaluates product fit, addressable need, timing, evidence, commercial compatibility and sales context.

**V7 Somutlaştırması + V8 Düzeltmeleri:**

---

### 4.2.1 Safety Net Clamp ve Normalize (Düzeltme D4)

**Problem:** Safety Net penalty'leri skoru 0'ın altına düşürebilir.

**V8 Final Çözümü:**


```python
def compute_safety_net_score(base_score, penalties):

raw_score = base_score + sum(penalties)

---

# Clamp: skor 0'ın altına düşemez

clamped = max(0.0, raw_score)

---

# Normalize: 0-1 aralığına çek

if clamped > 1.0:

clamped = 1.0

return clamped

---

# Örnek: base=0.80, penalties=[-0.30, -0.20] = -0.50


---

# raw = 0.30 → clamped = 0.30 (geçerli)


---

# Örnek: base=0.20, penalties=[-0.30] = -0.30


---

# raw = -0.10 → clamped = 0.0 (minimum) ```

**Safety Net Skor Aralığı:** Her zaman 0.0 - 1.0 arasındadır. Negatif değerler clamp edilir.

**Kalibre Edilmiş Ağırlıklar (Learning Engine Çıktısı):**
| Değişken  | Eski Ağırlık  | Kalibre Ağırlık  | Değişim  | Gerekçe
|   | ---------- | ------------- | ----------------- |---------
| --------- |   | Fit  | 0.20  | **0.35**
| +0.15  | Simülasyonda en güçlü başarı prediktörü  |   | Need  | 0.20
| **0.25**  | +0.05  | İkinci en güçlü prediktör  |  | Evidence
| 0.25  | **0.15**  | -0.10  | Aşırı yüksek ağırlık, noise oluşturuyor  |
| Timing  | 0.20  | **0.10**  | -0.10  | Daha az prediktif
|   | Counterfactual  | 0.15  | **0.10**  | -0.05
| Robustness önemli ama aşırı değil  |   | Findeks  | 0.00  | **0.05** | +0.05 | Yeni eklendi, finansal sağlık sinyali |

**Kalibrasyon Döngüsü:**
```

Prediction → Action → Outcome (WON/LOST/ERROR) →

→ Learning Engine analiz eder → Ağırlıkları günceller →

→ Shadow Model test eder → Validated → Production
```


---

### 4.3 Counterfactual Engine (V6 — V7'de Eksikti, V8'de Eklendi)

Her opportunity için:

```python

---

# Örnek: Factory + Hiring + Investment + RFQ = 91 signals = [factory_expansion, hiring_surge, machine_investment, ekap_rfq] base_score = 91

for signal in signals:

score_without = compute_ensemble_without(signal)

contribution = base_score - score_without

store_in_prediction_ledger(signal, contribution)

---

# Eğer tek bir sinyalin çıkarılması skoru 40+ düşürüyorsa,


---

# opportunity fragile olarak işaretlenir.


---

# Fragile fırsatlar: max INVESTIGATE, CONTACT_NOW yasak ```

**Kural:** Bu sinyal katkısı/robustness ölçümüdür, kendisi başına nedensellik kanıtı değildir.---

---

## 5. KATMAN 4: DECISION ENGINE — Ekip Şimdi Ne Yapmalı?

**V6 Prensibi:** Actions: contact now, monitor, investigate, clarify, wait, revisit later, account-level validation, deprioritize.

**V7 AI Agent + WhatsApp + Redis Entegrasyonu + V8 Düzeltmeleri:**

---

### 5.1.2 DEPRIORITIZE Seviye 2: Kullanıcı Uyarısı (Kullanıcı Görür)

- **Tetikleyici (herhangi biri):**

• Evidence 0.20-0.30 **VE** Contradiction detected, **VEYA**

• Contraction sinyali **VE** Fit < 0.50, **VEYA**

• Counterfactual robustness < 0.40 (fragile fırsat) - **Sonuç:** Kullanıcıya DÜŞÜK GÜVEN etiketiyle gösterilir - **Aksiyon:** Sadece INVESTIGATE (CONTACT_NOW yasak) - **Açıklama:** Bu fırsatta çelişkili sinyaller var, önce araştırın - **Renk Kodu:** 🟠 (MONITOR ile aynı renk, ama etiket farklı)

**Eşik Standartizasyonu (Düzeltme D3):**
| Eşik  | Değer  | Anlamı  |  |------
| ------- | -------- |   | Evidence  | < 0.20
| Seviye 1 DEPRIORITIZE (filtre)  |   | Evidence  | 0.20-0.30 + Contradiction  | Seviye 2 DEPRIORITIZE (uyarı)
|   | Evidence  | < 0.20 (tek başına)  | Gate 4 başarısız, fırsat değil  |
| Evidence  | 0.20-0.50  | INVESTIGATE veya MONITOR  |  | Evidence | > 0.50 | CONTACT_NOW mümkün (diğer kapılar da geçmeli) |

---

### 5.3 Saatlik Contact Limiti (B2 Seçeneği Riski Giderme)

**Problem:** Max 3 kullanıcı/gün/firma hâlâ rahatsız edici olabilir.

**V8 Final Çözümü:** - **Max 1 contact/saat/firma** (günlük 3 yerine saatlik limit) - **Queue system:** Kullanıcılar sıraya girer, firma 1'er 1'er aranır - **OSB bazlı batch:** Aynı OSB'deki firmalar aynı gün toplu ziyaret edilebilir

---

### 5.4 WhatsApp Voice-to-Intent Agent (V7)

Saha kullanımı: - Sesli mesaj → Speech-to-Text → ChromaDB vektör sorgusu → Ensemble → Redis cache - **Ama:** Agent, sadece eşleştirme önerir; Decision Engine'in aksiyonunu önerir. Karar satış ekibindedir.

---

### 5.5 Buyer/Decision-Maker Kuralı

**V6 Prensibi korunur:** If the buyer/decision-maker cannot be found, do not invent one. Use company-level validation.

V8 Final'de: Neo4j graph'de DECISION_MAKER node'u varsa ve kanıtlıysa (LinkedIn, ASO üye listesi) kullanılır. Yoksa firma seviyesinde iletişim önerilir.

---

## 6. KATMAN 5: PORTFOLIO ENGINE — 10,000 Eşleşmeden 20'sini Seç

**V6 Prensibi:** Major differentiator. Allocates scarce resources using Expected Commercial Value, evidence confidence, win probability, timing, time-to-cash, strategic value, sales effort, deal complexity, resource conflicts, opportunity cannibalization, evidence-backed expansion value.

**V7 Hybrid Credit Modeli + V8 Düzeltmeleri:**

---

### 6.2 Account Opportunity Map + Global Deduplication


```sql
-- Aynı firmada birden fazla ürün fırsatı varsa SELECT firm_id, COUNT(*) AS opp_count,

MAX(timing_score) AS max_timing,

SUM(expected_value) AS total_value FROM opportunities

WHERE status = 'active' GROUP BY firm_id HAVING COUNT(*) > 1;
```
**Kural:** Eğer bir firmada 3+ aktif fırsat varsa, sadece en yüksek Portfolio_Score'lu 1-2'si contact now olarak işaretlenir. Diğerleri monitor veya revisit later.

**+ Global Deduplication:** Aynı firma-ürün kombinasyonu başka bir kullanıcı tarafından rezerve edilmişse, bu kullanıcıya gösterilmez.

---

### 6.3 Human Override

**V6 Prensibi korunur:** Human Override is allowed, but human preference is not objective evidence. Satış ekibi bir opportunity'yi el ile yukarı/aşağı çekebilir. Bu tercih Learning Engine'e human_bias etiketiyle kaydedilir; model bunu kanıt olarak değil, gürültü olarak işler.

---

## 7. KATMAN 6: LEARNING ENGINE — Gerçekten Ne İşe Yarıyor?

**V6 Prensibi:** Learn which signals, combinations, contexts, products, sectors and timing patterns actually lead to outcomes.

**V7'de bu katman tamamen eksikti. V8'de 10 bileşen + Kalibrasyon + Shadow Model aktif.**

---

### 7.1 Learning Loop


```

Signal → Prediction → Opportunity → Action → Reaction → Outcome → Learning → Validation → Model Improvement
```


---

### 7.2 Bileşenler


| Bileşen  | V6 Tanımı  | V8 Final Implementasyonu  |  |---------
| ----------- | ------------------- |   | **Prediction Ledger**  | Her material prediction'ı timestamp, evidence, unknowns ile kaydet
| PostgreSQL predictions tablosu. Her Ensemble skoru bir prediction'dır.  |   | **Outcome Ledger**  | Verified Won, Reported Won, Verified Lost, Reported Lost, Delayed, Unknown  | PostgreSQL outcomes tablosu. Verification: invoice, PO, contract, delivery, payment.
|   | **Feedback Engine**  | 👍/👎 minimum giriş  | WhatsApp Agent'tan 👍/👎 + kategori (need wrong, timing wrong, product wrong, company wrong, budget unsuitable, other). Her feedback 1 kredi iadesi.  |
| **Signal Quality**  | Hangi kaynaklar güvenilir?  | PostgreSQL: source_domain başına precision, recall, F1.  |  | **Prediction Error**
| 10 hata tipi  | PostgreSQL: error_type (wrong company, wrong need, wrong timing, wrong product, wrong budget, stale data, signal interpretation, common-cause, missing info).  |   | **Pattern Discovery**  | Yeni kombinasyonlar bul
| ChromaDB + Neo4j: yeni sinyal kombinasyonlarını cluster'la.  |   | **Pattern Memory**  | Eski pattern'leri unutma  | PostgreSQL: pattern_history tablosu. Eski pattern'ler deprecated olarak işaretlenir, silinmez.
|   | **Shadow Model**  | Yeni algoritma üretim yanında koşar  | **Güvenlik Valfi + A/B Test Motoru** (Bölüm 7.2.1 detaylandırıldı)  |
| **Validation**  | Candidate → Shadow → Validated → Production  | 4 aşamalı lifecycle. Promotion: yeterli örnek, kanıt, stabilite, validation.  |  | **Model Drift Detection**
| Prediction error over time  | PostgreSQL time-series: weekly prediction error rate. Eğer 4 hafta üst üste artıyorsa alert.  |   | **Kalibrasyon Motoru** (YENİ)  | Skor ağırlıklarını outcome verisiyle güncelle | Her ay outcome verisi analiz edilir, Ensemble ağırlıkları güncellenir. |

---

### 7.2.1 Shadow Model — Güvenlik Valfi + A/B Test Motoru (Düzeltme D1)

**Problem:** Shadow Model'in nasıl çalıştığı belirsizdi. Prediction Ledger'a yazıyor ama karar alıp almadığı, üretim modeline nasıl katkı sunduğu net değildi.

**V8 Final Çözümü: 2 Görevli Shadow Model**
```
┌─────────────────────────────────────────────────────────────────┐ │ SHADOW MODEL = Güvenlik Valfi + A/B Test Motoru

│ ├─────────────────────────────────────────────────────────────────┤ │

│ │ 1. GÜVENLİK VALFİ (Gerçek Zamanlı)

│ │

• Ensemble Divergence > 0.3 ise Shadow Model devreye girer

│ │

• Shadow Model INVESTIGATE derse, üretim CONTACT_NOW olsa

│ │

bile INVESTIGATE yapılır

│ │

• Bu cesur ama güvenli prensibini korur

│ │

• Divergence hesabı: |ensemble_prod - ensemble_shadow| > 0.3│ │

│ │ 2. A/B TEST MOTORU (Aylık)

│ │

• Shadow Model farklı ağırlıklarla çalışır

│ │

(örn: evidence ağırlığı %20 daha yüksek)

│ │

• Her ay: Shadow vs Üretim performans karşılaştırması

│ │

• Shadow %5+ daha iyi ise → Shadow üretim olur

│ │

(eski üretim yeni Shadow olur)

│ │

│ │ 3. PREDICTION LEDGER (Ayrı Kayıt)

│ │

• Her iki modelin skorları ayrı satırlarda kaydedilir

│ │

• shadow_model_flag = TRUE/FALSE ile ayrılır

│ │

• divergence = ABS(ensemble_prod - ensemble_shadow)

│ │

• divergence > 0.3 → alert + Güvenlik Valfi aktif

│ │

│ └─────────────────────────────────────────────────────────────────┘
```
**Shadow Model Akış Şeması:**
```
[Kullanıcı Sorgusu] → [Üretim Ensemble] → [Shadow Ensemble]

↓

↓

[ensemble_score_prod]

[ensemble_score_shadow]

↓

↓

[Divergence Hesapla]

[Divergence Hesapla]

↓

↓

divergence = |prod - shadow|

↓

↓

divergence > 0.3?

↓

├─ EVET → Güvenlik Valfi aktif

│

Shadow aksiyonu = INVESTIGATE ise

│

Üretim aksiyonu CONTACT_NOW → INVESTIGATE

│

Kullanıcıya: 3 model farklı karar verdi, araştırın

↓

└─ HAYIR → Üretim aksiyonu geçerli

↓

[Her ay A/B Test] → [Shadow performans > Üretim +%5?]

↓

├─ EVET → Shadow ←→ Üretim swap

↓

└─ HAYIR → Mevcut devam
```
**Shadow Model SQL (Prediction Ledger):**


```sql
-- Shadow Model kayıtları ayrı flag ile predictions tablosunda CREATE TABLE predictions (

prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

firm_id UUID REFERENCES firms(firm_id),

product_id UUID,

-- Üretim model skorları

topsis_score FLOAT,

learning_score FLOAT,

safety_score FLOAT,

ensemble_score FLOAT,

-- Shadow Model skorları (D1)

shadow_topsis_score FLOAT,

shadow_learning_score FLOAT,

shadow_safety_score FLOAT,

shadow_ensemble_score FLOAT,

shadow_model_flag BOOLEAN DEFAULT FALSE,

-- Divergence (D1)

ensemble_divergence FLOAT,

divergence_alert BOOLEAN DEFAULT FALSE,

-- Diğer alanlar

unknowns JSONB,

predicted_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP );
```


---

# Aylık kalibrasyon döngüsü def calibrate_weights():

outcomes = fetch_last_month_outcomes()

---

# Her değişkenin WON ile korelasyonunu hesapla

correlations = {

'fit': spearman(outcomes.fit, outcomes.won),

'need_prob': spearman(outcomes.need_prob, outcomes.won),

'evidence': spearman(outcomes.evidence, outcomes.won),

'timing': spearman(outcomes.timing, outcomes.won),

'counterfactual': spearman(outcomes.counterfactual, outcomes.won),

'findeks': spearman(outcomes.findeks, outcomes.won)

}

---

# Korelasyonları normalize et → yeni ağırlıklar

total_corr = sum(abs(c) for c in correlations.values())

new_weights = {k: abs(v)/total_corr for k, v in correlations.items()}

---

# Shadow Model'de test et

shadow_performance = test_shadow_model(new_weights)

current_performance = test_current_model()

if shadow_performance > current_performance * 1.05:

---

### 7.3.1 Kalibrasyon Cold-Start Stratejisi (Düzeltme D5)

**Problem:** Faz 1'de (Ay 1-3) Learning ağırlığı 0, yeterli outcome verisi yok.

**V8 Final Çözümü: 3 Fazlı Kalibrasyon**
| Faz  | Dönem  | Learning Ağırlığı  | Kalibrasyon  | Shadow Model
|   | ----- | ------- | ------------------- |-------------
| -------------- |   | **Cold-Start**  | Ay 1-3  | 0 (devre dışı)
| Statik ağırlıklar (simülasyon sonrası)  | Pasif (kayıt only)  |   | **Warm-Up**  | Ay 4-6
| 0.20 (düşük)  | Aylık manuel review + yarı-otomatik  | Aktif (A/B test)  |  | **Full**
| Ay 7+  | 0.45 (hedef)  | Tam otomatik aylık kalibrasyon  | Aktif (Güvenlik Valfi + A/B)  |

**Cold-Start Ağırlıkları (Ay 1-3, statik):**
| Değişken  | Ağırlık  | Gerekçe  |  |----------
| --------- | --------- |   | Fit  | 0.35
| Simülasyonda en güçlü prediktör  |   | Need  | 0.25  | İkinci en güçlü
|   | Evidence  | 0.15  | Noise oluşturuyordu, düşürüldü  |
| Timing  | 0.10  | Daha az prediktif  |  | Counterfactual
| 0.10  | Robustness  |   | Findeks  | 0.05
| Yeni eklendi  | **Minimum Sample Threshold (Kalibrasyon için):**

 | Aşama  | Min Outcome  | Min Süre
| Aksiyon  |   | ------- | ------------- |----------
| --------- |   | Cold-Start  | 0  | 0
| Statik ağırlıklar kullan  |   | Warm-Up  | 20  | 1 ay
| İlk kalibrasyon denemesi  |   | Full  | 50  | 3 ay
| Otomatik kalibrasyon aktif  | **Kalibre Edilmiş Ağırlıklar (Zamanla):**

 | Değişken  | Başlangıç  | Kalibre (Ay 3)
| Kalibre (Ay 6)  | Kalibre (Ay 12)  |   | ---------- |-----------
| ---------------- | ---------------- | ----------------- |  | Fit
| 0.20  | 0.30  | 0.35  | 0.38  |
| Need  | 0.20  | 0.22  | 0.25  | 0.26
|   | Evidence  | 0.25  | 0.20  | 0.15
| 0.12  |   | Timing  | 0.20  | 0.15
| 0.10  | 0.08  |   | Counterfactual  | 0.15
| 0.10  | 0.10  | 0.09  |  | Findeks
| 0.00  | 0.03  | 0.05  | 0.07  |

---

### 7.4 Learning Safety Rules (V6'nın 10 Kuralı Korunur)

1. Unknown is allowed. 2. Never invent missing commercial facts. 3. Feedback ≠ verified outcome. 4. Correlation ≠ causality. 5. Copied sources ≠ independent evidence. 6. Missing ≠ negative. 7. One customer must not define a global pattern. 8. Old patterns must be monitored for drift. 9. Production weights do not change simply because a new pattern was discovered. 10. New models must pass shadow validation.

**+ V8 Final Ek Kuralı:** 11. **Monetization Learning:** Hangi fiyatlandırma tier'inde (Terminal/Strategic/Enterprise) hangi feature'lar gerçekten retention ve expansion sağlıyor? Hybrid Credit tüketim pattern'leri Learning Engine'e input olarak girer. 12. **Kalibrasyon Güvenliği:** Ağırlık değişimi tek seferde max %10 olabilir. Daha büyük değişimler Shadow Model'de 4 hafta test edilmelidir. 13. **Shadow Model Güvenliği:** Ensemble Divergence > 0.3 ise sistem conservative moda geçer (max INVESTIGATE). Divergence 2 hafta üst üste devam ederse alert.

---

### 7.5 Minimum Sample Threshold

**V6 Prensibi:** A pattern with 8 successes out of 8 is not automatically a production rule.

V8 Final'de: - **Candidate:** N ≥ 5, başarı oranı > 0.6 - **Shadow:** N ≥ 20, 4 hafta boyunca üretim modelinden daha iyi performans - **Validated:** N ≥ 50, sektörde 3+ farklı müşteri tarafından teyit edilmiş - **Production:** N ≥ 100, Model Drift Detection aktif---

---

## 8. KATMAN 0: EVIDENCE & DATA QUALITY LAYER

**V6'nın 9 Boyutu + V7 Pydantic Gate:**
| V6 Boyutu  | V8 Final Implementasyonu  | Başarısız Olursa  |  |-----------
| ------------------- | ----------------- |   | Source Reliability  | PostgreSQL sources tablosu: domain başına reliability_score (0-1)
| reliability < 0.3 → quarantine  |   | Freshness  | updated_at timestamp; sinyal yaş > 90 gün → stale  | freshness < 0.5 → weight düşür
|   | Independence  | Neo4j: aynı kaynak domain'den gelen sinyaller independence=0.5  | independence < 0.5 → momentum düşür  |
| Entity Resolution Confidence  | 3 adımlı eşleştirme (VKN → Telefon/Domain → Fuzzy) + confidence skoru  | confidence < 0.8 → quarantine_firms  |  | Completeness
| Pydantic schema validation: zorunlu alanlar  | incomplete → quarantine  |   | Contradiction  | ChromaDB contradiction vector: aynı firmada + ve - sinyal
| contradiction detected → flag + düşük evidence  |   | Evidence Type  | direct (fatura, sözleşme) vs inferred (haber, iş ilanı)  | inferred → lower weight
|   | Evidence Age  | PostgreSQL: evidence_age_days  | age > 365 → deprecated  | | Direct vs Inferred | evidence_type ENUM: DIRECT, INFERRED, DERIVED | INFERRED/DERIVED → confidence penalty |

---

### 8.1 Quarantine Pipeline


```
[Raw Data] → [Pydantic Validation Gate] → [Valid] → PostgreSQL/ChromaDB/Neo4j

↓

[Invalid] → quarantine_firms (JSONB + error_reason)

↓

[Analyst Review / RL Agent] → resolved_status
```
**Kural:** Poor evidence reduces confidence. Hiçbir veri tamam işte doğru olarak kabul edilmez; her verinin kanıt skoru vardır.

---

## 9. BİRLEŞİK VERİ ALTYAPISI


---

### 9.1 Teknoloji Stack


| Katman  | Teknoloji  | Rol  | V6 Karşılığı  | V7 Karşılığı
|   | -------- | ----------- | ----- |-------------
| ------------- |   | İlişkisel SSOT  | PostgreSQL 16 + PostGIS  | Master firma, sinyaller, ledger'lar, kredi
| Soyut Data Layer  | PostgreSQL schema  |   | Vektör  | ChromaDB
| Capability matching, contradiction detection  | Soyut Fit  | ChromaDB 1536-dim  |  | Graph
| Neo4j  | Risk yayılımı, symbiosis, common cause  | Soyut Relationship  | Neo4j graph  |
| Cache / PubSub  | Redis  | <300ms latency, warm cache, scheduled signals  | Yok  | Redis
|   | Validation  | Pydantic  | Schema validation, quarantine gate  | Soyut Quality | Pydantic Gate |

---

## 10. UI/UX: İNSANLAR SKORLARI NASIL GÖRECEK?

**V6 Prensibi:** Do not expose false precision. If price, budget, decision-maker or win probability is not evidenced, show Unknown / not estimated.

**V8 Final Çözümü: 5 Boyutlu Skor + Ensemble Şeffaflığı + 2 Aşamalı Anonimlik (Düzeltme D2)**

---

### 10.1 Fırsat Kartı (Opportunity Card) — Kimlik Açıldıktan Sonra


```
┌─────────────────────────────────────────────────────────────────────────────┐ │

FIRSAT KARTI (Opportunity Card)

│ ├─────────────────────────────────────────────────────────────────────────────┤ │

│ │

🔥 Sıcaklık: YÜKSEK

📍 OSTİM

💰 85K-120K TRY (Tahmini)

│ │

│ │

┌─────────────────────────────────────────────────────────────────────┐

│ │

│

Özdemir Lazer Kesim

│

│ │

│

⭐ A+ Verified Supplier

|

🏭 Field Verified

│

│ │

└─────────────────────────────────────────────────────────────────────┘

│ │

│ │

🎯 NEDEN BU FİRMA?

│ │

• Son 14 günde 3 yeni iş ilanı (CNC Operatörü, Lazer Teknikeri)

│ │

• Yeni makine yatırımı sinyali (2 kaynaktan doğrulandı)

│ │

• EKAP'ta benzer ürün grubunda ihale kazanmış

│ │

│ │

📊 5 BOYUTLU SKOR (Tek skor yerine — V6 Prensibi)

│ │

│ │

İhtiyaç Olasılığı

████████░░

78%

[Güçlü kanıt]

│ │

Zamanlama

██████░░░░

65%

[Son 10 gün aktif]

│ │

Ürün Uyumu

█████████░

85%

[NACE + Capability match]

│ │

Momentum

███████░░░

72%

[İvme yukarı]

│ │

Kanıt Gücü

██████░░░░

60%

[2 bağımsız kaynak]

│ │

│ │

⚠️

BİLİNMEYENLER (Şeffaf gösterim — V6 Prensibi)

│ │

• ❓ Karar verici ismi bilinmiyor

│ │

• ❓ Bütçe aralığı tahmin edilemiyor

│ │

• ❓ Rakip tedarikçi durumu bilinmiyor

│ │

│ │

🎯 ENSEMBLE SKOR: 0.769

│ │

[TOPSIS: 0.730 | Learning: 0.636 | Safety: 1.0]

│ │

→ Learning ağırlığı yüksek çünkü outcome verisi güçlü

│ │

│ │

┌─────────────────────────────────────────────────────────────────────┐

│ │

│

ÖNERİLEN AKSIYON:

📞 ŞİMDİ ARA (CONTACT NOW)

│

│ │

│

│

│ │

│

Neden? Fit > 0.50, Need > 0.40, Evidence > 0.35, Timing > 0.30

│

│ │

│

Counterfactual robustness: 0.91 (tek sinyale bağımlı değil)

│

│ │

└─────────────────────────────────────────────────────────────────────┘

│ │

│ │

[👍 Doğru Fırsat]

[👎 Yanlış Fırsat]

[💾 Kaydet]

[📤 Paylaş]

│ │

│ └─────────────────────────────────────────────────────────────────────────────┘
```


---

### 10.2 Karşılaştırmalı Görünüm (Dashboard)


```
┌─────────────────────────────────────────────────────────────────────────────┐ │

KARŞILAŞTIRMALI GÖRÜNÜM (Dashboard)

│ ├─────────────────────────────────────────────────────────────────────────────┤ │

│ │

Sıra | Firma

| 5 Skor Radar

| Ensemble | Aksiyon

│ │

─────┼───────────────────┼─────────────────────┼──────────┼──────────────│ │

1

│ Özdemir Lazer

│ ████████░░ ██████░░░│

0.769

│ 📞 Ara

│ │

│

│ █████████░ ███████░░│

│

│ │

│

│ ██████░░░░

│

│

│ │

─────┼───────────────────┼─────────────────────┼──────────┼──────────────│ │

2

│ Sincan Robotik

│ ██████░░░░ ████████░│

0.742

│ 📞 Ara

│ │

│

│ ████████░░ ███████░░│

│

│ │

│

│ ██████░░░░

│

│

│ │

─────┼───────────────────┼─────────────────────┼──────────┼──────────────│ │

3

│ OSTİM Mil

│ █████████░ ████░░░░░│

0.698

│ 🔍 Araştır

│ │

│

│ ██████░░░░ ███████░░│

│

│ │

│

│ ██████░░░░

│

│

│ │

│ │

🎨 Renk Kodlaması:

│ │

🟢 Need > 70% + Fit > 70% → Otomatik CONTACT_NOW önerisi

│ │

🟡 Need 40-70% veya Fit 50-70% → INVESTIGATE önerisi

│ │

🟠 Need < 40% veya Fit < 50% → MONITOR önerisi

│ │

🔴 Contraction veya Evidence < 0.20 → DEPRIORITIZE (Seviye 1/2)

│ │

│ └─────────────────────────────────────────────────────────────────────────────┘
```


---

### 10.3 Mobil / WhatsApp Agent Görünümü


```
📱 WhatsApp Mesajı:

Özdemir Lazer - 5 Eksen CNC İhtiyaç: 78% | Zamanlama: 65% | Uyum: 85% Ensemble: 0.77 | Öneri: 📞 ARA

Neden? Son 14 günde 3 iş ilanı + yeni makine yatırımı. 2 bağımsız kaynak doğruladı.

[Bilgileri Gör] [Ara] [Sonra Hatırlat]
```


---

## 11. MONETİZASYON: HYBRID CREDIT + LEARNING ENTegrasyonu

**V7'nin 7 gelir kalemi V6 prensipleriyle filtrelenir:**
| Gelir Kalemi  | Fiyat  | V6 Prensibi Uygulaması  |  |-------------
| ------- | ---------------------- |   | B2B Industrial Terminal  | 85,000 TRY/yıl
| 100 kredi. Learning Engine: bu tier'daki kullanıcıların feedback'leri global pattern'a dahil edilmez (Rule 7: One customer must not define a global pattern).  |   | Strategic Intelligence  | 220,000 TRY/yıl  | 500 kredi + Idle Capacity + HS Code. Portfolio Engine: bu tier'daki firmalar daha karmaşık deal'lar üretir, cannibalization riski yüksektir.
|   | Enterprise (Prime Contractor)  | 650,000 TRY+/yıl  | Unlimited API + C-Level + Neo4j Graph Risk. **Data Strategy:** ERP entegrasyonu sadece bu tier'da opsiyonel.  |
| Credit Pack  | 750 TRY / 50 kredi  | Pay-per-match. Learning Engine: kredi tüketim pattern'leri churn prediction için kullanılır.  |  | Emergency RFQ Fee
| 2,500 TRY / RFQ  | Hot Opportunity push. **Kural:** Emergency RFQ sadece Evidence > 0.8 ve Timing > 0.9 ise push edilir. Uydurma acil yok.  |   | Verified Supplier Badge  | 35,000 TRY/yıl
| Field Verification Bonus (+0.20 TOPSIS). **Kural:** Badge sahte değil; saha ekibi gerçekten doğrular.  |   | Hot Sales Lead Sale  | 12,500 TRY / lead  | Qualified lead. **Kural:** Lead, Opportunity Engine'den geçmiş, kanıtlı, timing'li olmalı. Rastgele liste değil.
|   | Success Fee  | 2-4% hacim  | Closed subcontract volume. Outcome Ledger'da VERIFIED_WON ile teyit edilir.  |

**V6 ↔ V8 Final Kuralı:** Monetizasyon, Learning Engine'e girdi sağlar. Hangi tier'da hangi feature retention sağlıyor? Hangi fiyatlandırma churn'e yol açıyor? Bu veriler Shadow Model'de test edilir.

---

## 12. SAHA OPERASYONU & FIELD BRIDGES


| Köprü  | V7 Özelliği  | V6 Prensibi Uygulaması  |  |-------
| ------------ | ---------------------- |   | WhatsApp Voice-to-Intent  | Sesli mesaj → ChromaDB query
| Agent, sadece eşleştirme önerir; Decision Engine aksiyon önerir.  |   | TOBB Capacity Report OCR  | PDF → makine envanteri  | OCR çıktısı Pydantic gate'den geçer; anomali quarantine'a alınır.
|   | Digital Dispute & Arbitration  | B2B Findeks escrow  | Dispute sürecinde firma skoru pending olarak işaretlenir; Unknown ≠ Lost.  | | OSB Grid Monitoring | Bakım → Under Maintenance | RFQ otomatik yönlendirme. Bu bir signal'dir; Signal & Momentum System'e girer. |

---

## 13. GÜVENLİK & COMPLIANCE


| V7 Özelliği  | V6 Prensibi  | V8 Final Uygulaması  |  |-------------
| ------------ | --------------- |   | Zero-Knowledge CAD Encryption  | —
| CAD modelleri at-rest encrypted. İndirme anında dinamik watermark.  |   | PLG Findeks Hook  | —  | Self-service lead-gen. Kendi B2B Findeks skorunu ücretsiz sorgula.
|   | İYS Consent Shield  | Privacy-conscious  | İYS izni olmayan kişilere otomatik mesaj atılmaz.  | | Latency SLA <300ms | — | Redis warm cache. Complex graph/vector queries cache'lenir. |

---

## 14. ADVERSARIAL TEST FRAMEWORK V3

**V6'nın V2'si V8'de genişletilir. V7'nin tüm katmanları test edilir.**

Her test 7 eksene saldırır: 1. Data correctness 2. Data completeness 3. Signal independence 4. Causality 5. Timing 6. Generalization 7. Decision impact

**Sonuçlar:** - 🟢 GEÇTİ - 🔴 KALDI - 🟠 ALGORİTMA DEĞİŞMELİ - 🔵 ASK / BİLGİ EKSİK

---

### 14.1 V7'ye Özel Yeni Testler


| Test  | Açıklama  | Hedef Katman  |  |------
| ---------- | ------------- |   | TOPSIS Hallucination  | Sinyal bonusu olmayan firma, sinyal bonusu varmış gibi skorlanıyor mu?
| Opportunity Engine  |   | Credit Exhaustion  | Kredi bitince sistem contact now önermeye devam ediyor mu?  | Portfolio Engine
|   | ERP Poison  | Zehirli ERP verisi TOPSIS skorunu manipüle ediyor mu?  | Evidence Layer  |
| WhatsApp Noise  | Anlaşılmayan sesli mesaj quarantine'a gidiyor mu?  | Field Bridges  |  | Neo4j Cascade Failure
| Bir Tier-3 iflası Tier-1 skorunu gereksiz düşürüyor mu?  | Graph Risk  |   | Monetization Bias  | Yüksek gelirli lead'ler düşük kanıtlıyken öne çıkarılıyor mu?
| Portfolio Engine  |   | Badge Fraud  | Ödeme yapılmadan A+ badge atanabiliyor mu?  | Evidence Layer
|   | **Ensemble Divergence** (YENİ)  | 3 model birbirinden çok farklı skor veriyor mu? (>0.3 fark)  | Opportunity Engine  |
| **Kalibrasyon Drift** (YENİ)  | Ağırlıklar tek yöne sapıyor mu? (örn. fit %50'yi aşıyor mu?)  | Learning Engine  |  | **Deduplication Leak** (YENİ)
| Rezerve edilmiş fırsat başka kullanıcıya gösteriliyor mu?  | Portfolio Engine  |   | **Shadow Model Swap** (YENİ)  | Shadow Model üretim olduğunda eski senaryolar bozuluyor mu?
| Learning Engine  |   | **Anonim Bypass** (YENİ)  | A+ olmayan kullanıcı kimlik açmadan iletişim bilgisi görüyor mu?  | UI/UX
|   | **DEPRIORITIZE Leak** (YENİ)  | Seviye 1 DEPRIORITIZE fırsatları kullanıcıya sızıyor mu?  | Decision Engine  |

**Kural:** When a rule changes, regression-test previous scenarios. Shadow Model'de yeni algoritma, eski senaryoları da geçmeli.

---

## 15. AÇIK PROBLEMLER (V6'nın Listesi Güncellenmiş + V8 Final)

V7'de bu liste yoktu. V8'de şeffafça korunur:

1. **Final event taxonomy** — Sinyal tiplerinin tam sınıflandırması 2. **Graph + relational data model** — Neo4j ↔ PostgreSQL senkronizasyon optimizasyonu 3. **Signal weighting** — AHP ağırlıklarının sektöre göre otomatik kalibrasyonu 4. **Counterfactual implementation** — Performans optimizasyonu (her sinyal için tekrar hesaplama maliyetli) 5. **Common-cause detection** — Neo4j graph'te otomatik CAUSED_BY_SAME_INCENTIVE tespiti 6. **Momentum mathematical formulation** — Velocity + acceleration + recency + independence formülasyonunun kesinleştirilmesi 7. **Timing model** — Ne zaman satış yapmalı? için sezonsal, sektörel, firma-özel timing modeli 8. **Confidence calibration** — Ensemble skorlarının gerçek olasılıklara kalibrasyonu 9. **Portfolio optimization** — 10,000×100 matrisinde gerçek-zamanlı optimizasyon 10. **Outcome verification** — Invoice/PO doğrulamasının otomatikleştirilmesi 11. **Entity resolution** — LinkedIn, EKAP gibi VKN'siz kaynaklarla eşleştirme 12. **Source reliability** — Yeni bir kaynağın reliability skorunun cold-start'ta belirlenmesi 13. **Pricing/value estimation without hallucination** — Bütçe/tahmini fiyat çıkarımı (V6: Never invent budget) 14. **Privacy/legal boundaries** — GİB verisi, EKAP verisi, LinkedIn scraping yasal sınırları 15. **MVP scope** — İlk 90 günde hangi 3 özellik canlıya alınacak? 16. **Minimum data required for useful predictions** — Kaç firma, kaç sinyal, kaç gün veriyle anlamlı skor çıkar? 17. **Benchmark methodology** — V8 Benchmark: 100 firma × 100 ürün × realistic outcomes 18. **Go-to-market and onboarding** — OSTİM'de ilk 10 müşteriyi nasıl kazanırız? 19. **Churn prediction** — Hangi müşteri neden ayrılır? (V7 monetizasyonu + V6 Learning) 20. **Multi-language NLP** — Türkçe teknik terimlerin ChromaDB embedding kalitesi 21. **Ensemble convergence** (YENİ) — 3 modelin skorları ne zaman birbirine yaklaşır? Ne zaman ayrılır? 22. **Kalibrasyon frequency** (YENİ) — Ağırlıklar ne sıklıkla güncellenmeli? Haftalık? Aylık? 23. **Deduplication fairness** (YENİ) — Rezervasyon sistemi küçük kullanıcıları dışlar mı? 24. **Shadow Model maintenance** (YENİ) — 2 modelin bakım maliyeti nasıl optimize edilir? 25. **Anonim profile conversion rate** (YENİ) — Kullanıcılar kimlik açma butonuna basıyor mu?

---

## 16. MVP YOL HARİTASI: 3 FAZ


---

### Faz 1: MVP (Ay 1-3) — Kanıt Topla

- GİB E-Fatura + OSTİM/İvedik/ASO dizinleri → PostgreSQL - Pydantic Validation Gate + quarantine_firms - **Temel Ensemble (sadece TOPSIS + Safety Net, Learning ağırlığı 0)** — Cold-Start - Hibrit Fit (KATMAN 1: NACE kuralı + KATMAN 2: sadece A+ badge için saha onayı) - 100×100 Benchmark başlat - **ERP entegrasyonu YOK** — V6 Data Strategy prensibi - **Global deduplication (basit versiyon)** - **Anonim Profil (Aşama 1+2)** - **DEPRIORITIZE Seviye 1 aktif** (Seviye 2 Faz 2'de)

---

### Faz 2: Growth (Ay 4-9) — Öğrenmeye Başla

- EKAP + LinkedIn (açık veri) ekle - Signal & Momentum System aktif - **Learning Engine: Prediction Ledger + Feedback Engine + Kalibrasyon (Warm-Up)** - Counterfactual Engine (basit versiyon) - WhatsApp Agent + TOBB OCR - Hybrid Credit monetizasyonu başlat - **Shadow Model devreye al (A/B Test)** - **Ensemble tam versiyon (3 model)** - **DEPRIORITIZE Seviye 2 aktif** - **Shadow Model Güvenlik Valfi aktif**

---

### Faz 3: Scale (Ay 10-18) — Otonomlaş

- ERP/MES API Gateway (opsiyonel, Enterprise tier) - Neo4j Graph Risk + Industrial Symbiosis - HS Code Import Substitution - **Model Drift Detection + otomatik kalibrasyon (Full)** - Full Adversarial Test Framework V3 - Expansion: Ankara OSB'ler → Türkiye - **Shadow Model otomatik swap aktif**

---

## 17. HANDOFF RULES FOR ANOTHER AI (V6'nın 12 Kuralı Korunur)

Treat this document as the current design state, not a finished specification.

When improving it: 1. Preserve accepted principles unless strong evidence shows a flaw. 2. Criticize assumptions. 3. Propose alternatives before changing core architecture. 4. Stress-test every major algorithmic change. 5. Never invent data availability. 6. Label assumptions, unknowns and evidence. 7. Prefer useful simplicity over unnecessary complexity. 8. For every score, explain what decision it changes. 9. For every data field, explain how it can realistically be collected. 10. For every learning rule, explain how it can fail and how it will be tested. 11. Regression-test old scenarios after changes. 12. Keep the customer-facing product simpler than the internal intelligence layer.

**+ V8 Final Ek Kuralı:** 13. For every monetization feature, explain how it aligns with evidence-backed intelligence and does not incentivize hallucination or false urgency. 14. **For every ensemble model, explain how divergence between models is detected and resolved.** 15. **For every UI score, explain what unknown information is hidden and why.** 16. **For every shadow model decision, explain how it affects the production model and when it overrides.** 17. **For every anonymization feature, explain the conversion funnel and privacy boundaries.**

---

## 18. CORE PRINCIPLE

> The goal is not to find more data. The goal is to make better commercial inferences from fragmented data while being explicit about uncertainty.

**V8 Final Füzyonu:** Daha fazla veri (V7'nin altyapısı) + daha iyi çıkarım (V6'nın zekası) + şeffaf belirsizlik (her iki versiyonun prensibi) + **simülasyonla doğrulanmış düzeltmeler** + **doküman tutarlılığı** = **Kanıt-odaklı, öğrenen, ölçeklenebilir, tutarlı B2B Commercial Intelligence.**

---

**END — MASTER CONTEXT V8 FINAL**

**Değişiklik Özeti:** - 5 Simülasyon Bulgusu Düzeltildi (Bulgu 1-5) - 8 Doküman Tutarlılık Düzeltmesi Uygulandı (D1-D8) - 3 Yeni Adversarial Test Eklendi (Shadow Model Swap, Anonim Bypass, DEPRIORITIZE Leak) - 3 Yeni Açık Problem Eklendi (Shadow Model maintenance, Anonim conversion, Deduplication fairness) - 2 Yeni Handoff Kuralı Eklendi (Shadow Model, Anonimlik)