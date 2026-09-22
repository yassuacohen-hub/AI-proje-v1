# UI Stack Değerlendirmesi — Müşteri Paneli (Huginn )

> **Revizyon 2 · 2026-09-18** — KAHİN'in kapsam düzeltmesi ve 4 pazarlık dışı kısıtı sonrası baştan yazıldı.
> Kapsam: **müşteri paneli** (port 8000). Admin paneli (Muninn, 8501) bu dokümanın dışındadır.
> Karar dokümanıdır. **Kod yazılmadı**, KAHİN onayı bekleniyor.

---

## 0. Tek cümlelik sonuç

Müşteri paneli **React değil, saf HTML + CSS + JavaScript** ve **Chart.js zaten kurulu çalışıyor**; bu yüzden önerilen 7 parçanın tamamı ya ücretli, ya mevcut bir parçanın ikizi, ya da günler süren bir geçiş gerektiriyor — **yeni paket almadan, eldeki wireframe'i eldeki araçlarla uygulamak en hızlı ve en ucuz yol.**

---

## 1. Kapsam düzeltmesi — müşteri paneli neyle yazılmış?

Revizyon 1'de yanlışlıkla Streamlit varsayılmıştı. Gerçek durum:

| Soru | Cevap | Kanıt |
|------|-------|-------|
| Müşteri paneli nasıl servis ediliyor? | FastAPI statik HTML döndürüyor | `web_app.py:2590` → `serve_dashboard()` → `WEB_DIR / "index.html"` |
| Hangi dizin? | `web_dashboard/` | `web_app.py:311` → `WEB_DIR = ROOT / "web_dashboard"` |
| Framework var mı? | **Yok.** Vanilla JS | `index.html` + `app.js`, `import`/`export` yok |
| Build adımı var mı? | **Yok.** Bundler, webpack, vite yok | `package.json` boş: `dependencies: {}` |
| Grafik kütüphanesi var mı? | **Var — Chart.js (CDN)** | `index.html:11` → `cdn.jsdelivr.net/npm/chart.js` |
| Tasarım sistemi var mı? | **Var — CSS token dosyası** | `css/admin_tokens.css` + `css/theme.css` |
| Tema (açık/koyu) var mı? | **Var, FOUC korumalı** | `theme.js` head içinde senkron yükleniyor |

### Mevcut kod hacmi (ölçüldü)

| Dosya | Satır | Boyut |
|-------|------:|------:|
| `web_dashboard/js/app.js` | **1.689** | 96,5 KB |
| `web_dashboard/css/style.css` | 439 | 37,6 KB |
| `web_dashboard/index.html` | 289 | 24,6 KB |
| `web_dashboard/js/messages.js` | 183 | 18,7 KB |
| `web_dashboard/css/admin_tokens.css` | 165 | 5,4 KB |
| `web_dashboard/js/theme.js` | 161 | 5,1 KB |
| `web_dashboard/css/theme.css` | 137 | 4,9 KB |
| `web_dashboard/css/responsive.css` | 81 | 4,0 KB |
| `web_dashboard/js/nace_labels.js` | 32 | 2,0 KB |
| **Toplam** | **~3.176** | **~199 KB** |

### Panelde bugün çalışan bölümler (`index.html` haritası)

1. Üst şerit — paket rozeti, canlı gösterge, tema düğmesi, yenile
2. Yan panel — Bilgi Merkezi, İzlenen Firmalar
3. Veri Sağlığı — **2 Chart.js grafiği** (`coverageChart`, `qualityChart`)
4. Eşleştirme (match) — puanlama + sonuç listesi
5. Sinyal Panosu — büyüme / yatırım / risk + **canlı akış (SSE)**
6. NACE dağılımı · Kaynaklar · Hızlı filtreler
7. Firma tablosu — sıralama + sayfalama (`renderTable`, `renderPagination`, `sortTable`)
8. Sağ detay paneli

**Yani panel boş değil; 94 fonksiyonluk çalışan bir uygulama var.**

---

## 2. AL / ELE / ERTELE kararları

KAHİN'in 4 kısıtı: **(1)** ücretsiz · **(2)** çakışma yok · **(3)** düşük zaman · **(4)** iyi dashboard.

