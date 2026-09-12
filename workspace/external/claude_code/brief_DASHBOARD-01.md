# Dashboard İyileştirme Planı — Claude Code Görev Brief'i

## Mevcut Durum
- **Proje:** Huginn Data Insights — Ankara B2B Commercial Intelligence
- **Veri:** 14.000 firma, Streamlit + HTML dashboard
- **Teknoloji:** FastAPI backend, Supabase PostgreSQL, Chart.js frontend
- **Sorunlar:** P7-19/20/21 sadece docstring'de, uygulanmamış; bug'lar var; tema/UX/oturum süreçleri eksik

## Mevcut Öneriler
- **P7-16:** Firma Detay Modal
- **P7-17:** Kalite Trend Grafiği
- **P7-18:** Gelişmiş Filtre UI
- **P7-19:** SSE Gerçek Zamanlı Bildirim
- **P7-20:** Admin Panel
- **P7-21:** Performans Metrikleri
- **UX:** Modal yapı, responsive, dark/light tema
- **Oturum:** Giriş, kayıt, yetkilendirme, şifre sıfırlama

## Senden İsteniyor
1. Bu planı değerlendir — ne eksik/ne fazla?
2. **Güvenlik ve oturum yönetimi** perspektifinden önerilerini sırala (en önemliden en az önemliye)
3. Öncelik sırası öner (hangisi önce yapılmalı?)
4. Riskleri belirt (özellikle güvenlik, KVKK, veri gizliliği)
5. Yeni fikirler ekle

## Claude Code Önerileri

### Plan Değerlendirmesi (Ne Eksik / Ne Fazla?)

- **Ne Fazla (Erken Erken Yapılması Riskli Olanlar):**
  - **P7-19 (SSE Bildirimleri):** Gerçek bir event bus (PostgreSQL `LISTEN/NOTIFY` veya Redis Pub/Sub) ve backend event lifecycle kurulmadan UI seviyesinde SSE eklemek yalnızca sunucu yükü (connection leak) ve sahte canlılık algısı oluşturur.
  - **P7-20 (Admin Paneli UI):** Merkezi RBAC (Rol Tabanlı Erişim Kontrolü), yetkilendirme middleware'i ve Audit Trail olmadan UI üzerinde Admin paneli yapmak ciddi bir "Security through Obscurity" (gizleme yoluyla güvenlik) hatasıdır.

- **Ne Eksik (Kritik Altyapı ve Veri İhtiyaçları):**
  - **Tek BFF / API Katmanı Standartlaşması:** Streamlit ile HTML Dashboard'un farklı SQL/ORM sorguları çalıştırması tutarsızlık riski yaratmaktadır. İki arayüz de tek bir FastAPI BFF katmanına bağlanmalıdır.
  - **KVKK & Veri Maskeleme Katmanı (Data Redaction):** Ticari istihbarat ve yetkili kişi bilgilerinin (telefon, e-posta, TCKN/VKN) anonim/ücretsiz kullanıcılar için maskelenmesi mekanizması eksiktir.
  - **Server-Side Pagination & Cursor Fetching:** 14.000+ firma verisinin frontend'e tek seferde çekilmesi veya derin `OFFSET` sorguları performans patlamasına yol açar. Keyset/Cursor pagination şarttır.
  - **Denetim İzi (Audit Logging):** Kim hangi firma verisini sorguladı, ne zaman toplu CSV indirdi kaydı tutulmamaktadır.

---

