# Brief: ORKESTRA-NAMING-AUDIT-02 — Adlandırma Kuralları Denetimi (D-55/D-57)

**Görev ID:** ORKESTRA-NAMING-AUDIT-02  
**Sahip:** İHSAN (Orkestratör)  
**Öncelik:** P1  
**Tahmini Süre:** 2s  
**Dosyalar:** `data/orchestrator/task_board.json`, rapor dosyaları

---

## DURUM
Zincir adımı 2. Önceki: **DOC-V10-AUDIT-01** (tamamlanınca otomatik tetiklenir).

---

## AMAÇ
**D-55** (ürün sahibi raporlama) ve **D-57** (görev başlığı kalıbı) kurallarını denetle:
- Görev başlıkları `[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)` formatında mı?
- Task ID ön eki ALAN ile aynı mı? (`[UI]` → `UI-*`)
- Rapor dosyaları `<TASK>_rapor_<tarih>_<rol>.md` formatında mı?
- Ajan adları (İHSAN, UTKU, SALİH, YASU) büyük harf mı?

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. Task ID / Başlık Kalıbı (D-57)
- Format: `[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)`
- Örnek: `[UI] Ayarlar sayfasını yaz → admin_kullanici_ayarlari.py (2s)`
- task_id ön eki = ALAN
  - Hatalı: `[UI] ... ` ama task_id `API-123` → ❌
  - Doğru: `[UI] ... ` ve task_id `UI-123` → ✅
- ALAN kanonik: UI, API, VERI, TEST, DOC, ALTYAPI, ORKESTRA
- FİİL kanonik: yaz, düzelt, taşı, sil, denetle, ölç, belgele, araştır
- SURE: `\d+[sd]` format (ör: `2s`, `1d`)

### 2. Rapor Dosya Adı (D-55)
- Format: `data/orchestrator/<TASK-ID>_rapor_<YYYY-AA-GG>_<rol>.md`
- Rol: `orkestrator`, `uretim`, `denetim`, `test` (ajan takma adı değil)
- Hatalı: `<ajan_adi>_rapor_...` veya `_raporx_...`
- Doğru: `ALTYAPI-SQLITE-INIT_rapor_2026-09-20_uretim.md`

### 3. Ajan Hitabı Büyük Harf (D-64)
- Gösterim: İHSAN, UTKU, SALİH, YASU (tüm büyük harf)
- Hatalı: `ihsan`, `İhsan`, `Ihsan`, `sahip`, `ajan`
- Doğru: `İHSAN`, `UTKU`, `SALİH`, `YASU`
- Geçerlileri kontrol: rapor başlıkları, task_board "sahip" alanı (küçük harf), title gösterimi (büyük harf)

### 4. Audit Raporu Şeması
- Tablo: task_id | başlık | status | eksik
  - 🟢 uyumlu
  - 🟡 kısmen (örn: başlık D-57'ye uyuyorsa ama rapor yok)
  - 🔴 non-compliant (başlık yanlış)
- Toplam istatistik: X görev, Y% D-57 uyumlu
- Listeleme: Hatalı başlıklar (varsa fix önerisi)

### 5. Test Dosyası
- `tests/test_naming_audit.py` — 8 test
  - `test_task_id_prefix_match` (2 test)
  - `test_baslik_d57_kalibı` (2 test)
  - `test_rapor_dosya_adi` (2 test)
  - `test_ajan_hitab_buyuk_harf` (2 test)
- Tüm testler yeşil: `python -X utf8 -m pytest tests/test_naming_audit.py -v`

---

## DOSYALAR
- Oku: `data/orchestrator/task_board.json`
- Oku: `data/orchestrator/*_rapor_*` (tümü)
- Yaz: `data/orchestrator/ORKESTRA-NAMING-AUDIT-02_rapor_2026-09-20_orkestrator.md`
- Düzenle: `tests/test_naming_audit.py`

---

## DEĞERLENDİRME KRİTERLERİ
✅ D-57 başlık kalıbı kontrol (tablo raporlama)  
✅ Task ID ön eki = ALAN match  
✅ D-55 rapor dosya adı format doğru  
✅ D-64 ajan hitabı büyük harf (gösterim)  
✅ İstatistik: % uyumlu görev  
✅ Test sayısı: 8 (tümü yeşil)  
✅ UTF-8 temiz

---

## SONRAKI GÖREV
ORKESTRA-DECISION-LOG-03 (zincir otomatik tetiklenir)
