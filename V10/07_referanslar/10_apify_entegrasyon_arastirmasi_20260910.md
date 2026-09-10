# Apify Entegrasyon Araştırması — API + MCP Çift Yönlü Bağlantı, Web Kazıma Alternatifleri ve Revize Plan Önerisi

> - **Tarih:** 2026-09-10
> - **Kapsam:** APIFY-01 — Apify uygunluk ve entegrasyon mimarisi araştırması
> - **Yöntem:** Salt okunur kod/belge incelemesi + resmî Apify ve alternatif sağlayıcı belgeleri
> - **Durum:** Araştırma raporu. Go/no-go ve ADR önerisi **insan onayına sunulur**.
> - **Bağlantılar:** [[04_web_kazima_kaynak_arastirmasi]] · [[01_versiyon_9_baglam_dokumani]] · [[09_proje_denetimi_2026-09-09]]
> - **Not:** Rapor sırasında kod, belge, kilit, migration farkları ve resmî ürün belgeleri incelendi. Uygulama/pytest çalıştırılmadı, canlı veritabanına bağlanılmadı, Actor çalıştırılmadı, ücretli işlem yapılmadı.

---

## 1. Yönetici Kararı Önerisi

**Apify, Huginn için uygun bir "alternatif veri toplama katmanı" olabilir; API ve MCP üzerinden çift yönlü entegrasyon teknik olarak mümkündür.** Ancak mevcut kazıma sorunlarının tamamı erişim/anti-bot kaynaklı değildir. Kodda veri işleme, firma eşleştirme, mükerrer kayıt, dosya yolu ve izin kontrolü sorunları da vardır.

**Önerilen strateji:**

> **Mevcut yerel scraper'lar + gerektiğinde Apify → ortak doğrulama ve karantina → PostgreSQL → mevcut sinyal motoru.**
> Üretim veri akışında REST API; araştırma ve kontrollü ajan kullanımında MCP.

**Neden "hemen her şeyi Apify'ye taşıma" değil?**

1. Apify; sitede olmayan veriyi oluşturmaz, yetkisiz erişimi hukuken meşru hale getirmez.
2. Hatalı firma eşleştirmesini, boş `external_id` tekrarını ve yol/izin hatalarını düzeltmez.
3. Aktör, proxy ve koşu maliyeti dolar bazlıdır; veri değeri kanıtlanmadan ölçeklendirme erken maliyet üretir.

**V9 ile uyum:** V9'un özü "daha çok veri değil, izi sürülebilen ve belirsizliği koruyan daha iyi ticari kanıt"tır. Apify, kanıt üreten veri toplama sağlayıcısı olarak bu çerçeveye oturtulmalı; ana veritabanı ve orkestratörün yerine geçmemelidir.

---

## 2. Mevcut Sistemde Doğrulanan Bulgular

### 2.1 Orkestrasyon / Pano

İnceleme anındaki `task_board.json` özeti: **100 done, 9 plan, 4 aktif, 3 blocked, 1 cancelled**.

- `file_locks.json` içindeki 7 kilidin **5'i tamamlanmış görevlerle ilişkili** (T1, T3b, P1-7 ×2, P7-10).
- İŞKUR (P7-5) ve Kariyer.net (P7-6) görevlerinde **pano sahibi ile kilit sahibi farklı** (pano `kazi_scraper`/`kariyer_scraper`, kilit `web_kazima`).
- Kariyer.net dosyası kilitli görünmesine rağmen ilgili konumda bulunmuyor; eski kilitli migration dosyası da yok.
- `GOV-01` (uzlaştırma) ve `APIFY-01` (Apify araştırması) zaten aktif; bu kapsamda **yeni görev açılmamalı**.
- **Sonuç:** Kilitler otomatik silinmemeli; önce sahip/görev/çalışma ağacı uzlaştırması yapılmalı.

### 2.2 Güvenlik

| Bulgu | Kanıt | Risk |
|---|---|---|
| Boş `DASH_API_KEY` ile yönetici erişiminin açık kalabilmesi | `web_app.py:1576–1587` | `require_admin` yalnız anahtar veya role=admin token kabul eder; boş anahtar ortamında güvenlik fail-open kalır |
| Çoklu kaynak CSV sorgusunda hatalı SQL oluşturma | `web_app.py:719–729` | Parantez/IN ifadesi bozuk SQL üretir |
| Job scraping'de `verify=False` | `sources/base.py:125–139` | TLS doğrulaması kapalı |
| Harici ajan yol kontrolünde metin öneki karşılaştırması | `orchestrator/workspace.py:24–47` | `startswith`; yol sınırı aşım riski (kanonik karşılaştırma yerine) |

