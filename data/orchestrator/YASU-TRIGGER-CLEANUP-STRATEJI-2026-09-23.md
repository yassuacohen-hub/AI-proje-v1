# YASU — TRIGGER-LOGGING-CLEANUP Git & Görev Stratejisi

## Durum Özeti

✓ **trigger.py logging**: print() → logger.info(), silent except → logger.exception(), D-190 yorum blokları silindi
✓ **Testler**: 34/34 passing (gorev_trigger, tetik_senk_log, mojibake_dizin, task_board_kilit)
? **Git**: Staged changes, fakat commit/stash kararı bekliyor
? **Board**: TRIGGER-LOGGING-CLEANUP henüz pano dışında (active orkestrator = ihsan, değil roo)

---

## Strateji: Git Workflow

**Karar: `git commit`**

Sebep (D-77, D-68 kuralları):
- Pano işleri = orkestratör (ihsan) işleri, ama logging cleanup = altyapı (yasu) kodu
- Commit → checksum stabil → tetik_senk.py (D-68 senkronizasyonu) sorun çekmez
- Stash → geçici, progress kayıt edilmez, MIMIR rapor (D-190) context kayıp

**Komut:**
```bash
git add Huginn\ Data\ Insights/src/company_master/orchestrator/trigger.py
git add Huginn\ Data\ Insights/tests/test_*.py
git commit -m "TRIGGER-LOGGING-CLEANUP: logger eklemesi, D-190 yorum blokları silindi, 34 test yeşil"
git push
```

---

## Sonraki 3 Adım (Sırayla)

### 1. TRIGGER-LOGGING-CLEANUP Panoya Ekle
**Kimin:** Orkestratör (ihsan) — D-77 kuralı
**Komut:**
```bash
gorev-at --baslik "[ALTYAPI] trigger.py logging cleanup: print→logger, except→logger.exception (2s)" \
  --ajan orkestrator \
  --task-id TRIGGER-LOGGING-CLEANUP \
  --oncelik P1
```
**Sonra:** Tetik-pano senkronizasyonu (tetik_senk.py) otomatik D-68 kuralıyla güvenli tutar.

### 2. 3 Aktif ALTYAPI Görevini Formal Al
**Kimin:** yasu
**Görevler:**
- ALTYAPI-KILIT-OTOMATIK-01 (P0, sahip=yasu, durum=aktif)
- ALTYAPI-MOJIBAKE-DIZIN-01 (P2, sahip=yasu, durum=aktif)
- ALTYAPI-TETIK-ZAMAN-01 (P2, sahip=yasu, durum=aktif)

**Komut (her görev için):**
```bash
gorev-kutusu al ALTYAPI-KILIT-OTOMATIK-01 --ajan yasu
# Brief oku: plans/brief_yasu_ALTYAPI-KILIT-OTOMATIK-01.md
# Talimat oku: data/orchestrator/.../ALTYAPI-KILIT-OTOMATIK-01_brif.md
# Başla
```

### 3. 2 Review Görevini Onay Kuyruğuna Taşı
**Kimin:** Orkestratör (ihsan) — review → onay D-68 protokolü
**Görevler:**
- MARKA-... (review)
- IMPORT-... (review)

**Komut:**
```bash
gorev-kutusu onayla MARKA-... --ajan ihsan
# Rapor yaz: data/orchestrator/MARKA-..._rapor_2026-09-23_ihsan.md
```

---

## Özet Tablo

| Adım | Kış | Task | Status |
|------|-----|------|--------|
| 1 | Git commit | trigger.py + testler | ✓ Ready |
| 2 | Board ekle | TRIGGER-LOGGING-CLEANUP | → ihsan panoya ekle |
| 3 | Formal al | 3 ALTYAPI (yasu) | → `gorev-kutusu al` |
| 4 | Review → onay | 2 görev | → ihsan review kuyruğu |

**Kural:** D-77 (pano = orkestratör), D-68 (tetik-pano sync), D-87 (tek komut atama).

---

**Hazırlayan:** Orkestratör Asistanı  
**Tarih:** 2026-09-23 13:46 UTC
