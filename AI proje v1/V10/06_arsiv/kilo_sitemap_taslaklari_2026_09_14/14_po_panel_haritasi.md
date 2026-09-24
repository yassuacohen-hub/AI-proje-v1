# PO Panel Haritası — Göstergeler, Görevler ve Yol Haritası

Bağlantılar: [[01_sirket_master_ana_belgesi]] · [[12_kalite_metrikleri]] · [[13_po_karar_analizi]] · [[product_owner_kararlari]] · [[PO-01_urun_vizyonu_ve_kararlar]] · [[ROO_ELESTIRI_NOTLARI]] · data/orchestrator/task_board.json · CHANGELOG → [[CHANGELOG]]

---

## 1. Ürün Sahibi Stratejisi — Admin vs Müşteri Panel

Bu belge, ürünün iki ana panelle neden ayrıldığını ve her paneline hangi gösterge ve görevin düştüğünü tek bir yerde toparlar.

### Neden İki Panel?

**Ürün Vizyonu:** "Veriden gelire — tüm operasyon tek panelde"

Tek panel hedefine ulaşmak için **Admin Panel** (iç operasyon, sistem sağlığı, veri kalitesi) ile **Müşteri Panel** (B2B müşterinin gördüğü değer, arama, profil, paket) ayrımı şeffaf olmalıdır. İki panel aynı veri kaynağından beslenir ama **farklı persona**, **farklı KPI** ve **farklı eylem** için tasarlanmıştır.

---

### Admin Panel (Yönetim Paneli)

**Dosya Yolu:** web_dashboard/tabs/admin_*.py

**Sorumluluk Alanları:**
- Sistem yönetimi ve kullanıcı yönetimi
- API analitikliği, performans izleme, maliyet takibi
- Dead Letter Queue (DLQ) yönetimi
- Webhook güvenliği ve izleme
- Veri kalitesi metrikleri (Entity Accuracy, Duplicate Rate, Freshness, Source Reliability)
- Genel sistem sağlığı KPI'ları (Data Quality Score)

**Hedef Kitle:** Veri mühendisleri, sistem yöneticileri, PO, CTO

---

### Müşteri Panel (Müşteri Paneli)

**Dosya Yolları:** web_dashboard/tabs/ana_kontrol.py, paketler.py, pazarlama.py

**Sorumluluk Alanları:**
- B2B müşterinin gördüğü ana dashboard
- Şirket arama ve keşif deneyimi (Search Quality)
- Profil görüntüleme ve doğrulama (Profile Accuracy)
- Paket yönetimi ve kullanım limitleri
- Pazarlama ve lead yönetimi araçları
- Coverage (Ankara B2B şirket yakalanma oranı) görüntüleme

**Hedef Kitle:** B2B müşteriler (satış ekipleri, pazarlama, iş geliştirme)

---

## 2. 10 Temel Göstergenin Panel Dağılımı

| # | Gösterge | Panel | Açıklama | Ülke Sekmesi | Kaynak |
|---|----------|-------|----------|------------|--------|
| 1 | Coverage | Müşteri | Ankara B2B şirketlerinin yakalanma oranı | Müşteri bulut genişliği | 01_sirket_master §16 |
| 2 | Entity Accuracy | Admin | Yanlış bölme/birleştirme oranı | Entity resolution düzeltmeleri | 01_sirket_master §16 |
| 3 | Duplicate Rate | Admin | Mükerrer firma oranı | Dedup araçları | 01_sirket_master §16 |
| 4 | Field Completeness | Her ikisi | Alan doluluk oranı | Admin izler, müşteri görür | 01_sirket_master §16 |
| 5 | Freshness | Admin | Veri güncellik süresi | Veri tazelik izleme | 01_sirket_master §16 |
| 6 | Source Reliability | Admin | Kaynak performansı | Kaynak yönetimi | 01_sirket_master §16 |
| 7 | Search Quality | Müşteri | Arama başarısı oranı | Müşteri arama deneyimi | 01_sirket_master §16 |
| 8 | Profile Accuracy | Müşteri | Profil doğruluğu | Müşteri profil görüntüleme | 01_sirket_master §16 |
| 9 | Evidence Coverage | Her ikisi | Kanıt desteklenme oranı | Admin takibi, müşteri yararlanır | 01_sirket_master §16 |
| 10 | Data Quality Score | Admin | Genel kalite skoru | Sistem sağlığı KPI'sı | 12_kalite_metrikleri |