### 2.3 CI

- Kritik Flake8 (`E9,F63,F7,F82`), Black ve pytest **zaten hard-fail üretebiliyor**.
- Geniş Flake8 `--exit-zero`, Bandit `|| true`, coverage eşiği yok, migration drift kapısı yok.
- Deploy adımı örnek/placeholder komut içeriyor.
- **Doğru ifade:** "CI hiç hard-fail etmiyor" değil, **"güvenlik ve kalite kapıları eksik uygulanıyor"**.

### 2.4 Veri Hattı (Apify'den önce düzeltilmeli)

1. **Şirket yerine ilan başlığı eşleştirmeye gönderiliyor** (`scripts/ingest_job_postings.py:74–107`):
   - `title`, `company_name` alanından önce kullanılıyor.
   - Firma domain'i yerine `source_url` (portal için portal domain'i) kullanılıyor.
   - Dışarıdan gelen `raw_data.company_id` için UUID biçimi kontrol ediliyor; güvenilir iç ilişkilendirme kanıtı aranmıyor.
   - Güven skoru bir yerde `90.0`, normalizer'da `0–1` aralığında (tutarsız ölçek).
2. **Kariyer sayfası, tekil ilan gibi kaydediliyor** (`sources/company_career.py:182–214`):
   - Birden fazla ilan kartından tek özet kayıt oluşturuluyor.
   - İlan detayları yerine ilk kartın örnek içeriği alınıyor.
   - `external_id=None` bırakılıyor.
3. **Mükerrer kayıt korumasında boş ID sorunu:** `UNIQUE(source_name, external_id)` PostgreSQL NULL davranışı nedeniyle boş `external_id` değerlerini tekilleştirmez; içerik hash'i çatışma anahtarı değil.
4. **Scraper çıktı yolu ile ingest yolu uyuşmuyor:** `sources/base.py:19` kökü `src/` konumuna çözüyor (ör. `src/data/job_intelligence/...`), ingest ise uygulama kökündeki `data/job_intelligence/...` bekliyor.
5. **Dinamik firma sitelerinde izin kontrolü atlanıyor:** Kariyer scraper'ı `domain=None` kullanıyor; temel sınıf bu durumda `_check_permission`'dan doğrudan geçiyor. `kvkk_safe=False` tek başına engelleme değil, uyarı üretiyor.
6. **Migration çoğaltılmış ve kopyalar aynı değil:** Job Intelligence migration'ı 3 yerde; iki kopyada geçersiz `DROP TRIGGER IF NOT EXISTS`, diğerinde düzeltilmiş `DROP TRIGGER IF EXISTS`.
7. **P7 test kanıtı eksik:** Test dizininde `CompanyMatcher`, `ScrapedJob`, `prepare_job_record` ve Job Intelligence akışına doğrudan referans bulunamadı; bazı API testleri canlı Supabase'e bağlı.

**Net değerlendirme:** Apify entegrasyonunun ön koşulu yalnızca güvenlik değil, **doğru çalışan bir veri kabul sözleşmesi** (çıktı kökü, tekil ilan modeli, firma eşleştirme, dedup, karantina).

---

## 3. Apify Ne Zaman Faydalı, Ne Zaman Çözüm Değil?

| Kullanım | Uygunluk | Öneri |
|---|---|---|
| Şirketlerin kariyer sayfaları | Yüksek | İlk pilot |
| JavaScript ile oluşan ilan detayları | Yüksek | Yerel HTTP başarısızsa tarayıcı tabanlı alternatif |
| Şirket haberleri, yatırım ve tesis duyuruları | Yüksek | P7 doğrulamasından sonraki aşama |
| OSB rehberleri | Orta | Çalışan yerel scraper'ları gereksiz yere taşıma |
| Ürün, makine, sertifika sayfaları | Orta–yüksek | Beyan edilen bilgi ile doğrulanmış kapasiteyi ayır |
| Kariyer.net / LinkedIn | Koşullu | Actor bazında erişim, kullanım şartı, kalite ve maliyet pilotu |
| EKAP | Koşullu | Resmî erişim ve kullanım koşulları ayrıca doğrulanmalı |
| VKN keşfi | Sınırlı | Kamuya açık sayfalardan aday çıkarma |
| MERSİS/GİB yetkili verisi | Erişim sorununu çözmez | Resmî izin/API süreci gerekir |
| Gerçek çalışan sayısı, ciro, satın alma niyeti | Doğrudan sağlamaz | Kanıt yoksa tahmin kesin bilgiye dönüştürülmemeli |

