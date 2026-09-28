# Hedef Kapsam Kıyası — "Maksimum Kolon" Listesi vs Gerçek Veritabanı

> **Girdi:** `veri kümesi maxmum kolon .txt` (ürün sahibi, 26 veri ailesi, ~130 alan)
> **Ölçüm mandalı:** `python scripts/olcum_kapsam.py` — aşağıdaki her sayı o betiğin çıktısıdır (D-246 madde 1).
> **Tarih:** 2026-09-28 · **Durum:** ÖLÇÜM RAPORU, karar değil.

---

## 0. Tek cümlelik özet

Şema hedefin büyük kısmını **zaten tanımlıyor** (54 tablo, 515 kolon) ama
**41 tablo tamamen boş**. Yani sorun "kolon eksik" değil, **kolonlar dolu değil**.
Hedefe eklenecek yeni alan değil, mevcut boş tabloları besleyecek **kaynak** gerekiyor.

---

## 1. Ölçülen gerçek

| Ölçüt | Değer |
|---|---:|
| Tablo | 54 |
| Kolon | 515 |
| **Boş tablo** | **41** (%76) |
| Veri olan tablo | 13 |
| Firma sayısı (`companies`) | 9412 |
| Ham kayıt (`source_records`) | 14000 |
| Aktif kaynak (`sources`) | 4 |

**Boş tabloların hedef listesindeki karşılığı:**

| Boş tablo | Hedef listesinde karşılığı |
|---|---|
| `company_contacts`, `key_personnel` | Ortaklık ve Yönetim Yapısı / UBO |
| `company_locations` | Şube, üretim tesisi, depo, metraj |
| `company_identifiers`, `company_names`, `company_aliases` | MERSİS, sicil, unvan geçmişi |
| `certifications` | ISO 9001/14001/45001, IATF, CE/TSE, Kapasite Raporu |
| `company_capabilities`, `company_products`, `products` | Makine parkuru, mamul dökümü |
| `company_tech_profile` | CRM/ERP, CMS, bulut, ödeme ağ geçidi |
| `commercial_signals`, `company_signals`, `company_events` | Yatırım, teşvik, ihale, büyüme sinyalleri |
| `company_intelligence_scores`, `momentum_snapshot` | Kredi/risk/momentum skorları |
| `evidence` | Her iddianın kaynak kanıtı (D-245 zorunluluğu) |
| `quarantine_firms` | Karantina (sözleşme K-2) |

---

## 2. Hedef listesinin 26 ailesi — şema karşılığı ve durum

| # | Hedef ailesi | Şema karşılığı | Durum |
|---|---|---|---|
| 1 | Resmi Kimlik ve Kayıtlar | `companies`, `company_identifiers` | **KISMİ** — 9412 firmada 7 geçerli vergi no (sözleşme §0) |
| 2 | Ortaklık / Yönetim / UBO | `company_contacts`, `key_personnel` | BOŞ |
| 3 | İletişim ve Lokasyon | `companies.primary_phone` %87,7 · `primary_email` %42,9 · `adres` %61,6 · `company_locations` BOŞ | KISMİ |
| 4 | Finansal Tablolar | — | **ŞEMA YOK** |
| 5 | Kredi / Borçluluk Riski | `company_intelligence_scores` | BOŞ |
| 6 | Hukuki ve İdari Durum | — | **ŞEMA YOK** |
| 7 | Dış Ticaret ve Gümrük (GTİP, konşimento) | — | **ŞEMA YOK** |
| 8 | Tedarik Zinciri / Müşteriler | — | **ŞEMA YOK** |
| 9 | Kamu İhaleleri (KİK, DMO, MSB) | `commercial_signals` | BOŞ (VERI-02 bloke) |
| 10 | Teknolojik Altyapı | `company_tech_profile` | BOŞ |
| 11 | Siber Güvenlik Profillemesi | — | **ŞEMA YOK** |
| 12 | İnsan Kaynakları / İstihdam | `companies.employee_count` **%0** · `employee_count_estimate` %100 (tahmin) | KISMİ — tahmin var, gerçek yok |
| 13 | İşe Alım / Büyüme | `job_postings` **8 satır** · `v_company_job_summary` | KISMİ |
| 14 | Fikri ve Sınai Mülkiyet | — | **ŞEMA YOK** |
| 15 | Gayrimenkul ve Varlık | — | **ŞEMA YOK** |
| 16 | Dijital Pazarlama / Medya | `companies.social_media_score` %100 (skor, veri değil) | KISMİ |
| 17 | Web Trafiği ve Analitiği | — | **ŞEMA YOK** |
| 18 | Müşteri Algısı ve İtibar | — | **ŞEMA YOK** |
| 19 | Yatırım ve Teşvik Geçmişi | `commercial_signals` | BOŞ |
| 20 | Sektörel Belgeler / Uyumluluk | `certifications` | BOŞ |
| 21 | Üretim Kapasitesi / Fabrika | `company_capabilities` | BOŞ |
| 22 | Sanayi Sicil Belgesi | `company_identifiers` | BOŞ |
| 23 | Üretim Alanı / OSB / Metraj | `companies.is_osb_member` %100 · `osb_id` %87,1 · `osb_parsel` **%0,2** | KISMİ |
| 24 | Makine ve Ekipman Envanteri | `company_capabilities` | BOŞ |
| 25 | Enerji ve Tüketim Profili | — | **ŞEMA YOK** |
| 26 | İSG / Tehlike Sınıfı / Sendika | — | **ŞEMA YOK** |

