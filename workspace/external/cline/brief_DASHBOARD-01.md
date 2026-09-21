[[Huginn Data Insights/workspace/external/claude_code/brief_DASHBOARD-01.md]]

# 📊 Dashboard İyileştirme Planı — Fikir İsteniyor

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
```
## Cline Önerileri

### Öncelik Sırası
1. [Görev] — [Neden önce?]
2. [Görev] — [Neden önce?]
...

### Ek Fikirler
- [Yeni fikir]

## Cline Önerileri — Entegrasyon & Mevcut Sistem Uyumu

### Öncelik Sıralaması (Entegrasyon Etkiye Göre)

1. **Mevcut API Envanteri & Uyumluluk Haritası** — Yeni paneller için hangi endpoint'ler hazır, hangileri eksik/bozuk? Hangi endpoint'ler farklı veri döndürüyor? Önce harita, sonra inşa.
2. **P7-16: Firma Detay Görünümü (Mevcut `/api/company/{id}` Entegrasyonu)** — En düşük emek, en yüksek değer. API hazır, sadece frontend bağlamak gerek. İlk hedef olmalı.
3. **P7-18: Gelişmiş Filtre UI → Mevcut `/api/companies` Params Kontrolü** — API'de `sources=`, `nace=`, `min_score=` params'larının çalıştığından emin ol. UI eklemek için önce backend stabil olmalı.
4. **P7-17: Kalite Trend Grafiği → `/api/quality-trend` Gerçek Veri Kontrolü** — Endpoint var ama snapshot tablosu var mı? Veri birikmiş mi? Grafiğin anlamlı olması için önce veri kaynağı gerekli.
5. **UX-4/5: Yükleme ve Toast Bildirimleri** — `app.js` mevcut `fetch` çağrılarına loading state ve toast wrapper eklenebilir. Mimarideki çözüm; tüm fetch'leri saran bir `apiClient` modülü.
6. **P7-21: Performans Metrikleri → `/api/performance` Endpoint Doğrulaması** — Endpoint docstring'de var, gerçek ölçüm yapıyor mu? Önce mevcut endpoint'i doğrula, sonra UI ekle.
7. **P7-19: SSE Gerçek Zamanlı Bildirim → Backend Event Yapısı Kontrolü** — Frontend SSE'ye hazır ama backend event yayınlıyor mu? PostgreSQL `LISTEN/NOTIFY` veya Redis Pub/Sub gerekli — önce altyapı, sonra UI.
8. **P7-20: Admin Panel → Mevcut `/api/admin/*` Endpoint Uyumu** — Admin endpoint'leri var ama RBAC yok. Önce rol kontrolü middleware'i, sonra admin UI.
9. **S-1/S-2/S-3: Oturum Süreçleri → Mevcut Auth Endpoint'leri Birleştirme** — `/api/buyer/*` ve admin auth farklı yerlerde. Önce merkezi auth katmanı, sonra UI akışı.
10. **Tema/Responsive** — CSS değişkenleri `<head>` ve `data-theme` attribute ile 1-2 saatte tamamlanır. Ama toast ve modal sistemi önce olmalı (bağımlılık).

### Ek Mimari Fikirler (Entegrasyon Perspektifi)

- **Mevcut `/api/companies` response'unu küçütün:** 14K firma için `select(*)` yerine sadece listeye gerekli alanlar (`id, name, quality_score, source, nace_code`) gönderilsin. Detay için ayrı endpoint.
- **Mevcut endpoint'lere `fields=` parametresi ekleme:** İstekte `fields=id,name,score` gelirse sadece o alanlar döndürülür (GraphQL-style projection, REST'te).
- **Mevcut `web_dashboard/js/app.js`'te `apiClient` modülü:** Tüm fetch çağrılarını tek bir yerden yönet. Loading, error, retry, auth header — hepsi tek modülde.
- **Mevcut `/api/intelligence/dashboard` endpoint'ini genişletme:** Zaten var olan bu endpoint'e yeni KPI'lar eklemek, yeni endpoint açmaktan daha hızlı ve güvenli.
- **Veri akış şeması dokümanı:** Supabase → FastAPI BFF → Frontend (Streamlit/HTML). Her katmandaki dönüşümlerin çizilmesi, sonraki tüm geliştirmeler için referans olur.

### Riskler ve Çözümler

| Risk | Etki | Çözüm |
|------|------|-------|
| **Endpoint'ler farklı veri formatı döndürür** | Tutarsızlık, debug zorluğu | Pydantic response model zorunluluğu + contract test |
| **Frontend'de 14K firma için `select *`** | Sayfa 5-10sn+ yükler | Sadece gerekli alanlar + keyset pagination |
| **Mevcut `/api/quality-trend` boş/snapshot yok** | Grafik anlmsız | Önce `company_quality_snapshots` tablosu + CDC |
| **SSE için backend event yok** | Canlılık yanılsaması | PostgreSQL `LISTEN/NOTIFY` veya Redis Pub/Sub zorunluluğu |
| **Auth endpoint'leri dağınık** | Güvenlik açığı, tutarsızlık | Merkezi auth middleware + HttpOnly cookie |
| **Tema CSS'i mevcut stilleri bozar** | UX regresyonu | CSS değişkenleri + `[data-theme]` scope, progressive enhancement |

### Faz Önerisi

| Faz | İçerik | Süre |
|-----|--------|------|
| **Faz 1** | API envanteri, mevcut endpoint doğrulama, P7-16 detay görünümü | 2-3 saat |
| **Faz 2** | P7-18 filtre UI + server-side pagination + `apiClient` modülü | 4-5 saat |
| **Faz 3** | P7-17 trend + snapshot tablosu + P7-21 performans | 5-6 saat |
| **Faz 4** | P7-19 SSE + P7-20 admin + tema/responsive | 6-7 saat |

---

**Net karar:** Mevcut sistemde **hazır endpoint'ler var ama kullanımda tutarsızlık ve eksik var**. Yeni şeyler inşa etmek yerine, **mevcut endpoint'leri doğrulayıp, standartlaştırıp, birleştirmek** en hızlı ve en güvenli yol. P7-16 (Firma Detay) ve P7-18 (Filtre) ile başlamak, "mevcut sistemi anlamak" hedefiyle örtüşür.

### Öncelik Sırası

1. **API envanteri ve uyumluluk haritası** — Neler çalışıyor, neler eksik?
2. **P7-16: Firma Detay Görünümü** — Hazır API'yi frontend'e bağla
3. **P7-18: Gelişmiş Filtre UI** — Backend params + UI kontrolleri
4. **apiClient modülü** — Tüm fetch çağrılarını standartlaştır
5. **P7-17 + snapshot tablosu** — Veri kaynağı + grafik
6. **P7-21: Performans metrikleri** — Mevcut endpoint doğrula + UI
7. **P7-19: SSE** — Backend event altyapısı + frontend
8. **P7-20: Admin panel** — RBAC + UI
9. **Tema + Responsive** — CSS değişkenleri + progressive enhancement
10. **S-1/S-2/S-3: Oturum** — Merkezi auth + UI akışı

### Ek Fikirler

- Mevcut `/api/intelligence/dashboard` endpoint'ini genişletme
- `fields=` parametresi ile selektif alan çekme
- Veri akış şeması dokümanı (Supabase → BFF → Frontend)

### Riskler

- Endpoint'ler farklı veri formatı döndürür → Pydantic + contract test
- 14K için `select *` → Sadece gerekli alanlar + keyset pagination
- SSE için backend event yok → Altyapı zorunluluğu
- Auth endpoint'leri dağınık → Merkezi auth middleware
```
