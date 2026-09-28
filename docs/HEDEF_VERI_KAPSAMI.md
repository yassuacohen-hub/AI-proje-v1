# Hedef Veri Kapsamı — Maksimum İşletme Dosyası

> **Bu belge bir yol haritası değil, bir aynadır.**
> Sol sütun ürün sahibinin tanımladığı **hedef**; sağ sütun **bugün ölçülen durum**.
> "Şunu yapacağız" demez; "şunu istiyoruz, bugün buradayız" der.

- **Kaynak:** ürün sahibinin hedef kapsam metni (dış kökteki iki dosya, D-259'da bu belgeye taşındı ve silindi)
- **İçerik:** aynen korundu. Yalnızca biçim (başlık/liste) verildi, tek kelime eklenmedi/çıkarılmadı.
- **Ölçüm tarihi:** 2026-09-28 · **Firma evreni:** 9412 (Ankara OSB)
- **Ölçüm kaynağı:** canlı şema (`information_schema` + satır sayımı) ve D-257 kaynak erişim ölçümü

## Durum etiketleri

| Etiket | Anlamı |
|---|---|
| **VAR** | Şemada kolon var **ve** dolu — kaç firmada dolu olduğu yazılır |
| **BOŞ** | Şemada kolon/tablo var, **veri yok** (0 satır / 0 dolu) |
| **YOK** | Şemada karşılığı hiç yok |
| **KAPALI** | Kaynak ölçüldü, erişilemiyor (D-257) — veri yokluğu bizim eksiğimiz değil, kapının kapalı olması |

> D-249 gereği: **"veri yok" ≠ "0 puan".** BOŞ/YOK/KAPALI olan bir alan,
> firmanın o niteliğe sahip olmadığı anlamına gelmez; bizim onu ölçmediğimiz anlamına gelir.

---

## Özet sayım

| Durum | Öbek |
|---|---|
| VAR (kısmen veya tam dolu) | 5 |
| BOŞ (şemada var, veri yok) | 4 |
| KAPALI (kaynak erişilemez — D-257) | 4 |
| YOK (şemada karşılık yok) | 22 |
| **Toplam öbek** | **35** |

Şema tarafı: **52 public tablo, 43'ü tamamen boş (0 satır).** `companies` 50 kolon /
9412 satır; kolonların 11'i %0 dolu.

---

## 1. Temel Kurumsal Profil

### Resmi Kimlik ve Kayıtlar
> Şirket unvanı, vergi dairesi/numarası, MERSİS no, ticaret sicil memurluğu, oda sicil no, kuruluş tarihi, yasal şirket türü, aktiflik statüsü, sermaye tutarı ve ana sözleşme değişiklikleri.

**KISMEN VAR / KAPALI** — unvan `legal_name` 9412 (%100), statü `status` 9412 (%100).
Vergi no `tax_number` yalnızca **5 firmada** (%0,1). `mersis_number`, `establishment_date`,
`company_type`, `tax_office`, `trade_registry_number`, `trade_registry_office` kolonları
**şemada var, %0 dolu**. Sermaye ve ana sözleşme için şemada karşılık **YOK**.
MERSİS ve Ticaret Sicil Gazetesi **KAPALI** (D-257: MERSİS sorgu ekranı 404, TSG captcha+üyelik).

### Ortaklık ve Yönetim Yapısı
> Hissedarlar, ortaklık payları, yönetim kurulu üyeleri, imza yetkilileri, genel müdürler, kilit yöneticiler, intifa senedi sahipleri ve nihai faydalanıcı (UBO) kimlikleri.

**BOŞ** — `key_personnel` tablosu şemada var, **0 satır**. Ortaklık payı / UBO için
ayrı karşılık **YOK**. Kaynağı (TSG) **KAPALI**.

### İletişim ve Coğrafi Lokasyon
> Genel merkez adresi, şubeler, üretim tesisleri, depolar, irtibat ofisleri, KEP (Kayıtlı Elektronik Posta) adresi, resmi e-postalar, sabit/mobil telefonlar ve faks numaraları.

**VAR** — `address` 5798 (%61,6), `primary_phone` 8251 (%87,7),
`primary_email` 4038 (%42,9), `website_domain` 5446 (%57,9), `osb_id` 8196 (%87,1).
Şube/tesis/depo ayrımı için `company_locations` tablosu var ama **0 satır**.
KEP ve faks için karşılık **YOK**.

### Finansal ve Mali Tablolar
> Yıllık/çeyreklik bilançolar, gelir tabloları, nakit akış tabloları, özkaynak değişim tabloları, finansal rasyolar, likidite oranları, kârlılık göstergeleri ve bağımsız denetim raporları.

**YOK** — şemada hiçbir karşılığı yok.

### Kredi ve Borçluluk Riski
> Ticari kredi notu, banka limit/risk doluluk oranları, protestolu senetler, arkası yazılan çekler, banka borç yapılandırmaları ve piyasa ödeme vadesi alışkanlıkları.

**YOK** — şemada karşılığı yok.

### Hukuki ve İdari Durum
> Devam eden veya geçmiş hukuk/ticaret davaları, icra takipleri, iflas, konkordato, tasfiye süreçleri, vergi cezaları, rekabet kurumu soruşturmaları ve idari para cezaları.

**YOK** — şemada karşılığı yok.

### Dış Ticaret ve Gümrük
> Konşimento (Bill of Lading) kayıtları, ithalat/ihracat hacimleri, gönderici/alıcı firma adları, taşınan ürünlerin GTİP (HS Code) kodları, gümrük kapıları ve ticaret yapılan ülkeler.

**YOK** — şemada karşılığı yok.

### Tedarik Zinciri ve Müşteriler
> Ana tedarikçiler, bağımlı olunan ham madde üreticileri, en büyük kurumsal müşteriler, bayilik ağları, distribütörlük anlaşmaları ve lojistik/nakliye partnerleri.

**YOK** — şemada karşılığı yok.

### Kamu İhaleleri ve Sözleşmeler
> Katılınan, kazanılan ve iptal edilen devlet ihaleleri, ihale bedelleri, şartnameler, idari sözleşmeler, KİK (Kamu İhale Kurumu) yasaklılık durumları ve hak ediş geçmişleri.

**KAPALI** — şemada karşılığı yok; kaynak EKAP **erişilemez** (D-257: HTTP 406 / TLS SECLEVEL).

### Teknolojik Altyapı
> Web sitesinde kullanılan CRM/ERP yazılımları, bulut sunucu sağlayıcıları, ödeme ağ geçitleri, pazarlama otomasyonları, içerik yönetim sistemleri (CMS) ve programlama dilleri.

**BOŞ** — `company_tech_profile` tablosu şemada var, **0 satır**.

### Siber Güvenlik Profillemesi
> SSL/TLS sertifika geçerlilikleri, e-posta güvenlik protokolleri (SPF/DKIM/DMARC), açık portlar, IP kara liste durumları, siber zafiyet skorları ve geçmiş veri sızıntısı kayıtları.

**KISMEN VAR** — yalnızca e-posta doğrulama tarafı: `email_validation_data` 8923 (%94,8),
`email_validity_score` 4048 (%43,0). SSL/port/zafiyet/sızıntı için karşılık **YOK**.

### İnsan Kaynakları ve İstihdam
> Toplam çalışan sayısı, departman bazlı kadro dağılımı, beyaz/mavi yaka oranı, ortalama çalışan kıdem süresi, kilit personelin ayrılma sıklığı ve sendikalaşma durumu.

**BOŞ** — `employee_count`, `employee_count_estimate`, `employee_count_score` kolonları
şemada var, **üçü de %0 dolu**. Departman/kıdem/sendika için karşılık **YOK**.

### İşe Alım ve Büyüme Trendleri
> Aktif iş ilanları, ilanların açık kalma süreleri, en çok aranan uzmanlık alanları, yeni açılan departmanlar ve insan kaynakları bütçe büyüme sinyalleri.

**VAR (çok zayıf)** — `job_postings` tablosu **8 satır**; `job_postings_count` yalnızca
**8 firmada** dolu (9412'de %0,1). Pratikte yok sayılmalı.

### Fikri ve Sınai Mülkiyet
> Şirket adına tescilli markalar, ulusal/uluslararası patentler, faydalı modeller, endüstriyel tasarımlar, telif hakları, coğrafi işaretler ve tescil başvuru geçmişleri.

**YOK** — şemada karşılığı yok.

### Gayrimenkul ve Varlık Envanteri
> Şirkete ait tapulu arsalar, binalar, fabrikalar, araç filoları, iş makineleri, üretim bantları, demirbaşlar ve bunların üzerinde bulunan rehin/ipotek kayıtları.

**KISMEN VAR (çok zayıf)** — yalnızca `osb_parcel` (OSB parsel) **19 firmada** (%0,2).
Tapu/filo/makine/rehin için karşılık **YOK**.

### Dijital Pazarlama ve Medya
> Sosyal medya takipçi sayıları, etkileşim oranları, SEO/SEM anahtar kelimeleri, Google Ads reklam bütçe tahminleri, yayınlanan dijital reklam kreatifleri ve medya görünürlüğü.

**KISMEN VAR** — yalnızca varlık sinyali: `social_media_score` 8504 (%90,4).
Takipçi sayısı, etkileşim, SEO/SEM, reklam bütçesi için karşılık **YOK**.

### Web Trafiği ve Analitiği
> Aylık tekil/çoğul ziyaretçi sayıları, hemen çıkma oranları, trafikteki coğrafi dağılım, trafiğin yönlendiği kaynaklar (organik, direkt, sosyal) ve ortalama oturum süreleri.

**YOK** — şemada karşılığı yok.

### Müşteri Algısı ve İtibar
> Google Business, Şikayetvar, Trustpilot veya sektörel forumlardaki müşteri yorumları, şikayet çözme hızları, yıldız puanları ve kamuoyundaki marka imajı algısı.

**YOK** — şemada karşılığı yok.

### Yatırım ve Teşvik Geçmişi
> Alınan tohum/seri yatırımlar, risk sermayesi (VC) ve melek yatırımcı fonları, değerleme geçmişleri, KOSGEB/TÜBİTAK destekleri ve devlet yatırım teşvik belgeleri.

**YOK** — şemada karşılığı yok.

### Sektörel Belgeler ve Uyumluluk
> ISO kalite belgeleri, Sanayi Sicil Belgesi, Kapasite Raporu, ÇED (Çevresel Etki Değerlendirmesi) raporları, mesleki faaliyet belgeleri ve sektöre özel lisanslar.

**BOŞ / KAPALI** — `certifications` tablosu şemada var, **0 satır**.
Kapasite Raporu kaynağı TOBB **KAPALI** (D-257: API HTTP 401).

---

## 2. Üretim Kapasitesi ve Fabrika Verileri

### Kapasite Raporları
> Türkiye'de TOBB tarafından onaylanan, şirketin yıllık üretim gücünü, yıllık ham madde ihtiyacını ve makine parkurunu gösteren resmi kapasite raporu verileri.

**KAPALI** — şemada karşılığı yok; TOBB API **401** döndürüyor (D-257).

### Sanayi Sicil Belgesi
> Şirketin resmi olarak "sanayici" statüsünde olup olmadığını, tescil tarihini ve güncel vize durumunu gösteren kayıtlar.

**BOŞ** — `certifications` tablosu var, **0 satır**.

### Üretim Alanı ve Lokasyon Metrajı
> Fabrika kapalı/açık alan metrekare bilgileri, üretim tesisinin OSB (Organize Sanayi Bölgesi) içinde olup olmadığı ve limanlara/tren hatlarına olan lojistik mesafesi.

**KISMEN VAR** — OSB üyeliği `is_osb_member` 9412 (%100) ve `osb_id` 8196 (%87,1) **VAR**.
Metrekare ve lojistik mesafe için karşılık **YOK**.

### Makine ve Ekipman Envanteri
> Tesiste kullanılan CNC tezgahları, enjeksiyon makineleri, robotik kollar veya fırınlar gibi ana üretim araçlarının sayısal ve marka bazlı tahmini dökümü.

**BOŞ** — `company_capabilities` tablosu şemada var, **0 satır**.

---

## 3. 🚛 Tedarik Zinciri, Ham Madde ve Lojistik

### GTİP (HS Code) Bazlı Dış Ticaret
> Şirketin ithal ettiği ham maddelerin ve ihraç ettiği yarı mamul/mamullerin 12'li GTİP kodları, yıllık sevkiyat hacimleri ve tonaj bilgileri.

**YOK** — şemada karşılığı yok. (Sektör kodu olarak yalnızca NACE var: `nace_code`
8289 firmada dolu — ama **%100'ü tahmin**, doğrulanmış değil; D-258.)

### Gümrük Konşimento (Bill of Lading) Verileri
> Küresel tedarik zinciri ağında hangi ülkelerdeki hangi üreticilerden ham madde aldığının ve hangi küresel markalara üretim yaptığının (Alıcı/Satıcı eşleşmesi) tespiti.

**YOK** — şemada karşılığı yok.

### Lojistik ve Depolama Kapasitesi
> Şirketin sahip olduğu toplam antrepo/depo alanları, soğuk hava deposu varlığı, forklift ve lojistik araç filosu (TIR, kamyon sayıları) envanteri.

**YOK** — şemada karşılığı yok.

### Enerji ve Tüketim Profili
> Fabrikanın tahmini enerji (elektrik/doğal gaz) tüketim sınıfı, yüksek enerji tüketen sanayi tesisi olup olmadığı ve kendi enerjisini üreten (çatı GES vb.) yatırımlara sahip olma durumu.

**YOK** — şemada karşılığı yok.

---

## 4. 📜 Belgeler, Standartlar ve İhale Geçmişi

### Sektörel ve Kalite Belgeleri
> ISO 9001 (Kalite), ISO 14001 (Çevre), ISO 45001 (İş Sağlığı), IATF 16949 (Otomotiv), AS9100 (Havacılık) ve CE/TSE uygunluk işaretleri.

**BOŞ** — `certifications` tablosu şemada var, **0 satır**.

### Yatırım Teşvik Belgeleri
> Sanayi ve Teknoloji Bakanlığı'ndan alınan güncel teşvikler; şirketin yeni makine alımı, fabrika genişletme veya modernizasyon yatırımı yapıp yapmadığının takibi.

**YOK** — şemada karşılığı yok.

### ÇED (Çevresel Etki Değerlendirmesi) Raporları
> Şirketin çevresel izinleri, emisyon durumları, atık yönetimi lisansları ve "ÇED Olumlu/Gerekli Değildir" kararlarının geçmişi.

**YOK** — şemada karşılığı yok.

### Kamu ve Savunma Sanayii İhaleleri
> Devlet Malzeme Ofisi (DMO), MSB veya ASELSAN/TAI gibi ana sanayi devlerinin ihalelerine katılım, kazanılan sözleşmeler ve tedarikçilik geçmişi.

**KAPALI** — şemada karşılığı yok; EKAP **erişilemez** (D-257).

---

## 5. 👥 İş Gücü ve Operasyonel Risk

### Mavi Yaka / Beyaz Yaka Oranı
> Toplam istihdam içindeki üretim hatlarında çalışan mavi yaka işçi yoğunluğu ve mühendislik kadrosunun (Ar-Ge personeli) oranı.

**BOŞ** — `employee_count` kolonu var, **%0 dolu**; yaka kırılımı için karşılık **YOK**.

### Tehlike Sınıfı ve İSG Geçmişi
> Tesisin iş kazası riski (Az Tehlikeli, Tehlikeli, Çok Tehlikeli) sınıflandırması ve geçmişteki büyük iş durdurma veya ceza kayıtları.

**YOK** — şemada karşılığı yok.

### Sendikal Durum
> Fabrikadaki işçilerin bağlı olduğu sendikalar, toplu iş sözleşmesi (TİS) dönemleri ve olası grev/lokavt risk süreleri.

**YOK** — şemada karşılığı yok.

---

## Kaynak notu (metnin kapanışı)

> Bu verileri toplamak için Türkiye'de TOBB, Sanayi ve Teknoloji Bakanlığı, KİK ve Gümrük veri sağlayıcıları gibi kaynakları entegre etmeniz gerekecek.

**Ölçülen durum (D-257):** metnin saydığı dört kaynağın **üçü bugün kapalı**.

| Kaynak | Ölçülen durum |
|---|---|
| TOBB | API **HTTP 401** — üyelik/anahtar gerekiyor |
| KİK / EKAP | **HTTP 406** — TLS SECLEVEL reddi |
| MERSİS | Sorgu ekranı **404** |
| Ticaret Sicil Gazetesi | **captcha + üyelik** |
| Sanayi ve Teknoloji Bakanlığı | Açık uç nokta ölçülmedi — bilinmiyor |

Ayrıca **kısır döngü** (D-257): açık kalan tüm uçlar girdi olarak **VKN/TCKN** istiyor;
elimizde 9412 unvan var ama yalnızca **5 VKN**. Yani kapı açık olsa bile anahtarımız yok.

---

## Bu belgenin sınırı

Bu belge **bugünün aynası**. Yarın bir alan dolarsa buradaki etiket eskir.
Etiketleri elle güncellemek yerine yeniden **ölçün** — D-245: kaynağı olmayan değer kabul edilmez.