### Öncelik Sırası
1. **Ortak BFF/API Sözleşmesi ve Yanıt Seması (Standartlaştırma)** — Streamlit ve HTML dashboard'un aynı veriyi farklı göstermesini önler. Pydantic şemaları ile yanıtlar garanti altına alınır.
2. **Merkezi Kimlik Doğrulama (Auth) & Rol Tabanlı Yetkilendirme (RBAC)** — Supabase Auth + JWT. API Key'lerin URL/localStorage yerine `HttpOnly`, `Secure` Cookie mimarisine taşınması ve backend yetki kontrolü.
3. **Server-Side Filtreleme ve Cursor Pagination (P7-18 Evrimi)** — 14.000+ firma verisini performanslı sorgulamak için `OFFSET` yerine Keyset/Cursor pagination ve PostgreSQL GIN/Trigram indeks desteği.
4. **Firma Detay Görünümü & UX Temelleri (P7-16 + UX-1/2/4/5)** — Modal yerine URL paylaşılabilir ve erişilebilir (a11y) "Drawer" veya `/company/{id}` detay sayfası. Loading/Empty/Error durumlarının standartlaştırılması.
5. **Gözlemlenebilirlik ve Performans Metrikleri (P7-21)** — P50/P95/P99 latency takibi, slow query loglama ve Redis/In-Memory TTL önbellekleme (Cache).
6. **KVKK Uyum & Audit Logging (Veri Güvenliği Katmanı)** — Veri indirme (CSV Export) sınırı, IP & kullanıcı bazlı rate-limiting, yetkili iletişim bilgisi maskeleme.
7. **Tarihsel Kalite Trend Modeli (P7-17)** — Kalite skorunun tarihsel olarak izlenmesi için `company_quality_snapshots` tablosu veya Change Data Capture (CDC) mimarisinin kurulması.
8. **Responsive Tasarım & Dark/Light Tema (UX-3)** — Çekirdek işlevsellik ve güvenlik oturduktan sonra UI cilalama.
9. **Gerçek Zamanlı Bildirimler (P7-19)** — Redis Pub/Sub veya PostgreSQL `LISTEN/NOTIFY` altyapısı hazırlandıktan sonra SSE entegrasyonu.
10. **Admin Paneli & Kullanıcı Yönetimi (P7-20 & S-4/S-5)** — Tüm RBAC ve Audit Trail altyapısı tamamlandıktan sonra yönetim arayüzü.

---

### Güvenlik ve Oturum Önerileri (Önem Sırasına Göre)

1. **HttpOnly & Secure Cookie Geçişi (En Yüksek Öncelik):**
   - *Risk:* API anahtarlarının URL parametresi veya `localStorage` içinde saklanması XSS durumunda tüm yetkilerin çalınmasına sebep olur.
   - *Çözüm:* Supabase Auth JWT token'ları `HttpOnly`, `SameSite=Strict`, `Secure` çerezlerinde (Cookie) saklanmalı, JavaScript erişimine kapatılmalıdır.

2. **Backend Rol Tabanlı Erişim Kontrolü (RBAC) & Supabase RLS (Yüksek Öncelik):**
   - *Risk:* Ön yüzde buton/sayfa gizlemek güvenlik sağlamaz; doğrudan API isteği atan biri yetkisiz erişim sağlayabilir.
   - *Çözüm:* `Anon`, `User`, `Analyst`, `Admin` rolleri tanımlanmalı. Tüm API endpoint'lerinde FastAPI middleware seviyesinde rol doğrulaması ve Supabase PostgreSQL RLS politikaları aktif edilmelidir.

3. **Veri Maskeleme & KVKK Uyum Katmanı (Yüksek Öncelik):**
   - *Risk:* Şahıs firmalarına ait TCKN/VKN, şahıs e-postaları ve kişisel telefonların açık sunulması KVKK ihlalidir.
   - *Çözüm:* Ücretsiz/Anonim kullanıcılara şahıs firması bilgileri `m****@g****.com`, `0532 *** ** 12` şeklinde maskeli dönmeli, sadece doğrulanmış yetkili kurumsal hesaplara açılmalıdır.

4. **Güvenli CSV/Excel Export & Rate Limiting (Orta Öncelik):**
   - *Risk:* Rakiplerin veya botların tüm 14.000 firmalık veriyi tek tıkla scrape edip veri tabanını indirmesi.
   - *Çözüm:* Export işlemine günlük kota (örn. max 50 kayıt/gün) ve IP/User bazlı rate limiting (SlowAPI) konulmalı. Toplu export işlemleri senkron değil arka plan görevi (Celery/Arq) yapılmalı, zaman ayarlı geçici indirme bağlantısı (Signed URL) sunulmalıdır.

5. **Kapsamlı Audit Logging (Denetim İzi) (Orta Öncelik):**
   - *Çözüm:* Kritik eylemler (`EXPORTS_DATA`, `SEARCH_COMPANIES`, `UPDATE_USER_ROLE`, `VIEW_SENSITIVE_FIELD`) kullanıcının IP'si, User-Agent bilgisi ve zaman damgasıyla `audit_logs` tablosuna yazılmalıdır.

