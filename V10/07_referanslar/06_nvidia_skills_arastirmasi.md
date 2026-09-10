# NVIDIA Build Skills Araştırması



Bağlantılar: [[00-Home]] · [[04_web_kazima_kaynak_arastirmasi]] · [[10_ankara_osb_sentez]] · [[project_state]] · [[CHANGELOG]]



**Tarih:** 2026-09-01

**Analist:** Araştırmacı Ajan + Koordinatör Ajan



---



## 1. Giriş



Product Owner talebi: NVIDIA Build platformundaki açık kaynak, kurulabilir, projeyle ilgili skill'leri araştır. Aşağıdaki 3 skill özellikle istenmiştir:

- data-designer

- skill-card-generator

- cuopt-numerical-optimization-formulation



Araştırma 3 kaynaktan yapıldı:

1. https://build.nvidia.com/skills (NVIDIA Build skills kataloğu)

2. https://github.com/NVIDIA/skills (GitHub repo, 3.2k star, 369 fork)

3. https://build.nvidia.com (Ana sayfa)



---



## 2. İstenen 3 Skill — Kurulum Komutları



### 2.1 data-designer

- **Komut:** 

px skills add nvidia/skills --skill data-designer --yes

- **Açıklama:** NeMo Data Designer ile sentetik veri seti oluşturmak için kullanılır. LLM tabanlı veri üreteçleri, sampler'lar ve validation column'ları ile veri pipeline'ı kurar.

- **Fayda:** Veri kalite skoru artırma, ETL test verisi üretme, NACE sınıflandırma için sentetik eğitim verisi oluşturma

- **Kurulum denemesi:** **BAŞARILI** — .agents/skills/data-designer/ dizinine kuruldu

- **Lisans:** Apache-2.0

- **Kaynak:** https://github.com/NVIDIA-NeMo/DataDesigner



### 2.2 skill-card-generator

- **Komut:** 

px skills add nvidia/skills --skill skill-card-generator --yes

- **Açıklama:** Mevcut skill dizinlerinden NVIDIA governance skill card (skill-card.md) üretir. Skill'in metadata'sını analiz eder, JSON context oluşturur, markdown card render eder.

- **Fayda:** Wiki kartları, ADR kartları, skill dokümantasyonu otomasyonu, governance süreçleri

- **Kurulum denemesi:** **BAŞARILI** — .agents/skills/skill-card-generator/ dizinine kuruldu

- **Lisans:** CC-BY-4.0 AND Apache-2.0

- **Kaynak:** https://github.com/NVIDIA/Trustworthy-AI



### 2.3 cuopt-numerical-optimization-formulation

- **Komut:** 

px skills add nvidia/skills --skill cuopt-numerical-optimization-formulation --yes

- **Açıklama:** LP (Linear Programming), MILP (Mixed Integer LP), QP (Quadratic Programming) problemlerini formüle etmek için kullanılır. Problem metninden değişkenler, kısıtlar, amaç fonksiyonu çıkarır.

- **Fayda:** Scraping optimizasyonu, eşleştirme algoritmaları, NACE kodu atama optimizasyonu, kaynak planlama

- **Kurulum denemesi:** **BAŞARILI** — .agents/skills/cuopt-numerical-optimization-formulation/ dizinine kuruldu

- **Lisans:** Apache-2.0

- **Kaynak:** https://github.com/NVIDIA/cuopt



---



## 3. Bulunan Diğer İlgili Skill'ler (araştırma sonucu)



NVIDIA toplam **346 skill** barındırıyor. Projeyle ilgili potansiyel skill'ler:



| # | Skill Adı | Kategori | Kurulum | Fayda | URL |

|---|---|---|---|---|---|

| 1 | aiq-research | AI/Research | 

px skills add nvidia/skills --skill aiq-research --yes | Derin araştırma workflow'ları | github.com/NVIDIA-AI-Blueprints/aiq |

| 2 | rag-blueprint | RAG Pipeline | 

px skills add nvidia/skills --skill rag-blueprint --yes | Bilgi getirme sistemleri | github.com/NVIDIA-AI-Blueprints/rag |

| 3 | rag-eval | RAG Değerlendirme | 

px skills add nvidia/skills --skill rag-eval --yes | RAG kalite metrikleri | github.com/NVIDIA-AI-Blueprints/rag |

| 4 | portfolio-optimization | Finans/Optimizasyon | 

px skills add nvidia/skills --skill portfolio-optimization --yes | Portföy optimizasyonu | github.com/NVIDIA-AI-Blueprints/portfolio-optimization |

| 5 | cuopt-routing-api-python | Optimizasyon | 

px skills add nvidia/skills --skill cuopt-routing-api-python --yes | Rotalama optimizasyonu | github.com/NVIDIA/cuopt |

| 6 | cuopt-numerical-optimization-api | Optimizasyon | 

px skills add nvidia/skills --skill cuopt-numerical-optimization-api --yes | Sayısal optimizasyon API | github.com/NVIDIA/cuopt |

| 7 | cuopt-multi-objective-exploration | Optimizasyon | 

px skills add nvidia/skills --skill cuopt-multi-objective-exploration --yes | Çok amaçlı optimizasyon | github.com/NVIDIA/cuopt |

| 8 | accelerated-computing-cudf | Veri İşleme | 

px skills add nvidia/skills --skill accelerated-computing-cudf --yes | GPU hızlandırmalı DataFrame | github.com/rapidsai/cudf |

| 9 | nemo-retriever | Bilgi Getirme | 