**Sayım: 26 aileden 4'ü kısmen dolu, 9'u şemada var ama boş, 13'ünün şeması yok.**

---

## 3. Şu anda gerçekten satılabilir olan alanlar

D-245 (doluluk ≠ geçerlilik) uygulanarak, `companies` tablosunda **kanıtlı** alanlar:

| Alan | Doluluk | Uyarı |
|---|---:|---|
| `legal_name` | %100 | — |
| `trade_name` | %100 | — |
| `primary_phone` | %87,7 | biçim doğrulanmadı (OLCUM-ALAN-01) |
| `nace_code` | %88,1 | sektör sayacı kirli (VERI-NACE-TEMIZ-01) |
| `osb_id` | %87,1 | ostim içinde 102 ASO kaydı (VERI-KAYNAK-SIZINTI-01) |
| `adres` | %61,6 | ayrıştırılmamış serbest metin |
| `website_domain` | %57,3 | ~2660'ı haksız puan üretiyor (KALITE-PUAN-01) |
| `primary_email` | %42,9 | %94,8'i doğrulanmış (`email_validated_at`) |

### Tuzak: skor kolonları %100 dolu ama bir kısmı tek değerden oluşuyor

Ölçüm mandalı: `python scripts/_olcum_skor.py`

| Kolon | Farklı değer | En çok geçen |
|---|---:|---|
| `source_diversity_score` | **1** | `0` × 9412 (%100) |
| `job_postings_score` | **1** | `0` × 9412 (%100) |
| `employee_count_score` | **1** | `0` × 9412 (%100) |
| `job_postings_count` | **1** | `0` × 9412 (%100) |
| `employee_count_estimate` | **1** | `0` × 9412 (%100) |
| `social_media_score` | 2 | `5` × 4994 (%53,1) |
| `data_freshness_score` | 2 | `8` × 8193 (%87,0) |
| `phone_format_score` | 3 | `2` × 7770 (%82,6) |
| `email_validity_score` | 3 | `0` × 5199 (%55,2) |
| `data_quality_score` | 15 | `60.00` × 2423 (%25,7) |

**Kanıtlanan:** 5 kolon tek bir değerden (`0`) oluşuyor — hiçbir firmayı
diğerinden ayırmıyor. `%100 dolu` görünüyorlar ama **sıfır bilgi taşıyorlar**.
Bu D-245'in tam karşılığı: doluluk ≠ bilgi.

**Sonuç:** `data_quality_score` (15 farklı değer, gerçekten hesaplanıyor)
aslında **9 sinyalin 4'ü** üzerinden üretiliyor; 5 sinyal sabit `0`.
Yani kalite puanı 9 boyutluymuş gibi sunulan 4 boyutlu bir ölçüm.

