# TEST-BLOKE-FAKTOR-ARASTIRMA-01 — Bulgular

**Tarih:** 2026-09-24  
**Ajan:** Yasu

---

## Bulgu 1: `admin_audit.py` dosyası mevcut değil (ORTA RİSK)

**Kanıt:** `src/company_master/` dizininde `admin_audit.py` dosyası yok.  
**Etki:** API-21 (Şüpheli Aktivite) görevi için temel dosya eksik.  
**Öneri:** `admin_audit.py` modülü oluşturulmadan API-21 başlamamalı. Bu, blokaj değil — ancak orta risk.

---

## Bulgu 2: 5 test dosyasının tümü yok (DÜŞÜK RİSK)

**Kanıt:** `tests/` dizininde `test_api_aktivite.py`, `test_churn.py`, `test_ui_search_gap.py`, `test_admin_audit.py`, `test_ui_upsell.py` bulunamadı.  
**Etki:** Test iskeletleri oluşturulmadan ilerleme zor.  
**Öneri:** Test dosyaları research tamamlandıktan sonra oluşturulacak.

---

## Bulgu 3: `user_activity_log` migrationu tamamlandı ✅ (DÜŞÜK RİSK)

**Kanıt:** `src/company_master/schema/migrations/0017_user_activity_log.sql` mevcut, `test_migration_0017.py` 12/12 geçiyor.  
**Etki:** API-14 başlayabilir, diğer görevler için temel veri yapısı var.

---

## Bulgu 4: `credit_ledger` tablosu DB'de mevcut ✅ (DÜŞÜK RİSK)

**Kanıt:** UI-22 brief'inde `credit_ledger` tablosunun veritabanında mevcut olduğu belirtiliyor.  
**Etki:** UI-22 için girdi hazır, ek migration gerekmez.

---

## Bulgu 5: `api_usage_daily` ve `packages`/`company_packages` tabloları yok (DÜŞÜK RİSK)

**Kanıt:** SSOT EK BULGU-9/10 (satır 329-330).  
**Etki:** Sahte metrik gösterimi (0 basıyor). `UI-ADMIN-SAHTE-KPI-01` ve `UI-ADMIN-SAHTE-EXEC-02` ile giderilebilir.

---

## Sonuç

API-14 başlayabilir. API-16, UI-20, API-21 paralel test hazırlığı için ready. API-21'de `admin_audit.py` eksikliği orta risk. UI-22 için girdi mevcut.