px skills add nvidia/skills --skill nemo-retriever --yes | Corpus tabanlı soru-cevap | github.com/NVIDIA/NeMo-Retriever |

| 10 | rag-perf | Performans | 

px skills add nvidia/skills --skill rag-perf --yes | RAG performans analizi | github.com/NVIDIA-AI-Blueprints/rag |

| 11 | cuopt-server-api-python | Optimizasyon | 

px skills add nvidia/skills --skill cuopt-server-api-python --yes | cuOpt sunucu API | github.com/NVIDIA/cuopt |

| 12 | aiq-deploy | AI Deploy | 

px skills add nvidia/skills --skill aiq-deploy --yes | AI-Q servis dağıtımı | github.com/NVIDIA-AI-Blueprints/aiq |



---



## 4. Kurulum Denemesi Sonuçları



### 4.1 Node.js / npm / npx Durumu

- 

ode --version: v24.19.0

- 

pm --version: 11.17.0

- 

px --version: 11.17.0

- **Durum:** Tüm araçlar çalışır durumda



### 4.2 Deneme Komutları ve Çıktıları



**Komut 1:** 

px skills add nvidia/skills --skill data-designer --yes

- **Sonuç:** BAŞARILI

- **Çıktı:** 346 skill keşfedildi, 1 skill seçildi, 77 agent'a kuruldu

- **Yol:** .agents/skills/data-designer/

- **Güvenlik:** Gen=Safe, Socket=0 alerts, Snyk=Low Risk



**Komut 2:** 

px skills add nvidia/skills --skill skill-card-generator --yes

- **Sonuç:** BAŞARILI

- **Çıktı:** 346 skill keşfedildi, 1 skill seçildi, 77 agent'a kuruldu

- **Yol:** .agents/skills/skill-card-generator/

- **Güvenlik:** Gen=Safe, Socket=0 alerts, Snyk=Med Risk



**Komut 3:** 

px skills add nvidia/skills --skill cuopt-numerical-optimization-formulation --yes

- **Sonuç:** BAŞARILI

- **Çıktı:** 346 skill keşfedildi, 1 skill seçildi, 77 agent'a kuruldu

- **Yol:** .agents/skills/cuopt-numerical-optimization-formulation/

- **Güvenlik:** Gen=Safe, Socket=0 alerts, Snyk=Low Risk



### 4.3 Kurulum Klasörü

- **Hedef:** C:\Projeler\Huginn Data Insights\.agents\skills\

- **Toplam dosya sayısı:** 30 dosya

- **Toplam boyut:** ~0.21 MB

- **Mevcut skills listesi (kurulum öncesi):**

  - .kilo/skills/adbc/

  - .kilo/skills/agent-md-refactor/

  - .kilo/skills/airflow/

  - .kilo/skills/changelog-generator/

  - .kilo/skills/database-observability/

  - .kilo/skills/dd-logs/



**Yeni kurulan skills:**

- .agents/skills/data-designer/ (SKILL.md, skill-card.md, BENCHMARK.md, skill.oms.sig, evals/, references/, scripts/, workflows/)

- .agents/skills/skill-card-generator/ (SKILL.md, skill-card.md, BENCHMARK.md, skill.oms.sig, evals/, references/, scripts/)

- .agents/skills/cuopt-numerical-optimization-formulation/ (SKILL.md, skill-card.md, BENCHMARK.md, skill.oms.sig, evals/)



---



## 5. Projeye Etki Analizi



| Skill | Hangi Ajan Kullanır | Hangi Görevde |

|---|---|---|

| data-designer | 09 Veri Analisti | Veri kalite skoru, ETL test verisi, sentetik veri üretimi |

| skill-card-generator | 07 Yazma Ajanı (Doc Writer) | Wiki kartları, ADR kartları, skill dokümantasyonu |

| cuopt-numerical-optimization-formulation | 11 Performans Ajanı | Scraping optimizasyon, eşleştirme algoritması, NACE atama |

| aiq-research | 02 Araştırmacı | Derin araştırma, kaynak tarama |

| rag-blueprint | 09 Veri Analisti | Bilgi getirme pipeline'ı |

| portfolio-optimization | 11 Performans Ajanı | Optimizasyon problemleri |



---



## 6. Öneriler



- **data-designer** → **Hemen kur** (kuruldu) — Veri kalite ve sentetik veri için kritik

- **skill-card-generator** → **Hemen kur** (kuruldu) — Dokümantasyon otomasyonu için gerekli

- **cuopt-numerical-optimization-formulation** → **Hemen kur** (kuruldu) — Optimizasyon problemleri için

- **aiq-research** → Faz 2'de değerlendir — Araştırma workflow'ları için

- **rag-blueprint** → Faz 2'de değerlendir — RAG pipeline kurulmak istenirse

- **portfolio-optimization** → Şu an kurma — Finansal portföy yönetimi projemizde yok

- **accelerated-computing-cudf** → Şu an kurma — GPU gerektirir, bizde yok



---



## 7. Sonraki Adımlar



1. Kurulan 3 skill'i test etme (bir sonraki sprint)

2. data-designer ile sentetik NACE verisi üretme denemesi

3. skill-card-generator ile mevcut .kilo/skills/ için skill card'ları oluşturma

4. cuopt-numerical-optimization-formulation ile scraping optimizasyon problemi formüle etme

5. Faz 2 için aiq-research ve rag-blueprint değerlendirmesi



---



## İlgili Wiki

- [[04_web_kazima_kaynak_arastirmasi]] — Diğer kaynak araştırması

- [[10_ankara_osb_sentez]] Karar 9 (yeni) — Skill entegrasyon kararı

