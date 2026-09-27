# Brief: YASU — Altyapı Görevleri + Acil Temizlik (SPRINT 2026-09-23)

## Görevler (3 + 1 acil, 2-3 gün)

### 1. ALTYAPI-KILIT-OTOMATIK-01 — Otomatik Kilit Mekanizması
**Status:** review → aktif  
**Başlama:** 2026-09-23T12:23:45Z  
**Hedef:** Kilitli görevleri otomatik serbest bırak (24h+)

**Yapılacaklar:**
- lock_birak_gorev(task_id): Kilitli görev serbest bırak
- stale_kilitler(hours=24): Eski kilitler tara
- Self-lock guard (depo kilidi kendisini serbest bırakmasın)
- tests/test_lock_auto.py: 9 test
- Başarı kriteri: 9/9 test PASS

**Dosyalar:**
- scripts/kilitler.py (güncelle)
- tests/test_lock_auto.py (yeni)
- task_board.json (referans: locked status)

---

### 2. ALTYAPI-TETIK-ZAMAN-01 — Tetikleme Zamanlaması & Logging
**Status:** review → aktif  
**Başlama:** 2026-09-23T12:23:45Z  
**Hedef:** tetik_senk zamanlaması optimize, logging güçlendir

**Yapılacaklar:**
- --gunluk flag: Günlük tetikleme
- tetik_senk_log.jsonl: Zamanlaması log (exit 0/1/2/3/4)
- Latency < 100ms doğrula
- 14 sapma düzeltildi
- tests/test_trigger_timing.py: 4 test
- Başarı kriteri: 4/4 test PASS, latency < 100ms

**Dosyalar:**
- scripts/tetik_senk.py (güncelle)
- tests/test_trigger_timing.py (yeni)
- HuginnData-TetikSenk zamanlayıcı (referans: cron)

---

### 3. ALTYAPI-MOJIBAKE-DIZIN-01 — UTF-8 Encoding (Türkçe)
**Status:** review → aktif  
**Başlama:** 2026-09-23T12:23:45Z  
**Hedef:** Türkçe karakterleri onar (mojibake)

**Yapılacaklar:**
- --dizin **/*.md: Tüm MD dosyaları tara
- --dry-run varsayılan (güvenli)
- 45 MD tarandi (plans/), 0 değişti
- tests/test_encoding_mojibake.py: 7 test
- Başarı kriteri: 7/7 test PASS

**Dosyalar:**
- scripts/mojibake_onar.py (referans)
- tests/test_encoding_mojibake.py (yeni)

---

### 🔴 ACİL (30 min) — TRIGGER-LOGGING-CLEANUP

**Status:** plan → aktif  
**Hedef:** trigger.py temizlik + logging

**Yapılacaklar:**
1. Satır 296-299: Yorum sil (teslim_et() → onayla() rapor tetikleme fazlalığı)
2. Satır 410: `except: pass` → `logger.exception("Rapor yazma hatası", exc_info=True)`
3. Logging başlı (import logging, uyar, hata seviyeleri)
4. Test: test_d190_mimir_rapor.py (varolan) — regresyon check

**Dosyalar:**
- src/company_master/orchestrator/trigger.py (güncelle)
- tests/test_d190_mimir_rapor.py (regression)

---

## Zaman Tahmini
- ALTYAPI-KILIT-OTOMATIK-01: 8 saat
- ALTYAPI-TETIK-ZAMAN-01: 8 saat
- ALTYAPI-MOJIBAKE-DIZIN-01: 4 saat
- ACİL TRIGGER-LOGGING: 30 min

**Toplam:** 2.5 gün (YASU için yoğun sprint)

## Teslim Kriteri
- Tüm testler PASS
- Code review geçmiş
- trigger.py temizlik tamamlandı (1. gün)
- task_board.json güncellendi

## Dikkat
⚠️ Zamanlaması critical (tetik_senk cron timers):
- HuginnData-TetikSenk zamanlayıcısı denetimle
- Latency ölçümü gerçek koşulda yap
- 14 sapma log'unu sakla (referans)

## İletişim
- Sorun? → ihsan @ orchestrator
