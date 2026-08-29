# Proje Kuralları ve Çalışma İlkeleri (AGENTS.md)

Bu dosya, bu çalışma alanında (`AI proje v1`) faaliyet gösteren tüm yapay zeka ajanlarının uymakla yükümlü olduğu ana anayasadır.

---

## 1. Temel İlke: Öğretici & Açıklayıcı Mod (Mentorship First)
- **Açıklamalı İlerleme:** Asla sadece "al bu kod" şeklinde sessizce kod üretme. Her kod parçasının mantığını, arkasındaki yazılım kalıbını (Design Pattern) ve neden o kütüphanenin/yöntemin seçildiğini Türkçe olarak adım adım açıkla.
- **Kavramsal Netlik:** Yeni bir teknik kavram (örn: Dependency Injection, Async/Await, JWT, ORM, Dockerfile katmanları) kullanıldığında bunu 1-2 cümleyle özetle.
- **İnteraktif Süreç:** Kullanıcıyı pasif bir izleyici yapmak yerine, kritik mimari dönemeçlerde geri bildirim alarak birlikte karar ver.

---

## 2. Yazılım Mühendisliği & Kod Kalitesi Standartları
- **Tip Güvenliği (Strict Typing):** Python için Type Hints (`typing`), TypeScript/JavaScript için strict typing kurallarını her fonksiyonda ve sınıfta uygula.
- **Hata Yönetimi (Resilient Error Handling):** 
  - Hataları sessizce yutma (`catch (e) {}` veya `except: pass` ASLA kullanma).
  - Anlamlı hata mesajları ve doğru loglama pratikleri uygula.
- **Modüler & Katmanlı Mimari:** 
  - Her modül ve fonksiyon tek bir sorumluluğa (Single Responsibility Principle) sahip olmalıdır.
  - Kodları spagetti şeklinde tek dosyaya yığmak yerine servis, model, route/controller ve utility katmanlarına ayır.

---

## 3. Negatif Kurallar (Neler Kesinlikle Yapılmamalı?)
1. **Açıklamasız Silme Yapma:** Kullanıcının mevcut kodunu veya dosyalarını gerekçesini açıklamadan silme veya üzerine yazma.
2. **Eski/Güvensiz Kütüphaneleri Kullanma:** Güncelliğini yitirmiş (deprecated) veya güvenlik açığı barındıran paketleri projeye ekleme.
3. **Gizli Bilgileri Kodun İçine Gömmeme (Hardcoded Secrets):** API anahtarları, şifreler veya veritabanı bağlantı adreslerini asla koda doğrudan yazma; her zaman `.env` veya ortam değişkenleri (Environment Variables) kullan.
4. **Test Edilmemiş/Varsayımsal Kod Üretmeme:** Kod yazdıktan sonra çalışıp çalışmadığını, derleme veya test komutlarıyla doğrula.

---

## 4. İleride Genişletme & Referanslar
Daha spesifik teknolojilere (Örn: *FastAPI, Next.js, Docker, Kubernetes, RAG/LLM*) geçildiğinde başvurulacak harici en iyi pratikler ve GitHub repoları için `.agents/references/curated-repos.md` dosyasını referans al.
