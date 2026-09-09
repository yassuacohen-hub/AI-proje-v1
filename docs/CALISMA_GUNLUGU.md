
## 2026-09-09 — Şifreli oturum sistemi + İşletmem sekmeleri + bilgi bankası notları ✅

**Şifre sistemi (PBKDF2):**
- Migration 0015: users tablosuna `password_hash` + `tax_number` + `phone` (Supabase + yerel PG)
- `web_app.py`: `_hash_password`/`_verify_password` (PBKDF2-SHA256, 120k iter, rastgele salt); kayıtta şifre zorunlu (min 8), login şifre doğrulamalı; hash'i olmayan eski MVP kayıtları için geçiş dönemi istisnası
- Yeni endpoint'ler: `POST /api/buyer/logout` + `POST /api/buyer/change-password` (mevcut şifre doğrulamalı)
- Üyelik modalı: kayıta şifre alanı + girişe şifre alanı eklendi

**İşletmem overlay yenilendi:**
- **4 sekme:** Firma Profili (firma/NACE/ürün/departman/çalışan sayısı/sertifikalar) · **Bilgiler** (yetkili, web, **VKN**, **telefon**, e-posta kilitli) · Eşleştirme (amaç + hedef sektörler) · **Hesap** (şifre değiştir)
- Başlıkta **oturum bilgisi + Çıkış düğmesi** (token silinir)
- Alan etiketlerine **hover bilgi notları** (neden isteniyor, nasıl kullanılıyor)

**Canlı test (Docker 8000, 8/8):** şifreli kayıt 200 → yanlış şifre 401 → şifresiz 401 → admin onay 200 → doğru şifre login 200 → şifre değiştir 200 → eski şifre 401 / yeni şifre 200 → profil PUT VKN+telefon kaydedildi. Bug fix: INSERT bind param ismi (ph→phash). Layout 8/8 PASS, 0 exception.

## 2026-09-09 — Profil zenginleştirme + admin-only görev tahtası + tam üyelik akış testi ✅

**Profil geliştirme (çalışan sayısı + sertifikalar):**
- Migration 0014 (`scripts/migrate_0014_profile_enrich.py`): users tablosuna `employee_range` + `certificates` — Supabase ve yerel PG'ye uygulandı
- `GET/PUT /api/buyer/profile` alanları işliyor; tamlama skoru 8→**10 alan**a çıktı
- İşletmem formuna: Çalışan Sayısı dropdown (1-5/6-20/21-50/51-250/250+) + Sertifikalar input

**Görev tahtası artık gerçek admin-only:**
- `openTasks()` admin değilse overlay hiç açılmıyor (toast uyarısı); sidebar'daki "Görev Tahtası (Yönetici)" öğesi admin oturumu yokken **gizli**, admin girişinde görünür — js v22

**Tam üyelik akış testi (canlı, 7 adım, hepsi 200):** kayıt (kurumsal e-posta+KVKK) → admin pending'de göründü → terminal tier onayı (100 kredi) → üye girişi → match sonrası kredi 99 (1 kredi düşüldü) → profil PUT yeni alanlar (tamlama %80) → GET doğrulama ✓. Test üyesi sonrasında DB'den temizlendi (`scripts/cleanup_test_users.py`).

**Ürün Kategorileri (Y25) kartının konumu hakkında:** admin overlay'de Üye Onay Paneli'nin altında ayrı karttır — katalog (kayıt formlarındaki ürün kategorileri) eşleştirme kalitesini yönetir; yalnızca admin görür.

## 2026-09-09 — Y22 MATCH v2: eşleştirme yönü seçimi ✅ + admin panel erişim rehberi

