# API Referansı

> Süreç: web_app.py kaynaklı
> Versiyon: 1.0
> Güncelleme: 2026-09-14

## 1. Sistem

| Endpoint | Yöntem | Açıklama |
|----------|--------|----------|
| \/api/health\ | GET | Sağlık kontrolü |
| \/metrics\ | GET | Prometheus formatında metrik verisi |
| \/api/kpi\ | GET | KPI özeti (cached, ttl=60s) |
| \/api/performance\ | GET | Performans metrikleri (cached, ttl=30s) |

## 2. Firma

| Endpoint | Yöntem | Açıklama |
|----------|--------|----------|
| \/api/companies\ | GET | Firma listesi (filtre, arama, paginasyon) |
| \/api/companies/export\ | GET | CSV/Excel export |
| \/api/company/{id}\ | GET | Tek firma detayı (KVKK maskolu) |
| \/api/companies/search\ | GET | Arama (NACE, sektör, kaynak) |

## 3. E-Ticaret

| Endpoint | Yöntem | Açıklama |
|----------|--------|----------|
| \/api/buyer/categories\ | GET | Ürün katalogu |
| \/api/buyer/profile\ | GET | Profil + kredi + hareketler |
| \/api/buyer/profile\ | PUT | Profil güncelleme |
| \/api/buyer/ledger\ | GET | Hesap defteri |
| \/api/buyer/login\ | POST | Giriş |
| \/api/buyer/logout\ | POST | Çıkış |
| \/api/buyer/change-password\ | PUT | Şifre değiştirme |
| \/api/buyer/register\ | POST | Kurumsal kayıt |
| \/api/buyer/match\ | GET | Eşleştirme |

## 4. Admin

| Endpoint | Yöntem | Açıklama | Cache |
|----------|--------|----------|-------|
| \/api/admin/pending\ | GET | Onay bekleyenler | 60s |
| \/api/admin/approve\ | POST | Onay + kredi yükleme | — |
| \/api/admin/credit\ | POST | Kredi paketi / manuel yükleme | — |
| \/api/admin/api-usage\ | GET | Tier bazlı API kullanım raporu | 300s |
| \/api/admin/rotate-key\ | POST | API key yenileme | — |
| \/api/admin/categories\ | GET | Ürün kategorileri | 300s |
| \/api/admin/categories\ | POST | Kategori ekle/güncelle | — |

## 5. Analityk

| Endpoint | Yöntem | Açıklama |
|----------|--------|----------|
| \/api/admin/panel\ | GET | Admin paneli verisi |
| \/api/admin/search\ | GET | Admin arama |
| \/api/admin/export\ | GET | Admin export |
| \/api/admin/auto-refresh\ | GET | Auto refresh durumu |
| \/api/admin/kpi\ | GET | Admin KPI (cached, ttl=60s) |
| \/api/admin/extras\ | GET | Admin extras |
| \/api/admin/sistem\ | GET | Sistem metrikleri |
| \/api/admin/dashboard\ | GET | Admin dashboard |

## 6. Gerçek Zamanlı

| Endpoint | Yöntem | Açıklama |
|----------|--------|----------|
| \/api/intelligence/dashboard/stream\ | GET | SSE stream (5s aralık) |

## 7. Mesaj Kuyrugu (BE-03)

| Endpoint | Yöntem | Açıklama |
|----------|--------|----------|
| (Redis Queue) | PUBLISH | Mesaj yayınla (topic + payload) |
| (Redis Queue) | CONSUME | Mesaj tüket |

## 8. Authentication

- API key: \Authorization: Bearer {key}\ header
- Admin token: \Authorization: Bearer {admin_token}\ header
- Session token: Cookie veya header

## 9. Hata Kodları

| Kod | Açıklama |
|-----|----------|
| 401 | Yetkisiz erişim |
| 403 | Yetki reddedildi |
| 404 | Kaynak bulunamadı |
| 429 | Rate limit aşıldı |
| 500 | Sunucu hatası |
