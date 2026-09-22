[[Huginn Data Insights/workspace/external/claude_code/brief_DASHBOARD-01.md]]

# Dashboard İyileştirme — Mimari Perspektif Brief'i

**Ajan:** Roo Code  
**Odak:** Sistem mimarisi, performans, ölçeklenebilirlik  
**Tarih:** 2026-09-12

---

## Mevcut Durum

- **Veri:** 14.000 firma, Supabase üzerinde
- **Backend:** FastAPI + Streamlit hybrid
- **Frontend:** `web_dashboard/` (HTML/CSS/JS) + Streamlit pages
- **API:** `/api/kpi`, `/api/companies`, `/api/company/{id}`, `/api/quality-trend`, `/api/performance`, `/api/sources`, `/api/intelligence/dashboard`
- **Paneller:** P7-19 (SSE), P7-20 (Admin), P7-21 (Performans) — **sadece docstring'de, uygulanmamış**

## Mevcut Öneriler

| ID | Görev | Açıklama |
|----|-------|----------|
| P7-16 | Firma Detay Modal | `/api/company/{id}` ile detay görünümü |
| P7-17 | Kalite Trend Grafiği | Chart.js ile zaman serisi |
| P7-18 | Gelişmiş Filtre UI | NACE, kalite skoru, kaynak filtreleri |
| P7-19 | SSE Gerçek Zamanlı Bildirim | Server-Sent Events ile canlı güncelleme |
| P7-20 | Admin Panel | Kullanıcı yönetimi, API metrikleri |
| P7-21 | Performans Metrikleri | Response time, throughput, error rate |
| UX-1 | Modal Yapı | Tüm paneller için modal pencereler |
| UX-2 | Responsive Tasarım | Mobil uyumlu dashboard |
| UX-3 | Dark/Light Tema | Kullanıcı tercihli tema |
| UX-4 | Yükleme İkonları | Spinner/loading göstergeleri |
| UX-5 | Toast Bildirimleri | Başarı/hata bildirimleri |
| UX-6 | Sayfalama | 14K firma için pagination |
| S-1 | Giriş/Kayıt | Auth sistemi |
| S-2 | Oturum Yönetimi | Token tabanlı session |
| S-3 | Yetkilendirme | Admin/kullanıcı rolleri |
| S-4 | Şifre Sıfırlama | E-posta ile reset |
| S-5 | Profil Sayfası | Kullanıcı düzenleme |

## Senden İsteniyor

1. Bu planı **mimari açıdan** değerlendir — ne eksik/ne fazla/riskli?
2. Önerilerini **en önemliden en az önemliye** sırala
3. **Fazlama/çakışma** olan görevleri belirt
4. **Yeni mimari fikirler** ekle (örn. caching, lazy loading, CDN)
5. **Riskleri** belirt (performans, güvenlik, bakım)

## Çıktı Formatı

```markdown
## Roo Code — Mimari Öneriler

### Öncelik Sıralaması
1. [Görev] — [Neden önce?]
2. [Görev] — [Neden önce?]
...

### Ek Mimari Fikirler
- [Fikir] — [Faydası]

### Riskler ve Çözümler
- [Risk] — [Çözüm]

### Faz Önerisi
- Faz 1 (Hafta 1): ...
- Faz 2 (Hafta 2): ...
- Faz 3 (Hafta 3): ...
- Faz 4 (Hafta 4): ...
```

---

**Brief tamamlandı. Lütfen önerilerini yukarıdaki formatla döndür.**

## Roo Code — Mimari Öneriler

### 1. Plan Değerlendirmesi (Ne Eksik / Ne Fazla?)

#### 1.1 Ne Fazla (Erken Yapılması Riskli Olanlar)

