---
baslik: Marka Konumlandırma ve Kapsam
tur: ana_belge
surum: V10
durum: aktif
gorev: MRK-03
kod_aynasi: docs/MARKA_KONUMLANDIRMA.md
etiketler: [marka, huginn, muninn, odin, konumlandirma]
---

> **Kaynak belge budur.** Kod tarafındaki ayna: `docs/MARKA_KONUMLANDIRMA.md`. Değişiklik önce burada yapılır, sonra aynaya yansıtılır. İlgili kararlar: [[../05_versiyonlar/01_versiyon_9_baglam_dokumani|V9 Ana Bağlam]] · Marka sözleşmesi: `ANA_KURALLAR.md` → "Marka Adları ve Dil Sözleşmesi".

> **Uygulama notu (MRK-01 kararı):** 8000 HTML yüzeyi = **Huginn** (müşteri), 8501 Streamlit yüzeyi = **Muninn** (Süper Admin), **Odin** = çekirdek. Aşağıdaki "Süper Kullanıcı / Süper Admin" ifadeleri bu eşlemeyle okunur.

# 📑 PROJE KAPSAM VE KONUMLANDIRMA DÖKÜMANI
*(Project Scope, AI Prompt Guide & Brand Strategy)*

## 1. GİRİŞ VE MİMARİ FELSEFE
Bu proje, gücünü ve mimari felsefesini İskandinav mitolojisindeki Bilgelik Tanrısı Odin'in iki kuzgunundan alır. Tıpkı Odin'in dünyadaki her şeyden haberdar olmak için bu iki kuzgunu evrene salması gibi, sistemimiz de veri akışını, izlemeyi ve yönetim gücünü bu iki temel panel üzerinden yürütür.

### 🦅 1.1. Kod Adı: HUGINN (Süper Kullanıcı Paneli)
* **Mitolojik Karşılık:** "Düşünce" (Thought)
* **Sistem Rolü:** Huginn, evreni gözlemleyen, veriyi anlık olarak işleyen ve mantık yürüten yapıyı temsil eder. Sistemimizde Süper Kullanıcı Paneli, operasyonun canlı mekanizmasıdır.
* **Sembolik Anlamı:** Geleceğe ve şimdiki zamana odaklanan dinamik döküman gücü.
* **Yazılımdaki Karşılığı (Canlı Operasyon ve Gözlem):**
    * **Anlık Veri Akışı (Real-time Telemetry):** Tıpkı Huginn'in her gün dokuz diyarı uçarak anlık bilgi toplaması gibi, bu panel de platformdaki canlı kullanıcı hareketlerini, sistem performansını ve anlık operasyonel verileri izler.
    * **Analitik ve Proaktif Kararlar:** Toplanan veriler üzerinde mantık yürüterek operasyonel kararların alınmasını sağlar. Sistemdeki "aktif zekayı" temsil eder.

### 🛡️ 1.2. Kod Adı: MUNINN (Süper Admin Paneli)
* **Mitolojik Karşılık:** "Hafıza / Hafızadaki Bilgi" (Memory)
* **Sistem Rolü:** Muninn, geçmişi, birikmiş bilgiyi ve evrenin köklü sırlarını korur. Sistemimizde Süper Admin Paneli, platformun en derin yetkilerini ve geçmiş veri tabanını barındıran sarsılmaz omurgadır.
* **Sembolik Anlamı:** Geçmişin bilgeliği, kalıcılık, arşiv ve mutlak otorite.
* **Yazılımdaki Karşılığı (Loglama, Güvenlik ve Derin Yönetim):**
    * **Mutlak Kayıt ve Loglama (Immutable Logs):** Sistemde gerçekleşen her şey Muninn'in hafızasına (veri tabanına) silinmez bir şekilde işlenir. Geçmiş analizler ve sistem geçmişi buradan yönetilir.
    * **Kök Yetkiler (Root Configuration):** Tıpkı hafızanın kimliğimizi oluşturması gibi, Muninn de sistemin kimliğini, çekirdek ayarlarını, kullanıcı rollerini ve en kritik güvenlik protokollerini yönetir.

