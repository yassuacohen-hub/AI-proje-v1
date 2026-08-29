---
name: architecture-and-planning
description: >-
  Yazılım projeleri için sistem mimarisi, katmanlı tasarım, veritabanı şeması,
  API sözleşmeleri ve modüler klasör hiyerarşisini adım adım planlayan mimari becerisi.
---

# Mimari & Sistem Planlama Becerisi (Architecture & Planning Skill)

Bu beceri, yeni bir proje veya büyük bir modül geliştirilirken spagetti kod oluşmasını engellemek, ölçeklenebilir ve sürdürülebilir bir sistem tasarımı oluşturmak için kullanılır.

---

## 1. Mimari Tasarım Aşamaları

Yeni bir özellik veya sistem geliştirirken şu sırayı takip et:

### 1. Gereksinim Analizi (Domain & Requirements)
- Sistem tam olarak ne yapacak? (Girdi $\rightarrow$ İşlem $\rightarrow$ Çıktı)
- Hangi harici servislerle (Veritabanı, AI API'leri, Bulut servisleri) iletişim kurulacak?

### 2. Katmanlı Mimari Şablonu (Layered Architecture)
Projeyi her zaman temiz katmanlara ayır:
```text
src/
├── config/         # Ortam değişkenleri, ayarlar (.env yönetimi)
├── models/         # Veritabanı modelleri / Şemalar (Pydantic, SQLAlchemy, Zod vb.)
├── services/       # İş mantığı, algoritmalar, dış API çağrıları
├── controllers/    # API endpoint'leri / Route tanımları
├── utils/          # Yardımcı fonksiyonlar, loglama, ortak araçlar
└── tests/          # Otomatik birim ve entegrasyon testleri
```

### 3. Veri Akışı ve API Sözleşmeleri
- İstek (Request) ve Yanıt (Response) modellerini önceden netleştir.
- HTTP Durum Kodlarını (200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Internal Server Error) standartlara uygun olarak belirle.
