# ADIM 8 — Görev Üretim Özeti

**Tarih:** 2026-09-25T11:30:00
**Sprint:** 2026-09-25 ~ 2026-10-02 (8 gün)

## Dağıtım

| Kişi | Görev Sayısı | P0 | P1 | P2 | Bağımlılık Sayısı |
|------|--------------|----|----|----|--------------------|
| Utku | 5 | 1 | 4 | 0 | 3 |
| Yasu | 5 | 1 | 4 | 0 | 8 |
| Orkestrator | 5 | 1 | 4 | 0 | 12 |

## Görevler

### Utku Görevleri (UTKU-01 ~ UTKU-05)
- **UTKU-01:** [HUB] Önem alanı ekle (P0, 1d) ← kritik
- **UTKU-02:** [TEST] Brief dosyaları yaz (P1, 2d) ← UTKU-01 sonrası
- **UTKU-03:** [UI] Dashboard render test (P1, 2d)
- **UTKU-04:** [UI] UX audit (P1, 3d) ← UTKU-03 sonrası
- **UTKU-05:** [ALTYAPI] API entegrasyon test (P1, 3d) ← UTKU-03 sonrası

### Yasu Görevleri (YASU-01 ~ YASU-05)
- **YASU-01:** [UI] Sistem grubu küçült (P0, 1d) ← kritik
- **YASU-02:** [UI] Ayarlar profil'e taşı (P1, 2d) ← YASU-01 sonrası
- **YASU-03:** [UI] Gelir & Paketler grubu (P1, 2d) ← YASU-01 sonrası
- **YASU-04:** [DOC] Wireframe raporu (P1, 4d) ← YASU-01/02/03 sonrası
- **YASU-05:** [TEST] Menu visual test (P1, 5d) ← YASU-01/02/03 sonrası

### Orkestrator Görevleri (ORCH-01 ~ ORCH-05)
- **ORCH-01:** [ORKESTRA] Koordinasyon planı (P0, 1d) ← kritik
- **ORCH-02:** [ALTYAPI] Arşiv tasnifi (P1, 2d)
- **ORCH-03:** [DOC] ADIM 8 raporu (P1, 8d) ← tüm görevler sonrası
- **ORCH-04:** [ALTYAPI] Task validation (P1, 3d)
- **ORCH-05:** [REPORT] Görev dağıtım dashboard (P1, 1d) ← ORCH-01 sonrası

## Kritik Path

1. **UTKU-01** (P0, 1d) → UTKU-02 (1d) → UTKU-03 (1d) → UTKU-04 + UTKU-05 (1d paralel) = **5 günlük yol**
2. **YASU-01** (P0, 1d) → YASU-02 + YASU-03 (1d paralel) → YASU-04 + YASU-05 (2d paralel) = **5 günlük yol**
3. **ORCH-01** (P0, 1d) + **ORCH-02** (2d) + **ORCH-04** (3d) + **ORCH-03** (8d) = **8 günlük yol**

**Toplam Sprint:** 8 gün (2026-09-25 ~ 2026-10-02)
**Tamamlanma Tarihi:** 2026-10-02 (perşembe 11:30 UTC+3)

---

**Oluşturdu:** ADIM 8 Görev Üretim Motoru
**Zaman:** 2026-09-25T11:30:00