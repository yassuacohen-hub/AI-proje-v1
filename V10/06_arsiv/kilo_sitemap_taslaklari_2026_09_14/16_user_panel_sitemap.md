# Kullanıcı Paneli Menü Ağaçı (Sitemap) — V10

Bağlantılar: [[15_admin_panel_sitemap]] · [[14_po_panel_haritasi]] · [[13_po_karar_analizi]] · data/orchestrator/task_board.json · CHANGELOG → [[CHANGELOG]]

> **Durum:** TASLAK — öncelik EXCLUSIVELY Admin Panel'dir. Bu belge planlama amaçlıdır, kullanıma hazır değildir.
> **Tarih:** 2026-09-14
> **Amac:** Admin Panel menü yapısını müşteri paneline uyarlayarak bir User Panel sitemap oluşturmak.

---

## 1. Kullanıcı Paneli Menü Ağaacı

### 🏠 Ana Kontrol (Dashboard) — mevcut ✅

```
🏠 Ana Kontrol (ana_kontrol.py)
├── 📊 Müşteri Özet KPI
│   ├── Toplam Firma Sayısı
│   ├── Aktif Kullanıcı Sayısı
│   ├── Toplam Sinyal
│   └── API Çağrı Sayısı
├── 🎯 Kalite Skoru Trendi
│   ├── Son 7/30/90 Gün
│   └── Sektör Bazlı Ortalama
├── 📈 Sektör Bazlı Özet
│   ├── İmalat C (Öncelik)
│   └── Diğer Sektörler
└── ⚡ Hızlı Eylem
    ├── Yeni Firma Ara
    ├── Kalite Düşük Firmalar
    └── Taze Veri Yenile
```

### 📦 Paketler & Abonelik — mevcut ✅

```
📦 Paketler (paketler.py)
├── Aktif Paket Bilgisi
│   ├── Temel (499 TL)
│   ├── Standart (2.999 TL)
│   ├── Profesyonel (7.999 TL)
│   └── Kurumsal (19.999 TL)
├── Fiyat ve Tier Karşılaştırma
├── Upgrade / Downgrade Seçenekleri
├── Ödeme Geçmişi
└── Kullanım Sınırları
    ├── API Çağrı Limiti
    ├── Veri Depolama Limiti
    └── Kullanıcı Licencesi
```

### 📢 Pazarlama & Kampanyalar — mevcut ✅

```
📢 Pazarlama (pazarlama.py)
├── Aktif Kampanyalar
│   ├── Kampanya Adı ve Süresi
│   ├── Discount / Ürün
│   └── Durum (Aktif / Bitmiş)
├── Segment Önerileri
├── Fırsatlar ve Teklifler
└── Kampanya Durum Makinesi
    ├── Taslak → Aktif → Bitmiş → Arşiv
    └── Otomatik Denetim (PO-BACK-03)
```

### 🤝 Destek Merkezi — PO-BACK-06 ile 🔧 PLANLANIYOR

```
🤝 Destek Merkezi (PO-BACK-06)
├── Yeni Bilet Oluştur
│   ├── Konu / Açıklama / Öncelik
│   └── Ekran / Dosya Ekleri
├── Bilet Listesi
│   ├── Açık (Open)
│   ├── Beklemede (Pending)
│   └── Kapalı (Closed)
├── Atama / Kapatma / Eskalasyon
└── SSS ve Bilgi Bankası
```

### 🔍 Veri Keşfi — PO-BACK-10 ile 🔧 PLANLANIYOR

```
🔍 Veri Keşfi (PO-BACK-10)
├── Firma Arama
│   ├── Unvan / VKN / Telefon / E-posta
│   └── NACE / Sektör Filtreleme
├── Kalite Skoru Filtreleme
├── İlçe / Sektör Bazlı Browse
├── Firma Detay / Profil Görüntüleme
└── Kaynak ve Kanıt Görüntüleme
```

### 📊 Raporlama — PO-BACK-05 ile 🔧 PLANLANIYOR

```
📊 Raporlama (PO-BACK-05)
├── Kalite Raporu
│   ├── Alan Bazlı Doluluk
│   └── Kaynak Bazlı Kalite
├── Sektör Raporu
├── Veri Tazelik Raporu (Tazelik Etiketi)
└── CSV / Excel Export
```

### ⚙️ Hesap Ayarları — mevcut ✅

```
⚙️ Hesap Ayarları (admin_panel.py → ayarlar)
├── Kullanıcı Bilgileri
├── Bildirim Tercihleri
├── Tema ve Dil Ayarları
└── API Anahtarı (Gerekirse)
```

### 📋 Segmentler — PO-BACK-02 ile 🔧 PLANLANIYOR

```
📋 Segmentler (PO-BACK-02)
├── Segment Eligibility Skoru
│   ├── 5 Segment Tanımı
│   └── %95+ Uygunluk Hedefi
├── Segment Bazlı Öneriler
└── Segment Değişiklik Geçmişi
```

---

## 2. Durum Tablosu

| Menü Sekmesi | Durum | Kaynak |
|---|---|---|
| 🏠 Ana Kontrol | ✅ Canlı | ana_kontrol.py |
| 📦 Paketler | ✅ Canlı | paketler.py |
| 📢 Pazarlama | ✅ Canlı | pazarlama.py |
| 🤝 Destek Merkezi | 🔧 Planlanıyor | PO-BACK-06 |
| 🔍 Veri Keşfi | 🔧 Planlanıyor | PO-BACK-10 |
| 📊 Raporlama | 🔧 Planlanıyor | PO-BACK-05 |
| ⚙️ Hesap Ayarları | ✅ Canlı | admin_panel.py |
| 📋 Segmentler | 🔧 Planlanıyor | PO-BACK-02 |

---

## 3. Admin Panel ile Uyum Haritası

| Admin Panel Sekmesi | User Panel Sekmesi | Uyum |
|---|---|---|
| Ana Sayfa / Dashboard | 🏠 Ana Kontrol | ✅ Aynı KPI verisi |
| Müşteri Yönetimi | 📋 Segmentler | ⚠️ Sadece okuma |
| Veri & Kalite | 📊 Raporlama | ⚠️ Sadece özet |
| Sistem & Altyapı | ❌ | 🚫 Kapsam dışı |
| Güvenlik & Denetim | ❌ | 🚫 Kapsam dışı |
| Paket Yönetimi | 📦 Paketler | ✅ Aynı veriler |
| Kampanya Yönetimi | 📢 Pazarlama | ✅ Aynı veriler |
| Destek Merkezi | 🤝 Destek Merkezi | 🔧 Henüz yok |
| Arama | 🔍 Veri Keşfi | 🔧 Henüz yok |

---

## 4. İş Akışı (User İçin)

```
1. 🏠 Ana Kontrol → Genel bakış
2. 📦 Paketler → Abonelik durumu
3. 📢 Pazarlama → Aktif fırsatlar
4. 🔍 Veri Keşfi → Firma araştırması
5. 📊 Raporlama → Sonuçlar ve export
6. ⚙️ Ayarlar → Tercihler
```

---

*Son güncelleme: 2026-09-14*
*Doküman: V10/16_user_panel_sitemap.md — DURUM: TASLAK*
*Öncelik: Admin Panel inşa edildikten sonra User Panel planlanacaktır.*
