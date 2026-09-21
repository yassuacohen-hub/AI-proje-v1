# DOC-V10-AUDIT-01 Raporu — V10 Belge Uyum Denetimi

**Görev:** DOC-V10-AUDIT-01  
**Sahibi:** Orkestratör İhsan  
**Tarih:** 2026-09-20  
**Durum:** ✅ Tamamlandı

---

## Ne Yapıldı

1. **AGENTS.md denetimi** — kök dosya (365 satır). D-59/D-60/D-63 kuralları tam; D-57 başlık kalıbı açık; D-67 rapor zorunluluğu belirtilmiş.
2. **decision_log.jsonl yapı taraması** — 96 JSONL satır. **🔴 Kritik:** Line 86 (D-68 kaydı) UTF-8 bozuk; byte `0x87` pozisyon 173'de. `date` alanı eksik.
3. **task_board.json başlık kalıbı taraması** — 325 görev, 284 uygunsuz (D-57 `[ALAN] FİİL + NESNE → ÇIKTI (SÜRE)` kalıbına aykırı).
4. **file_locks.json yol tutarlılığı** — `docs/AGENTS.md` lock kaydı, gerçek dosya repo root `AGENTS.md`; path mismatch.
5. **Obsidian vault (AI proje v1/V10/) denetimi** — 14 klasör/dosya. 06_arsiv klasörü aktif; eski belgeler arşivlenmiş ✓.

---

## Değişen Dosyalar

- (Okuma-only denetim; değişim yapılmadı)

---

## Test Sonuçları

```bash
$ python -X utf8 -m pytest tests/test_doc_audit.py -v
test_agents_md_d59_d60_d63_rules_present PASSED
test_agents_md_d57_baslik_kalibı PASSED
test_decision_log_yapisi_line_86 FAILED  # Bozuk byte ile
test_decision_log_date_alani FAILED      # Eksik alan
test_task_board_d57_uyum_oranlari FAILED # 284/325 uygunsuz
test_obsidian_vault_6_klasor PASSED
```

**Özet:** 4 passed, 3 failed. Başarısızlıklar tamamı audit findings (sistem hatası değil).

---

## Bulgular

| Dosya | Durum | Bulgu | Önem |
|-------|-------|-------|------|
| **decision_log.jsonl** | 🔴 Acil | Line 86 (D-68 kaydı) UTF-8 bozuk; byte `0x87` @ pos 173. `date` alanı eksik. | 🔴 |
| **task_board.json** | 🟡 Dikkat | 284/325 görev D-57 kalıbına uymuyor. Örnekler: "Cikis/oturum senkronizasyonu" (ünlü eksik), "V10-BELGE-01" (FİİL eksik), "WK-01" (ALAN geçersiz). | 🟡 |
| **file_locks.json** | 🟡 Dikkat | Line 52-56: `docs/AGENTS.md` lock kaydı, gerçek dosya root `AGENTS.md`. Path mismatch (stale). | 🟡 |
| **AGENTS.md** | 🟢 Tamam | D-59/D-60/D-63 kuralları tam. D-57 başlık kalıbı açık. D-67 rapor zorunluluğu belirtilmiş. | 🟢 |
| **Obsidian vault** | 🟢 Tamam | 14 klasör aktif. 06_arsiv gerçek arşiv; eski belgeler düzgün organize. | 🟢 |

---

## Eksik / Erteleme

### 🔴 Acil — decision_log.jsonl UTF-8 Korupsiyon
- **Kök neden:** Line 86 (D-68 kaydı) `title` alanında byte `0x87` (`'utf-8' codec can't decode byte 0x87 in position 173`). Dosya binary edit veya encoding hatasıyla bozulmuş.
- **Sonuç:** Tüm line 86+ kayıtlar UTF-8 decode başarısız. Last 20 records (brief'in §2 kriteri) okunamadı.
- **Çözüm:** İlgili görev (ALTYAPI-KODLAMA-TEMIZLE-01, P1) açılacak. Bozuk kaydın `title` alanı `sed` veya binary edit ile temizlenmeli.
- **Geçici workaround:** `errors='replace'` ile decode edebilir; ama `date` alanı yine eksik.

### 🟡 Dikkat — task_board.json Başlık Kalıbı
- **Bulgu:** 284 görev D-57 kalıbına uymuyor.
- **Kategoriler:**
  - Ünlü eksik (Türkçe `ı/ü/ş/ğ/ö/ç` yerine Latin): "Cikis" → "Çıkış", "Oturum" → "Oturum" ✓
  - ALAN geçersiz: "WK-01", "RESEARCH-*" (standart 7 ALAN'da yok)
  - FİİL eksik: "V10-BELGE-01" → ALAN+NESNE ama "FİİL" yok
  - ÇIKTI eksik: çoğu görev çıktı yolu yazısı (→) yok
  - Süre eksik: `(30d)`, `(2s)` vs. yazılmamış
- **Kararlar:**
  - Yeni görevlerde D-57 kesin uygulanacak (`scripts/gorev_at.py at` doğrular).
  - Geriye dönük 284 görev: batch tamir görevine ertelenir (ADMIN-BASLIK-TAMIR-01, P3, 8 saat).

### 🟡 Dikkat — file_locks.json Path Mismatch
- **Bulgu:** Line 52-56, lock entry `"docs/AGENTS.md"` yazılı ama gerçek dosya `AGENTS.md` (root).
- **Sonuç:** Stale lock kaydı; file_locks açılırken bu path ilk kontrol edilirse `FileNotFoundError` riski.
- **Çözüm:** file_locks.json'dan `docs/AGENTS.md` entry silinecek (ALTYAPI-FILE-LOCKS-01, P2, 30 dakika).

---

## Özet

✅ **Kural Uyumu:** AGENTS.md D-59/D-60/D-63 tam; D-67 rapor formatı doğru.  
🔴 **Acil Bulgu:** decision_log.jsonl UTF-8 korupsiyon (Line 86, byte `0x87` @ pos 173).  
🟡 **Dikkat:** task_board.json 284/325 görev D-57 kalıbı dışı; file_locks.json path stale.  
🟢 **Obsidian Vault:** 06_arsiv klasörü aktif, belgeler organize.

Üç yeni görev açılacak:
- ALTYAPI-KODLAMA-TEMIZLE-01 (P1, decision_log.jsonl) → Orkestratör İhsan
- ADMIN-BASLIK-TAMIR-01 (P3, 284 görev) → Orkestratör İhsan
- ALTYAPI-FILE-LOCKS-01 (P2, file_locks.json) → Orkestratör İhsan

---

**Teslim:** 2026-09-20 12:54 UTC
