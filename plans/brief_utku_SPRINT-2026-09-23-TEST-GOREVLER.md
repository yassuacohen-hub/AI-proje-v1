# Brief: UTKU — Test Görevleri (SPRINT 2026-09-23)

## Görevler (3 adet, 2-3 gün)

### 1. TEST-ADMIN-PERF-01 — Admin Performance Test Suite
**Status:** review → aktif  
**Başlama:** 2026-09-23T12:23:45Z  
**Hedef:** tests/test_admin_performance.py oluştur (admin_panel.py KPI kartları)

**Yapılacaklar:**
- MetricCard → kpi_karti geçişi regression test (11 görünüm)
- KPI hesaplaması (ortalama, max, min)
- Cache TTL = 300s doğrula
- Admin UI tab geçişleri
- Başarı kriteri: 10/10 test PASS

**Dosyalar:**
- tests/test_admin_performance.py (yeni)
- web_dashboard/tabs/admin_panel.py (referans)
- web_dashboard/tabs/admin_performance.py (referans)

---

### 2. TEST-WEBHOOK-KPI-01 — Webhook Monitor Mock
**Status:** review → aktif  
**Başlama:** 2026-09-23T12:23:45Z  
**Hedef:** webhook_monitor mock hedefini güncelle

**Yapılacaklar:**
- st.metric mock → webhook_monitor.kpi_karti mock
- test_webhook_monitor_tab.py güncelle (2 test)
- Webhook log parse testi
- Başarı kriteri: 2/2 test PASS

**Dosyalar:**
- tests/test_webhook_monitor_tab.py (güncelle)
- web_dashboard/tabs/webhook_monitor.py (referans)

---

### 3. UI-SUBHEADER-MUSTERI-01 — Müşteri Yönetimi Subheader
**Status:** review → aktif  
**Başlama:** 2026-09-23T12:23:45Z  
**Hedef:** st.subheader → Section() refactor

**Yapılacaklar:**
- 5 st.subheader → Section(...).render()
- Pazarlama.py kalıbını kullan
- UI regression test
- Başarı kriteri: 92/92 test PASS

**Dosyalar:**
- web_dashboard/tabs/musteri_yonetimi.py (güncelle)
- web_dashboard/tabs/pazarlama.py (kalıp referans)
- tests/test_dashboard_nav.py (regression)

---

## Zaman Tahmini
- TEST-ADMIN-PERF-01: 1 gün
- TEST-WEBHOOK-KPI-01: 4 saat
- UI-SUBHEADER-MUSTERI-01: 2 saat

**Toplam:** 1.5 gün

## Teslim Kriteri
- Tüm testler PASS
- Code review geçmiş (yorum yok)
- task_board.json durum = done

## İletişim
- Sorun? → ihsan @ orchestrator