**Özel uyarı:** Apify Website Content Crawler, temiz metin üretirken footer gibi alanları kaldırabiliyor. VKN ararken bu davranış ters etki yapabilir. VKN profili ile haber/kariyer profili **ayrı** olmalı; gerekirse ham HTML veya ilgili DOM bölgesi korunmalı.

**Apify neyi çözer:** Tarayıcı çalıştırma, kuyruk, proxy ve yeniden deneme yükünü azaltır.
**Apify neyi çözmez:** Sitede olmayan veriyi oluşturmaz; yetkisiz erişimi hukuken meşru yapmaz; hatalı firma eşleştirmesini düzeltmez; her hedefte kesintisiz başarı garantisi vermez.

---

## 4. API ve MCP ile Çift Yönlü Entegrasyon

### 4.1 Huginn → Apify: REST API (üretim için önerilen ana yol)

Akış:
1. Huginn hedef URL'leri, izin kararını ve bütçeyi belirler.
2. Apify Actor asenkron başlatılır (`POST /v2/actors/:actorId/runs`).
3. `run_id`, Actor/build bilgisi ve `defaultDatasetId` kalıcı kaydedilir.
4. Çalışma durumu sorgulanır.
5. Dataset sayfalanarak alınır.
6. Veri doğrulanır, eşleştirilir ve tekilleştirilir.
7. Kabul edilen kayıtlar mevcut sinyal hattına aktarılır.

Güncel resmî API: `POST https://api.apify.com/v2/actors/:actorId/runs` (asenkron). Sonuçlar dataset endpoint'inden alınır.
### 4.2 Huginn/IDE ajanı → Apify: MCP

Apify'nin resmî MCP sunucusu: `https://mcp.apify.com` — Actor keşfetme, çalıştırma ve depolanan sonuçlara erişim sunar. Hosted bağlantıda Streamable HTTP/OAuth; yerel kullanımda stdio seçeneği. Üretim için **açıkça araç listesi belirtilmeli** (ör. `?tools=actors,docs,apify/rag-web-browser`).

Uygun kullanım:
- "Şu firma için kariyer sayfası bul."
- "Bu kaynak için uygun Actor'ları karşılaştır."
- "Bu koşunun hata nedenini ve örnek sonuçlarını göster."
- "Şema değişmiş mi kontrol et."

**Kural:** MCP'yi zamanlanmış üretim ETL'sinin zorunlu bağımlılığı yapma. LLM kararı gerektirmeyen düzenli işler REST üzerinden deterministik yürür. IDE → Apify MCP bağlantısı, Huginn'in izin/bütçe kontrolünü kendiliğinden çalıştırmaz; üretime yazan araçlar ortak politika katmanından geçmeli.

### 4.3 Apify → Huginn: Webhook / API

Apify çalışma tamamlanınca Huginn'e HTTP POST gönderebilir. İlgili olaylar:
- `ACTOR.RUN.SUCCEEDED`, `ACTOR.RUN.FAILED`, `ACTOR.RUN.ABORTED`, `ACTOR.RUN.TIMED_OUT`

Webhook alıcısı:
1. Ayrı webhook sırrını doğrular.
2. Olayı kalıcı kaydeder.
3. Hızlıca `2xx` döner.
4. Worker, çalışma durumunu Apify API üzerinden **tekrar doğrular**.
5. Dataset'i güvenilir API adresinden alır.

Resmî belgeler: yinelenen teslimat ihtimali, 2 dakika timeout, 11 yeniden deneme (üstel geri çekilme). Bu nedenle **idempotency zorunlu**. Özel header destekleniyor; **yerleşik HMAC imzası doğrulanamadı — tasarımda var kabul edilmemeli**.