### 🤝 1.3. Mimari Sinerji: "Odin'in Omuzlarındaki Bilgi"
Mitolojide Huginn ve Muninn her akşam Odin'in omuzlarına konar ve topladıkları bilgelikleri onun kulağına fısıldar. Yazılımımızda bu fısıltı, merkezi karar destek mekanizmasını oluşturur.
* **Huginn (Düşünce)** sahada ne olduğunu görür ve veriyi toplar.
* **Muninn (Hafıza)** bu veriyi geçmiş tecrübeler ve kurallarla karşılaştırarak doğrular.
* **Sonuç:** İki panelin kusursuz senkronizasyonu, sistem yöneticilerine (Odin) platform üzerinde tam hakimiyet (Omniscience) sağlar.

---

## 🎨 2. MARKA KONUMLANDIRMA VE PAZARLAMA STRATEJİSİ
Bu konseptin pazarlamadaki temel vaadi şudur: "Geleceği tahmin etmek ve kontrol etmek için, şimdiki zamanın verisine (Huginn) ve geçmişin hafızasına (Muninn) sahip olmalısınız." Müşterilerinize ve yatırımcılarınıza karmaşık bir yazılım paneli değil, "Tam Hakimiyet ve Mutlak Güven" satıyoruz.

### 🎯 2.1. Marka Sloganları (Taglines)
* **Ana Slogan:** "Sisteminize Odin'in Gözleriyle Bakın."
* **Teknoloji Odaklı:** "Düşünce hızıyla izleyin (Huginn), mutlak hafızayla yönetin (Muninn)."
* **Yatırımcı/B2B Odaklı:** "Verinin gücü, mitolojinin bilgeliğiyle buluştu: Kusursuz Kontrol."
* **Kısa & Punchy:** "Gözlemle. Hatırla. Yönet."

### 📣 2.2. Pazarlama Hikayesi (The Brand Narrative)
"Modern iş dünyasında veri, uçsuz bucaksız bir evrendir. Bu evrende kaybolmamak için sadece görmek yetmez; hatırlamak ve analiz etmek gerekir. İskandinav mitolojisinde Bilgelik Tanrısı Odin, evrenin tüm sırlarına hakim olmak için iki kuzgununa güvendi: Huginn (Düşünce) ve Muninn (Hafıza).

Biz de yeni nesil yazılım platformumuzda bu kadim bilgeliği teknolojiyle yeniden canlandırdık. Huginn ile sisteminizin o anki canlı nefesini, anlık hareketlerini ve dinamizmini izliyoruz. Muninn ile geçmişin sarsılmaz tecrübesini, güvenliğini ve büyük verisini koruyoruz. İkisi bir araya geldiğinde, işletmeniz için karanlıkta hiçbir nokta kalmıyor. Sisteminiz artık kör değil. Güç sizin elinizde."

### 🎨 2.3. Görsel Kimlik ve Logo Konsepti (Visual Identity)
* **Renk Paleti:**
    * **Odin Core (Genel Marka):** Gece mavisi, fırtına grisi ve İskandinav rünlerini andıran altın sarısı detaylar (Güven ve bilgelik hissi).
    * **Huginn (Süper Kullanıcı):** Siber yeşil veya elektrik mavisi (Canlı veri, hız ve aksiyonu temsil eder).
    * **Muninn (Süper Admin):** Mat siyah veya koyu antrasit (Güvenlik, arşiv ve aşılması imkansız duvarları temsil eder).
* **Logo Fikri:** Sırt sırta vermiş, biri yukarı (geleceğe/gökyüzüne) diğeri aşağı (yere/arşive) bakan minimalist, geometrik iki kuzgun silüeti.

### ⚡ 2.4. Ürün Özelliklerinin Pazarlama Diline Çevrilmesi (Feature Flipping)

| Teknik Özellik | Pazarlama Adı | Müşteriye/Yatırımcıya Vaat |
| :--- | :--- | :--- |
| Real-time Stream & Analytics | **Huginn Eye (Huginn Gözü)** | "Sisteminizde o saniye ne olduğunu fırtına hızıyla görün. Krizleri doğmadan engelleyin." |
| Immutable Logs & Database | **Muninn Memory (Muninn Hafızası)** | "Asla silinmez, manipüle edilemez geçmiş kaydı. Güvenliğiniz geçmişin bilgeliğine emanet." |

---

