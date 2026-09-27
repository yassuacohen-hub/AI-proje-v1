# Brief: ORKESTRA-DECISION-LOG-03 — Karar Defteri Düzenleme & Validasyon

**Görev ID:** ORKESTRA-DECISION-LOG-03  
**Sahip:** İHSAN (Orkestratör)  
**Öncelik:** P1  
**Tahmini Süre:** 2s  
**Dosyalar:** `data/orchestrator/decision_log.jsonl`, `data/orchestrator/bulgu_defteri.md`

---

## DURUM
Zincir adımı 3 (son, İHSAN). Önceki: **ORKESTRA-NAMING-AUDIT-02** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
Karar defterini standardize et:
- decision_log.jsonl yapısı: D-XX numarası, tarih, özet, alınan karar
- bulgu_defteri.md — işlenmemiş bulgular tarama & kapama
- Oran: "X bulgu, Y closed, Z pending"
- Orphaned karar (hiçbir bulguda referans olmayan D-XX) uyarı

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. decision_log.jsonl Yapısı
Şema:
```json
{
  "decision_id": "D-XX",
  "date": "2026-09-20T10:30:00",
  "summary": "Kısa cümle (20-50 kelime)",
  "decision": "Yapılacak aksiyon veya kural",
  "context": "Arka plan (optional)",
  "affected_tasks": ["TASK-1", "TASK-2"],
  "reference": "URL/dosya (optional)"
}
```
- Satır başı numarası `D-XX`: D-01, D-02, ..., D-XX
- Tarih ISO 8601 (UTC)
- Tüm satırlar valid JSON (syntax control)

### 2. Bulgu Defteri (D-67)
- Satır biçimi (şimdi): `tarih | task_id | rol | sınıf | özet | karar`
- Sınıflar: 🔴 acil · 🟡 dikkat · 🟢 tamam · 🔵 öneri
- Karar:
  - `gorev:<TASK-ID>` — yeni görev aç
  - `karar:D-XX` — kararla kapandı
  - `red: <gerekçe>` — reddedildi
- **Boş karar = işlenmemiş** ⚠️

### 3. Validasyon
- decision_log.jsonl:
  - Satır-satır JSON parse (hatalı satırlar listele)
  - D-XX numarası sıralı mı? (gap olabilir ama N→N+1 veya N→N+k)
  - Duplicate D-XX? → Uyarı
  - Tüm `affected_tasks` panoda var mı?
- bulgu_defteri.md:
  - Boş karar hücreler listele
  - Karar başvurusu (D-XX) gerçekte var mı? (decision_log.jsonl'de)
  - Geçersiz rol (orkestrator, uretim, denetim, test dışında)?

### 4. Rapor Şeması
- "Karar Defteri Özeti"
  - ✅ decision_log.jsonl: N kayıt, tümü valid, D-XX range: D-01 → D-XX
  - ⚠️ bulgu_defteri.md: M satır, L processed, P pending (0% tamamlanmış)
  - 🔴 Sorunlar:
    - Geçersiz JSON satırı (kaç tane?)
    - Orphaned D-XX (kaç tane?)
    - İşlenmemiş bulgu (kaç tane?)

### 5. Test Dosyası
- `tests/test_decision_log.py` — 9 test
  - `test_decision_log_json_syntax` (2 test)
  - `test_decision_id_sequential` (2 test)
  - `test_bulgu_defteri_karar_valid` (2 test)
  - `test_orphaned_decision_detection` (2 test)
  - `test_affected_tasks_exist` (1 test)
- Tüm testler yeşil: `python -X utf8 -m pytest tests/test_decision_log.py -v`

---

## DOSYALAR
- Oku: `data/orchestrator/decision_log.jsonl`
- Oku: `data/orchestrator/bulgu_defteri.md`
- Yaz: `data/orchestrator/ORKESTRA-DECISION-LOG-03_rapor_2026-09-20_orkestrator.md`
- Düzenle: `tests/test_decision_log.py`

---

## DEĞERLENDİRME KRİTERLERİ
✅ decision_log.jsonl yapı doğru (all valid JSON)  
✅ bulgu_defteri.md karar hücreleri kontrol (0 pending)  
✅ D-XX orphan check (tüm decision'lar referans)  
✅ Oran: "X bulgu, Y closed, 0 pending"  
✅ Test sayısı: 9 (tümü yeşil)  
✅ UTF-8 temiz

---

## ZINCIR TAMAMLANIŞI
✅ Tüm 3 görev (DOC-V10-AUDIT-01, ORKESTRA-NAMING-AUDIT-02, ORKESTRA-DECISION-LOG-03) bitmişse zincir kapanır. İHSAN teslim eder.