**Yerel bilgisayar:** Apify `localhost:8000`'e ulaşamaz. İlk pilotta **polling** kullanmak, API'yi internete açmaktan daha basit ve güvenli.

### 4.4 Apify → Huginn: Ters yönlü MCP (MCP connectors)

Apify'nin MCP sunucusundan ayrı özelliği olan **MCP connectors**, Actor'ların dış MCP sunucularını çağırmasını sağlar. Özel MCP sunucuları, bearer/API key ve uygun OAuth yöntemleri desteklenir. Proxy, Actor'u yalnız bildirdiği araçlarla sınırlar (2 katmanlı yetki: connector allowlist + input şema `tools.required`).

Bunun için Huginn'de **henüz doğrulanmamış, yeni kurulacak sınırlı bir MCP sunucusu** gerekir. Önerilen araçlar:
- `get_source_policy`
- `get_collection_run_status`
- `submit_evidence_batch`
- `report_collection_failure`

**Asla verilmemesi gerekenler:**
- Keyfî SQL çalıştırma
- Üretim tablolarını doğrudan değiştirme
- Kullanıcı/kredi yönetimi
- Tüm müşteri verisini dışarı aktarma
- Dosya sisteminde serbest erişim

**Öneri:** Ters yönlü MCP ikinci fazda, tercihen bize ait Actor ile. Basit sonuç bildirimi için webhook yeterliyken MCP eklemek gereksiz karmaşıklıktır.

---

## 5. Hedef Mimari

```text
Zamanlayıcı / Yönetici / Yetkili ajan
                 │
                 ▼
       Huginn Toplama Kontrol Katmanı
    izin + URL güvenliği + bütçe + öncelik
                 │
         ┌───────┴────────┐
         ▼                ▼
   Yerel scraper      Apify sağlayıcısı
                         REST API
         │                │
         └───────┬────────┘
                 ▼
     Ham kanıt + çalışma metadatası
                 ▼
       Şema / PII / kalite kontrolü
                 ▼
      Firma eşleştirme + tekilleştirme
           │                 │
           ▼                 ▼
        Karantina        PostgreSQL
                             │
                             ▼
                 Job Intelligence / skorlar
                             │
                             ▼
                   Dashboard / bildirim
```

### Kritik tasarım kararları

- **Kaynak ile sağlayıcı ayrı olmalı.** Aynı kariyer ilanı: kaynak = firmanın sitesi, sağlayıcı = yerel scraper veya Apify. Sağlayıcı değişti diye iki bağımsız sinyal oluşmamalı.
- **Her kaydın izi tutulmalı:** kaynak + kanonik URL, toplama/yayın zamanı, actor/build/run/dataset, parser/şema sürümü, içerik hash'i, firma eşleştirme yöntemi + güveni, izin kararı, kabul/karantina nedeni.
- **Çalışma durumu, geliştirme görev panosundan ayrı olmalı:** `task_board.json` yazılım geliştirme görevleri içindir; scrape koşuları için PostgreSQL'de ayrı çalışma/olay kayıtları daha uygun.
- **Tek zamanlayıcı sahipliği olmalı:** Apify Schedule ile Windows zamanlayıcısı aynı işi bağımsız tetiklememeli.
---

## 6. Güvenlik, KVKK ve Maliyet

### 6.1 Güvenlik ve veri koruma

- Token frontend'e, Markdown belgelere veya URL query'sine yazılmamalı.
- REST çağrılarında `Authorization: Bearer` kullanılmalı.
- Limited-permission Actor'lar tercih edilmeli. Bu seviye, girdi olarak gönderilen verinin güvenliğini otomatik garanti etmez.
- İzin verilen Actor ve build listesi tutulmalı.
- Hedef URL, yönlendirme ve özel IP kontrolleri yapılmalı.
- Ham web içeriği LLM için talimat değil, **güvenilmeyen veri** olarak işlenmeli.
- Müşteri listesi, satış niyeti, iç skorlar ve veritabanı anahtarları Apify'ye gönderilmemeli.
- Saklama süresi, silme ve alt işleyen incelemesi yapılmalı.

**KVKK uyarısı:** "Kurumsal site" veya "resmî kurum" etiketi tek başına KVKK uygunluğu sağlamaz. Çalışan adı, kişisel iletişim bilgisi ve şahıs işletmesi verileri ayrıca değerlendirilmelidir. Türkiye'de işledikten sonra maskelemek, verinin daha önce yurt dışındaki hizmete gönderilmiş olması sorununu ortadan kaldırmaz.

