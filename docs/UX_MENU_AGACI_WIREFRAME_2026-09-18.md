# Admin Sol Menü Ağacı — Wireframe / UX / UI (2026-09-18)

> **Görev:** `ADMIN-UX-MENUTREE-01` · **Durum:** onay bekliyor (KAHİN emri: "menü ağacını wireframe ux ui olarak çıkar önce bu çalışmayı bitir sonra onay")
> **Kod yazılmadı.** Bu doküman onaylanınca `web_dashboard/tabs/__init__.py` içindeki `SECTIONS` / `ust_sayfalar()` değiştirilir.
> **Referans:** Claude Console sidebar (KAHİN ekran görüntüsü) + `docs/UX_ADMIN_PANEL_REVIEW_2026-09-14.md` (satır 57-68 önerilen IA).

---

## 1. Mevcut durum (AS-IS) — 6 üst sayfa / 23 alt sekme

```
🏠 Ana Kontrol                      (alt sekme yok)
👥 Müşteri Yönetimi
   ├─ 👥 Müşteriler            sira 0
   ├─ 👤 Kullanıcılar          sira 1
   ├─ 🎫 Destek Merkezi        sira 2
   └─ 💾 Dışa Aktarma          sira 3
📊 Proje Yönetimi
   ├─ 📔 Karar Defteri         sira 0
   ├─ 🤖 Abrakadabra           sira 1
   ├─ 📋 Denetim               sira 2
   ├─ ⚠️ Hatalar               sira 3
   └─ ⛔ DLQ                    sira 4
✅ Veri & Kalite
   ├─ 📊 KPI                   sira 0
   ├─ ✅ Kalite                sira 1
   ├─ 🔍 Arama                 sira 2
   └─ 📈 Executive Dashboard   sira 3
⚙️ Sistem                          ← 9 alt sekme, aşırı yüklü
   ├─ 🧭 Teknik Altyapı        sira 0
   ├─ ⚡ Performans            sira 1
   ├─ 🔌 API                   sira 2
   ├─ 🔗 Webhook               sira 3
   ├─ 💰 Maliyet               sira 4
   ├─ 📡 Canlı Veri            sira 5
   ├─ 🔄 Yenileme              sira 6
   ├─ 🎛️ Ayarlar              sira 7   ← KAHİN: MENÜDEN KALKACAK
   └─ ⏳ Yükleme               sira 8
🦅 Müşteri Önizleme
   ├─ 📦 Paketler              sira 0
   └─ 📢 Pazarlama             sira 1
```

### Tespit edilen 6 problem

| # | Sınıf | Problem | Kanıt |
|---|-------|---------|-------|
| 1 | 🔴 | `Sistem` altında 9 sekme — bilişsel yük sınırı (7±2) aşıldı | `ust="sistem"` 9 kayıt |
| 2 | 🔴 | `Ayarlar` menüde; admin kendi ayarları ağaçta görünüyor | KAHİN emri: kaldır |
| 3 | 🟡 | `Yenileme` + `Yükleme` tam sayfa değil, **ayar**; sekme hak etmiyor | `admin_auto_refresh`, `admin_loading` |
| 4 | 🟡 | `Maliyet` (finans) `Sistem` altında, `Executive` (gelir) `Veri & Kalite` altında — finans dağınık | 2 farklı üst sayfa |
| 5 | 🟡 | `Hatalar` + `DLQ` + `Denetim` operasyonel izleme ama `Proje Yönetimi` altında | `ust="proje_yonetimi"` |
| 6 | 🔵 | `Müşteri Önizleme` üst sayfası adı ürün ekranı gibi değil, geçiş etiketi gibi | `yuzey=YUZEY_HUGINN` notu |

---

## 2. Hedef ağaç (TO-BE) — 5 üst sayfa / 18 alt sekme