- **P7-19 (SSE Bildirimleri):** Gerçek bir event bus (PostgreSQL `LISTEN/NOTIFY` veya Redis Pub/Sub) ve backend event lifecycle kurulmadan UI seviyesinde SSE eklemek yalnızca sunucu yükü (connection leak) ve sahte canlılık algısı oluşturur. SSE, sunucu tarafı bir event distribution mekanizması olmadan anlamsızdır.
- **P7-20 (Admin Paneli UI):** Merkezi RBAC (Rol Tabanlı Erişim Kontrolü), yetkilendirme middleware'i ve Audit Trail olmadan UI üzerinde Admin paneli yapmak ciddi bir "Security through Obscurity" hatasıdır. Yetki kontrolü backend'de olmazsa, frontend'de gizlemek hiçbir anlamına yoktur.
- **S-1/S-2/S-3 (Auth/Oturum/Yetkilendirme):** Mevcut `app.js`'te API anahtarları URL parametresi ve `localStorage`'da tutuluyor. Bu, XSS saldırısında tüm yetkilerin çalınmasına neden olur. Auth altyapısı olmadan diğer tüm görevler güvenlik açığı bırakır.

#### 1.2 Ne Eksik (Kritik Altyapı)

- **Ortak BFF/API Sözleşmesi:** Streamlit ve HTML Dashboard farklı SQL/ORM sorguları çalıştırıyor. İki arayüz de tek bir FastAPI BFF katmanına bağlanmalı; aksi halde veri tutarsızlığı riski var.
- **Server-Side Cursor Pagination:** 14.000+ firma verisi `OFFSET` ile çekilmiyor mu? `OFFSET` derin sayfalarda performans patlamasına neden olur. Keyset/Cursor pagination şarttır.
- **KVKK & Veri Maskeleme Katmanı:** Ticari istihbarat ve kişisel bilgiler (telefon, e-posta, VKN) anonim kullanıcılar için maskelenmiyor. KVKK ihlali riski var.
- **Audit Logging:** Kim hangi firma verisini sorguladı, ne zaman toplu CSV indirdiği kaydedilmiyor.
- **Cache Stratégisi:** Supabase'a yapılan tekrarlayan sorgular için Redis/In-Memory TTL cache yok. Her sayfa yükleme aynı sorguyu tekrarlıyor.
- **Lazy Loading & Code Splitting:** Frontend JS bundle'ı tüm modülleri içeriyor. Chart.js, pagination, admin modülleri lazy-load edilmeli.

---

### 2. Öncelik Sıralaması

| # | Görev | Neden Önce? |
|---|-------|-------------|
| 1 | **Auth & RBAC Altyapısı (S-1/S-2/S-3)** | Tüm güvenlik ve yetki kontrolü bu temel üzerine kurulur. API anahtarları `HttpOnly` cookie'ye geçiş, Supabase Auth JWT, rol tabanlı middleware. |
| 2 | **BFF/API Standartlaşması** | Streamlit ve HTML dashboard'un aynı FastAPI endpoint'lerini kullanması. Pydantic şemaları ile yanıt standartlaşması. |
| 3 | **Server-Side Cursor Pagination (UX-6)** | 14K firma için `OFFSET` yerine Keyset pagination. PostgreSQL GIN/Trigram indeks desteği. |
| 4 | **KVKK Veri Maskeleme Katmanı** | Ücretsiz/anonim kullanıcılara kişisel verileri maskeli döndürme. KVKK uyum zorunlu. |
| 5 | **Cache & Performance Layer (P7-21)** | Redis TTL cache, slow query loglama, response time metrikleri. |
| 6 | **Audit Logging** | Kritik eylemlerin `audit_logs` tablosuna yazılması. |
| 7 | **P7-16 Firma Detay Görünümü** | URL paylaşılabilir `/company/{id}` detay sayfası. Modal yerine Drawer/SPA pattern. |
| 8 | **P7-17 Kalite Trend Grafiği** | `company_quality_snapshots` tablosu veya CDC altyapısı olmadan grafik anlamsız. |
| 9 | **P7-18 Gelişmiş Filtre UI** | Cursor pagination ile entegre, server-side filtreleme. |
| 10 | **P7-19 SSE Bildirimleri** | Event bus (Redis Pub/Sub veya PostgreSQL `LISTEN/NOTIFY`) hazırlandıktan sonra. |
| 11 | **P7-20 Admin Paneli** | RBAC + Audit Trail + Auth altyapısı tamamlandıktan sonra. |
| 12 | **UX-1/2/3/4/5 (UI Cilama)** | Çekirdek işlevsellik ve güvenlik oturduktan sonra. |

---