Apify'nin sözleşme/DPA sayfaları erişim denemelerinde doğrulanamadı (404). **Bu başlık kapandı sayılamaz; üretim öncesi hukuki kapı olarak kalmalıdır.**

### 6.2 Maliyet

Araştırma sırasında fiyat sayfasındaki aylık seçenekler: Free 5 USD kredi, Starter 19 USD + aşım, Scale 199 USD + aşım, Business 999 USD + aşım. Fiyatlar ve Actor modelleri değişebilir; abonelik tutarı toplam maliyetin tamamı değildir.

Güncel API'de maliyet kontrolü parametreleri:
- `maxTotalChargeUsd`: koşu maliyet sınırı
- `timeout`: çalışma süresi sınırı
- `maxItems`: pay-per-result için ücretlendirilecek kayıt sınırı (**çıktı sayısına genel garanti değil**)

Koşu sonrası dataset okuma/depolama gibi maliyetler ayrıca izlenmelidir.

**Temel ölçüm metrik:** *Toplam toplama ve işleme maliyeti / yeni, tekil, doğrulanmış ve firmaya bağlanmış faydalı kanıt sayısı.* "Bin sayfa kaç dolar?" tek başına ticari değer ölçümü değildir.

---

## 7. Web Kazıma Alternatifleri

| Yaklaşım | Avantaj | Sınır | Huginn'de konumu |
|---|---|---|---|
| Mevcut `requests` + BeautifulSoup | Düşük maliyet, az değişiklik | JS ve karmaşık oturumlar | Varsayılan |
| Apify hazır Actor | Hızlı pilot, yönetilen çalıştırma | Actor kalitesi/şeması/maliyeti değişir | Seçici alternatif |
| Huginn'e özel Apify Actor | Çıktı ve izin politikasında kontrol | Bakım sorumluluğu bizde | Pilot sonrası güçlü aday |
| Yerel Crawlee + Playwright | HTTP/tarayıcı, kuyruk ve retry | Yeni bağımlılıklar, işletim yükü | Bulut bağımlılığını azaltma |
| Browserless | Yönetilen tarayıcı; parser bizde kalır | Tek başına ETL sistemi değil | Karmaşık tarayıcı işleri |
| Firecrawl | API/MCP, temiz metin ve yapılandırılmış çıktı | İş alanı doğrulaması yine gerekli | Haber/ürün/duyuru karşılaştırması |
| Resmî API / RSS / ATS feed | Daha yapılandırılmış ve istikrarlı erişim | Kaynağa göre bulunmayabilir | Varsa ilk tercih |

---

## 8. Revize Plan Önerisi (geçici plan ile karşılaştırma)

### Önerilen başlık

**Huginn — Stabilizasyon, Kanıt Hattı ve Kontrollü Apify Entegrasyon Planı**

### Uygulama sırası

| Aşama | Kapsam | Kabul ölçütü |
|---|---|---|
| **GOV-01** | Mevcut pano, kilit, belge ve artifact uzlaştırması | Sahip/durum/kanıt matrisi; mükerrer görev yok |
| **SEC-01** | Admin fail-closed, CSV sorgusu, secret ve PII kararları | İzole regresyon testleri |
| **SEC-02** | TLS, dinamik domain izinleri, URL ve workspace izolasyonu | Ret kararlarının hiçbir sağlayıcıyla aşılmaması |
| **DATA-01** | Çıktı kökü, tekil ilan modeli, firma eşleştirme, dedup, karantina | Aynı veri tekrar işlendiğinde yeni ilan/sinyal oluşmaması |
| **P7-GATE** | Tek migration kaynağı ve dikey akış testi | Fixture → ingest → eşleştirme → sinyal → skor |
| **APIFY-01** | Mevcut araştırmayı ADR ile sonuçlandırma | Kaynak/Actor/izin/bütçe/pilot kararı |
| **APIFY-02** | REST adaptörü ve polling pilotu | Kalıcı run takibi, sayfalama, maliyet ve tekrar güvenliği |
| **APIFY-03** | Webhook + kalıcı olay işleme | Yinelenen/geciken olaylar ve worker restart testi |
| **MCP-01** | Kontrollü Apify MCP erişimi | Araç listesi, harcama onayı, veri sınırları |
| **MCP-02** | Gerekirse Huginn MCP ve ters connector | Dar kapsamlı yetki; doğrudan master yazımı yok |
| **REL/DOC** | CI, dağıtım, rollback ve belge senkronu | Tekrarlanabilir teslimat ve kanıt bağlantıları |

