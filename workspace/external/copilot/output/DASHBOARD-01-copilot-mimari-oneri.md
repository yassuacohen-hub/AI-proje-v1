## Copilot — Mimari Oneriler

### Sistem Elestirisi

Mevcut plan ozellik odakli; ancak veri sozlesmesi, guvenlik, gozlemlenebilirlik ve performans temelleri netlesmeden SSE, admin paneli ve gelismis auth'a gecmek riskli.

Mevcut kodda bazi maddeler zaten kismen mevcut:

- Pagination, filtreleme, watchlist ve gorev paneli HTML dashboard'da bulunuyor.
- API anahtari query parametresi ve `localStorage` uzerinden tasiniyor.
- `/metrics` ve performans sayaclari mevcut.
- Streamlit ve HTML dashboard ayni veriyi farkli sorgu mantiklariyla kullaniyor.
- Dashboard sorgulari icin bazi indeksler eklenmis.

Bu nedenle ilk hedef yeni ekran eklemek degil, iki dashboard yuzeyini ortak API ve yetki modeli etrafinda birlestirmek olmali.

### Oncelik Siralamasi

1. **Ortak API sozlesmesi ve veri modeli** — Streamlit ile HTML dashboard'un farkli sonuclar uretmesini onler. Pagination, filtre, siralama, hata ve tarih formatlari standartlastirilmali.
2. **Kimlik dogrulama ve yetkilendirme** — Admin, normal kullanici ve salt-okuma rolleri tanimlanmali. Supabase RLS veya backend tarafinda merkezi policy uygulanmali.
3. **P7-18: Gelismis filtre UI** — 14.000 firma icin en dogrudan kullanici degerini uretir. Filtreler backend'e tasinmali; tum kayitlar tarayiciya yuklenmemeli.
4. **P7-16: Firma detay gorunumu** — Liste kullanimini anlamli hale getirir. Modal yerine erisilebilir drawer veya detay route'u daha surdurulebilir olabilir.
5. **P7-21: Performans ve gozlemlenebilirlik** — P50/P95/P99 response time, sorgu suresi, hata orani, cache hit orani ve endpoint bazli trafik olculmeli.
6. **P7-17: Kalite trend grafigi** — Once tarihsel kalite snapshot tablosu veya event modeli olusturulmali; mevcut skor alanindan geriye donuk trend uretilmemeli.
7. **UX-2 / UX-4 / UX-5** — Responsive yapi, loading, empty, error ve toast durumlari tamamlanmali.
8. **UX-3: Tema** — Auth, veri dogrulugu ve performanstan sonra gelmeli.
9. **P7-19: SSE bildirimleri** — Yalnizca gercek bir olay kaynagi ve event lifecycle tanimlandiktan sonra uygulanmali.
10. **P7-20: Admin paneli** — Auth ve audit log olmadan admin paneli acilmamali.
11. **S-4: Sifre sifirlama** — Auth altyapisinin dogal parcasi olarak ele alinmali.
12. **S-5: Profil sayfasi** — Urun degerine etkisi dusuk; son faza birakilabilir.

### Fazlama ve Cakismalar

- **P7-16 + UX-1:** Tek bir `CompanyDetails` bileseni ve ortak state yonetimi kullanilmali.
- **P7-18 + UX-6:** Pagination ayri ozellik degil, gelismis filtreleme API'sinin parcasi olmali.
- **P7-19 + P7-21:** SSE saglik durumu ve baglanti metrikleri observability kapsaminda olmali.
- **P7-20 + S-1/S-2/S-3:** Admin paneli, auth ve RBAC'tan once yapilmamali.
- **P7-17:** Tarihsel veri yoksa grafik gercek trend degil, yalnizca gorunum olur.
- **P7-19:** Gercek SSE yoksa UI 'canli' etiketiyle yaniltici beklenti olusturmamali.

### Ek Mimari Fikirler

- Streamlit ve HTML icin ortak FastAPI/BFF katmani.
- Pydantic response modelleriyle sabit response ve hata semasi.
- `OFFSET` yerine cursor/keyset pagination.
- KPI ve kaynak ozetleri icin kisa TTL cache ve kontrollu invalidation.
- Grafiklerde lazy loading; ilk acilista tum endpoint'leri cagirmama.
- Sik kullanilan KPI/NACE sorgulari icin materialized view veya snapshot tablo.
- Trafik buyurse dashboard sorgulari icin read replica.
- Admin islemleri, auth degisiklikleri, CSV export ve hassas erisimler icin audit log.
- Buyuk CSV exportlarini async job yapma, rate limit ve satir siniri ekleme.
- Statik JS/CSS/chart asset'leri icin CDN ve hash'li cache basliklari.
- Her endpoint icin contract testi ve 14K+ kayitla load testi.

### Riskler ve Cozumler

- **API key'in URL/localStorage'da tasinmasi:** URL loglarina ve tarayici gecmisine sizabilir. HttpOnly, Secure, SameSite cookie veya Authorization header kullanilmali.
- **Yetkinin frontend'e birakilmasi:** Admin gizleme guvenlik degildir. Backend'de rol kontrolu zorunlu olmali.
- **SSE baglanti patlamasi:** Reconnect/backoff, heartbeat, baglanti limiti ve tenant izolasyonu eklenmeli.
- **Cache'in eski veri gostermesi:** TTL, invalidation ve `updated_at` veya dataset version eklenmeli.
- **14K kaydin istemciye tasinmasi:** Backend filtreleme, projection ve cursor pagination zorunlu olmali.
- **Iki dashboard'un veri tutarsizligi:** Tek API katmani ve contract testleri uygulanmali.
- **N+1 firma detay sorgulari:** Iliskiler tek sorgu veya kontrollu batch ile alinmali.
- **Hassas veri export'u:** Alan bazli izin, audit, rate limit ve maksimum satir siniri uygulanmali.
- **Trend verisinin olmamasi:** Kalite degisimleri snapshot/event tablosuna yazilmali.
- **Admin panelinin buyumesi:** Admin ozellikleri ayri route/module olarak tasarlanmali.

### Faz Onerisi

- **Faz 1 — Hafta 1:** API sozlesmeleri, response modelleri, merkezi auth/RBAC, backend pagination ve filtreleme.
- **Faz 2 — Hafta 2:** Firma detay gorunumu, loading/error/empty durumlari, sorgu indeksleri, P95 olcumu ve contract testleri.
- **Faz 3 — Hafta 3:** Kalite snapshot modeli, trend grafigi, cache, lazy loading, guvenli CSV export ve audit log.
- **Faz 4 — Hafta 4:** SSE, admin paneli, sifre sifirlama, responsive/tema iyilestirmeleri ve yuk testleri.

**Net karar:** P7-19 ve P7-20 hemen baslatilmamali. Ilk dikey dilim `auth/RBAC + ortak API + server-side filtre/pagination + firma detayi` olmali.