6. **Parola & Oturum Güvenliği (S-4 / S-5) (Alt Öncelik):**
   - *Çözüm:* Magic Link veya OTP (One-Time Password) desteği, Brute-force önleyici IP/Hesap kilitleme (5 hatalı girişte 15 dakika engelleme).

---

### Ek Fikirler (Gelecek Planına Katkı)

1. **B2B Ticari İstihbarat & Tedarik Ağı Haritası (Network Graph):**
   - Ankara Sanayi Bölgeleri (OSTİM, İvedik, ASO, Başkent) arasındaki tedarikçi-müşteri ilişkilerini ve NACE kümelenmelerini gösteren etkileşimli ağ grafiği (D3.js / Vis.js).
2. **Kişiselleştirilmiş Akıllı Radar & Bülten (Smart Signals & Watchlist):**
   - Kullanıcının takip ettiği sektör/bölgelerdeki firmalarda kalite skoru artışı, yeni firma girişi veya adres/iletişim değişikliğinde haftalık otomatik e-posta/Telegram bülteni.
3. **Coğrafi Sanayi Isı Haritası (GIS Heatmap):**
   - 14.000 firmanın Ankara haritası üzerinde sanayi bölgeleri ve NACE kodlarına göre yoğunluk dağılımını gösteren coğrafi görünüm (Mapbox / Leaflet).
4. **LLM Tabanlı Firma Özet Asistanı ("Huginn Co-Pilot"):**
   - Firma detayında, firma web sitesi metinleri ve NACE faaliyetlerinden otomatik üretilen 3 cümlelik "Faaliyet & Tedarik Kapasite Özeti".
5. **Otomatik Veri Zenginleştirme Botları (Data Enrichment Pipeline):**
   - Eksik e-posta/telefon/NACE koduna sahip firmaları tespit edip arka planda web scrape / kamu kaynaklarından otomatik tamamlayan ve kalite skorunu yükselten zenginleştirme kuyruğu.

---

### Riskler ve Mitigasyonlar

- **Risk 1: Veri Hırsızlığı ve Kitlesel Scraping**
  - *Etki:* Ticari verinin çalınması, rakip analiz sistemlerine kopyalanması.
  - *Mitigasyon:* Cloudflare + SlowAPI ile rate limiting, yanıt boyutlarına üst sınır (max 50 firma/sayfa) ve captcha zorunluluğu.
- **Risk 2: KVKK / Kişisel Verilerin İhlali**
  - *Etki:* Yasal cezalar ve prestij kaybı.
  - *Mitigasyon:* Kişisel iletişim verilerini veri katmanında Otomatik Redaction/Masking kütüphanesiyle filtreleme.
- **Risk 3: İki Arayüzün (Streamlit & HTML) Veri İki Başlılığı**
  - *Etki:* Farklı ekranlarda farklı firma sayıları veya skorlarının görünmesi, kullanıcı güven kaybı.
  - *Mitigasyon:* Her iki arayüzün de aynı FastAPI REST/BFF endpoints'ini kullanmasını zorunlu kılmak.
- **Risk 4: Veritabanı Aşırı Yüklenmesi (14K Kayıt Sorgu Çökmesi)**
  - *Etki:* Sayfa yüklenme sürelerinin 5-10 saniyeyi aşması, DB bağlantı havuzunun dolması.
  - *Mitigasyon:* `OFFSET` pagination yerine `Keyset/Cursor Pagination` kullanımı, PostgreSQL GIN ve B-Tree indekslerinin aktif edilmesi.
- **Risk 5: Tarihsel Kalite Verisi Olmadan Yanıltıcı Grafikler (P7-17)**
  - *Etki:* Kalite trend grafiğinin anlamsız veya uydurma veri göstermesi.
  - *Mitigasyon:* Grafikten önce günlük `company_quality_snapshots` tablosu veya Change Data Capture (CDC) altyapısı kurup veri biriktirmek.

---

## Kurallar
- Kullanıcı (sahip) ve Ürün Sahibi ile iletişim **Türkçe** olmalı
- Sistem/yazılım dokümanları İngilizce olabilir
- KVKK kurallarına dikkat et
- Hard-coded secret yasağı var
- Tüm dosyalar UTF-8 kodlamasında

## Dosya Yolu
`workspace/external/claude_code/brief_DASHBOARD-01.md`
