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