```
┌─────────────────────────────────┐
│ 🦅 Huginn Data Insights         │  ← marka başlığı (değişmez)
│ ─────────────────────────────── │
│ 🔍 Bölüm ara…            ⌘K     │  ← mevcut arama (topbar'dan taşınabilir, ayrı iş)
│ ─────────────────────────────── │
│                                 │
│ 🏠 Ana Kontrol                  │  ← alt sekme yok, doğrudan sayfa
│                                 │
│ İŞ                              │  ← grup etiketi (GRUP_IS)
│ 👥 Müşteriler              ⌄    │
│    ├─ Müşteri Listesi           │
│    ├─ Kullanıcılar              │
│    ├─ Destek Merkezi            │
│    └─ Dışa Aktarma              │
│ 💰 Gelir & Paketler        ⌄    │  ← YENİ üst sayfa (finans tek yerde)
│    ├─ Executive Dashboard       │
│    ├─ Maliyet                   │
│    └─ Paketler                  │
│ 📢 Pazarlama                    │  ← alt sekme yok, tek sayfa
│                                 │
│ SİSTEM                          │  ← grup etiketi (GRUP_SISTEM)
│ ✅ Veri & Kalite           ⌄    │
│    ├─ KPI                       │
│    ├─ Kalite                    │
│    └─ Arama                     │
│ ⚙️ Sistem Sağlığı          ⌄    │  ← 9 → 6 sekme
│    ├─ Teknik Altyapı            │
│    ├─ Performans                │
│    ├─ API                       │
│    ├─ Webhook                   │
│    ├─ Canlı Veri                │
│    └─ Hatalar & DLQ             │
│ 📊 Yönetim                 ⌄    │
│    ├─ Karar Defteri             │
│    ├─ Denetim                   │
│    └─ Abrakadabra               │
│                                 │
│ ─────────────────────────────── │
│ ↕ (esnek boşluk)                │
└─────────────────────────────────┘
        (sağ-altta profil popover — ADMIN-UX-PROFILMENU-01)
```

### Değişim tablosu

| Sekme | AS-IS üst | TO-BE üst | Gerekçe |
|-------|-----------|-----------|---------|
| Müşteriler | musteri_yonetimi | `musteriler` | üst sayfa adı kısaldı |
| Kullanıcılar | musteri_yonetimi | `musteriler` | değişmedi |
| Destek Merkezi | musteri_yonetimi | `musteriler` | değişmedi |
| Dışa Aktarma | musteri_yonetimi | `musteriler` | değişmedi |
| Executive Dashboard | veri_kalite | **`gelir`** | gelir metriği, kalite değil |
| Maliyet | sistem | **`gelir`** | finans tek yerde |
| Paketler | musteri_onizleme | **`gelir`** | fiyat/paket = gelir |
| Pazarlama | musteri_onizleme | **üst sayfa oldu** | tek sayfa, alt sekme gerekmez |
| KPI / Kalite / Arama | veri_kalite | `veri_kalite` | değişmedi |
| Teknik Altyapı / Performans / API / Webhook / Canlı Veri | sistem | `sistem` | değişmedi |
| Hatalar + DLQ | proje_yonetimi | **`sistem` (birleşik)** | ikisi de kuyruk/hata izleme |
| Karar Defteri / Denetim / Abrakadabra | proje_yonetimi | `yonetim` | ad netleşti |
| **Ayarlar** | sistem | **MENÜDEN KALKTI** | KAHİN emri → profil popover |
| **Yenileme** | sistem | **Ayarlar sayfasına taşındı** | sayfa değil, ayar |
| **Yükleme** | sistem | **Ayarlar sayfasına taşındı** | sayfa değil, ayar |
| **Müşteri Önizleme** | üst sayfa | **kaldırıldı** | alt sekmeleri dağıtıldı |

**Sayısal etki:** üst sayfa 6 → 5 (**%17 azalma**) · alt sekme 23 → 18 (**%22 azalma**) · en kalabalık grup 9 → 6 (**%33 azalma**).