## 💻 3. KULLANIM SENARYOLARI VE ARAYÜZ TASARIM İLKELERİ
* **Huginn (Süper Kullanıcı) Arayüzü:** Daha dinamik, canlı grafiklerin (charts) ön planda olduğu, sürekli güncellenen (real-time stream) ve operasyonel hızı yansıtan hafif (lightweight) bir tasarıma sahip olmalıdır.
* **Muninn (Süper Admin) Arayüzü:** Güvenliği ve kararlılığı hissettiren, derin veri tabanı sorgularının, audit loglarının (denetim izleri) ve yapılandırma (config) ayarlarının yer aldığı daha korunaklı ve oturaklı bir tasarıma sahip olmalıdır.

---

## 🤖 4. YAPAY ZEKA KODLAMA TALİMATI (AI SYSTEM PROMPT)

> **AI'a Giriş Komutu:** *"Aşağıdaki mimari felsefeyi ve klasör yapısını oku. Yazacağın tüm backend servisleri, API endpoint'leri ve arayüz bileşenleri bu mantığa, isimlendirme kurallarına ve felsefeye sadık kalmalıdır."*

### 📁 4.1. Klasör ve Modül Mimarisi (Folder Structure)
```text
├── src/
│   ├── modules/
│   │   ├── huginn/                 # SÜPER KULLANICI / CANLI OPERASYON
│   │   │   ├── controllers/        # Canlı veri akışı kontrolörleri
│   │   │   ├── services/           # Telemetri ve anlık işlem servisleri
│   │   │   └── views/              # Huginn UI (Canlı grafikler, anlık paneller)
│   │   │
│   │   ├── muninn/                 # SÜPER ADMIN / HAFIZA VE GÜVENLİK
│   │   │   ├── controllers/        # Log ve sistem ayarları kontrolörleri
│   │   │   ├── services/           # Audit log, yedekleme ve kök yetki servisleri
│   │   │   └── views/              # Muninn UI (Güvenlik, ayarlar, geçmiş raporlar)
│   │   │
│   │   └── odin/                   # MERKEZİ KARAR / ORTAK ÇEKİRDEK (Core)
│   │       ├── database/           # Veri tabanı bağlantıları
│   │       ├── middleware/         # Huginn ve Muninn yetki kontrol mekanizmaları
│   │       └── utils/              # Ortak yardımcı fonksiyonlar
```

> Not: Bu klasör ağacı **hedef/ilham** niteliğindedir. Mevcut kod tabanında `src/company_master/` altında `huginn_`/`muninn_`/`odin_` teknik önekleriyle ilerlenir (bkz. `ANA_KURALLAR.md` → "Tarihsel Çatı Adı" kuralı, sıfır migration).

### 🛠️ 4.2. Yapay Zekaya Kod Yazdırırken Kullanılacak İsimlendirme Kuralları
Yazılımdan fonksiyon veya API rotası isterken bu terminolojinin kullanılması zorunludur.

#### Huginn (Düşünce / Canlı Takip) Modülü İçin:
* **API Rotaları:** `/api/v1/huginn/live-stream`, `/api/v1/huginn/telemetry`
* **Fonksiyon İsimleri:**
    * `fetchActiveUsers()` *(Diyardaki canlı kullanıcıları getir)*
    * `trackSystemMetrics()` *(Anlık sistem durumunu uçarak raporla)*
    * `broadcastLiveChanges()` *(Değişiklikleri anında yansıt)*

#### Muninn (Hafıza / Arşiv / Kök Ayarlar) Modülü İçin:
* **API Rotaları:** `/api/v1/muninn/audit-logs`, `/api/v1/muninn/system-config`
* **Fonksiyon İsimleri:**
    * `writeToMemory()` *(Log kaydı oluştur - silinemez hafıza)*
    * `recallPastLogs()` *(Geçmiş kayıtları hafızadan çağır)*
    * `applyRootConfiguration()` *(Sistemin kök ayarlarını ve yetkilerini değiştir)*

### 💡 4.3. Yapay Zekayı Yönetmek İçin Hazır Prompt Şablonu (Örnek)
```text
"Bana Huginn modülü için websockets kullanarak anlık sistem çökmelerini ve hata uyarılarını canlı olarak ekrana basan bir Node.js servisi yaz. Bu veri daha sonra Muninn modülündeki writeToMemory() fonksiyonuna gönderilmeli ve veri tabanına kalıcı olarak işlenmeli. Kodu yukarıda belirlediğimiz klasör yapısına göre ayır."
```
