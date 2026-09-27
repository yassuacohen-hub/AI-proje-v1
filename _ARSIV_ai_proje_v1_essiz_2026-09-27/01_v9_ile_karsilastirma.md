
╔══════════════════════════════════════════════════════════════════════════════╗
║     V9 MASTER CONTEXT ↔ COMPANY MASTER V1.0 KARŞILAŞTIRMA & ÖNERİLER        ║
║                         2026-08-30 | Ankara B2B Intelligence                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

Bağlantılar: [[README]] · [[01_sirket_master_ana_belgesi]] · [[01_versiyon_6_baglam_dokumani]] · [[01_versiyon_7_baglam_dokumani]] · [[01_versiyon_8_baglam_dokumani]] · [[01_versiyon_9_baglam_dokumani]]

┌──────────────────────────────────────────────────────────────────────────────┐
│ 1. BÜYÜK RESİM KARŞILAŞTIRMASI                                               │
└──────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┬──────────────────────────────┬──────────────────────────┐
│ Boyut               │ V9 MASTER CONTEXT            │ COMPANY MASTER V1.0      │
├─────────────────────┼──────────────────────────────┼──────────────────────────┤
│ Kapsam              │ 6+1 Katman (Full Stack)      │ Sadece Company Master    │
│ Hedef               │ B2B Intelligence Platform    │ B2B Veri Platformu       │
│ Zaman Çizelgesi     │ Faz 1→2→3 (18 ay)            │ MVP (tek faz)            │
│ Şirket Hedefi       │ 10.000+ (ölçeklenebilir)     │ 8.000-10.000 (Ankara)    │
│ Sektör              │ NACE C öncelikli ama açık    │ Sadece NACE C (İmalat)   │
│ Veri Kaynakları     │ 6+ kaynak (EKAP, iş ilanı,   │ 4 kaynak (GİB, OSB, Oda, │
│                     │ GİB, ERP, TOBB, haber)       │ Web sitesi)              │
│ Tech Stack          │ PostgreSQL+ChromaDB+Neo4j+   │ PostgreSQL+ES/Meilisearch│
│                     │ Redis+Python                 │ +Python                  │
│ Intelligence        │ Var (6 katman)               │ Yok (sadece veri havuzu) │
│ Monetizasyon        │ Detaylı (8 gelir kalemi)     │ Yok                      │
│ AI Agent            │ Var (WhatsApp, System Prompt)│ Yok                      │
│ Test Framework      │ Var (26+ senaryo)            │ Yok                      │
│ Learning Engine     │ Var (Shadow, Kalibrasyon)    │ Yok                      │
└─────────────────────┴──────────────────────────────┴──────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 2. TEMEL UYUMLULUKLAR (✅ Her İkisi de Kabul Ediyor)                        │
└──────────────────────────────────────────────────────────────────────────────┘

  ✅ Ankara odaklı pilot
  ✅ NACE C grubu (İmalat) öncelikli
  ✅ PostgreSQL ana veritabanı
  ✅ KVKK uyumlu, kamuya açık veri
  ✅ OSB'ler kaynak olarak kullanılıyor
  ✅ Entity Resolution / Fuzzy Matching
  ✅ UNKNOWN prensibi (kanıtsız veri uydurma)
  ✅ Eksik alan tahmin edilmez
  ✅ Çelişki silinmez, güven skoru ile yönetilir
  ✅ Veri kalitesi boyutları (Accuracy, Completeness, Freshness...)
  ✅ Ham veri saklanır (source_records)
  ✅ "Önce şirketi doğru tanı" prensibi
  ✅ VKN benzersiz kimlik/doğrulama alanı
  ✅ MVP önceliklendirme (P0/P1/P2)
  ✅ ETL pipeline: Source → Raw → Normalize → Validate → Master

┌──────────────────────────────────────────────────────────────────────────────┐
│ 3. KRİTİK ÇELİŞKİLER (⚠️ Farklı Kararlar)                                   │
└──────────────────────────────────────────────────────────────────────────────┘

