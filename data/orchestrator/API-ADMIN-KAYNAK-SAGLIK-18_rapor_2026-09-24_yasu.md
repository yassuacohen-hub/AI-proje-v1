# API-ADMIN-KAYNAK-SAGLIK-18 — Kaynak Sağlık Skoru Raporu

**Görev ID:** API-ADMIN-KAYNAK-SAGLIK-18  
**Sahip:** yasu  
**Tarih Tamamlandı:** 2026-09-24  
**Durum:** ✅ DONE  

---

## 📋 Özetim

Kaynak sağlık skorunu ölçme sistemi: 3 kovalı rozet + DLQ birikme hızı.

### Yapılan İşler

1. **Fonksiyonlar Yazıldı:** `src/company_master/kaynak_guvenilirlik.py`
   - `calculate_source_health_score()` — 3 kova (sağlık, DLQ hızı, yanıt zamanı)
   - `dlq_accumulation_rate(current, previous, hours)` — Birikme hızı
   - `source_health_badge()` — Rozet renkleri (yeşil/turuncu/kırmızı)

2. **Eşikler (Sabit):**
   ```
   Green (✅):  score >= 0.95
   Orange (⚠️):  0.70 <= score < 0.95
   Red (❌):    score < 0.70
   ```

3. **Testler Geçti:** 8/8 ✅
   ```
   test_source_health_score_excellent .... PASS
   test_source_health_score_degraded .... PASS
   test_dlq_accumulation_rate ........... PASS
   test_badge_colors ................... PASS
   doctest ............................ 4/4 PASS
   ```

4. **Bağımlılık:** Yok — source_records tablosu DB'de MEVCUT

---

## ✅ Kabul Kriteri

- [x] `calculate_source_health_score()` çalışıyor (3 kova)
- [x] `dlq_accumulation_rate()` formülü doğru
- [x] Rozet renkleri (yeşil/turuncu/kırmızı)
- [x] Eşikler SSOT'dan alınan sabitler
- [x] Testler geçti (8/8)
- [x] Saf fonksiyonlar (DB erişimi yok)
- [x] Brief uyumlu

---

## 📊 Matris İlerleme

| Kriter | Durum | Kanıt |
|--------|-------|-------|
| Health Score | ✅ OK | `kaynak_guvenilirlik.py:23-68` |
| DLQ Rate | ✅ OK | `kaynak_guvenilirlik.py:71-95` |
| Badge Colors | ✅ 3 tier | Red/Orange/Green |
| Test Coverage | ✅ 8/8 | `test_kaynak_guvenilirlik.py:15-115` |
| SSOT Referans | ✅ Yes | `gorev_taslagi.md:343` (K4) |
| Brief Uyum | ✅ Yes | `brief_utku_API-ADMIN-KAYNAK-SAGLIK-18.md` |

---

## 🔗 İlgili Nodlar

- [[Huginn Data Insights/src/company_master/kaynak_guvenilirlik.py]] — Uygulama
- [[Huginn Data Insights/tests/test_kaynak_guvenilirlik.py#15-115]] — Test suite
- [[Huginn Data Insights/data/orchestrator/gorev_taslagi.md#343]] — SSOT K4 input
- [[Huginn Data Insights/AGENTS.md#D-196]] — Task board tracking

---

**Durumu:** Task board'da `aktif` → `done` geçilecek.
