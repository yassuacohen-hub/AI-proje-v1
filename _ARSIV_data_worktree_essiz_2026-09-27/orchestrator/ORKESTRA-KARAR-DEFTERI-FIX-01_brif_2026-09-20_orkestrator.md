# ORKESTRA-KARAR-DEFTERI-FIX-01 — Brif

**Task ID:** ORKESTRA-KARAR-DEFTERI-FIX-01  
**ALAN:** ORKESTRA  
**FİİL:** Düzelt  
**NESNE:** decision_log.jsonl (D-XX numaralandırması + zorunlu alanlar)  
**ÇIKTI:** `data/orchestrator/decision_log.jsonl` (temiz 98 kayıt)  
**SÜRE:** 1s  
**Öncelik:** P1  
**Sahip:** İHSAN (Orkestratör)

---

## İş Maddeleri

1. **`data/orchestrator/decision_log.jsonl` oku**: Tüm 98 satırı parse et
2. **Her kayıt için zorunlu alanları kontrol et**:
   - `decision_id`: D-00 … D-99 formatında, null/boş olmayacak
   - `kahin_onayi`: true/false veya açık (varsa)
   - `tarih`: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
   - `ozet`: metin (boş olabilir ama alan olmalı)
3. **Kayıtları düzelt veya ekle**:
   - Eksik `decision_id` → sonraki boş D-XX numarası atanır (D-63 ila D-99)
   - Eksik alanlar → `null` veya varsayılan değer yazılır
4. **Dosya kaydet**: UTF-8, satır sonu LF, BOM yok
5. **Test**: `python -X utf8 scripts/check_board_state.py` — hata olmamalı

---

## Kabul Kriterleri

- ✅ 98 satır valid JSON
- ✅ Her satırda `decision_id` D-XX formatında (null yok)
- ✅ Zorunlu alanlar (`kahin_onayi`, `tarih`, `ozet`) mevcut
- ✅ UTF-8, BOM yok, sözdizimi temiz
- ✅ `python -X utf8` hatasız çalıştırıldı

---

## Bağlamlar

- ORKESTRA-KARAR-DEFTERI-AUDIT-01 (tamamlandı): 🔴 kritik bulgu → bu görev
- YASU denetim raporu: decision_log bozuk, fix gerekli (P1)
