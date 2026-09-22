[[Huginn Data Insights/workspace/external/claude_code/brief_DASHBOARD-01.md]]

# Dashboard İyiveştirme Planı — Fikir İsteniyor

## Mevcut Durum
- **14.000 firma**, Streamlit + HTML dashboard
- **P7-19/20/21** sadece docstring'de, uygulanmamış
- Bug fix, tema, UX, oturum süreçleri eksik
- 46 görev task board'da (P7-14/15/19/20/21 aktif)

## Mevcut Öneriler
- **P7-16:** Firma Detay Modal — `/api/company/{id}` ile detay görünümü
- **P7-17:** Kalite Trend Grafiği — Chart.js ile aylık/haftalık trend
- **P7-18:** Gelişmiş Filtre UI — NACE, kalite skoru, kaynak checkbox'ları
- **P7-19:** SSE Gerçek Zamanlı Bildirim — Yeni firma/kalite değişikliği bildirimleri
- **P7-20:** Admin Panel — Kullanıcı yönetimi, API metrikleri
- **P7-21:** Performans Metrikleri — Response time, throughput, error rate
- **UX:** Modal yapı, responsive, dark/light tema, toast bildirimleri
- **Oturum:** Giriş, kayıt, yetkilendirme, şifre sıfırlama

## Senden İsteniyor
1. Bu planı değerlendir — ne eksik/ne fazla?
2. Kendi önerilerini sırala (en önemliden en az önemliye)
3. Öncelik sırası öner (hangisi önce yapılmalı?)
4. Riskleri belirt
5. Yeni fikirler ekle

## Çıktı Formatı
 ## Copilot Önerileri
 
 ---
 
 ## Copilot Yanıtı
 
 ### Sistem Eleştirisi
 
 Plan özellik odaklı; ancak ortak veri sözleşmesi, güvenlik, gözlemlenebilirlik ve performans temelleri netleşmeden SSE, admin paneli ve gelişmiş auth'a geçmek riskli. HTML dashboard'da pagination, filtreleme, watchlist, görev paneli ve `/metrics` bağlantısı zaten kısmen mevcut. Streamlit ve HTML dashboard aynı veriyi farklı SQL mantıklarıyla kullandığı için öncelik yeni ekran değil, ortak API ve yetki modeli olmalı.
 
 ### Öncelik Sırası
 
 1. **Ortak API sözleşmesi ve veri modeli** — Pagination, filtre, sıralama, hata ve tarih formatlarını standardize eder.
 2. **Kimlik doğrulama ve RBAC** — Admin, normal kullanıcı ve salt-okuma rollerini backend'de uygular.
 3. **P7-18: Gelişmiş filtre UI + server-side pagination** — 14.000 firma için tüm veriyi tarayıcıya taşımayı önler.
 4. **P7-16: Firma detay görünümü** — Modal yerine erişilebilir drawer veya detay route'u tercih edilmeli.
 5. **P7-21: Performans ve gözlemlenebilirlik** — P50/P95/P99, sorgu süresi, hata ve cache hit oranı ölçülmeli.
 6. **P7-17: Kalite trendi** — Önce kalite snapshot/event modeli oluşturulmalı.
 7. **UX-2/4/5** — Responsive, loading, empty, error ve toast durumları tamamlanmalı.
 8. **P7-19: SSE** — Gerçek olay kaynağı, heartbeat, reconnect/backoff ve bağlantı limiti tanımlandıktan sonra.
 9. **P7-20: Admin paneli** — Auth, RBAC ve audit log tamamlanmadan açılmamalı.
 10. **S-4/S-5** — Şifre sıfırlama auth kapsamına alınmalı; profil sayfası son faza bırakılmalı.
 
 ### Çakışmalar ve Fazlama
 
 - **P7-16 + UX-1:** Tek `CompanyDetails` bileşeni kullanılmalı.
 - **P7-18 + UX-6:** Pagination, filtreleme API'sinin parçası olmalı.
 - **P7-19 + P7-21:** SSE sağlık ve bağlantı metrikleri observability kapsamına alınmalı.
 - **P7-20 + S-1/S-2/S-3:** Admin paneli RBAC'tan önce yapılmamalı.
 - **P7-17:** Tarihsel veri yoksa grafik gerçek trend değildir.
 
 ### Ek Mimari Fikirler
 
 - Streamlit ve HTML için ortak FastAPI/BFF katmanı ve Pydantic response modelleri.
 - `OFFSET` yerine cursor/keyset pagination.
 - KPI/kaynak özetleri için kısa TTL cache ve kontrollü invalidation.
 - Grafiklerde lazy loading; sık kullanılan özetlerde materialized view veya snapshot tablo.
 - Admin işlemleri, auth değişiklikleri, CSV export ve hassas erişimler için audit log.
 - Büyük CSV exportlarını async job yapma; rate limit ve satır sınırı ekleme.
 - Endpoint contract testleri ve 14K+ kayıtla load testleri.
 
 ### Riskler ve Çözümler
 
 - **API key URL/localStorage'da:** URL loglarına sızabilir; HttpOnly/Secure/SameSite cookie veya Authorization header kullanılmalı.
 - **Frontend yetkisi:** Admin gizleme güvenlik değildir; her endpoint backend'de rol kontrolü yapmalı.
 - **SSE bağlantı patlaması:** Heartbeat, reconnect/backoff, limit ve tenant izolasyonu uygulanmalı.
 - **Eski cache verisi:** TTL, invalidation ve `updated_at`/dataset version eklenmeli.
 - **İki dashboard veri tutarsızlığı:** Tek API katmanı ve contract testleri kullanılmalı.
 - **Hassas export:** Alan bazlı izin, audit, rate limit ve maksimum satır sınırı uygulanmalı.
 
 ### Faz Önerisi
 
 - **Faz 1:** API sözleşmeleri, response modelleri, auth/RBAC, backend filtreleme ve pagination.
 - **Faz 2:** Firma detay görünümü, UI durumları, indeksler, P95 ölçümü ve contract testleri.
 - **Faz 3:** Kalite snapshot modeli, trend, cache, lazy loading, güvenli export ve audit log.
 - **Faz 4:** SSE, admin paneli, şifre sıfırlama, responsive/tema ve yük testleri.
 
 **Net karar:** İlk dikey dilim `auth/RBAC + ortak API + server-side filtre/pagination + firma detayı` olmalı. P7-19 ve P7-20 bu temel kurulmadan başlatılmamalı.

### Öncelik Sırası
1. [Görev] — [Neden önce?]
2. [Görev] — [Neden önce?]
...

### Ek Fikirler
- [Yeni fikir]

### Riskler
- [Risk] — [Çözüm önerisi]
```


---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]