### Eski planda düzeltilen ifadeler

- **"ErrorLedger tasarla"** yerine mevcut uygulamayı sağlamlaştır: `src/company_master/orchestrator/error_ledger.py` zaten var.
- Kilitlerin atomikliği yalnız dosyayı atomik yazmakla çözülmez; süreçler arası read–modify–write yarışları da ele alınmalı.
- `blocked` durumunun kilit ve bitiş zamanı anlamı netleştirilmeli; `done/cancelled` ile otomatik eşitlenmemeli.
- P7 doğrulaması, `P7-11` iş akışı bağlantısını ve aşağı akış sinyal tüketicilerini de kapsamalı.
- Apify araştırması stabilizasyonla paralel yürüyebilir.
- **Canlı veri yazan veya ücretli koşu başlatan entegrasyon**, güvenlik/veri sözleşmesi kapıları geçilmeden açılmamalı.
- Ödeme ve üyelik genişletmeleri bekleyebilir; mevcut güvenlik açıklarını kapatan API anahtarı düzeltmeleri bu beklemeye dahil edilmemeli.

---

## 9. Pilot Önerisi ve Kabul Ölçütleri

V9'daki 100 firma yaklaşımıyla uyumlu:

1. Önce **10 izinli firma** üzerinde teknik smoke pilot.
2. Ardından **100 firmalık sabit örneklem**.
3. Aynı URL listesinde yerel yöntem ile Apify karşılaştırması.
4. En az **iki toplama turu** ile tekrar ve güncellik kontrolü.
5. İlk turda gerçek master kayıtlarını değiştirmeyen **gölge çalışma**.

Ölçümler: ilan keşif ve çıkarım doğruluğu, firma eşleştirme doğruluğu, tekrar oranı, eksik yayın tarihi, yanlış "ilan yok" sonucu, yeni faydalı kanıt maliyeti, izin ve bütçe ihlali, yeniden başlatma sonrası toparlanma.

Önerilen başlangıç kapıları (onaylanacak hedefler): izinsiz hedefe sıfır istek, yeniden işlemelerde sıfır mükerrer kayıt, tüm kabul edilmiş kayıtlarda kaynak/run izi ve etiketli örneklemde en az %95 firma eşleştirme doğruluğu.

---

## 10. Açık Sorular / Doğrulanamayanlar

1. Apify sözleşme/DPA ve veri işleme maddeleri ilgili adreslerden doğrulanamadı — hukuki inceleme gerekir.
2. Webhook için yerleşik HMAC imzası resmî belgelerde doğrulanamadı — doğrulama yapılmalı veya header sırrı + cloud/API yeniden doğrulama kullanılmalı.
3. `MCPServer` ters yönlü bağlantı için Huginn tarafında MCP sunucusu yok — faz 2'de tasarlanacak.
4. Maliyet teklifi ürün resmî belgelerine dayanır; hesap açılmadan fiilî ücretlendirme doğrulanamaz.
5. Kariyer.net gibi kaynakların kullanım şartları ayrıca değerlendirilmeli.

---

## Kaynaklar

- [Apify Actor çalıştırma API'si](https://docs.apify.com/api/v2/actors-runs-post.md)
- [Apify MCP sunucusu](https://docs.apify.com/integrations/mcp.md)
- [Webhook davranışı ve güvenlik](https://docs.apify.com/integrations/webhooks/actions.md)
- [Website Content Crawler](https://apify.com/apify/website-content-crawler)
- [MCP connectors — ters yönlü bağlantı](https://docs.apify.com/integrations/mcp-connectors.md)
- [Actor yetki modeli](https://docs.apify.com/actors/running/permissions.md)
- [Apify fiyatlandırma](https://apify.com/pricing)
- [Crawlee Python](https://crawlee.dev/python/docs/introduction)
- [Browserless API karşılaştırması](https://docs.browserless.io/overview)
- [Firecrawl belgeleri](https://docs.firecrawl.dev/introduction)
