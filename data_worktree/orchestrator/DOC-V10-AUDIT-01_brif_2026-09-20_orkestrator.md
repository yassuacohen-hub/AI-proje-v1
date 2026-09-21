# Brief: DOC-V10-AUDIT-01 — V10 Belge Uyum Denetimi

**Görev ID:** DOC-V10-AUDIT-01  
**Sahip:** İHSAN (Orkestratör)  
**Öncelik:** P1  
**Tahmini Süre:** 2s  
**Dosyalar:** `docs/`, `AI proje v1/`, Obsidian vault

---

## DURUM
Zincir başlangıcı (İHSAN'ın 1. görev). Önceki görev yok; hemen tetiklenir.

---

## AMAÇ
V10 yönetim/karar belgelerini audit et:
- AGENTS.md güncellik (D-59/D-60/D-63 kuralları tam mı?)
- decision_log.jsonl — son 20 karar kaydı doğru mu?
- task_board.json — görevler D-57 başlık kalıbına uyuyor mu?
- Obsidian vault (AI proje v1/06_arsiv/) — arşiv dokümantasyonu güncel mi?

---

## TASARIM KONTRATI (Kabul Kriterleri)

### 1. AGENTS.md Denetimi
- D-59/D-60/D-63 (Ajan Rol Tanımları) var mı?
- Kanonik adlar (ihsan, utku, salih, yasu) doğru mu?
- Hitap kuralı (D-64) uygulanmış mı (rol önce)?
- D-57 başlık kalıbı açık mı?
- Rapor zorunluluğu (D-67) belirtilmiş mi?

### 2. decision_log.jsonl
- Son 20 kayıt: `D-XX` numaralı, tarih içeriyor
- Yapı: `{decision_id, date, summary, decision, ...}`
- Yazım tutarlı: Türkçe, kısaltılmış

### 3. task_board.json
- 3 alandan azı: `task_id`, `baslik`, `sahip`, `oncelik`, `durum`, `dosyalar`
- Başlık örnekleri D-57'ye uyuyor mu? `[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)`
- Eksik başlık olanlar listele (raporlamak için)

### 4. Obsidian Vault (AI proje v1/)
- Ana bölümler (6 klasör):
  - `01_Strateji/` — Sürüm planı, MVP, roadmap
  - `02_Tasarım/` — Wireframe, veritabanı şeması
  - `03_Belgeler/` — API, doküman, user guide
  - `04_Raporlar/` — Aylık bulgular, takip
  - `05_Ekip/` — Ajan roller, profil, iletişim
  - `06_Arsiv/` — Eski sürümler, deprecated
- Arşiv klasörü (`06_arsiv/`) güncel olmayan dosya barındırmış mı?

### 5. Rapor İçeriği
- "Audit Sonuçları" başlığı
- Tablo: Dosya | Durum | Bulgular | Önem
  - 🟢 (Uyumlu) / 🟡 (Dikkat) / 🔴 (Acil)
- Eksik/stale dosyalar listesi
- Öneriler

### 6. Test Dosyası
- `tests/test_doc_audit.py` — 6 test
  - `test_agents_md_d59_d60_d63` (2 test)
  - `test_decision_log_yapisi` (2 test)
  - `test_task_board_baslik_kalibı` (2 test)
- Tüm testler yeşil: `python -X utf8 -m pytest tests/test_doc_audit.py -v`

---

## DOSYALAR
- Oku: `docs/AGENTS.md`
- Oku: `data/orchestrator/decision_log.jsonl`
- Oku: `data/orchestrator/task_board.json`
- Oku: `AI proje v1/06_arsiv/` (recursive)
- Yaz: `data/orchestrator/DOC-V10-AUDIT-01_rapor_2026-09-20_orkestrator.md`
- Düzenle: `tests/test_doc_audit.py`

---

## DEĞERLENDİRME KRİTERLERİ
✅ AGENTS.md D-59/D-60/D-63 kuralları tam  
✅ decision_log.jsonl yapı doğru, son 20 kayıt kontrol  
✅ task_board.json başlıklar D-57 kalıbında  
✅ Obsidian vault 6 klasör: durum kontrol  
✅ Rapor 🟢/🟡/🔴 renk sınıflandırması  
✅ Test sayısı: 6 (tümü yeşil)  
✅ UTF-8 temiz

---

## SONRAKI GÖREV
ORKESTRA-NAMING-AUDIT-02 (zincir otomatik tetiklenir)