> **KALITE-SKOR-01 (YENİ, açık):** 5 skor kolonu tek değerden oluşuyor
> (`source_diversity`, `job_postings`, `employee_count` × 2, `job_postings_count`).
> Seçenekler: (a) besleyen veri gelene kadar NULL'a çek, (b) `data_quality_score`
> ağırlıklarından çıkar ve puanı 4 sinyal üzerinden ilan et. Şu hali
> müşteriye "9 sinyalli kalite puanı" olarak sunulamaz.

---

## 4. Hedefe ulaşmanın gerçek maliyeti (şema değil, kaynak)

Hedef listesindeki 13 "şeması yok" aile için gereken dış kaynaklar:

| Kaynak | Hangi aileleri açar | Erişim |
|---|---|---|
| TOBB Kapasite Raporu | 21, 22, 24 | üyelik/anlaşma |
| Sanayi ve Teknoloji Bakanlığı | 19, 22, 25 | anlaşma |
| KİK / EKAP | 9 | kamuya açık (kazınabilir) |
| Gümrük veri sağlayıcısı (konşimento) | 7, 8 | **ücretli, pahalı** |
| TÜRKPATENT | 14 | kamuya açık (kazınabilir) |
| Ticaret Sicil Gazetesi | 1, 2, 6 | kamuya açık (kazınabilir) |
| GİB mükellef sorgusu | 1 | GIB-MUKELLEF-01 bloke |
| Google Business / Şikayetvar | 18 | kazınabilir, ToS riski |
| Web teknoloji parmak izi | 10, 11, 17 | kendi kazıyıcımız |

**Kendi gücümüzle açılabilecekler (dış anlaşma gerekmez):** 9 (KİK), 14 (TÜRKPATENT),
1+2+6 (Ticaret Sicil Gazetesi), 10+11 (teknoloji/siber profil), 18 (itibar).
**Para veya anlaşma isteyenler:** 4 (finansal), 5 (kredi), 7+8 (gümrük), 21-25 (TOBB/Bakanlık).

---

## 5. Eleştiri — bu liste olduğu gibi hedef alınamaz

1. **Sıralama yok.** 130 alanın hepsi eşit değil. `legal_name` olmadan ürün yok;
   `sendikal durum` olmadan ürün satılır. Liste öncelik içermiyor.
2. **KVKK sınırı çizilmemiş.** Aile 2 (UBO, hissedar kimlikleri) doğrudan kişisel veri.
   KVKK-TCKN-02 hâlâ hukuki görüş bekliyor; UBO o kararın kapsamını genişletir.
3. **Kaynağı olmayan alan hedef olamaz.** "Makine parkuru marka bazlı döküm"
   TOBB kapasite raporu olmadan **ancak uydurulabilir**. D-245 bunu yasaklar.
4. **Mevcut 41 boş tablo yeni kolon eklemeden önce doldurulmalı.**
   Yeni alan eklemek boşluğu 515'ten 700'e çıkarır, dolu kolon sayısını değiştirmez.
5. **Skor katmanı şu anda yalan söylüyor** (§3 tuzak). Yeni veri ailesi eklemek
   bu yalanı büyütür: her yeni aile için bir "score" kolonu daha %100 dolu görünür.

---

## 6. Önerilen sıra (ürün sahibi onayı bekliyor)

| Sıra | İş | Gerekçe |
|---|---|---|
| 0 | KALITE-SKOR-01 kapat | Ölçüm aracı yalan söylerken hedef büyütülemez |
| 1 | SEMA-VKN-01 + K-1 (mevcut kuyruk) | Kimlik alanı ürünün çapası |
| 2 | Ticaret Sicil Gazetesi kazıyıcı | Aile 1+2+6'yı birden açar, bedava, kamuya açık |
| 3 | KİK/EKAP kazıyıcı | Aile 9, bedava, satış argümanı güçlü (ihale sinyali) |
| 4 | `certifications` + TÜRKPATENT | Aile 14+20, bedava |
| 5 | TOBB / Bakanlık anlaşması | Aile 21-25, **para/anlaşma kararı ürün sahibinde** |
| 6 | Gümrük sağlayıcı | Aile 7+8, **en pahalı, en son** |

---

## İlgili Nodlar

- [[VERI_KALITE_SOZLESMESI]]
- [[AGENTS]]