---

## 3. PO-BACK Görev Revizyonları

Mevcut 8 PO-BACK görevinin panel ataması, kapsadığı göstergeler ve gereken revizyon:

| Task ID | Başlık | Öncelik | Panel | Kapsanan Gösterge(ler) | Revizyon | Yeni Kabul Kriterleri |
|---------|--------|---------|-------|------------------------|----------|----------------------|
| PO-BACK-01 | Admin KPI Dashboard — Sistem Sağlığı | P1 | Admin | Data Quality Score (#10), Freshness (#5) | **Expand** | Freshness alt metrikleri (son sync, ortalama gecikme, SLA ihlali sayısı) eklenmeli; Data Quality Score hesaplama formülü dokümante edilmeli |
| PO-BACK-02 | Müşteri Arama Deneyimi İyileştirme | P1 | Müşteri | Search Quality (#7), Profile Accuracy (#8) | **Clarify** | Arama başarısı tanımı: "ilk 3 sonuçta doğru firma bulunma oranı" olarak netleştirilmeli; Profile Accuracy için alan bazlı doğruluk raporu eklenmeli |
| PO-BACK-03 | Entity Resolution Kalite İzleme | P1 | Admin | Entity Accuracy (#2), Duplicate Rate (#3) | **Expand** | Yanlış bölme/birleştirme örnekleri manuel review kuyruğuna düşmeli; Duplicate Rate için eşik değer (örn. %2) ve alarm tetikleyicisi tanımlanmalı |
| PO-BACK-04 | Müşteri Profil Sayfası Zenginleştirme | P2 | Müşteri | Profile Accuracy (#8), Evidence Coverage (#9) | **Confirm** | Mevcut tasarım onaylandı; Evidence Coverage için "en az 2 kaynak kanıtı" kuralı UI'da göstergeli uyarı olarak eklenmeli |
| PO-BACK-05 | Alan Doluluk Raporu (Field Completeness) | P1 | Her ikisi | Field Completeness (#4) | **Expand** | Admin: alan bazlı eksiklik trend grafiği; Müşteri: profil sayfasında "Bu profil %X tam" rozeti |
| PO-BACK-06 | Paket Kullanım ve Limit Takibi | P2 | Müşteri | Coverage (#1) — dolaylı | **Clarify** | Coverage metriği paket bazlı filtrelenebilmeli; kullanım limiti aşımında proaktif bildirim |
| PO-BACK-07 | Kaynak Performans ve Güvenilirlik | P1 | Admin | Source Reliability (#6) | **Expand** | Kaynak başına: başarı oranı, hata kategorisi, ortalama yanıt süresi, son 30 gün trendi; düşen kaynaklar için auto-alert |
| PO-BACK-08 | Executive Dashboard (Birleşik Görünüm) | P3 | Her ikisi | Tüm göstergeler (özet) | **Defer** | Faz 3'e ertelenmiştir; PO-BACK-01..07 tamamlendikten sonra tasarım revize edilecek |

---

## 4. Açık İşler — Yeni Görevler (KPI Boşlukları)

Mevcut PO-BACK görevlerinde karşılanmayan gösterge boşlukları:

| Yeni Task ID | Başlık | Panel | İlgili Gösterge | Açıklama |
|--------------|--------|-------|----------------|----------|
| PO-BACK-09 | Duplicate Rate Dashboard (Admin) | Admin | Duplicate Rate (#3) | Dedup araçları entegrasyonu; mükerrer firma grafikleri, merge/ayrıştırma eylem butonları, trend geçmişi |
| PO-BACK-10 | Coverage Analytics (Müşteri) | Müşteri | Coverage (#1) | Ankara B2B şirket yakalanma haritası; ilçe/sektör bazlı pokrytlılık; eksik segment uyarıları |
| PO-BACK-11 | Source Reliability Monitor (Admin) | Admin | Source Reliability (#6) | Gerçek zamanlı kaynak sağlığı paneli; SLA takibi; otomatik failover/degrade tetikleyicileri |

> **Not:** PO-BACK-07 "Kaynak Performans ve Güvenilirlik" kapsamında Source Reliability varsa da, PO-BACK-11 **operasyonel monitor + alerting** odaklı ayrı bir görev olarak ayrıştırılmıştır.

---

## 5. Yol Haritası (Fazlar)

### Faz 1 (P1) — Admin Panel KPIs
**Hedef:** Sistem sağlığı ve veri kalitesi tam gözlemlenebilir hale getirilir.
- PO-BACK-01: Admin KPI Dashboard — Sistem Sağlığı
- PO-BACK-03: Entity Resolution Kalite İzleme
- PO-BACK-05: Alan Doluluk Raporu
- PO-BACK-07: Kaynak Performans ve Güvenilirlik
- PO-BACK-09: Duplicate Rate Dashboard (Yeni)
- PO-BACK-11: Source Reliability Monitor (Yeni)

**Çıktı:** Admin panelde 6/10 gösterge canlı; Data Quality Score hesaplanıyor; alarmler aktif.

---

### Faz 2 (P1–P2) — Müşteri Panel KPIs
**Hedef:** Müşterinin gördüğü değer (arama, profil, coverage) ölçülebilir ve iyileştirilebilir hale getirilir.
- PO-BACK-02: Müşteri Arama Deneyimi İyileştirme
- PO-BACK-04: Müşteri Profil Sayfası Zenginleştirme
- PO-BACK-06: Paket Kullanım ve Limit Takibi
- PO-BACK-10: Coverage Analytics (Yeni)

**Çıktı:** Müşteri panelde 4/10 gösterge canlı; Search Quality ve Profile Accuracy hedefleri net; Coverage haritası erişilebilir.

---

### Faz 3 (P3) — Birleşik Executive Dashboard
**Hedef:** Yönetim ve müşteri başarısını tek ekranda birleştiren stratejik görünüm.
- PO-BACK-08: Executive Dashboard (Birleşik Görünüm)

**Bağımlılık:** Faz 1 ve Faz 2'nin tamamlanması (tüm alt metrikler beslenmeli).

---

## 6. Doküman Bağlantıları ve İzlenebilirlik

| Belge | Rol | Bağlantı |
|-------|-----|----------|
| PO-01 | Ürün vizyonu ve karar kayıtları | [[PO-01_urun_vizyonu_ve_kararlar]] |
| Product Owner kararları.txt | PO strateji özeti | [[product_owner_kararlari]] |
| 13_po_karar_analizi.md | V10 PO karar analizi (detaylı) | [[13_po_karar_analizi]] |
| **14_po_panel_haritasi.md** | **Unified panel map (bu belge)** | — |
| data/orchestrator/task_board.json | Görev durumu ve sprint takibi | data/orchestrator/task_board.json |
| ROO_ELESTIRI_NOTLARI.md | Risk defteri ve eleştiri notları | [[ROO_ELESTIRI_NOTLARI]] |
| CHANGELOG.md | Değişiklik geçmişi | [[CHANGELOG]] |
| 01_sirket_master_ana_belgesi | Master veri modeli ve §16 gösterge tanımları | [[01_sirket_master_ana_belgesi]] |
| 12_kalite_metrikleri | Kalite metrikleri tanım ve hesaplama | [[12_kalite_metrikleri]] |

---

## Değişiklik Geçmişi

| Versiyon | Tarih | Yazar | Açıklama |
|----------|-------|-------|----------|
| V10.0 | 2026-09-14 | PO | İlk birleşik panel haritası; 10 gösterge, 8 mevcut + 3 yeni görev, 3 fazlı yol haritası |
