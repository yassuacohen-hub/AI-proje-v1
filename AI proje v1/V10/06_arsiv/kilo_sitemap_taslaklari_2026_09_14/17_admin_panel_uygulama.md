# Admin Panel Uygulama Öncelik ve Planı — V10

Bağlantılar: [[15_admin_panel_sitemap]] → Ana menü ağacı
             [[14_po_panel_haritasi]] → Panel ve gösterge haritası
             [[13_po_karar_analizi]] → Detaylı PO karar analizi
             data/orchestrator/task_board.json → Görev durumu
             CHANGELOG → [[CHANGELOG]]

> **Durum:** Onay bekliyor — PO ve mimari onayı gereklidir.
> **Tarih:** 2026-09-14
> **Öncelik:** ADMIN PANEL İNŞAATI ÖNCELİKTEDİR. User Panel planlanmadır.

---

## 1. Uygulama Faza ve Önem Sıralaması

### Faz 1 — Core Admin Deneyimi (Hafta 1-2) — P1

> İlk açılan ekranlar. Kullanıcı deneyimi kritik.

**Hedef:** Admin panel ana akışı çalışır, denlenebilir.

| Sıra | Görev | Menü | Gösterge | PO-BACK |
|---|---|---|---|---|
| 1 | KPI Dashboard tamamlama | 🏠 Ana Sayfa | Coverage (Admin kısmı) | PO-BACK-01 |
| 2 | Sistem Sağlığı paneli | ⚡ Sistem | Data Quality Score | PO-BACK-01 |
| 3 | Canlı Veri SSE admin | 🔴 Canlı Veri | Freshness | PO-BACK-05 |
| 4 | Müşteri listesi ve filtreleme | 👥 Müşteri Yönetimi | Profile Accuracy | PO-BACK-02 |
| 5 | Kullanıcı yönetimi ve yetki | 🛡️ Güvenlik | Entity Accuracy | PO-BACK-07 |

**Çıktı:** Admin panel ana akışında 5 ana menü canlı. Deneme ve onay süreci başlar.

### Faz 2 — Veri ve İşletme Güçlendirme (Hafta 3-4) — P1-P2

> Veri kalitesi ve işletme operasyonları.

**Hedef:** Admin verinin kalitesi ölçülebilir ve yönetilebilir hale gelir.

| Sıra | Görev | Menü | Gösterge | PO-BACK |
|---|---|---|---|---|
| 6 | Kampanya denetimi | 📢 İş Düzenleme | Source Reliability | PO-BACK-03 |
| 7 | Paket fiyat kataloğu | 📦 Paketler | Field Completeness | PO-BACK-04 |
| 8 | Tazelik etiketi + refresh | Her sekmede | Freshness | PO-BACK-05 |
| 9 | Destek merkezi MVP | 🤝 Destek | Evidence Coverage | PO-BACK-06 |
| 10 | API analitiği | 📡 API | API Usage | Mevcut |

**Çıktı:** Veri kalitesi, kampanya denetimi, destek sistemi aktif.

### Faz 3 — Analitik ve Görselleştirme (Hafta 5-6) — P2-P3

> Gelişmiş metrikler ve raporlama.

| Sıra | Görev | Menü | Gösterge | PO-BACK |
|---|---|---|---|---|
| 11 | Duplicate Rate Dashboard | 🎯 Dedup | Duplicate Rate | PO-BACK-09 |
| 12 | Coverage Analytics | 🔍 Keşif | Coverage | PO-BACK-10 |
| 13 | Source Reliability Monitor | 📡 Kaynak | Source Reliability | PO-BACK-11 |
| 14 | Executive Dashboard | 📊 Raporlama | Tüm göstergeler | PO-BACK-08 |

**Çıktı:** Tüm 10 gösterge ölçülebilir. CEO dashboard canlı.

---

## 2. Faz Bağımlılıkları

```
Faz 1 (Core)
├── PO-BACK-01 → Faz 2'nin temelidir
├── PO-BACK-02 → Faz 3 Coverage için gereklidir
├── PO-BACK-03 → Faz 2'ye bağımsız
├── PO-BACK-05 → Faz 1 ve 2'ye bağımsız
└── PO-BACK-07 → Faz 1 Güvenlik için gereklidir

Faz 2 (Güçlendirme)
├── PO-BACK-04 → Faz 3 Pricing için gereklidir
├── PO-BACK-06 → Faz 3 Destek için gereklidir
└── PO-BACK-03 → Faz 2'ye bağımsız (tekrar)

Faz 3 (Gelişmiş)
├── PO-BACK-01 → Faz 1'den bağımlı (REVIZE)
├── PO-BACK-10 → Faz 1'den bağımlı (REVIZE)
├── PO-BACK-08 → Faz 1 ve 2'den bağımlı (REVIZE)
├── PO-BACK-09 → Faz 1'den bağımsız
└── PO-BACK-11 → Faz 1'den bağımsız
```

---

## 3. Mimari Kritik Geri Bildirim Noktaları

Roo Code ve Mimar eşgüdümü gerekli:

| Konu | Kritik Mesaj | Sorumlu |
|---|---|---|
| KPI dashboard | Müşteri + Sistem metrikleri aynı veriden beslenmeli | Roo Code |
| Müşteri yönetimi | Admin okuma, müşteri yazma ayrımı korunmalı | Mimar |
| Kampanya denetimi | Otomatik denetim önce test, sonra prod | Roo Code |
| Tazelik etiketi | Her sekmede tutarlı implementasyon | Roo Code |
| Destek merkezi | Ticket CRUD'dan önce durum makinesi netleşmeli | Mimar |
| Executive Dashboard | Tüm göstergeler measurement before build | Roo Code |

---

## 4. Test Stratejisi

| Faz | Test Türü | Kapsam |
|---|---|---|
| Faz 1 | Unit + Integration | KPI, Sistem, Müşteri, Kullanıcı |
| Faz 2 | Integration + E2E | Kampanya, Paket, Destek, API |
| Faz 3 | E2E + Performans | Dashboard, Analytics, Export |

---

## 5. Riskler ve Mitigasyon

| Risk | Etki | Mitigasyon |
|---|---|---|
| Veri kalitesi ölçülemez | Yüksek | Faz 1'de kalite skoru zorunlu |
| Kullanıcı deneyimi tutarsız | Orta | Her fazda UX denetimi |
| Maliyet artışı kontrolsüz | Yüksek | Maliyet dashboardu Faz 1'de |
| SLA ihlal edilir | Yüksek | Source Reliability Faz 3'te |

---

*Son güncelleme: 2026-09-14*
*Doküman: V10/17_admin_panel_uyglama.md*
*Durum: Onay bekleniyor*