┌────┬────────────────────────┬────────────────────────┬────────────────────────┐
│ #  │ V9 Kararı              │ CM V1.0 Kararı         │ Değerlendirme          │
├────┼────────────────────────┼────────────────────────┼────────────────────────┤
│ C1 │ UUID PK, VKN ayrı      │ VKN = Primary Key      │ CM: Basit, hızlı       │
│    │ alan                   │                        │ V9: Esnek, uluslararası│
│    │                        │                        │                        │
│    │ V9: "VKN'si olmayan    │ CM: "VKN zorunlu,      │ ⚠️ ORTA ÇELİŞKİ        │
│    │ kaynaklar desteklenir" │ uluslararası sonrası"  │                        │
├────┼────────────────────────┼────────────────────────┼────────────────────────┤
│ C2 │ PostgreSQL FTS yeterli │ Elasticsearch/         │ CM: Daha iyi arama     │
│    │ (MVP'de ES zorunlu     │ Meilisearch zorunlu    │ performansı            │
│    │ değil)                 │                        │ V9: Daha az karmaşıklık│
│    │                        │                        │                        │
│    │ V9: "İlk günden ES     │ CM: "Anlık filtreleme  │ 🟡 DÜŞÜK ÇELİŞKİ       │
│    │ zorunlu değil"         │ için ES gerekli"       │                        │
├────┼────────────────────────┼────────────────────────┼────────────────────────┤
│ C3 │ 6+ veri kaynağı        │ 4 veri kaynağı         │ CM: Daha odaklı        │
│    │ (EKAP, iş ilanı,       │ (GİB, OSB, Oda, Web)   │ V9: Daha kapsamlı      │
│    │ GİB, ERP, TOBB, haber) │                        │                        │
│    │                        │                        │ 🟢 UYUMLU (scope farkı)│
├────┼────────────────────────┼────────────────────────┼────────────────────────┤
│ C4 │ ChromaDB (vektör) +    │ Yok (sadece            │ CM: Daha basit         │
│    │ Neo4j (graf) + Redis   │ PostgreSQL+ES)         │ V9: Daha güçlü         │
│    │                        │                        │                        │
│    │ V9: "Vektör ve graf    │ CM: "Basit arama ve    │ 🟡 DÜŞÜK ÇELİŞKİ       │
│    │ intelligence için"     │ liste yeterli"         │ (MVP scope farkı)      │
├────┼────────────────────────┼────────────────────────┼────────────────────────┤
│ C5 │ Web scraping (dikkatli)│ Google Custom Search + │ CM: Daha agresif       │
│    │ "Yasal sınırlar içinde"│ web scraping (RegEx)   │ V9: Daha temkinli      │
│    │                        │                        │                        │
│    │ V9: "robots.txt, KVKK, │ CM: "Web sitesi iletişim│ 🔴 YÜKSEK ÇELİŞKİ      │
│    │ rate limiting"         │ sayfalarını tara"      │ (Yasal risk)           │
├────┼────────────────────────┼────────────────────────┼────────────────────────┤
│ C6 │ Intelligence katmanları│ Yok. Sadece veri       │ CM: Daha gerçekçi MVP  │
│    │ (Market→Customer→      │ listeleme ve arama     │ V9: Daha vizyoner      │
│    │ Opportunity→Decision→  │                        │                        │
│    │ Portfolio→Learning)    │                        │ 🟢 TAMAMLANMAYAN       │
│    │                        │                        │    (V9 = sonraki faz)  │
├────┼────────────────────────┼────────────────────────┼────────────────────────┤
│ C7 │ Monetizasyon var       │ Yok                    │ CM: Önce ürün, sonra   │
│    │ (8 gelir kalemi)       │                        │ para                   │
│    │                        │                        │ V9: Erken monetizasyon │
│    │                        │                        │ 🟢 UYUMLU (faz farkı)  │
├────┼────────────────────────┼────────────────────────┼────────────────────────┤
│ C8 │ 19 tablo (companies,   │ 19 tablo (aynı isimler │ ✅ TAMAMEN UYUMLU      │
│    │ locations, industries, │ + aynı yapı)           │ CM, V9'un Company      │
│    │ products, contacts...) │                        │ Master katmanını        │
│    │                        │                        │ detaylandırıyor         │
└────┴────────────────────────┴────────────────────────┴────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ 4. COMPANY MASTER V1.0'IN V9'A GÖRE AVANTAJLARI                              │
└──────────────────────────────────────────────────────────────────────────────┘

  🟢 ÇOK DAHA PRAGMATİK: Sadece "şirketleri topla, listele, ara" — yapılabilir
  🟢 DAHA GERÇEKÇİ SCOPE: 8-10K şirket, tek şehir, tek sektör — başarılabilir
  🟢 DAHA AZ TEKNOLOJİK KARMAŞIKLIK: PostgreSQL + ES — 2 teknoloji vs V9'un 4'ü
  🟢 HIZLI MVP: İlk veri 1-2 haftada toplanabilir (GİB listesi hazır)
  🟢 NET KPI'LAR: Coverage, Accuracy, Duplicate Rate, Freshness — ölçülebilir
  🟢 DETAYLI ŞEMA: 19 tablo, her alanın tipi, açıklaması, FK ilişkileri net
  🟢 ETL PIPELINE: Source → Raw → Normalize → Validate → Master net tanımlı
  🟢 P0/P1/P2 ÖNCELİKLEME: Zorunlu/Değerli/İntelligence hazırlığı net ayrım
  🟢 MİMARİ SINIR: "Bu katman şunları yapmaz" — net sorumluluk ayrımı