---

## 3. Bilgi mimarisi kuralları (uygulanacak)

| Kural | Değer |
|-------|-------|
| Maks. alt sekme / üst sayfa | **6** |
| Maks. derinlik | 2 seviye (üst → alt); 3. seviye yok |
| Grup etiketi | `İŞ` ve `SİSTEM` — büyük harf, `--color-text-muted`, 11px |
| Aktif sekme | sol 2px `--color-accent` (#6366F1) çubuk + `--color-surface` zemin |
| Varsayılan açık | yalnız aktif sayfanın üst sayfası; diğerleri kapalı |
| Kendi ayarı | menüde **YOK** — yalnız sağ-alt profil popover |
| İkon | üst sayfa emoji korunur; alt sekme ikonsuz (metin hizası) |

---

## 4. Erişilebilirlik ve klavye (kabul kriteri)

| Madde | Beklenen |
|-------|----------|
| Sekme sırası | topbar → sidebar → içerik → popover |
| Üst sayfa açma/kapama | `Enter` / `Space`, `aria-expanded` doğru |
| Aktif sayfa | `aria-current="page"` |
| Grup etiketi | `role="presentation"` (odaklanılmaz) |
| Kontrast | metin/zemin ≥ 4.5:1 (koyu + açık tema) |
| Hareket | `prefers-reduced-motion: reduce` → açılma animasyonu yok |

---

## 5. Uygulama planı (onay sonrası)

| Adım | Dosya | Test |
|------|-------|------|
| 1. `SECTIONS` içinde `ust`/`sira` alanlarını güncelle | `web_dashboard/tabs/__init__.py` | `tests/test_tabs_ia.py` (yeni) |
| 2. `ust_sayfalar()` anahtar kümesini 5'e indir | `web_dashboard/tabs/__init__.py` | üst sayfa sayısı = 5 |
| 3. `ayarlar` kaydını `ust=None, min_rol="admin"` + menüde gizli işaretle | `web_dashboard/tabs/__init__.py` | `"ayarlar" not in ust_sayfalar()` ve alt sekmelerde yok |
| 4. `yenileme` + `yukleme` render'larını Ayarlar sayfasına bölüm olarak taşı | `ADMIN-UX-AYARLAR-SAYFA-01` | anchor testi |
| 5. `hatalar` + `dlq` tek sekmede birleşik sunum | `web_dashboard/tabs/admin_errors.py` | mevcut testler yeşil |
| 6. Eski URL'ler kırılmasın | `ESKI_URL` eşlemesi | `tab_url_getir` testi |

**Geriye dönük uyum:** `url_path` değerlerinin hiçbiri değişmez; yalnız `ust`/`sira` değişir. Böylece kayıtlı bağlantılar ve derin linkler çalışmaya devam eder.

---

## 6. Onay için KAHİN'e özet

| Sınıf | Bulgu | Oran |
|-------|-------|------|
| 🔴 | `Sistem` menüsü 9 sekmeyle aşırı yüklüydü → 6 | %33 azalma |
| 🔴 | `Ayarlar` menüden kalkıyor, profil menüsüne taşınıyor | 1 sekme |
| 🟡 | Finans dağınıktı (2 yerde) → tek `Gelir & Paketler` grubu | 3 sekme birleşti |
| 🟡 | `Yenileme`/`Yükleme` sayfa değil ayar → Ayarlar sayfasına | 2 sekme |
| 🟢 | Tüm bağlantı adresleri aynı kalıyor, hiçbir link kırılmıyor | %100 uyum |
| 🔵 | Toplam menü kalabalığı 23 → 18 | %22 azalma |

---

## 7. Ek sadeleşme turu (TO-BE v2) — KAHİN sorusu 2026-09-18

### 7.1 Kod sayımı (gerçek durum, `web_dashboard/tabs/__init__.py` SECTIONS)

| Üst sayfa | Alt sekme sayısı | Sekmeler |
|-----------|------------------|----------|
| Ana Kontrol | 0 | — |
| Müşteri Yönetimi | 4 | musteriler, kullanicilar, destek, export |
| Müşteri Önizleme | 2 | paketler, pazarlama |
| Proje Yönetimi | 5 | karar_defteri, abrakadabra, denetim, hatalar, dlq |
| Veri & Kalite | 4 | kpi, kalite, arama, executive |
| Sistem | **9** | teknik_altyapi, performans, api, webhook, maliyet, canli_veri, yenileme, ayarlar, yukleme |
| **Toplam** | **24** | (wireframe §1'deki 23 sayımı 1 eksik) |

### 7.2 Hedef metrik (kabul kriteri olarak sabitlenir)

| Metrik | Hedef | Gerekçe |
|--------|-------|---------|
| Üst sayfa | **5** (maks 6) | Tek bakışta taranabilir; kaydırmasız sidebar |
| Alt sekme / üst sayfa | **≤ 5** (maks 6) | Sekme şeridi taşmasın |
| Toplam menü öğesi | **≤ 15** | 24 → 15 = %38 azalma |
| Derinlik | 2 seviye | 3. seviye yalnız profil menüsünde |
| Ölü sekme kuralı | 30 günde 0 açılış = kaldırılır | Menü kendi kendini budar |

### 7.3 18'den 13'e — 5 ek birleştirme

| # | Öneri | Kazanç | Gerekçe |
|---|-------|--------|---------|
| E1 | `arama` sekmesi kaldırılsın, global **Ctrl+K modal** olsun | −1 | Arama bir yer değil, bir eylem |
| E2 | `yukleme` (loading demo) menüden çıksın, dev bayrağına bağlansın | −1 | Geliştirici demosu, ürün sayfası değil |
| E3 | `kpi` + `executive` → tek **Metrikler** (rol'e göre içerik) | −1 | İkisi de aynı metrik yüzeyi |
| E4 | `hatalar` + `dlq` + `webhook` → tek **Olaylar & Hatalar** | −2 | Üçü de "bir şey ters gitti" yüzeyi |
| E5 | `teknik_altyapi` + `performans` → tek **Altyapı** | −1 | Harita + gecikme aynı hikâye |

Sonuç: 18 → **13**. Başlangıca göre toplam **24 → 13 = %46 azalma**.

### 7.4 TO-BE v2 ağacı

```
🏠 Ana Kontrol
👥 Müşteriler        → Firmalar · Kullanıcılar · Destek · Dışa Aktarım        (4)
💼 Gelir             → Paketler · Pazarlama                                    (2)
📊 Metrikler         → Özet · Kalite                                           (2)
🛠️ Sistem            → Altyapı · API · Olaylar & Hatalar · Maliyet · Canlı Veri (5)
📋 Proje             → Karar Defteri · Denetim · Abrakadabra                   (3)
```
Üst sayfa 6 · alt sekme 16 → E1-E5 uygulanınca ölçüt içinde (üst 6 ≤ 6, her grup ≤ 5).

**Not:** Üst sayfa 5'e inmesi için `Proje` → `Sistem` altına girebilir; ancak orkestratör
yönetimi ayrı ürüne çıkma ihtimali (KAHİN notu) nedeniyle **ayrı üst sayfa kalması önerilir**.

---

## 8. Uygulama kararı — 3 seviye kuralı + Dashboard Overview (KAHİN onayı 2026-09-18)

TO-BE v2 **onaylandı**. Bu bölüm uygulama kurallarını, Streamlit sınırını ve
Overview yeniden düzenlemesini tanımlar.

### 8.1 Derinlik kuralı (yeni demir kural)

| Seviye | Ne | Nerede çizilir |
|--------|-----|----------------|
| 1 | Üst sayfa (Ana Kontrol, Müşteriler, …) | Sidebar grup başlığı |
| 2 | Alt sekme (Firmalar, Kullanıcılar, …) | Sidebar bağlantısı |
| 3 | Sekme içi bölüm | **Sayfa gövdesi** — `st.tabs` / `st.segmented_control` |
| 4+ | ❌ Yasak | `st.expander` ile aynı gövdede çözülür, menüye taşınmaz |

Kısaca: **menüde 2 seviye, sayfada 1 seviye daha = toplam 3.** 4. seviye menüye çıkmaz.

### 8.2 Streamlit sınırının tam nedeni 🔴

**Sınır:** `st.navigation` menüde **en fazla 2 seviye** çizer.

| Kanıt | Detay |
|-------|-------|
| API imzası | `st.navigation(pages, *, position, expanded)` — `pages` yalnız `list[st.Page]` **veya** `dict[str, list[st.Page]]` kabul eder |
| Kısıt | `dict` değeri **düz liste**; `dict[str, dict[str, list[st.Page]]]` desteklenmez |
| Sonuç | Grup başlığı (1) + sayfa (2) = tavan 2. Menüde 3. seviye **API'de yok** |
| Kod yeri | [`app.py`](../app.py:289) `sayfalari_uret()` düz `list[st.Page]` üretir; [`app.py`](../app.py:402) `render_sidebar()` grupları elle çizer |
| Ek kısıt | `st.Page` nesnesinin `parent` / `children` alanı yoktur; hiyerarşi yalnız dict anahtarıyla kurulur |

**Karar:** Bu bir engel değil. 3. seviye **sayfa gövdesinde** `st.tabs` /
`st.segmented_control` ile çizilir; URL tek seviye kalır (`/firmalar`), alt bölüm
sorgu parametresiyle taşınır (`?bolum=iletisim`). `SECTIONS` kayıt yapısı **değişmez**.

### 8.3 Güncel menü ağacı (3 seviye kuralına göre)

```
🏠 Ana Kontrol                                                    [1]
👥 Müşteriler                                                     [1]
   ├─ Firmalar                                                    [2]
   │    └─ (gövde) Liste · Detay · İletişim                       [3]
   ├─ Kullanıcılar                                                [2]
   │    └─ (gövde) Bekleyenler · Aktif · Krediler                 [3]
   ├─ Destek                                                      [2]
   └─ Dışa Aktarım                                                [2]
💼 Gelir                                                          [1]
   ├─ Paketler                                                    [2]
   └─ Pazarlama                                                   [2]
📊 Metrikler                                                      [1]
   ├─ Özet            (E3: kpi + executive birleşti)              [2]
   └─ Kalite                                                      [2]
🛠️ Sistem                                                         [1]
   ├─ Altyapı         (E5: teknik_altyapi + performans)           [2]
   ├─ API                                                         [2]
   ├─ Olaylar & Hatalar (E4: hatalar + dlq + webhook)             [2]
   │    └─ (gövde) Hatalar · DLQ · Webhook                        [3]
   ├─ Maliyet                                                     [2]
   └─ Canlı Veri                                                  [2]
📋 Proje                                                          [1]
   ├─ Karar Defteri                                               [2]
   ├─ Denetim                                                     [2]
   └─ Abrakadabra                                                 [2]
```

Ölçüm: üst sayfa **6** (≤6 ✅) · alt sekme **13** (≤15 ✅) · grup başına maks **6** (≤6 ✅).
Başlangıç 24 → 13 = **%46 azalma**.

Menü dışına alınanlar: `arama` (→ Ctrl+K modal, E1), `yukleme` (→ dev bayrağı, E2),
`ayarlar` (→ profil popover), `yenileme` (→ Overview butonu, §8.4).

### 8.4 Dashboard Overview yeniden düzenlemesi

**Sorun:** Overview şu an sabit metin + KPI kartları. Aksiyon yok, sekmelere giriş yok.

#### 8.4.1 Aksiyon butonları (5 adet — hepsi gerçek iş tetikler)

| # | Buton | Ne yapar (tek satır) | Renk token | Sonuç gösterimi |
|---|-------|----------------------|------------|-----------------|
| 1 | ⟳ **Veriyi Yenile** | Önbelleği temizler, tüm kartları yeniden yükler | `primary-solid` (indigo) | "Son yenileme: 14:32" |
| 2 | ⬇ **Veri Güncelle** | OSINT kazıma hattını tetikler (`scripts/refresh_pipeline.py`) | `info` (mavi) | İlerleme çubuğu → "1.204 kayıt · 2 dk 11 sn" / hata metni |
| 3 | ♥ **Sağlık Kontrolü** | `/metrics` + `/api/webhooks/apify/health` sorgular | `success` (yeşil) | Rozet: 🟢 Sağlıklı / 🔴 API yanıt yok |
| 4 | ⬆ **Dışa Aktar (CSV)** | `/api/companies/export` çağırır, dosyayı indirir | `warning` (amber) | "3.842 satır · 1,2 MB" + indirme düğmesi |
| 5 | ✓ **Bekleyen Onaylar (N)** | `/api/admin/pending` sayısını gösterir, tıkla → Kullanıcılar sekmesi | `danger` N>0 ise, yoksa gri | Rozet üzerinde canlı sayı |

Kurallar: her buton `st.spinner` ile yükleniyor durumu gösterir; sonuç `st.session_state`'e
yazılır ve **aynı ekranda** kalır (rerun sonrası kaybolmaz); son çalışma zamanı butonun
altında `st.caption` olarak durur. Süs buton yok — 5 buton, 5 iş.

#### 8.4.2 Sekme giriş kartları (4 adet)

| Kart | Gider | Üzerinde gösterdiği canlı sayı |
|------|-------|-------------------------------|
| 👥 Firmalar | Müşteriler › Firmalar | Toplam firma |
| 🧑 Kullanıcılar | Müşteriler › Kullanıcılar | Onay bekleyen |
| ⚠️ Olaylar & Hatalar | Sistem › Olaylar & Hatalar | Son 24 sa hata |
| 📊 Metrikler | Metrikler › Özet | Günlük API çağrısı |

#### 8.4.3 Kalite çıtası (9router referansı)

| Kural | Uygulama |
|-------|----------|
| Hizalama | Tek `st.columns(5)` şeridi, `vertical_alignment="center"` |
| Boşluk | Buton şeridi ile kartlar arası `BOSLUKLAR["6"]` (24px) |
| İkon + etiket | Her butonda ikon **solda**, etiket tek kelime + tek isim |
| Durum rengi | Yalnız `tokens.py` token'ları — yeni renk tanımı yok |
| Yükleniyor | `st.spinner` + buton `disabled=True` (çift tıklama yok) |
| Birincil buton | Ekranda **tek** birincil (Veriyi Yenile); diğerleri `type="secondary"` + renkli kontur |

#### 8.4.4 Kısıtlar (KAHİN maddesi 4)

- Yeni bağımlılık **yok** — `get_api` / `post_api` ([`scripts/dash04_api_client.py`](../scripts/dash04_api_client.py:40)) ve mevcut `kpi_karti` kullanılır.
- [`web_dashboard/tabs/__init__.py`](../web_dashboard/tabs/__init__.py:166) `SECTIONS` kayıt yapısı **bozulmaz**; yalnız `ust` / `sira` alanları değişir.
- `url_path` değerleri **sabit kalır**; kaldırılan sekmeler [`ESKI_URL`](../web_dashboard/tabs/__init__.py:530) ile yönlendirilir → bağlantı kırılmaz.

### 8.5 Sonraki faz — Streamlit sınırı nedeniyle ertelenenler 🟡

| # | Madde | Sınırın kaynağı | Geçici çözüm (MVP) |
|---|-------|-----------------|--------------------|
| S1 | Menüde gerçek 3. seviye | `st.navigation` yalnız `dict[str, list[st.Page]]` alır | Sayfa gövdesinde `st.tabs` |
| S2 | Ctrl+K klavye kısayolu | Streamlit'te global kısayol API'si yok | Üst şeritte arama düğmesi + `st.dialog` |
| S3 | Profil popover'ında açılır alt menü | `st.popover` içinde iç içe açılır bileşen kısıtlı | Düz liste + ayraç |
| S4 | Buton üzerinde canlı sayaç (otomatik tazeleme) | `st.fragment(run_every=)` deneysel | 30 sn `cache_data` TTL |
| S5 | Menü öğesi başına açılış sayacı (ölü sekme kuralı) | Telemetri altyapısı yok | `search_events` benzeri tablo — ayrı görev |

---

## 9. Revizyon esnekliği — mevcut durum ve en kısa yol

### 9.1 Tek kaynak var mı? 🟢 Evet

`SECTIONS: tuple[TabTanimi, ...]` — `web_dashboard/tabs/__init__.py` satır 166-527.
Tüm menü buradan üretilir: `ust_sayfalar()`, `alt_sekmeler()`, `gruplar()`, `bolum_ara()`,
`tab_url_getir()`. Sidebar'da elle yazılmış menü yok.

| Revizyon tipi | Dokunulan yer | Efor |
|---------------|---------------|------|
| İsim değişikliği | `baslik=t("menu_x")` → i18n sözlüğünde 1 satır | 🟢 1 dk |
| Sıra değişikliği | `sira=` sayısı | 🟢 1 dk |
| Sayfa taşıma (grup değişimi) | `ust=` alanı | 🟢 1 dk |
| Yeni sayfa | 1 `TabTanimi` bloğu + render fonksiyonu | 🟡 render kadar |
| Sayfa kaldırma | Kayıt silinir + `ESKI_URL` eşlemesi | 🟢 5 dk |
| İkon / açıklama | Aynı blok | 🟢 1 dk |

🟡 **Sınır:** `SECTIONS` bir Python listesi (JSON/YAML değil). KAHİN kendi başına
düzenlemek isterse Python sözdizimi bilmesi gerekir. YAML'a taşıma önerilmiyor —
kazanç düşük, kırılma riski yüksek (tip güvenliği ve `__post_init__` doğrulaması kaybolur).

### 9.2 Ekran görüntüsündeki iki yetenek

| Yetenek | Mevcut durum | Eksik olan | Tahmini diff |
|---------|--------------|------------|--------------|
| **Ctrl+K arama modalı** | 🟢 `bolum_ara(sorgu)` var (`app.py` 234-244), üst şeritte çalışıyor | `st.dialog` sarmalı + sonuçların `Recent` / `Pages` başlıklarıyla gruplanması | ~25 satır, yeni dosya yok |
| **Çift seviyeli kullanıcı menüsü** | 🟢 `_hesap_karti_popover()` var (`app.py` 369-399) | Popover içinde 2. seviye açılır (`st.expander`) + Çıkış/Dil/Yasal maddeleri | ~20 satır |

🔴 **Çelişki uyarısı:** §3 bilgi mimarisi kuralı "maks 2 seviye derinlik" diyor.
Ekran görüntüsündeki `Legal center ›` alt menüsü 3. seviye. Öneri: kural
**"menü ağacında 2 seviye; profil popover'ı istisna"** şeklinde güncellensin.

🟡 **Streamlit sınırı:** Ctrl+K klavye kısayolu Streamlit'te yerleşik değil; `st.dialog`
bir düğmeyle açılır. Gerçek Ctrl+K için küçük bir JS enjeksiyonu gerekir — MVP'de
düğme + `/` kısayolu yeterli, kısayol Faz 2'ye bırakılabilir.
