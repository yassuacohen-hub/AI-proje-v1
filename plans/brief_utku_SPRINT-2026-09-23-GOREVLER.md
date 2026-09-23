# UTKU — Sprint 2026-09-23 Görevleri

**Sprint:** SPRINT-2026-09-23-PANO-DENETIM  
**Tarih:** 2026-09-23  
**Sahip:** UTKU  
**Başlangıç:** 2026-09-23T12:23:45Z  
**Durum:** Aktif

---

## Atanan Görevler (3 adet — P0)

### 1. TEST-ADMIN-PERF-01
**Başlık:** Admin performans test  
**Öncelik:** P0  
**Durum:** aktif  
**Açıklama:** Pano denetimi sırasında tespit edilen admin paneli performans sorunları. Test senaryoları yazılacak ve performans ölçümleri alınacak.

**Adımlar:**
- Admin panelinde 377 görev yüklendiğinde sayfa yükleme süresi ölçülsün
- JavaScript profile oluştur (DevTools)
- Bottleneck tespit et ve rapor hazırla
- Performance test case'i commit et (tests/test_admin_perf.py)

**Çıktı:** Performance test suite + rapor (data/orchestrator/TEST-ADMIN-PERF-01_rapor_2026-09-23_utku.md)

---

### 2. TEST-WEBHOOK-KPI-01
**Başlık:** Webhook KPI test  
**Öncelik:** P0  
**Durum:** aktif  
**Açıklama:** Pano denetiminde görev atamaları webhook ile senkronize edildi. Webhook doğrulama ve KPI metriklemeleri.

**Adımlar:**
- Webhook log'ları kontrol et (mimar_rapor.py ve trigger.py çıktılarında)
- 6 görev atanması için webhook fire sayısını doğrula
- Hata varsa kapanış işlemini kontrol et
- Test case'i yaz (tests/test_webhook_kpi.py)

**Çıktı:** Webhook test suite + KPI rapor

---

### 3. UI-SUBHEADER-MUSTERI-01
**Başlık:** Müşteri subheader UI bileşeni  
**Öncelik:** P0  
**Durum:** aktif  
**Açıklama:** UI standardizasyonu: tüm panellerde alt başlık tutarlılığı (subheader styling, alignment).

**Adımlar:**
- web_dashboard/tabs/ dosyalarında subheader kullanımını tara
- CSS standart belirle (padding, font-size, color)
- Tutarsız yerler düzelt
- Regression test yaz

**Çıktı:** UI test + CSS commit

---

## Bağlamsal Bilgi

**Pano Denetimi Özeti (2026-09-23 12:15-12:27):**
- 377 görev sınıflandırıldı
- 21 review görev detaylı analiz
- Tamamlanma: %63 (239 görev)
- Sahip atama: Tüm görevler atanmış

**İlgili Dosyalar:**
- web_dashboard/tabs/admin_panel.py
- tests/test_admin_perf.py (yeni oluştur)
- tests/test_webhook_kpi.py (yeni oluştur)
- tests/test_dashboard_nav.py (mevcut)

**Sprint Hedefi:** 2-3 gün içinde tamamlanacak.  
**Blokaj:** Yok.

---

## İletişim

Herhangi bir sorun/bloker: `data/orchestrator/TEST-ADMIN-PERF-01_rapor_2026-09-23_utku.md` dosyasına not ekle.