┌──────────────────────────────────────────────────────────────────────────────┐
│ 5. V9'UN COMPANY MASTER V1.0'A GÖRE AVANTAJLARI                              │
└──────────────────────────────────────────────────────────────────────────────┘

  🟢 VİZYON: Sadece liste değil, intelligence platformu
  🟢 ÖĞRENME MOTORU: Shadow Model, Kalibrasyon, Outcome Ledger
  🟢 TEST ÇERÇEVESİ: 26+ adversarial senaryo, simülasyon
  🟢 MONETİZASYON: 8 gelir kalemi, erken para kazanma planı
  🟢 AI AGENT: WhatsApp entegrasyonu, itiraz yönetimi
  🟢 GÜVENLİK: mTLS, OAuth2, Zero-Knowledge encryption
  🟢 ÇEŞİTLİ KAYNAKLAR: EKAP, iş ilanları, ERP, TOBB — zengin sinyal
  🟢 PORTFÖY OPTİMİZASYONU: 10K eşleşmeden 20 aksiyon seçme
  🟢 KARAR MOTORU: CONTACT_NOW vs INVESTIGATE vs MONITOR — net aksiyon
  🟢 UI/UX: ASCII mockup'lar, dashboard tasarımları

┌──────────────────────────────────────────────────────────────────────────────┐
│ 6. BAŞLANGIÇ İÇİN 3 ALTERNATİF STRATEJİ                                      │
└──────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║ ALTERNATİF A: "Company Master First" (ÖNERİLEN)                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FAZ 0 (Ay 0-1): Company Master V1.0'ı implemente et                        ║
║  ├── GİB e-Fatura listesini çek (Ankara, NACE C)                            ║
║  ├── PostgreSQL şemasını kur (VKN = PK, UUID geçiş planı)                   ║
║  ├── OSB verilerini ekle (Ostim, İvedik, ASO)                               ║
║  ├── Basit web arayüzü (arama, filtreleme, profil)                          ║
║  └── HEDEF: 5.000 şirket, %80 alan doluluğu                                 ║
║                                                                              ║
║  FAZ 1 (Ay 2-3): V9 Intelligence Layer'ı ekle                               ║
║  ├── EKAP ihale verisi (sinyal kaynağı)                                     ║
║  ├── Job posting scraper (NLP + NER)                                        ║
║  ├── ChromaDB (vektör) + Neo4j (graf) ekle                                  ║
║  ├── B2B Findeks skorlaması başlat                                          ║
║  └── HEDEF: 8.000 şirket, ilk sinyaller üret                                ║
║                                                                              ║
║  FAZ 2 (Ay 4-6): V9 Opportunity + Decision Engine                           ║
║  ├── TOPSIS eşleştirme motoru                                               ║
║  ├── 3-Score System (Need/Fit/Timing)                                       ║
║  ├── Decision Matrix (CONTACT_NOW/INVESTIGATE/MONITOR)                      ║
║  ├── Portfolio Engine (10K→20 optimizasyon)                                 ║
║  └── HEDEF: İlk 100 fırsat üret, 10 kapanış                                 ║
║                                                                              ║
║  FAZ 3 (Ay 7-12): V9 Full Stack + Monetizasyon                              ║
║  ├── WhatsApp AI Agent                                                      ║
║  ├── ERP entegrasyonu (Logo, CANIAS)                                        ║
║  ├── Monetizasyon (kredi sistemi, abonelik)                                 ║
║  ├── Shadow Model + Kalibrasyon                                             ║
║  └── HEDEF: İlk gelir, self-sustaining                                      ║
║                                                                              ║
║  AVANTAJ: Pragmatik, hızlı MVP, riske dayanıklı                            ║
║  DEZAVANTAJ: İlk 1-2 ay "sadece liste" — gelir yok                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║ ALTERNATİF B: "V9 Lite" (Hızlı Intelligence)                                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  FAZ 1 (Ay 0-2): Hafifletilmiş V9                                           ║
║  ├── Company Master (sadece P0 alanlar: unvan, VKN, adres, telefon, web)    ║
║  ├── EKAP + Job posting scraper (2 kaynak)                                  ║
║  ├── PostgreSQL + ChromaDB (sadece 2 DB)                                    ║
║  ├── Basit TOPSIS (sabit ağırlıklar, kalibrasyon yok)                       ║
║  ├── Basit arayüz: "Hot Radar" (yüksek skorlu 20 fırsat)                    ║
║  └── HEDEF: 3.000 şirket, 50 fırsat/hafta                                   ║
║                                                                              ║
║  FAZ 2 (Ay 3-6): Derinleştir                                                ║
║  ├── OSB verileri, TOBB OCR, GİB e-Fatura                                   ║
║  ├── Neo4j graf, Redis cache                                                ║
║  ├── Kalibrasyon motoru başlat                                              ║
║  └── Monetizasyon: Credit Pack (750 TRY/50 kredi)                           ║
║                                                                              ║
║  AVANTAJ: Hızlı "wow" faktörü, erken fırsat üretimi                        ║
║  DEZAVANTAJ: Şema değişikliği riski, veri kalitesi düşük olabilir           ║
╚══════════════════════════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════════════════════════╗
║ ALTERNATİF C: "Hybrid" (ÖNERİLEN — En Dengeli)                               ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  PARALEL İKİ SPİRINT:                                                       ║
║                                                                              ║
║  TAKIM A — Veri (Company Master odaklı):                                    ║
║  Sprint 1-2: GİB + OSB verisi → PostgreSQL                                  ║
║  Sprint 3-4: Web sitesi scraping (dikkatli) → zenginleştirme               ║
║  Sprint 5-6: Entity resolution, duplicate temizliği                         ║
║                                                                              ║
║  TAKIM B — Intelligence (V9 odaklı):                                        ║
║  Sprint 1-2: EKAP scraper + Job posting NLP                                 ║
║  Sprint 3-4: ChromaDB kurulumu + vektörleştirme                            ║
║  Sprint 5-6: TOPSIS motoru + basit skorlama                                ║
║                                                                              ║
║  BİRLEŞTİRME (Sprint 7):                                                   ║
║  ├── Takım A'nın verisi + Takım B'nin sinyalleri = Birleşik platform        ║
║  ├── Arayüz: "Şirket Ara" + "Fırsat Radar" iki sekme                        ║
║  └── HEDEF: 6.000 şirket, 30 fırsat/hafta, %70 doğruluk                    ║
║                                                                              ║
║  AVANTAJ: Paralel ilerleme, risk dağılımı, hızlı sonuç                      ║
║  DEZAVANTAJ: İki takım koordinasyonu gerekli, daha fazla kaynak             ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ 7. KRİTİK KARARLAR (V9 ↔ CM V1.0 Uyumlandırması)                             │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ KARAR 1: VKN PK mi, UUID PK mi?                                              │
└──────────────────────────────────────────────────────────────────────────────┘

  CM V1.0: VKN = Primary Key
  V9:      UUID = Primary Key, VKN = UNIQUE INDEX

  ÖNERİ (Hybrid):
  ├── MVP'de (Faz 0): VKN = PK (hızlı başlangıç, GİB verisi zaten VKN'li)
  ├── Faz 1'de: UUID kolonu ekle, VKN = UNIQUE + NOT NULL
  ├── Faz 2'de: UUID = PK, VKN = FK → companies_identifiers tablosuna taşı
  └── Geçiş: ALTER TABLE ile yapılabilir, veri kaybı olmaz

  NEDEN: GİB verisi zaten VKN'li, başlangıçta UUID ek karmaşıklığı
         Ama uluslararası genişleme ve VKN'siz kaynaklar için UUID şart

