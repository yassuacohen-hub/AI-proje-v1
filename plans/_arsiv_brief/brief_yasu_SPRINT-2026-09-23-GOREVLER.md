# YASU — Sprint 2026-09-23 Görevleri

**Sprint:** SPRINT-2026-09-23-PANO-DENETIM  
**Tarih:** 2026-09-23  
**Sahip:** YASU  
**Başlangıç:** 2026-09-23T12:23:45Z  
**Durum:** Aktif

---

## Atanan Görevler (3 adet — P0)

### 1. ALTYAPI-KILIT-OTOMATIK-01
**Başlık:** Otomatik kilit mekanizması  
**Öncelik:** P0  
**Durum:** aktif  
**Açıklama:** Pano denetimi sırasında 6 görev için kilit mekanizması otomatikleştirildi. Sistem sağlığı doğrulaması ve test yazılacak.

**Adımlar:**
- src/company_master/orchestrator/pano_denetim.py kilit seçim mantığını kontrol et
- Otomatik kilit trigger'ının çalışmasını doğrula
- 6 görev için lock state'lerini log'ta kontrol et
- Lock timeout ayarı doğru mu? (Varsayılan: 2h)
- Test case'i yaz (tests/test_lock_auto.py)

**Çıktı:** Lock automation test suite + timing rapor (data/orchestrator/ALTYAPI-KILIT-OTOMATIK-01_rapor_2026-09-23_yasu.md)

---

### 2. ALTYAPI-TETIK-ZAMAN-01
**Başlık:** Tetikleme zamanlaması (scheduling)  
**Öncelik:** P0  
**Durum:** aktif  
**Açıklama:** Pano denetimi ve görev atamalarında timing tutarlılığı. Webhook + tetik_senk synchronization.

**Adımlar:**
- trigger.py çalıştırma saatlerini log'tan çıkar (12:23:45 başlangıç, 12:25 bitiş)
- 6 görev atanması için tetik sırasını doğrula
- Exit 2 handling check: tetik_senk.py exit kodu var mı?
- Gecikme ölçümü (latency): avg < 100ms?
- Test case'i yaz (tests/test_trigger_timing.py)

**Çıktı:** Trigger timing test + latency rapor

---

### 3. ALTYAPI-MOJIBAKE-DIZIN-01
**Başlık:** Dizin yapısı ve encoding (Mojibake fix)  
**Öncelik:** P0  
**Durum:** aktif  
**Açıklama:** Türkçe karakterler (ü, ş, ç, ğ, ı, ö) sistem dosya yollarında düzgün işlensin. UTF-8 encoding tutarlılığı.

**Adımlar:**
- Tüm Python dosyaları `# -*- coding: utf-8 -*-` başlığına sahip mi?
- JSON dosyalarının encoding'i kontrol et (ensure_ascii=False)
- Dosya yollarında Türkçe karakter varsa symlink/shortcut yap
- data/orchestrator/ dizin adında ö/ü vb. varsa test et
- Test case'i yaz (tests/test_encoding_mojibake.py)

**Çıktı:** Encoding test suite + karakter uyum raporu

---

## Bağlamsal Bilgi

**Pano Denetimi Özeti (2026-09-23 12:15-12:27):**
- 377 görev sınıflandırıldı
- 21 review görev detaylı analiz
- Tamamlanma: %63 (239 görev)
- Sahip atama: Tüm görevler atanmış

**Görev Atama Zamanı:** 2026-09-23T12:23:45Z (pano denetimi sırasında)

**İlgili Dosyalar:**
- src/company_master/orchestrator/pano_denetim.py
- src/company_master/orchestrator/trigger.py
- src/company_master/orchestrator/tetik_senk.py
- tests/test_lock_auto.py (yeni oluştur)
- tests/test_trigger_timing.py (yeni oluştur)
- tests/test_encoding_mojibake.py (yeni oluştur)

**D-66 Kararı:** Bypass tetikleme mekanizması (ihsan ile koordine)

**Sprint Hedefi:** 2-3 gün içinde tamamlanacak.  
**Blokaj:** Yok (D-66 kararı parallel çalışacak).

---

## Acil: TRIGGER-LOGGING-CLEANUP (P1 — 30 min)

**Görev:** trigger.py temizlik  
**Açıklama:** Yorum satırlarını sil, logging ekle.  
**Dosya:** src/company_master/orchestrator/trigger.py

**Yapılacaklar:**
1. `# TODO:` ve `# FIXME:` yorumlarını listele
2. Gerekli olanları task_board.json'a not ekle, diğerlerini sil
3. `import logging` ekle ve kilit noktalarına log ekle:
   - Tetik başı: `logging.info(f"Trigger started: {datetime.now()}")`
   - Webhook fire: `logging.info(f"Webhook fired for {task_id}")`
   - Exit: `logging.info(f"Trigger exit code: {exit_code}")`

**Çıktı:** Cleaned trigger.py + logging aktif

---

## İletişim

Herhangi bir sorun/bloker: `data/orchestrator/ALTYAPI-KILIT-OTOMATIK-01_rapor_2026-09-23_yasu.md` dosyasına not ekle.

