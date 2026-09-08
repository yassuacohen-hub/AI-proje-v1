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

---

## 5. Çoklu Ajan Koordinasyonu

Bu çalışma alanında birden fazla ajan paralel çalışabilir. Her işe başlamadan önce çalışma alanı kökündeki `AGENT_SYNC.md` dosyasını oku ve iş bitince güncelle. Ayrıntılar kökteki `AGENTS.md` dosyasındadır.

### 5.1 Ana Bağlam Kaynağı (Zorunlu)
- **Ana bağlam dokümanı:** `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
- Her ajan, iş başlatmadan önce bu belgeyi okur ve hedef/MVP/öncelik ile uyumlu hareket eder.
- Bu belge, ürün hedefi, teknik sınırlar, veri politikası ve öngörülen MVP kapsamını tanımlar.
- Ajanlar, kısa süreli çözümler üretirken bu belgeyi aşamaz; aksi halde kararlar ve hedefler çelişir.

### 5.2 MVP ve Geliştirme Sınırı
- Veri tabanı kurulumu, veri kalitesi ve temel iş akışı doğrulanmadan müşteri odaklı web arayüzü üretilmez.
- Hızlı iç doğrulama için Streamlit gibi sade dashboard kullanılabilir.
- Yeni özellik istekleri veya teknik genişlemeler, ana bağlam dokümanındaki hedef ve sınırlar çerçevesinde değerlendirilir.
- UI/iş mantığı ve veri katmanı önceliği korunur; erken frontend genişlemesi beklenmez.

### 5.3 Doküman Hiyerarşisi
- Aktif ana kaynak: `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
- Referans geçmiş sürümler: `01_versiyon_8_baglam_dokumani.md`, `01_versiyon_7_baglam_dokumani.md`, `01_versiyon_6_baglam_dokumani.md` ve benzeri
- Eski sürümler, tarihsel bağlam ve neden-sonuç ilişkilerini açıklamak için okunur; aktif iş ve kararlar her zaman V9 bağlamına göre yürütülür.
- V9 ile çelişen eski kararlar, geçerli karar değil; referans olarak tartışılır ve üstüne yeni mantık inşa edilir.

### 5.4 Ajan Başlangıç Şablonu
Her iş başlamadan önce aşağıdaki sırayı uygula:
1. `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md` dosyasını oku.
2. `AGENT_SYNC.md` dosyasını kontrol et ve aktif iş kaydını gör.
3. `AI proje v1/V10/TODO.md` ve `AI proje v1/V10/project_state.md` üzerinde açık görev/MVP sınırını doğrula.
4. Aynı dosyaya başka ajan dokunuyor mu kontrol et; çakışma varsa koordinasyon yap.
5. Sadece ana bağlam ve MVP sınırlarıyla uyumlu adımlarla ilerle.
6. İş bitince `AGENT_SYNC.md` ve ilgili durum dosyalarını güncelle.

---

## 6. Harici Ajan Entegrasyonu (External Agents)

Bu çalışma alanında, iç ajan setine ek olarak dış yapay zeka ajanları (Cursor Grok, GitHub Copilot, Claude Code vb.) da kullanılabilir. Tüm harici ajan etkileşimi **orkestratör üzerinden** ve **yalnızca `workspace/external/{agent_id}/` workspace'i** üzerinden yürütülür.

### 6.1 Temel Kurallar

- Harici ajanlar proje köküne **doğrudan erişemez**; yalnızca kendi workspace'inde çalışır.
- `.env`, gizli anahtarlar, KVKK kapsamındaki veriler ve üretim şeması harici ajana **gönderilmez**.
- Her görev, orkestratör tarafından hazırlanan **JSON/Markdown brief + bağlam + kısıtlar** paketiyle başlatılır.
- Harici ajan çıktısı **güvenilir değildir**; orkestratör + kalite ajanı + insan onayı döngüsünden geçmeden ana dala alınmaz.
- Başarısızlık durumunda **maksimum 3 deneme**, sonrasında iç ajanlara reassign yapılır.

### 6.2 Görev Tipleri (Harici Ajanlara Özel)

1. **Code Review** — mevcut kodları gözden geçirme, iyileştirme önerileri.
2. **Refactoring** — kod optimizasyonu, design pattern uyumu.
3. **Test Üretme** — unit test, integration test senaryoları.
4. **Dokümantasyon** — README, yorum, API dökümanları.
5. **Veri Dönüşümü** — CSV/JSON dönüşümleri, migration helper.
6. **Araştırma** — teknoloji karşılaştırma, benchmark.

### 6.3 Hata Yönetimi

- Tüm hatalar `AGENT_SYNC.md` → "ErrorLedger" bölümüne kaydedilir.
- 3 başarısızlık sonrası görev iç ajanlara reassign edilir.

### 6.4 Referanslar

- [[V10/08-Ajanlar/07_harici_ajan_protokolu]]
- [[V10/08-Ajanlar/08_harici_ajan_gorev_onerileri]]
- [[AGENT_SYNC]] (External Agent Registry + ErrorLedger)