┌──────────────────────────────────────────────────────────────────────────────┐
│ KARAR 2: Elasticsearch şart mı?                                              │
└──────────────────────────────────────────────────────────────────────────────┘

  CM V1.0: ES/Meilisearch zorunlu
  V9:      PostgreSQL FTS yeterli (MVP'de)

  ÖNERİ (Aşamalı):
  ├── Faz 0: PostgreSQL Full Text Search (tsvector, GIN index)
  │           └── 10K şirket için performans yeterli (<100ms)
  ├── Faz 1: Meilisearch ekle (daha hafif, açık kaynak, kolay kurulum)
  │           └── Faceted search, typo tolerance, instant search
  └── Faz 2: Elasticsearch (ölçek için, aggregation'lar için)

  NEDEN: Meilisearch ES'den daha hafif, daha kolay, MVP için yeterli
         PostgreSQL FTS ile başla, gerektiğinde geç

┌──────────────────────────────────────────────────────────────────────────────┐
│ KARAR 3: Web Scraping — Nasıl, Ne Kadar?                                     │
└──────────────────────────────────────────────────────────────────────────────┘

  CM V1.0: "Google Custom Search + web sitesi iletişim sayfalarını tara"
  V9:      "Yasal sınırlar içinde, robots.txt, rate limiting"

  ÖNERİ (KVKK-Safe Scraping Protocol):
  ├── ✅ YAPILABİLİR:
  │   ├── robots.txt kontrolü (scraping yasak mı?)
  │   ├── Rate limiting: max 1 request/5 saniye/site
  │   ├── Sadece KURUMSAL veri: info@, telefon, adres (kişisel değil)
  │   ├── Sadece kendi web siteleri (3. parti siteler değil)
  │   └── User-Agent: "AnkaraB2B-Bot/1.0 (contact@example.com)"
  ├── ⚠️ DİKKAT GEREKEN:
  │   ├── LinkedIn scraping → YASAK (robots.txt + kullanım şartları)
  │   ├── Kariyer.net scraping → YASAK (ücretli API var)
  │   ├── Google SERP scraping → YASAK (Terms of Service)
  │   └── 3. parti dizin siteleri → KVKK riski
  └── ❌ YAPILMAYACAK:
      ├── Kişisel e-posta (ahmet@şirket.com)
      ├── Cep telefonu (555 ile başlayan)
      ├── LinkedIn profil verisi
      └── Paralı API'ların ücretsiz scraping'i

  ALTERNATİF (Daha Güvenli):
  ├── Şirketlerden OPT-IN toplama: "Verinizi güncelleyin" formu
  ├── OSB'lerden resmi liste talebi (çoğu OSB üye listesini paylaşır)
  ├── Ticaret Odası üye listesi (ücretli ama yasal)
  └── GİB e-Fatura (zaten kamuya açık)

┌──────────────────────────────────────────────────────────────────────────────┐
│ KARAR 4: ChromaDB + Neo4j — MVP'de Şart mı?                                  │
└──────────────────────────────────────────────────────────────────────────────┘

  CM V1.0: Yok (sadece PostgreSQL+ES)
  V9:      Var (ChromaDB vektör, Neo4j graf, Redis cache)

  ÖNERİ (Fazlandırılmış):
  ├── Faz 0 (Company Master): PostgreSQL + Meilisearch
  │   └── Yeterli: arama, filtreleme, liste, profil
  ├── Faz 1 (Signal Layer): + ChromaDB (1536-dim vektörler)
  │   └── Gerekli: ürün kabiliyet eşleştirme, benzer şirket bulma
  └── Faz 2 (Graph Layer): + Neo4j (tedarik zinciri, risk yayılımı)
      └── Gerekli: tedarikçi-tedarikçi ilişkileri, symbiosis

  NEDEN: Her fazda bir DB eklemek maliyet ve karmaşıklık
         Ama her fazın ihtiyacı farklı — aşamalı ekleme en mantıklı

┌──────────────────────────────────────────────────────────────────────────────┐
│ 8. BAŞLANGIÇ İÇİN NET EYLEM PLANI (Alternatif A — Önerilen)                  │
└──────────────────────────────────────────────────────────────────────────────┘

  HAFTA 1-2: VERİ TOPLAMA
  ├── [ ] GİB e-Fatura mükellef listesini indir (efatura.gov.tr)
  ├── [ ] Ankara + NACE C filtresi uygula (~15.000 ham kayıt)
  ├── [ ] PostgreSQL şemasını kur (CM V1.0 tabloları)
  ├── [ ] Ham veriyi `source_records` tablosuna yükle
  └── [ ] İlk temizlik: boş VKN'ler, duplicate kontrolü

  HAFTA 3-4: ZENGİNLEŞTİRME
  ├── [ ] OSB üye listelerini topla (Ostim, İvedik, ASO)
  ├── [ ] OSB verisi ile GİB verisini eşleştir (VKN üzerinden)
  ├── [ ] Şirket web sitelerini bul (manuel + Google arama)
  ├── [ ] İletişim bilgilerini topla (web sitesi üzerinden, dikkatli)
  └── [ ] Entity resolution: Fuzzy matching, 70+ eşik, manual review

  HAFTA 5-6: ARAYÜZ
  ├── [ ] Basit web arayüzü: arama, filtreleme (ilçe, sektör, OSB)
  ├── [ ] Şirket profil sayfası: unvan, adres, telefon, web, sektör
  ├── [ ] PostgreSQL FTS ile arama (tsvector + GIN index)
  └── [ ] Admin paneli: veri kalitesi dashboard'u

  HAFTA 7-8: KALİTE + DOĞRULAMA
  ├── [ ] Veri kalitesi skoru hesapla (her şirket için)
  ├── [ ] Rastgele 100 şirketi doğrula (telefonla arama)
  ├── [ ] Duplicate rate ölçümü
  ├── [ ] Coverage hesapla: Ankara'daki NACE C şirketlerinin %kaçı?
  └── [ ] HEDEF: 5.000+ şirket, %80 alan doluluğu, %5 duplicate

  SONRA (Ay 2+): V9 Intelligence Katmanları
  ├── [ ] EKAP scraper kur
  ├── [ ] Job posting NLP pipeline
  ├── [ ] ChromaDB ekle (vektörleştirme)
  ├── [ ] Basit TOPSIS (sabit ağırlıklar)
  └── [ ] "Hot Radar" sayfası: yüksek skorlu 20 fırsat

┌──────────────────────────────────────────────────────────────────────────────┐
│ 9. SONUÇ: HANGİSİ DAHA İYİ?                                                  │
└──────────────────────────────────────────────────────────────────────────────┘

  Company Master V1.0 = DAHA İYİ BAŞLANGIÇ DOKÜMANI
  ├── Pragmatik, gerçekçi, hızlı MVP
  ├── Detaylı şema, net ETL, ölçülebilir KPI'lar
  ├── "Önce şirketi tanı" — temel prensip doğru
  └── AMA: Sadece veri havuzu, intelligence yok

  V9 = DAHA İYİ VİZYON DOKÜMANI
  ├── Kapsamlı, öğrenen, monetize edilebilir platform
  ├── Test edilmiş, simülasyon doğrulanmış
  ├── 6+1 katman, Shadow Model, Kalibrasyon
  └── AMA: Karmaşık, 18 ay timeline, daha fazla kaynak

  ÖNERİ: İKİSİNİ BİRLEŞTİR
  ├── Company Master V1.0 = Faz 0 implementasyon detayı
  ├── V9 = Uzun vadeli yol haritası ve vizyon
  └── Birlikte: Pragmatik başlangıç + Vizyoner hedef

═══════════════════════════════════════════════════════════════════════════════

  "Önce şirketi doğru tanı. Sonra değişimini anla. Sonra ihtiyacı çıkar.
   Sonra müşterinin ürünüyle eşleştir. Sonra aksiyon öner. Sonra öğren."

  Company Master V1.0 → İlk 2 adımı (tanı + anla) mükemmel yapar.
  V9 → Son 4 adımı (ihtiyaç + eşleştir + aksiyon + öğren) ekler.

  Birlikte: TAM B2B INTELLIGENCE PLATFORM.

═══════════════════════════════════════════════════════════════════════════════