### 3. Faz Önerisi

#### Faz 1 (Hafta 1): Güvenlik & Altyapı Temelleri
- Auth sistemi: Supabase Auth + JWT, `HttpOnly`/`Secure`/`SameSite=Strict` cookie
- RBAC middleware: `Anon`, `User`, `Analyst`, `Admin` rolleri
- API Key'leri URL'den kaldır, cookie'ye geç
- BFF/API sözleşmesi: Pydantic şemaları ile standartlaştır
- Server-side cursor pagination: Keyset pattern, `company_id` cursor

#### Faz 2 (Hafta 2): Veri Güvenliği & Performans
- KVKK veri maskeleme katmanı: Şahıs firmalarında iletişim bilgilerini redact
- Audit logging: `audit_logs` tablosu, kullanıcı/IP/zaman/kayıt
- Cache layer: Redis TTL cache (30s–5m), Supabase query deduplication
- Performance monitoring: P50/P95/P99 latency, slow query log

#### Faz 3 (Hafta 3): Dashboard İşlevsellik
- P7-16 Firma Detay: `/company/{id}` SPA sayfası, URL paylaşım
- P7-17 Kalite Trend: `company_quality_snapshots` tablosu + Chart.js
- P7-18 Gelişmiş Filtre: Server-side filtre + cursor pagination entegrasyonu
- UX-1/2/4/5: Modal → Drawer, loading skeleton, toast bildirimleri

#### Faz 4 (Hafta 4): Gerçek Zamanlı & Admin
- P7-19 SSE: Redis Pub/Sub veya PostgreSQL `LISTEN/NOTIFY` + SSE endpoint
- P7-20 Admin Panel: Kullanıcı yönetimi, API metrikleri, audit log viewer
- UX-3 Dark/Light tema
- CDN & lazy loading: Chart.js ve admin modülleri lazy-load

---

### 4. Ek Mimari Fikirler