| # | Öneri | Karar | Tek cümle gerekçe |
|---|-------|:-----:|-------------------|
| 1 | **Untitled UI** | 🔴 **ELE** | Ücretli (~300-500 $) → Kısıt 1. |
| 2 | **Flowbite Pro** | 🔴 **ELE** | Ücretli (~200 $) ve Untitled UI ile aynı boşluğu doldurur → Kısıt 1. |
| 3 | **Tremor** | 🔴 **ELE** | Chart.js zaten kurulu ve iki grafiği çiziyor; ikinci grafik kütüphanesi → Kısıt 2. |
| 4 | **Next.js + Tailwind** | 🔴 **ELE** | Build sistemi + tema yeniden yazımı gerektirir, 199 KB kodun tamamı elden geçer → Kısıt 3. |
| 5 | **shadcn/ui** | 🔴 **ELE** | React'sız çalışmaz; ayrıca `admin_tokens.css` bizim tasarım sistemimiz, ikincisi olmaz → Kısıt 2+3. |
| 6 | **Aceternity UI** | 🟡 **ERTELE** | Tanıtım sayfası animasyonları içindir, dashboard işi değil; web sitesi yapılırken bakılır → Kısıt 4. |
| 7 | **TanStack Table** | 🟡 **ERTELE** | Çekirdeği (`table-core`) React'sız kullanılabilir ve MIT, ama mevcut tablo sıralama+sayfalama ile çalışıyor; tablo gerçekten yetmezse gündeme gelir → Kısıt 2. |
| 8 | **React Flow** | 🟡 **ERTELE** | Gerçek boşluk (firma ilişki ağı bizde yok) ama React gerektirir ve ana sayfa kapsamında değil; ağ görünümü sıraya girince ücretsiz vanilla alternatifiyle birlikte değerlendirilir. |
| — | **Yeni paket (genel)** | 🟢 **AL: hiçbiri** | Kısıt 2 ve 3'ün doğal sonucu: ana sayfa hedefi mevcut Chart.js + CSS token sistemiyle tamamen karşılanabilir. |

### Özet sayılar

| Sonuç | Adet | Oran |
|-------|-----:|-----:|
| 🔴 ELE | 5 | %62,5 |
| 🟡 ERTELE | 3 | %37,5 |
| 🟢 AL (yeni paket) | 0 | %0 |
| **Ek lisans maliyeti** | **0 ₺** | — |

### Ücretli bir bileşen zorunlu mu? — Hayır

KAHİN'in kuralı: ücretli ancak *gerçekten zorunlu* ve ücretsiz alternatifi yoksa. İki ücretli öneri için de ücretsiz karşılık elimizde mevcut:

| Ücretli öneri | Ne veriyor | Bizdeki ücretsiz karşılığı |
|---|---|---|
| Untitled UI | Hazır bileşen kütüphanesi | `css/style.css` + `admin_tokens.css` (kart, tablo, rozet, modal hepsi var) |
| Flowbite Pro | Hazır dashboard blokları | `index.html`'deki 8 bölüm + `UX_ANA_SAYFA_WIREFRAME` düzeni |

---

## 3. Uygulama planı — müşteri paneli ana sayfası

Temel: `docs/UX_ANA_SAYFA_WIREFRAME_2026-09-18.md`. **Sıfırdan tasarım yok**, o wireframe'in şerit düzeni mevcut panele uyarlanıyor.

### Dokunulacak dosyalar (sadece 3)

- `web_dashboard/index.html` — şerit iskeleti
- `web_dashboard/css/style.css` — şerit/kart stilleri
- `web_dashboard/js/app.js` — kart doldurma + grafik

### Değişmeyecekler (garanti)

- Hiçbir API endpoint'i değişmez (`/api/kpi`, `/api/companies`, `/api/match`, `/api/intelligence/dashboard` …)
- Canlı akış (SSE) bozulmaz
- Tema sistemi (`theme.js`) bozulmaz
- `package.json` boş kalır — **yeni bağımlılık yok**

### Adımlar

