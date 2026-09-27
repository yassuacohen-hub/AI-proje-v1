# ALTYAPI-TEST-FAILURE-FIX-01 — Brif

**Görev ID:** ALTYAPI-TEST-FAILURE-FIX-01  
**Sahip:** Üretim/Hacim Utku  
**Öncelik:** P1  
**Tahmini Süre:** 4s  
**Çıktı:** `data/orchestrator/ALTYAPI-TEST-FAILURE-FIX-01_rapor_2026-09-20_uretim.md`

---

## Problem

Test suite'de 4 pre-existing test failure mevcut. Bu failureler zincir görevlerin başında düzeltilmesi gerekir; UI-MENUTREE-02 ve sonrası görevler için temiz zemin lazım.

Mevcut durum:
- **Toplam test:** 3972 passed, 4 failed, 16 error
- **Failed:** Test logic hatası (assertion yanlış, mock eksik, vb.)
- **Error:** Altyapı (DB şema, app.py eksik modül, vb.)

**Sonuç:** Zincir başlamadan failureler iki kategoriye ayrılıp tek tek düzeltilmesi gerekir.

---

## İş Maddeleri

1. **Failureları Tespit et:** `pytest tests/ -v 2>&1` çalıştır, 4 failed + 16 error ayrıntı yakalanacak
   - Her failure/error için dosya yolu ve stack trace not et
   - Hataları kök neden bazında grupla (assertion / mock / DB şema / import / vb.)

2. **Her Failure için Kök Neden Raporla:**
   - **Failed:** Assertion, expected vs actual, test mock ayarları, fixture eksikleri kontrol et
   - **Error:** ImportError, ModuleNotFoundError, DB connection, app.py yapı sorunları araştır
   - Not: Gerçek fix yazılacak, bypass/skip yapılmayacak

3. **Düzelt ve Doğrula:**
   - Kök neden bulunduktan sonra kod düzeltmeleri yap (test/altyapı/config)
   - Her düzeltme sonrası ilgili test tekrar çalıştır: `pytest tests/<test_file> -v`
   - Toplam suite'yi tekrar çalıştır: `pytest tests/ -q`

4. **Metrikleri Kaydet:**
   - **Başlangıç:** 3972 passed, 4 failed, 16 error
   - **Hedef:** ≥3970 passed, 0 failed, <5 error (pre-existing error'lar bypass değil)
   - Değişen dosya sayısı, kodu satırı, test sayısı bir tablo yapılacak

5. **Rapor Yaz (D-67 formatı):**
   - **Ne yapıldı:** 4 failure analiz + kök neden raporu + düzeltmeler
   - **Değişen dosyalar:** Etkilenen modüller, dosya yolları, satır farkları
   - **Test sonuçları:** Before/after metrik tablosu
   - **Bulgular:** Kök neden özeti, tekrar riski, alınan aksiyonlar (🟢/🟡/🔴)
   - **Eksik/Erteleme:** Varsa yada yok yazılacak

---

## Kabul Kriterleri

- ✅ 4 failure tekil olarak tespit ve raporlandı
- ✅ Her failure için kök neden yazıldı (dosya + satır + tür)
- ✅ Gerçek fix uygulandı (skip/bypass değil)
- ✅ Test suite sonrası ≥3970 passed
- ✅ Rapor D-67 formatında yazıldı (5 başlık zorunlu)
- ✅ Kilit disiplini: değiştirilen dosya mı, kilitli miydi, değilse özette belirtildi
- ✅ Kodlama denetim: `python scripts/kodlama_denetim.py` temiz çıktı

---

## Kilit Dosyalar

Tahmini etkilenen dosyalar (düzeltmeler sonrası denetlenecek):
- `tests/` — Test dosyaları (fixture, mock, assertion)
- `src/company_master/` — Altyapı modülleri (ihtiyaca göre)
- `web_dashboard/` — Dashboard bağımlılıkları (ihtiyaca göre)

Sonrası: **UI-MENUTREE-02** başlayabilir (paralel mümkün)

---

## Ön Koşullar

- Repo temiz, branch aktif
- Test suite kurulu (`requirements-dev.txt`)
- PostgreSQL erişim (ihtiyaca göre)