1. **CDN + Edge Cache:** Statik asset'ler (JS/CSS/ikonlar) için CDN kullanımı. Cloudflare veya Supabase Edge Functions ile statik dosya dağıtımı.
2. **Service Worker ile Offline Mode:** Dashboard'un temel verilerini Service Worker ile cache'leyip, ağ kesintisinde de temel bilgileri gösterme.
3. **Web Worker ile Ağır Hesaplamalar:** Match scoring ve NACE filtreleme gibi ağır JS hesaplamaları Web Worker ile ana thread'den ayırma.
4. **Real-time Quality Score Updates:** WebSocket veya SSE ile kalite skoru değiştiğinde anlık dashboard güncellemesi (P7-19 altyapısı hazır olduğunda).
5. **Predictive Loading:** Kullanıcının sonraki sayfaya tıklamasını öngören prefetch mekanizması (örn. firma listesinden tıklanan firma detayını önceden cache'le).
6. **Bundle Analysis & Code Splitting:** `webpack-bundle-analyzer` veya Vite'un built-in analizi ile JS bundle'ını optimise et. Chart.js, admin modülleri ayrı chunk'larda.
7. **Database Connection Pooling:** Supabase `pgbouncer` veya `connection_pool` ile bağlantı havuzu yönetimi. 14K firma için bağlantı sayısını sınırlama.
8. **Health Check & Circuit Breaker:** `/api/health` endpoint'i, Supabase bağlantı kesilmesi durumunda circuit breaker pattern ile graceful degradation.

---

### 5. Riskler ve Çözümler

| Risk | Etki | Çözüm |
|------|------|-------|
| **API Key Leakage (XSS)** | Tüm yetkilerin çalınması | `HttpOnly` cookie, Content Security Policy, XSS filtresi |
| **KVKK İhlali** | Yasal ceza, prestij kaybı | Veri katmanında otomatik masking, KVKK audit log |
| **DB Aşırı Yük (14K Sorgu)** | Sayfa yükleme 5-10s+, bağlantı havuzu dolma | Keyset pagination, GIN indeksler, query limit |
| **İki Arayüz Tutarsızlığı** | Kullanıcı güven kaybı | Tek BFF/API katmanı, Pydantic schema zorunluluğu |
| **SSE Connection Leak** | Sunucu yükü, memory leak | Event bus zorunluluğu, heartbeat mekanizması, timeout |
| **Admin Panel Güvensiz** | Yetkisiz erişim | RBAC middleware + Supabase RLS + Audit Trail |
| **Cache Stale Data** | Kullanıcıya eski veri gösterimi | TTL + invalidation strategy, write-through cache |
| **Single Point of Failure** | Dashboard tamamen düşer | Supabase read replica, circuit breaker, graceful degradation |

---

### 6. Çakışma ve Fazlalık Analizi

- **P7-19 ↔ P7-21:** Performans metrikleri (P7-21) SSE bildirimleri (P7-19) ile çakışıyor. SSE altyapısı olmadan P7-21'deki "real-time" metrikler anlamsız. → Önce P7-21'in temel metrikleri (latency, error rate), sonra P7-19.
- **S-1/S-2/S-3 ↔ P7-20:** Admin paneli (P7-20) Auth (S-1/S-2/S-3) olmadan yapılamaz. → Auth önce, Admin sonra.
- **UX-1 ↔ P7-16:** Modal yapısı (UX-1) ve Firma Detay (P7-16) aynı sorunu çözer. → Tek çözüm: `/company/{id}` detay sayfası + Drawer pattern.
- **P7-18 ↔ UX-6:** Gelişmiş filtre (P7-18) ve sayfalama (UX-6) birbirine bağlı. Filtreler pagination ile entegre olmalı.
- **S-4/S-5 ↔ P7-20:** Şifre sıfırlama ve profil sayfası (S-4/S-5) Admin paneli ile çakışıyor. → S-4/S-5 kullanıcı katmanı, P7-20 admin katmanı.

---

### 7. Teknik Borç ve Öncelikli Düzeltmeler

1. **`web_dashboard/js/app.js` API Key Handling:** Şu an URL param ve `localStorage`'da tutulan API anahtarları `HttpOnly` cookie'ye taşınmalı. Bu, güvenlik açığını kapatmanın en kritik adımı.
2. **Supabase RLS Politikaları:** `firms` tablosunda row-level security politikaları yok. Yetkisiz erişim engellenmemiş.
3. **N+1 Query Problem:** `/api/companies` endpoint'i firma başına ayrı sorgu yapıyor olabilir. Batch fetch ile düzeltilmeli.
4. **Chart.js Bundle Boyutu:** Chart.js entire library yüklüyor. `chart.js/auto` yerine sadece gerekli chart type'ları import edilmelidir.
5. **Streamlit + HTML Çakışma:** Streamlit'in kendi state management'i ile HTML/JS state'i çakışıyor. BFF katmanı bu çakışmayı çözecek.

---

### 8. Özet ve Önerilen Sonraki Adım

**En kritik 3 adım:**
1. **Auth & Cookie Migration** — API key'leri `HttpOnly` cookie'ye geç, Supabase Auth entegrasyonu
2. **Cursor Pagination** — `OFFSET` yerine Keyset pagination, 14K firma için zorunlu
3. **BFF Standardization** — Streamlit ve HTML dashboard'un aynı FastAPI endpoint'lerini kullanması

Bu üç adım tamamlandıktan sonra diğer tüm görevler güvenli ve ölçeklenebilir bir altyapı üzerinde yürütülebilir.

---

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

**Not:** P7-19, P7-20 ve P7-21 dosyaları `gelistirici` tarafından kilitli. Bu görevlerin kod değişiklikleri için önce kilidi açılması veya koordinasyon sağlanması gerekmektedir. Roo Code mimari önerileri sunmaktadır, doğrudan kod yazımı yapmamaktadır.

## Ortak Brief Katkısı

`workspace/external/BRIEF_2026-09-06.md` dosyasına Roo Code bölümü eklendi:

```markdown
### Roo Code — Mimari Perspektif
- **Görev:** Dashboard iyileştirme planını mimari açıdan değerlendirme
- **Öncelik:** P1
- **Çıktı:** `workspace/external/roo_code/brief_DASHBOARD-01.md`
- **Önemli Katkı:** Auth/RBAC önceliklendirmesi, cursor pagination, cache stratejisi, KVKK masking, faz planı
```