| Adım | İş | Süre | Risk |
|:----:|----|-----:|:----:|
| **A1** | Üst şeride durum satırı: veri tazeliği + kayıt sayısı + canlı rozet tek satırda toplanır | 1,5 sa | 🟢 |
| **A2** | KPI şeridi: 4 kart (firma · kalite · kaynak · sinyal), her kartta değer + değişim yüzdesi | 3 sa | 🟢 |
| **A3** | Kartlar tıklanabilir olur → ilgili bölüme kaydırır (`scrollToSection` zaten var) | 1 sa | 🟢 |
| **A4** | Grafik şeridi: mevcut 2 Chart.js grafiği üst sıraya alınır, yan yana yerleşim | 2 sa | 🟢 |
| **A5** | Sinyal Panosu kartlaştırılır (3 liste → 3 kompakt kart, "tümünü gör" ile açılır) | 3 sa | 🟡 |
| **A6** | Ölü alan temizliği: NACE + Kaynaklar tek satıra iner, boş bölümler gizlenir | 2 sa | 🟢 |
| **A7** | 3 durum kontrolü: yükleniyor / boş / hata — her yeni kart için | 2 sa | 🟢 |
| **A8** | Responsive kontrol (1440 · 1024 · 640) + kontrast ≥ 4.5:1 | 2 sa | 🟡 |
| **A9** | Test: `tests/test_style_css.py` genişletme + HTML yapı testi | 2 sa | 🟢 |
| | **Toplam** | **~18,5 sa ≈ 2,5 gün** | |

### İlk teslim edilebilir dilim

> **A1 + A2 + A3 + A4 = ~7,5 saat (yaklaşık 1 gün)**

Bu dilim tek başına çalışır ve ekranda görülür: **durum satırı + 4 KPI kartı + tıklanabilirlik + grafiklerin üste alınması.** Geri kalan bölümler bu sırada hiç bozulmaz, oldukları yerde çalışmaya devam eder. KAHİN bu dilimi görüp beğenirse A5–A9 devam eder, beğenmezse geri alma maliyeti düşüktür (tek commit).

### Beklenen kazanım

| Ölçü | Şimdi | Sonra | Değişim |
|------|------:|------:|--------:|
| Ana ekranda özet kart | 0 | 4 | **+4** |
| İlk ekranda görülen bilgi | ~%35 | ~%70 | **+%100** |
| Tıklanabilir kart oranı | %0 | %100 | **+%100** |
| Sayfa yüksekliği (ekran) | ~2,4 | ~1,7 | **−%29** |
| Yeni bağımlılık | 0 | **0** | **değişmedi** |
| Ek lisans maliyeti | 0 ₺ | **0 ₺** | **değişmedi** |

---

## 4. Açık soru — "Stermit" adı

Öneri metninde geçen **"Stermit"** projede hiçbir yerde geçmiyor. Kayıtlı marka isimlerimiz:

| İsim | Anlamı | Port |
|------|--------|-----:|
| **Huginn** 🦅 | Müşteri yüzü | 8000 |
| **Muninn** 🛡️ | İç ekip paneli | 8501 |
| **Odin** ⚡ | Çekirdek kütüphane | — |

Bu isim yeni bir ürün mü, yoksa dışarıdan gelen öneride bir yazım hatası mı — netleşmesi gerekiyor.

---

## 5. KAHİN özeti (D-55 formatı)

| Renk | Bulgu | Oran / Rakam |
|:----:|-------|-------------:|
| 🟢 | Ana sayfayı yenilemek için **hiçbir yeni paket gerekmiyor** | 0 paket, 0 ₺ |
| 🟢 | Müşteri panelinde grafik altyapısı **zaten var** (Chart.js, 2 grafik çalışıyor) | — |
| 🟢 | İlk görülebilir sonuç **1 günde** ekranda | ~7,5 saat |
| 🟡 | Önerilen 8 parçanın 5'i eleniyor, 3'ü erteleniyor | %62,5 ELE |
| 🟡 | Ertelenen 3 parçanın hepsi React istiyor; ileride kullanmak istersek önce React kararı gerekir | 3/3 |
| 🔴 | İki ücretli paket (Untitled UI + Flowbite Pro) **aynı işi yapıyor** ve ikisinin de ücretsiz karşılığı bizde var | ~500-700 $ tasarruf |
| 🔴 | Next.js'e geçmek 199 KB'lık çalışan kodun tamamının elden geçmesi demek | ~3.176 satır |
| 🔵 | Firma ilişki ağı (React Flow'un çözdüğü iş) bizde gerçekten yok — ama ana sayfa işi değil, ayrı karar | 1 gerçek boşluk |
| 🔵 | "Stermit" adı projede hiç geçmiyor, netleşmeli | — |

---

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/MUSTERI_PANELI_HUB]]

## 6. Onay için karar

Onay verilirse **A1–A4 dilimi** yazılır, KAHİN ekranda görür, sonra devam edilir. Onay gelmeden kod yazılmaz.