**Y22 uygulama:**
- Backend: `/api/match?yon=tedarikci|musteri|rakip` — `tedarikci` mevcut ileri yön (montaj→yan sanayi); `musteri` **ters yön** (hedef firmanın komşuluk haritası buyer grubuna bakar; `musteri-kanal`/`musteri-uzak` etiketleri — ör. yedek parçacıya 45.20 servis / 46.75 toptan kanalları); `rakip` sadece aynı NACE ana grubu
- Frontend: match paneline "Arama Yönü" dropdown (tooltip'li), durum satırı yön etiketli ("müşteri/satış kanalı arama" vb.), js v21
- Doğrulama: py_compile + node --check OK; Docker imaj rebuild; canlı test (nace=29, alt dilim): tedarikci→`uzak-sektor` / musteri→`musteri-uzak` / rakip→`farkli` — yön ayrımı çalışıyor; layout 8/8 PASS + 0 exception

**Admin panele giriş (canlı doğrulandı):**
1. **İşletmem** (navigasyon 1. öğe veya sağ üst buton) → **Giriş** → `admin@huginn.local` yaz → Giriş
   (üyelik kayıt formundan **ayrı**; admin hesabı seed'li: `admin@huginn.local`, enterprise, role=admin)
2. Hızlı Erişim → **Görev Tahtası (Yönetici)** → admin açıkken panelde: Üye Onay Paneli + Ürün Kategorileri kartları görünür
3. Alternatif: sayfaya `#tasks` hash'i ile gir → overlay otomatik açılır
- Canlı test: login 200 (role=admin, enterprise) → `/api/admin/pending` 200 ✓

## 2026-09-09 — İzleme listesi bug fix + Y25 product_categories admin paneli ✅

**Bug fix (izleme listesi):** `toggleWatchDetail` `toggleWatch(c.company_id)` çağırıyordu — `company_id` boş firmalarda ekleme hiç yapılmıyor, toast "çıkarıldı" diyordu. `watchKeyOf()` tek anahtar mantığına geçirildi (tüm izleme işlemleri). Canlı CDP regresyon testi eklendi (`check_dashboard_layout.mjs`): localStorage temizle → toggle → toast/buton/set doğrula → geri al. js v19→v20.

**Y25 — product_categories yönetim arayüzü (admin):**
- Backend: `GET /api/admin/categories` (aktif+pasif tam liste) + `POST /api/admin/categories` (create/update; code unique 409, nace_group 2 hane validasyonu, category_id UUID doğrulama) — ikisi de `require_admin`
- Frontend: Görev Tahtası admin paneline "Ürün Kategorileri" kartı — ekleme formu (kod/ad/NACE), satır bazlı inline düzenleme, aktif/pasif toggle (göz ikonu), durum badge'leri, özet satırı ("X aktif / Y toplam")
- Doğrulama: py_compile + node --check OK; 8010 ve Docker (8000, imaj rebuild) yeniden başlatıldı; canlı API testi: GET 14 kategori, POST create/toggle/update 200 OK, test kaydı DB'den silindi
- Not: `company_capabilities` bağlama (kategori ↔ firma) ayrı görev olarak plana alınmalı

## 2026-09-09 — Görev Tahtası admin-only bağımsız sayfa + admin onay paneli ✅

**Kullanıcı istekleri:**
1. Görev Tahtası verilerin arasından kaldırıldı → **Hızlı Erişim** menüsüne taşındı ("Görev Tahtası (Yönetici)")
2. **Admin-only**: token'da `role=admin` yoksa görev listesi + onay paneli görüntülenmez, yönetici giriş formu çıkar
3. Örnek@örnek.com akışı uçtan uca test edildi

**Admin altyapısı:**
- Seed admin: `admin@huginn.local` (role=admin, onayli, enterprise) — her iki DB'de
- `require_admin` dependency: DASH_API_KEY **veya** admin kullanıcı tokenı (Bearer) kabul eder
- Admin endpoint'leri (pending/approve/credit) require_admin'e bağlandı — non-admin token ile erişim **403** ✅ (test edildi)

**Admin panel (Görev Tahtası overlay içinde, admin görünür):**
- Onay bekleyen üyeler: firma/e-posta/ürün + **tier seç (Terminal/Strategic/Enterprise)** + Onayla/Reddet
- Onaylı üyeler: kredi bakiyesi + **Credit Pack yükleme** (miktar girilir)
- Enterprise onayında API key otomatik üretilir

**Test (örnek@ornek.com akışı, 11/11):** kayıt → admin login → pending → approve (100 kredi) → üye login → match kredi 99 → credit pack +50 (149) → profil GET (tamlama %62) → **profil PUT (departman dahil, tamlama %88)** → non-admin 403 engeli.

**Not:** `örnek@örnek.com` kaydı DB'de yoktu (Unicode e-posta formda başarısız olmuş); `ornek@ornek.com` olarak API ile kaydedilip onaylandı — sayfa yapısını görmek için panelde hazır.

## 2026-09-09 — "İşletmem" bağımsız tam ekran panele taşındı (kullanıcı feedback'i) ✅

**Kullanıcı:** "verilerin arasında duran bir yerde olmaz, bağımsız olsun — navigasyonun ilki veya sağ üstte Yenile'nin orası olabilir; tıklayınca kayıt sayfası açılır."

**Uygulanan çözüm — 2 giriş noktası + bağımsız overlay:**
1. **Topbar sağ üst**: mavi vurgulu **"İşletmem"** butonu (CANLI/Yenile grubunun yanında) — üye değilken de görünür, ilk temas noktası
2. **Navigasyonda İLK öğe**: İşletmem (Genel Bakış'ın üstüne taşındı)
3. **Bağımsız tam ekran overlay** (980px ortalanmış panel): veri kartlarının arasına gömülü değil; kendi başlık + Kapat butonu olan bağımsız sayfa gibi açılır (arka plan koyu, body scroll kilidi, dış tık = kapat)
4. Verilerin arasındaki eski chart-card **tamamen kaldırıldı**

**Doğrulama (headless Edge):** topbar butonu ✓ · openIsletmem 2 çağrı noktası ✓ · nav ilk sırada İşletmem ✓ · 18 tooltip ✓ · `node --check` OK · cache v10

## 2026-09-09 — "İşletmem" sayfası: profil yönetimi + kredi merkezi ✅

**Kullanıcı kararı:** Üyelik CTA match panelinden ayrıldı → navigasyonda **"İşletmem"** sayfası (fa-briefcase).

**Bölüm içeriği (giriş durumuna göre 3 görünüm):**
- **Giriş yok:** "İşletmenizi sisteme tanıtın" + Kayıt Ol/Giriş butonu (üyelik modalını açar)
- **Onay bekliyor:** bilgi banner'ı + profil formu (onay öncesi doldurulabilir)
- **Onaylı:** tam yönetim paneli

**Onaylı panelde:**
| Kart | İçerik |
|---|---|
| Özet chips | Durum · Paket/Tier · **Kredi Bakiyesi** · **Profil Tamamlanma %** (renkli ilerleme çubuğu) |
| Kredi Yükle | Credit Pack talebi (750 TRY/50 — yönetici onayıyla) |
| Profil formu | Firma adı, NACE, ürün/hizmet tanımı, **hedef sektörler**, **departman/rol** (yeni!), eşleştirme amacı (müşteri/tedarikçi/iş ortağı), yetkili, web |
| Kredi hareketleri | Son 12 ledger kaydı (+/- renkli, bakiye ile) |
| Enterprise | API key görüntüle/kopyala |

**API:** `GET/PUT /api/buyer/profile` (profil_tamlama hesaplamalı — 8 alan doluluğu), `GET /api/buyer/ledger` · `department` kolonu eklendi (0012 ALTER, iki DB'de).

**Doğrulama:** headless DOM: isletmem-section ✓ · briefcase nav ✓ · 16 tooltip ✓ · credit-badge slotu ✓ · `node --check` + py_compile OK · cache v9 · Docker rebuild sonrası canlı.

## 2026-09-09 — Monetizasyon MVP: üyelik + kredi sistemi canlıda ✅

**V7 Hybrid Credit modeli uygulandı** (bağlam dokümanlarından birebir):

| Bileşen | Detay |
|---|---|
| **Migrasyon 0012** | `users` (kurumsal e-posta, tier, credit_balance, api_key, status) + `credit_ledger` (denetimli kredi hareketleri) + `product_categories` (**14 kategori seed**: makine/CNC, metal işleme, otomotiv yan sanayi, yazılım/otomasyon, savunma tedariği…) — hem Supabase hem yerel PG'ye uygulandı |
| **Kayıt** | `POST /api/buyer/register` — kurumsal e-posta zorunlu (gmail/hotmail RED), KVKK checkbox zorunlu, web domain eşleşmesiyle mevcut firma kaydına bağlanır (`linked_company_id`), durumu `onay_bekliyor` |
| **Onay (senin elinde)** | `GET /api/admin/pending` + `POST /api/admin/approve` (tier seç → kredi yükle: terminal 100 / strategic 500 / enterprise sınırsız + **otomatik API key üretimi**) + `POST /api/admin/credit` (Credit Pack: 750 TRY/50) |
| **Giriş** | `POST /api/buyer/login` → 24 saatlik HMAC token (OAuth Scale'de) · `GET /api/me` → kredi bakiyesi |
| **Kredi entegrasyonu** | `/api/match?user_token=...` → **1 kredi düşer**; kredi 0 → **otomatik maskeleme + credit_pack önerisi** (V8 Credit Exhaustion UX); enterprise = sınırsız; ledger'a her hareket kaydolur |

**Frontend:** Match panelinde **"Firmanızı Tanıtın"** CTA → üyelik modalı (3 adımlı form + KVKK + giriş bölümü) · topbar'da **kredi göstergesi** (onaylı kullanıcıya: kredi sayısı + firma adı).

**Test:** 13 senaryo — **13/13 OK** (ücretsiz domain reddi, KVKK, kurumsal kayıt, duplicate, onaysız login, admin pending/approve/kredi, login token, /api/me, match kredi düşümü 99, kredi 0 maskeleme, credit pack +50, kategoriler=14).

### 🆕 Ajan yol haritası (Y23-Y26 panoya işlendi)
- **Y23** Ödeme entegrasyonu iyzico/Stripe (Scale) — otomatik kredi satışı
- **Y24** E-posta doğrulama + Telegram hoş geldin raporu
- **Y25** product_categories admin paneli (company_capabilities doldurma fırsatı)
- **Y26** Enterprise API key yönetimi + tier bazlı kullanım metrikleri

Pano: **84/102 done** · Docker rebuild sonrası canlı.

## 2026-09-09 — Responsive dashboard tamamlaması ve gerçek tarayıcı regresyonu

- Mevcut, henüz commit edilmemiş HTML korunarak mobil menü ve detay kapatma kontrollerinin eksik CSS/JS bağlantıları tamamlandı.
- 1150 px altında firma detayı artık satır seçimiyle sağdan açılır; kapatma, arka plan tıklaması ve Escape desteklenir. 760 px altında navigasyon açılır menüdür.
- Grid üst satırı içerik yüksekliğine uyar; gövde alanları bağımsız kayar. KPI/grafikler, filtreler ve üst çubuk dar ekranda yeniden düzenlenir.
- CSS v15, JS v14. Yerel canlı sunucu güncel dosyaları sunuyor; bu çalışma ayrıca push edilmedi.
- `scripts/check_dashboard_layout.mjs`: Node yerleşik WebSocket ile ayrı headless Edge CDP oturumunda canlı veriyle doğrulama. 1600, 1366, 1150, 1024, 768, 760, 390, 320 px: yatay taşma yok, üst çubuk çakışması yok, firma detayı ve mobil menü açma/kapama başarılı, JS runtime exception yok.
- Ekran görüntüleri yerel `logs/layout-1600.png` ve `logs/layout-390.png`. Test veri/üyelik/kredi değiştirmez.


## 2026-09-09 — Layout kök fix: grid satır/kolon atamaları (iç içe geçme + kayma sorunu) ✅

**Kök neden:** `.app` grid'inde `grid-template-rows` ve elemanlara `grid-row/column` ataması yoktu:
- Topbar `position:sticky` + grid karışımı → satır hesapları bozuluyordu
- Detail-panel (sağ 320px) alt satıra kayıyordu → body `overflow:hidden` olduğundan **görünmüyordu** ("firma detay sağ tarafta gözükmüyor" şikayetinin nedeni)
- İçerik kartları scroll ile aşağı yukarı hareket ediyordu

**Fix (style.css):**
- `.app`: `grid-template-rows:56px minmax(0,1fr)` + kolonlar `minmax(0,1fr)` (taşma önleyici)
- `.topbar`: `grid-row:1` (sticky kaldırıldı — grid'de gereksiz)
- `.sidebar`: `grid-column:1; grid-row:2`
- `.main`: `grid-column:2; grid-row:2; min-height:0; min-width:0`
- `.detail-panel`: `grid-column:3; grid-row:2`
- **Responsive:** ≤1150px'de detail-panel gizlenir, grid 2 kolona düşer

**Doğrulama (headless, 1600×900):** detail-panel ✓ · companies-section ✓ · KPI render ✓ · cache v13.

## 2026-09-09 — Topbar hizalama fix + match mantığı netleştirmesi

**Topbar fix:** CANLI / Son güncelleme / Yenile iç içe geçiyordu → `.topbar-actions{flex-shrink:0;margin-left:auto;white-space:nowrap}` (sağa sabit) + brand `max-width:280px` ve dar ekran (<1100px) media query (slogan gizlenir, h1 küçülür). cache v7.

**Match mantığı — 3 yön (kullanıcı sorusu üzerine netleştirme):**
MVP puanı sektör komşuluğu + konum + kalite + kanıt verir; "kim istifade eder" hedefe bağlı:
1. **Tedarikçi bul** (A): otomotiv montajcısı → 28 makine / 25 metal / 24 hammadde firmaları
2. **Müşteri bul / satış kanalı** (B): yedek parça üreticisi → 45.20 oto servis + 46.75 toptan + bayiler
3. **Rakip analizi** (C): aynı NACE firmaları

Şu anki `mode=komple` 1+3 karışımı; **yön seçimi** Y22 olarak plana eklendi (buyer profilinde "ne için arıyorsun?" sorusu → skor yorumu değişir).

## 2026-09-09 — UX düzeltmeleri: dropdown dolumu + topbar ortası + nav scroll + canlı Görev Tahtası ✅

**Kullanıcı bildirimi 3 sorunun fix'i:**

| # | Sorun | Kök neden | Fix |
|---|---|---|---|
| 1 | Match "Alıcı Sektörü" dropdown'u boş | `populateMatchNace` yalnız nav tıklamasında çağrılıyordu | `loadAll()` sonuna taşındı — sayfa açılışında dolar |
| 2 | Arama çubuğu en sağa kaymış | `.topbar-search{flex:1}` kutuyu sola sıkıştırıp actions'a itiyordu | `display:flex;justify-content:center` + iç kutu `max-width:460px` — **ortalı** |
| 3 | Nav menüler bölüm kaymıyordu | `showView` yalnızca active-class; section'lara id yoktu | Her nav-item'a `scrollToSection()` bağlandı + id'ler verildi: `companies-section`, `sources-section`, `quality-section`, `tasks-section` (Genel → scrollToTop) |

**Bonus:** Görev Tahtası nav'ı ölüydü (HTML'de bölüm yoktu) → **yeni canlı Görev Tahtası bölümü** eklendi (`/api/tasks`): özet chips (Toplam/Tamamlanan/Plan/Aktif/Engelli) + bekleyen 12 görev (renkli durum badge'leri, ajan sahibi, not) + son tamamlananlar + Yenile butonu. `loadTasks()` loadAll zincirine eklendi.

**Test (headless Edge, virtual-time 12 sn):** dump 181KB · KPI render ✅ · **match-nace options doldu (40 option)** · tasks özet chips=5 ✅ · data-tip=14 ✅ · section id'leri 3/3 ✅ · `node --check` OK · cache-buster v6

## 2026-09-09 — UX/UI paketi: tüm öneriler + hover bilgi notları ✅

**1. Detay paneli aksiyon butonları:**
- **"Kimler Uygun?"** (primary) → firmayı buyer profiliyle match panelinde açar (`matchFor()` → NACE ana grubu seçilir → `runMatchFor(company_id)`)
- "İzlemeye Al/Çıkar" (watchSet localStorage entegrasyonu)
- "Telefon Kopyala" / "E-posta Kopyala" → `navigator.clipboard` + toast bildirimi

**2. Match sonuç CSV export:** `exportMatchCSV()` — client-side blob (firma, ticaret adı, NACE, puan, kırılım, web; BOM'lu UTF-8, Excel uyumlu)

**3. Match satırında yıldız izleme:** `toggleWatch` entegrasyonu (event.stopPropagation ile satır tıklamasından bağımsız)

**4. Özet kartı:** Toplam / Gösterilen / Ortalama Puan / İlişki Dağılımı chips'leri + CSV butonu

**5. Ctrl+K klavye kısayolu** → global aramaya odak; arama kutusunda `Ctrl+K` kbd göstergesi

**6. Toast bildirim sistemi** (`#toast`, kopyalama/izleme/CSV geri bildirimleri)

**7. Hover bilgi notları (tooltip):** CSS-only `.tip[data-tip]` sistemi — 14 noktaya eklendi: 6 nav-item (Genel/Firmalar/Kaynaklar/Kalite/Eşleştirme/Görevler), arama kutusu, CSV/API/Metrikler hızlı erişim, match'in 4 kontrolü (sektör/mod/min puan/buton), match CSV butonu, detay 4 butonu. Sağ kenar çakışması `tip-left` sınıfıyla çözülü.

**Test (headless Edge, gerçek DOM):** dump 172KB · **data-tip=14** · match-section ✓ · fa-handshake=2 · kbd-hint ✓ · tip-left=4 · `node --check` OK · cache-buster v5 · volume mount → rebuild'siz canlıda.

## 2026-09-09 — Match motoru dashboard'a taşındı + UX iyileştirmeleri ✅

**Dashboard "Eşleştirme" paneli (Y19 UI):**
- Sol menüye **"Eşleştirme"** nav-item (scroll entegrasyonlu) + Sektör Dağılımı üstünde `#match-section` kartı
- Kontroller: buyer NACE dropdown (mevcut NACE listesinden otomatik doldurulur), mod (Komple/Aynı), min puan slider, "Eşleştir" butonu
- Sonuç satırları: firma adı+ticaret adı+domain, NACE kodu, **renkli puan çubuğu** (≥80 yeşil / ≥60 mavi / ≥40 turuncu / altı kırmızı), ilişki badge'i (Aynı Sektör mavi / Komple Sektör yeşil / Uzak gri), **4'lü kırılım mini-barları** (sektör/konum/kalite/kanıt, tooltip'li)
- Satıra tıklayınca firma detay paneli açılır (`window._matchItems` indeksleme — JSON quote-escape güvenli)
- Statü banner'ları: bilgi/yükleniyor/uyarı/hata (renkli), boş durum mesajı

**Doğrulama:** `node --check` OK · headless Edge DOM testi: 5 match elementi render ✅ · volume mount sayesinde **rebuild'siz canlıya düştü** (port 8000) · cache-buster v4

**İç ajan gözlemi + koordinasyon:**
- Pano: **81/98 done** · arastirmaci'da 5 plan (Y16/Y17/Y18/Y21 + GİB)
- ✅ "Company Matcher" görevi → **done** (Y19 duplicate)
- 🔒 "İSKUR Scraper" (web_kazima) → **blocked**: Y21 risk analizi + kullanıcı onayı olmadan ajan başlamayacak (koordinatör kararı panoya işlendi)

## 2026-09-09 — Y19: Smart Matching MVP (V9) canlıda ✅

**`GET /api/match`** — buyer-firma eşleştirme motoru (V9 "kime satis yapilir" MVP'si):

| Bileşen | Ağırlık | Kaynak |
|---|---|---|
| Sektör uyumu | 0-45p | NACE ana-grup eşleşmesi + **komşuluk haritası** (`_NACE_KOMSU`: 29→28/25/24 üretim zinciri, 62→63 yazılım-iletişim vb.) |
| Konum | 0-20p | aynı OSB 20 · Ankara 12 |
| Firma kalitesi | 0-25p | `data_quality_score/100 × 25` |
| Kanıt gücü | 0-10p | web 5 + email 3 + telefon 2 |

**Parametreler:** `buyer_id` (DB'den profil) veya `nace` (serbest) · `mode=komple|ayni` · `min_puan` · `mask=1` (KVKK) · limit≤100, offset
**Doğrulama:** 6 senaryo (otomotiv komple/ayni, yazılım+mask, min_puan=99→0, nace yok→400, UUID değil→404) — **hepsi OK**; Docker rebuild sonrası **canlı port 8000'de çalışıyor** (5000 aday, ilk sonuçlar 89.5p).

**Örnek:** otomotiv buyer (29.10) → montaj firmaları 89.5p; mode=komple → makine (28) 78.8p, metal (25) 74.3p gibi **tamamlayıcı tedarik zinciri** önerileri gelir.

### 🆕 Y21 açıldı (İSKUR kurumsal eşleştirme — kullanıcının fikri)
Brief: `workspace/external/BRIEF_Y21_iskur.md`. **Risk uyarıları (koordinatör):**
1. 🔴 Scraping = İSKUR kullanım şartları ihlali riski → **önce resmî API/açık veri kanalı doğrulanacak**
2. 🔴 KVKK: ilan iletişim bilgileri bireysel olabilir → kişi verisi toplanmayacak, firma+sinyal yeterli
3. 🟡 İlan firması adı serbest metin → entity resolution yükü artar
4. 🟡 **"İlan yok = pasif firma" TÜMDÜĞELİMİ** — negatif etiketleme yasak; ilan sinyali yalnızca pozitif (kanıt gücü +) kullanılabilir
5. 🟡 Ticari yeniden dağıtım için lisans/attribution kontrolü şart

Pano: **85/98 done** · Y21 arastirmaci'da.

## 2026-09-09 — Y20: Test kirliliği kökten çözüldü (192 passed) ✅

**3 kök neden:**

| # | Sorun | Fix |
|---|---|---|
| 1 | `connection.py` — `get_engine`'in parametresiz `lru_cache(maxsize=1)`'i: env değişince **eski engine'e kilitli kalıyordu** | URL-bazlı `_engine_for(url)` cache eklendi; `get_engine` cache'siz delegasyon |
| 2 | `test_ankara_osb.py` — **import-time** `DATABASE_URL=sqlite://` set'i: pytest collection'da **tüm suite'i** sqlite'a kilitleyordu (19 fail'in asıl kaynağı) | Module-scope `_sqlite_env` fixture'a taşındı (set + teardown restore) |
| 3 | `test_connection.py` (3) + `test_extra_coverage.py` (1) — çıplak `os.environ` set'leri restore edilmiyordu | Hepsi `monkeypatch.setenv`'e çevrildi (otomatik restore) |

**Doğrulama:**
- Tam suite (`tests/`): **192 passed, 0 failed** (önce: 19 fail + 21 error) — 3.6 sn
- **Yerel PG (localhost:5433) env'yle**: `43 passed` — 2.2 sn (Supabase koşumuna göre ~8x hızlı)
- Artık testler hem Supabase hem yerel PostgreSQL ile koşabilir — Docker Faz 3b'nin tam kazancı

Pano: **83/90 done** · Y20 done.

## 2026-09-09 — Y15: Yerel DB index'leri (~8x ek hızlanma) ✅

**`scripts/setup_local_indexes.py`** (kalıcı araç — restore sonrası tekrar koşulabilir, idempotent):
- `pg_trgm` extension + **7 index**: `legal_name_trgm`, `search_text_trgm` (arama), `er_company_id`, `sr_source_id`, `sr_external_id`, `nace`, `score` (join/sıralama)
- Sonuç: **ILIKE arama 11.6ms → 1.4ms** (~8x ek hızlanma; Supabase'e göre ~600x — 300-900ms'den)
- EXPLAIN OK (total_cost 60.3)

**Doğrulama:** Supabase ile canlı testler **25 passed** (aynı beklenen değer).

**Bulunan bug → Y20 açıldı:** `DATABASE_URL` env override'ı testlerde sqlite fallback'a düşüyor (19 fail) — `connection.py` env/`+psycopg` işleyişini düzeltecek görev (gelistirici).

Pano: 82/90 done · Y20 plan'da.

## 2026-09-09 — Faz 3b: Yerel PostgreSQL + Git init ✅

**Yerel PostgreSQL (Docker, `localdb` profili):**
- `postgres:16-alpine` → `localhost:5433` (db: `huginn`, şifre: `LOCAL_PG_PASSWORD` env, default `huginn_local_dev`), container `huginndatainsights-db-1` healthy
- Taze backup alındı (`backup_20260909_123933.zip`, 23 tablo / 37.197 satır)
- **restore_db.py JSONB fix:** CSV'den gelen Python-repr JSON değerleri (`{'...` tek tırnak) PostgreSQL JSONB parser'ını çökertiyordu → `_json_fix` (parse/NULL) + `_json_param` (psycopg `Json` adapter, SQLite fallback `json.dumps`) eklendi
- Restore sonucu: **14.000 companies + 8.905 entity_resolution + 14.000 source_records + 270 kvkk yedek + 4 sources**
- **Performans: ~30x hızlanma** — COUNT 11.2 ms, ILIKE arama 11.6 ms (Supabase: 300-900 ms network roundtrip)

**Git:**
- Repo init + ilk commit: **631 dosya** (`95c2f11`) + JSONB fix commit'i (`2603f16`)
- **Remote bağlandı ve push edildi:** `github.com/yassuacohen-hub/AI-proje-v1` (private) — GitHub Desktop'ın credential'ı Git Credential Manager üzerinden kullanıldı, ayrıca token gerekmedi
- **Otomatik push kuruldu:** `scripts/git_auto_push.bat` + **"Huginn Git Push"** scheduler görevi (her gün **04:00** — DB backup 03:00'ten sonra): değişiklik varsa commit → pull --rebase → push; yoksa sessiz geçer. Log: `logs/git_push.log`
- `.gitignore` doğrulandı: `.env`, `backups/`, `AI proje v1/`, `*.db` dışarıda (gizli veri repo'ya girmiyor)

**Kullanım:** yerel ortamda çalışmak için `.env.local` dosyasına `DATABASE_URL=postgresql+psycopg://huginn:huginn_local_dev@localhost:5433/huginn` yazmak yeterli. Supabase (üretim) etkilenmedi.

## 2026-09-09 — Docker Faz 2-3: Motor ayağa kalktı, API konteynere taşındı ✅

**Faz 2 (motor):** `docker-desktop` WSL dağıtımı Stopped takılıydı → `wsl --shutdown` + Docker Desktop yeniden başlatma ile çözüldü (**Running**). WSL güncellemesi + yeniden başlatma sonrası bu sıfırlama gerekti.

**Faz 3 (build + çalıştırma):**
- `docker compose build api` → image `huginndatainsights-api` (python:3.12-slim, non-root, HEALTHCHECK) — build OK
- `docker compose up -d api` → **Up (healthy)**, port 8000
- `env_file: .env` runtime inject (image'e gömülmez, `.dockerignore` güvenli) · `restart: unless-stopped` → bilgisayar açılışında otomatik başlar

**Sunucu geçişi (tek 8000 kuralı):**
- Windows uvicorn supervisor emekliye ayrıldı: Startup kısayolu kaldırıldı, bat döngüsü + uvicorn durduruldu
- Artık tek dinleyici: Docker proxy (PID 8384) — `web_server_task.bat` arşivde kalsın (geri dönüş planı)
- Doğrulama: health=200 (konteynerden), kpi 2.9s (soğuk) → **0.39s** (ılık, bağlantı havuzu + cache)

**Yan iş:** change_notify baseline recalc sonrası tazelendi (14.000 firma) — yarın 08:00 raporu sahte alarm üretmez.

**Kazanımlar:** (1) Sunucu artık konteynerde — host bağımsız, Docker restart policy ile süreklilik. (2) Supabase gecikmesi (~300ms) conteynerden de aynı; kalıcı düşük gecikme için sıradaki adım `--profile localdb` yerel PostgreSQL + backup restore.


## 2026-09-09 — P4-4: Kalite Recalc + Performans Profili (done)

**1) Kalite recalc (Y7 temizliği sonrası):** `quality_recalc_fast.py` (set-based, timeout'suz).
- Ortalama skor **53.37 → 40.08** (4.636 çöp e-posta artık boş sayılıyor — skorlar gerçeği yansıtıyor)
- Skor ≥60: 7.721 → 5.428 | Dağılım: 60-79: 4.866, 40-59: 1.465, 20-39: 2.438, 0-19: 4.669

**2) Performans profili (P4-4):** kalıcı araç `scripts/perf_report.py`
- API latency: health 8ms; DB'li endpointler 330-920ms → gecikmenin tabanı **Supabase network roundtrip** (~300ms)
- **EXPLAIN ANALYZE:** arama sorgusu trigram indeks kullanıyor (`idx_companies_legal_name_trgm`, 0.02ms) → DB tarafı hızlı, sorun yok
- **BULGU + FIX:** `api_companies` cache'i yazıyor ama hiç okumuyordu (hit rate %0). `cache_get` sorgu öncesine eklendi → **2914ms → 3.1ms (940x)** tekrar eden isteklerde. TTL 300s, maske durumu anahtarda
- Öneri: kalıcı düşük gecikme için yerel PostgreSQL (Docker Faz 3) veya read-replica

**Sunucu:** uvicorn supervisor (`web_server_task.bat`) ile güncel kodda yeniden başlatıldı, health=200 ✅


## 2026-09-09 — Y7: KVKK Maskeleme + Veri Temizliği (done)

**Kapsam:** KVKK incelemesi (VKN/e-posta görünürlük politikası) → API sunum katmanı kuralları + DB temizliği + testler.

**Bulgular (tarama):**
- DB'de **270 bireysel e-posta** (gmail/hotmail/yahoo/yandex/outlook/icloud) sızıntısı — politika §3.1 ihlali.
- Şahıs adı toplanmıyor (`company_contacts` yalnızca kanal tipi) — §3 uyumlu ✅.
- PII doluluk: tel=8.974, email=8.994→8.724, vkn=40 (total 14.000).

**Uygulanan:**
1. **`web_app.py` maskeleme:** `_mask_email` (`in***@akkor.com.tr`), `_mask_phone` (`905***00`), `apply_kvkk_mask`. İki anahtar: istek bazlı `?mask=1` VEYA kalıcı `DASH_MASK_PII=1` env (müşteri dağıtım modu). Kapsam: `/api/companies`, `/api/companies/export`, `/api/company/{id}`. Unvan/web/VKN açık kalır (PO kararı §4: kamuya açık). Cache anahtarına maske durumu eklendi (maskeli/maskesiz karışmaz).
2. **Temizlik:** `scripts/kvkk_email_temizle.py` — 270 kayıt yedek tabloya (`kvkk_bireysel_email_yedek`) alınıp NULL'landı; teyit: bireysel e-posta = **0**, email sayısı 8994→8724 (tam eşleşme). Telefon/email newline taraması: 0 (temiz).
3. **Politika:** `03_kvkk_ve_veri_politikasi.md`'ye **§4.5 API Dağıtım Katmanı** bölümü (PII matrisi, iki anahtarlı maskeleme, müşteri senaryoları: deneme=maskeli / lisans=tam).
4. **Testler:** 6 yeni test (unit: maske fonksiyonları; API: mask=1 maskeli, default maskesiz, DB'de bireysel e-posta=0 kalıcı güvence).

**Canlı doğrulama:** maskesiz `'905542287200'`/`'info@akkor.com.tr'` → maskeli `'905***00'`/`'in***@akkor.com.tr'` ✅

**⚠️ Ek keşif (önemli):** Maske testi sayesinde ortaya çıktı — "dolu" görünen 4.636 e-posta (`'[]'`, `'null'` vb. JSON çöpü) ve 658 telefon çöp değerdi; `scripts/kvkk_cop_deger_temizle.py` ile NULL'landı (@-siz 3 email dahil). **Gerçek email doluluğu 8.724 değil ≈4.085 (%29).** Sonuç: kalite skorları email'i dolu sanan kayıtlar için yüksek hesaplanmış — **bir sonraki quality recalc'ta skorlar düşebilir** (doğru davranış; kalite ajanına not).



## 2026-09-09 — Web Sunucusu Süreklilik Çözümü (bağlantı kesilme fix)

**Sorun:** `http://127.0.0.1:8000/static/index.html` sık sık bağlantı kesilmesi veriyordu. Kök sebep: sunucu korumasız ön-planda çalışıyordu; process/terminal kapandığında servis ölüyordu.

**Çözüm (telegram bot'taki supervisor modeliyle aynı):**
- `scripts/web_server_task.bat` (YENİ): uvicorn'u sonsuz döngüde çalıştırır; çökerse 10 sn içinde yeniden başlatır, `logs/web_server.log`'a kaydeder.
- Startup kısayolu: `%APPDATA%\...\Start Menu\Programs\Startup\Huginn Web Server.lnk` → bilgisayar açılışında otomatik başlar. (Not: `schtasks /sc onlogon` yönetici izni istediği için kısayol yöntemi seçildi — telegram bot'ta da aynı yol kullanılmıştı.)
- **Dayanıklılık testi:** uvicorn bilerek öldürüldü (10:43:40) → 14 sn sonra `health=200` (otomatik toparlandı). ✅

**Ayrıca:** Y9 testleri yeniden koşuldu → **19 passed** (`tests/test_api_companies.py`, 22.6 sn, 0 fail).

## 2026-09-09 — DENET-4/5/6/7: Proje temizliği ve dosya düzeltme (done)

Kullanıcı onayı ile "yarım kalan temizlik/dosya düzeltme işleri" tamamlandı
(`AI proje v1/V10/07_referanslar/09_proje_denetimi_2026-09-09.md`):

**DENET-4 (geçici dosyalar):** `cop_kutusu_2026_09_09/DENET_arsiv_2026_09_09/`
altına taşındı — scripts geçici 19 dosya (`_tmp*`, `_probe*`, `_test*`,
`temp_match_stats.py`, `_fix_regex2.py`, `--help`), tests `_y9_sonuc*.txt` (3).
35MB `logs/ingest_ostim_detail.log` → gzip (0.65MB), orijinali kaldırıldı.
**DENET-5:** `C:\Projeler\Huginin Data Insights` (yazım hatası klasörü) yalnızca
1 bayt `scripts` içeriyordu, gerçek veri yok → klasör kaldırıldı.
**DENET-6:** `project_state.md` (doğru UTF-8) tek kaynak ilan edildi; mojibake'li
`project_state_iso.md`/`project_state_utf8.md` kopyaları arşivlendi (referans yok,
yalnızca `.obsidian/workspace.json` — o da yeni yolu gösteriyor).
**DENET-7:** Kök SQLite kopyaları (company_master.db, test.db = eski 8313 kayıt,
data/ankara_osb.db = 0B) arşivlendi; `backups/company_master_pre_dedup_*.db`
gerçek yedeği yerinde bırakıldı.
Pano: DENET-4/5/6/7 → done. Toplam **69/76** done. Gereksiz referans kontrolü:
hiçbir py/md/json `_iso`/`_utf8` e bağımlı değil; testler kırılmadı.

---
## 2026-09-09 — Y2 tamamlama: ETL/web_app parite + ASCII kalinti temizligi (done)

**Sorun:** `src/company_master/etl/normalize.py` ESKI ASCII sozlugu kullaniyordu
(TIC./STI./MUH. uretiyordu); web_app.py Y9'da Turkce kisaltmalara gecmisti. DB'de
kaynak bazinda ASCII kalinti: ostim 2452, ivedik 670, baskent 368 (toplam ~3.490).
API okumada web_app yeniden normalize ettigi icin Y9 testleri gizliyordu; ama
DB tuketicileri (change_notify, raporlar) ASCII kaliyordu.
**Cozum:** `etl/normalize.py` `web_app.normalize_company_name` / `extract_trade_name`
fonksiyonlarina delege ediyor (lazy import + ASCII yedek). Geriye donuk backfill:
14.000 firmanin **9.704'u** yeniden normalize edildi (yalnizca degisenler UPDATE).
ASCII kalinti -> **0**. Parite testi (etl == web_app) orneklerde OK.
change_notify baseline **14.000 firma** ile tazelendi (yanlis alarm onlendi).
Y9 testleri: **21 passed**.
**Ivedik notu:** raw `firmalar.jsonl` (3.354 satir) yalniz **14 benzersiz unvan**
iceriyor (ornek: "ALİ EŞREF ERKANİ" x224) — kaynak veri zayif; P1-1 (VPN engeli)
ile iliskili; dedup / tekrar scrape ayri gorev (P4-5). Baskent temiz (761 unique).
Pano Y2 -> done (63/69).

---

## 2026-09-09 — Telegram bot Scheduler + Y2: Ivedik/Baskent ingest (done)

**Bot Scheduler:** `schtasks` (admin) "ErIsIm engellendI" verdi; PowerShell
`Register-ScheduledTask` ile "Huginn Telegram Bot" kuruldu (ONLOGON, restart x3/1dk,
pille de calisir). `schtasks /query` -> Ready. Bot zaten calisiyordu (PID 8240,
baslama 01:53); yeni komutlar icin yeniden baslatma gerekiyor (polling Sureci eski
kodu tutuyor).
**Y2:** `source_records` 10105 -> `scripts/ingest_ivedik_baskent.py` (pipeline.py
deseni: content_hash dedup, ensure_source) `--count` once: ivedik 3134 + baskent 761
yeni. Yazildi: ivedik 3134 + baskent 761 -> source_records **14000**, sources 4.
Normalize on-kontrol: 2000 hamda bos unvan 0, ilk500 kucuk-harf sizinti 0.
`python -m company_master.etl.normalize`: once --only 5 (5/5), sonra tam **4768**.
Dagilim: ostim 9513, ivedik 3134, baskent 761, aso 592 = 14000; kucuk-harfli legal 0.
Pano Y2 -> done (63/69).

---

## 2026-09-09 — Y9: Web API Testleri (done) + Telegram komut aciklamalari

**Baslangic:** `tests/_y9_sonuc2.txt` (01:23) 1 fail / 36 pass: `test_ascii_kisaltma_kalintisi_yok`
`'AKSAM MOTOR ... TIC.LTD...'` kaydinda TIC. kalmis gorunuyordu. Suphe: `_tr_rx_key`
nokta-bitim bakisi `TIC.LTD.` bitisik zincirinde eslesmeyi engelliyordu.
**Kontrol:** normalize dogrudan testte `'AKSAM MOTOR VE DIS TIC.LTD.STI.'` ->
`'AKSAM MOTOR VE DIS TİC.LTD.ŞTİ.'` — TIC. donusmus (mechanizma OK).
`limit=500` probe: 500 kayitta ASCII kalinti **0**. Eski fail kaydi (limit=30, ilk sayfa)
su anki siralamada ilk 30'da degil — API `ORDER BY data_quality_score DESC` ama
test `limit=30` ile ilk sayfayi taradigi icin veri sirasi degisince fail kayboldu;
ayni kayit normalize sonrasi TIC. icermiyor.
**Bitis:** tam suit background job: **37 passed** (`tests/_y9_sonuc3.txt`). Pano Y9 -> done (62/69).
**Ek:** Telegram `/help` + `scripts/README_TELEGRAM.md` aciklamali hale getirildi;
`/degisiklik` `/gunluk` `/izleme` komutlari eklendi (change_notify motoru uzerinden).

---

## 2026-09-09 — Y14: Degisiklik Bildirimi (done)

**Baslangic:** Telegram altyapisi vardi (`telegram_bot.py` send_message,
`telegram_polling.py` komutlar, 09:00 daily rapor) ama Y14'un istedigi
"yeni firma / skor degisimi" tetiklemeli bildirim yoktu.
**Bitis:** `scripts/change_notify.py` (YENI) + `change_notify_task.bat` + Scheduler gorevi.
- Snapshot: `data/orchestrator/change_notify_state.json` (company_id -> ad+skor).
- Modlar: `--baseline` (izleme baslat) / `--check` (degisiklikte bildir, yoksa sessiz)
  / `--daily` (gunluk ozet) / `--no-send` (kuru test).
- Mesaj turleri: yeni firma listesi, skoru esigi asan (±10) degisimler, silinen kayit sayisi.
- Dogrulama: unit senaryo (1 yeni + 1 silinen + 1 skor degisimi) OK; baseline 9.227 firma;
  `--check --no-send` "Degisiklik yok"; gercek `--daily` Telegram'a ulasti (OK).
- Scheduler: "Huginn Change Notify" her gun 08:00 (backup 03:00 sonrasi).

---

# Huginn — Çalışma Günlüğü (İş Notları)

> Her görev için: başlangıç notu → yapılan iş → bitiş notu.
> Görev panosu: `data/orchestrator/task_board.json`

---

## 🟦 GÖREV 1 — P4-6: Backup/Restore Otomasyonu
**Tarih:** 2026-09-08 | **Sahip:** devops | **Başlangıç durumu:** plan

### Başlangıç Notu
- DB: PostgreSQL (Supabase, `aws-0-eu-west-2.pooler.supabase.com`)
- **pg_dump / psql YOK** (Windows'ta kurulu değil) → Python tabanlı export gerekiyor
- `backups/` klasöründe 2026-09-02 tarihli 2 eski `.sql.gz` yedeği var (nasıl alındığı belirsiz)
- Risk: P4-5 (duplicate temizleme) yıkıcı bir işlem → **önce yedek altyapısı kurulmalı**

### Yapılan İş
1. **`scripts/backup_db.py`** — pg_dump gerektirmeyen yedekleyici:
   - SQLAlchemy inspector ile tüm tabloları CSV olarak export eder (22 tablo)
   - `manifest.json` içerir: tarih, maskeli DB URL, kolon şemaları, satır sayıları
   - `--keep N` retention (eski yedekleri siler), `--list` ile mevcut yedekleri listeler
2. **`scripts/restore_db.py`** — geri yükleme:
   - `--dry-run` (içerik gösterir, değişiklik yapmaz), `--drop` (tabloyu düşürüp kurar — yıkıcı)
   - Şema bilgisi manifest'ten; SQLite/PostgreSQL tip dönüşümü yapar
3. **`scripts/backup_task.bat`** + **Windows Task Scheduler görevi "Huginn DB Backup"**
   - Her gün 03:00, `--keep 7`, log: `logs/backup.log`
   - İptal için: `schtasks /Delete /TN "Huginn DB Backup" /F`

### Doğrulama
- ✅ Yedek: `backup_20260908_084933.zip` — 22 tablo, 28.349 satır, 2.97 MB
- ✅ Restore dry-run: manifest okuma ve tablo listeleme başarılı
- ✅ Batch uçtan uca: `backup_20260908_085122.zip` + `logs/backup.log` yazıldı
- ✅ Scheduler: `\Huginn DB Backup` → Ready, sonraki çalışma 09.09.2026 03:00

### Bitiş Notu
**done.** pg_dump yokluğuna rağmen tam otomatik yedekleme kuruldu. P4-5 (yıkıcı dedup işlemi) artık güvenli — yedek garanti altında.

---

## 🟦 GÖREV 2 — P4-5: Veri Seti Doğrulama ve Duplicate Temizleme
**Tarih:** 2026-09-08 | **Sahip:** data | **Başlangıç durumu:** plan

### Başlangıç Notu
- Önceki yedek: `backup_20260908_085122.zip` (geri dönüş garantisi var)
- DB: PostgreSQL (Supabase). `companies` 9.319, `source_records` 10.105, `entity_resolution` 8.905 satır
- Plan: (1) duplicate analizi → (2) rapor → (3) temizlik stratejisi → (4) uygulama + doğrulama

### Yapılan İş
- `scripts/dedup_apply.py`: dry-run/--apply, tek transaction, audit CSV
- Eşleştirme: company_id + kanonik unvan bazlı; **92 duplicate silindi**
- Sonuç: `companies` 9.319 → **9.227**; ardından kalite yeniden hesabı ortalama **22.66 → 64.04** (`quality_recalc_fast.py`, set-based)

---

## 2026-09-09 — Docker Konteynerleştirme Faz 1 (altyapı hazırlığı)

**Tespit:** Docker CLI 29.7.2 + Compose v5.5.1 kurulu; ancak **WSL2 kurulumu bozuk**
(`Wsl/CallMsi/Install/REGDB_E_CLASSNOTREG`) → Docker Linux engine 500 dönüyor.
Eski Dockerfile/compose eski sürümden kalmaydı: Streamlit çağırıyor, `test.db`
mount ediyordu, **`.dockerignore` yoktu (`.env` image'e girecekti!)**, psycopg
requirements'ta eksikti.

**Faz 1 (bu oturum, engine'siz tamamlandı):**
- `Dockerfile`: python:3.12-slim, HEALTHCHECK, non-root, yalnız curl
- `.dockerignore` (YENİ): `.env`, `backups/`, `AI proje v1/`, `__pycache__` image dışı
- `docker-compose.yml` yeniden yazıldı: `api` (ana servis), `db` postgres:16-alpine
  (profile: `localdb`, host port 5433), streamlit/scraper/healthcheck/telegram-bot
  (profile: `legacy`) — `docker compose config` → **OK**
- `requirements-app.txt`: `psycopg[binary]` eklendi (API psycopg3 kullanıyor)
- `.env.example` (YENİ): şablon değişkenler

**Faz 2 (bekliyor — kullanıcı admin onayı):** WSL2 onarımı:
`wsl --install --no-distribution` (yönetici PowerShell) + yeniden başlatma →
Docker Desktop restart → `docker compose build api` → `/api/health` doğrulama.
**Faz 3:** `--profile localdb` ile yerel PG ayağa kaldır, `backup_db.py` dump'ını
`restore_db.py` ile yükle → Y9 testleri + P4-4 EXPLAIN ANALYZE pooler timeout'suz koşar.