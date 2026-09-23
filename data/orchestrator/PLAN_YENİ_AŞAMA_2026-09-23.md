# Yeni Planlama — 2026-09-23 Sonrası Roadmap

**Hazırlayan:** Orkestratör (İhsan)  
**Tarihi:** 2026-09-23T07:21:00Z  
**Önceki Tamamlanan:** ORKESTRA-VAULT-TEKRAR-01 (vault analizi) + DASH-UX-02a-SECTIONS (done)  
**Blokaj Durumu:** Temiz — başlamaya hazır  

---

## Bağlam

Geçen turda:
- ✅ P2/P5 iş dağıtımı yapıldı (PLAN_P2_P5_DAGITIM_2026-09-23.md)
- ✅ Vault mekanizması denetlendi (3 sorun, 4 iyileştirme)
- ✅ DASH-UX-02a-SECTIONS tamamlandı (Utku, durum: done)
- ✅ Geçici dosyalar ve duplikeler temizlendi
- ✅ Blokajlar kaldırıldı (AGENTS.md merge, ADMIN-UX-MENUTREE başlama)

Mevcut durum: **Yeşil**. İş akışı sürüyor.

---

## Aktif İşler (Şu Anda Yürüten)

| Görev ID | Sahip | Durum | Başlangıç | Hedef Bitis |
|----------|-------|--------|-----------|------------|
| ADMIN-UX-MENUTREE-01 | Utku | aktif | 2026-09-22 | 2026-09-24 |
| TEST-8-KIRMA | Salih | aktif | 2026-09-20 | 2026-09-25 |
| TEST-71-KAYIP | Salih | aktif | 2026-09-20 | 2026-09-26 |
| ALTYAPI-CACHE-OPT-01 | Yasu | aktif | 2026-09-21 | 2026-09-27 |
| GRAPH-FIX-02 | Yasu | aktif | 2026-09-20 | 2026-09-28 |
| ADMIN-UX-SIDEBAR-TAB | Utku | aktif | 2026-09-23 | 2026-09-25 |

**Beklenen Toplam Bitis:** 2026-09-28 (5 gün)

---

## Sonraki Başlatılacak İşler (Kuyruğa Hazır)

### 🔴 Kritik (P0/P1) — Hemen sonra başlat

1. **AGENTS.md UU Çatışması Çözümü** (İhsan)
   - **Süre:** 1–2 saat (merge + test)
   - **Blokaj:** Yok (temizlendi)
   - **Başlangıç:** 2026-09-24T08:00Z
   - **Bitis:** 2026-09-24T10:00Z
   - **Tavsiye:** `git merge origin/UU` + conflict resolve + AGENTS.md yukarı çek

2. **8 Kırılan Test Köklendirme** (Salih, devam)
   - **Durum:** aktif (başladı, %40 tamamlanan)
   - **Beklenen:** 2026-09-25T16:00Z
   - **Çıkmazlar:** Prometheus timeout pattern (D-123 ile ilgili)

3. **71 Kayıp Test Araştırması** (Salih, devam)
   - **Durum:** aktif (mapping yapılıyor)
   - **Beklenen:** 2026-09-26T12:00Z
   - **Tavsiye:** pytest baseline snapshot'ı 2024 tarihinde vs 2026 karşılaştır

---

### 🟡 Yüksek (P2) — Ardından başlat (2026-09-25)

4. **ADMIN-UI-CACHE-01** (Yasu)
   - **Tavsiye:** ALTYAPI-CACHE-OPT-01 bittikten sonra başla
   - **Hedef:** cache hit rate %30 → %60
   - **Beklenen:** 2026-09-27
   - **Brief:** Henüz yazılmadı — yazmak gerek

5. **GRAPH-CANONICAL-SECER-02** (Yasu)
   - **Tavsiye:** GRAPH-FIX-02 bitince başla
   - **Hedef:** Orphan nod backlink'lerini otomatik çöz
   - **Beklenen:** 2026-09-29
   - **Brief:** Henüz yazılmadı — yazmak gerek

6. **VAULT-CLEANUP-BATCH** (Orkestratör)
   - **Tavsiye:** ORKESTRA-VAULT-TEKRAR-01 raporu uygulanmalı
   - **Eylemler:**
     - [ ] `.ALARM.json` 25 dosya sil (5 dakika)
     - [ ] UTF-8 encoding temizliği tüm ajanlar (15 dakika)
     - [ ] `vault_archive_old_records()` çalıştır (10 dakika)
   - **Beklenen:** 2026-09-24T11:00Z

---

### 🟢 Normal (P3+) — Hafta sonu ya da sonraki sprint

7. **UI-ADOPT-MENUTREE-FASE-2** (Utku)
   - **Hedef:** Sidebar tab navigasyonu (ADMIN-UX-SIDEBAR-TAB sonrası)
   - **Beklenen:** 2026-10-01

8. **PERFORMANCE-PROFILING-01** (Yasu)
   - **Hedef:** Dashboard load time <2s (cache + CDN analiz)
   - **Beklenen:** 2026-10-02

9. **GRAPH-CANONICAL-EXPANSION** (Ajan TBD)
   - **Hedef:** 200 orphan hub bağlantı çöz
   - **Scope:** Büyük — 3-5 gün
   - **Beklenen:** 2026-10-05+

---

## Ajan İş Yükü Özeti (Sonraki 5 Gün)

| Ajan | Görev Sayısı | Durum | Kapasite |
|------|-------------|--------|----------|
| **Utku** | 2 (MENUTREE-01, SIDEBAR-TAB) | aktif | 80% |
| **Salih** | 2 (TEST-8/71) | aktif | 100% 🔴 |
| **Yasu** | 3 (CACHE-OPT, GRAPH-FIX, CACHE-UI) | aktif | 90% |
| **İhsan** | 1 (AGENTS.md + VAULT-CLEANUP) | aktif | 60% |

**Engel:** Salih aşırı yüklü (test köklendirme uzun). Tavsiye: P3 işler geciktir.

---

## Kararlar & Tetikler

### 1️⃣ AGENTS.md Çatışması (KAHIN Kararı Beklemede)

**Durum:** `git status` şunu gösteriyor:
```
both modified: AGENTS.md
```

**Durum:** UU ve trunk branch'leri çatışıyor (Türkçe kurallar bölümü).

**Tavsiye (Orkestratör):**
- [ ] `git merge origin/UU --no-commit` yap
- [ ] Conflict bölümü: `## Çoklu Ajan Koordinasyonu` satırını kontrol et
- [ ] Trunk'ın n8n-as-code bölümü + UU'nun Ajan kuralları → birleştir
- [ ] `git add AGENTS.md && git commit -m "AGENTS.md çatışması çöz"`
- [ ] Test: `python -m pytest tests/agents_rules_test.py` (varsa)
- **Başlangıç:** 2026-09-24T08:00Z
- **Bitis:** 2026-09-24T10:00Z

**Sorumlu:** İhsan (D-68 pull → merge yetkisi)

---

### 2️⃣ Test Köklendirme Hızlandırması

**Sorun:** Salih 8 kırılan test + 71 kayıp test ile %100 meşgul.

**Tavsiye:**
- Salih'e yardımcı atanabilir mi? (**Yasu** %10 free'se test mapping, veya **Utku** %20 free'se test fix)
- Paralel test koşumu: `pytest -n 4` (xdist)
- Root cause database: `tests/_bakim.xlsx` oluştur (mapping + status)

**Başlangıç:** 2026-09-24T10:00Z
**Beklenen Hızlanma:** -1 gün (bitis 2026-09-26 → 2026-09-25)

---

### 3️⃣ Vault Mekanizması Iyileştirmeleri

**Rapor:** [`ORKESTRA-VAULT-TEKRAR-01_rapor_2026-09-23_ihsan.md`](./ORKESTRA-VAULT-TEKRAR-01_rapor_2026-09-23_ihsan.md)

**Uygulanacak İşler (Orkestratör Sorumlu):**

| # | İşlem | Durum | Başlangıç | Bitis |
|---|--------|--------|-----------|-------|
| 1 | `.ALARM.json` 25 dosya sil | ⏳ TODO | 2026-09-24T10:00Z | 2026-09-24T10:05Z |
| 2 | UTF-8 temizliği (tüm ajanlar) | ⏳ TODO | 2026-09-24T10:05Z | 2026-09-24T10:20Z |
| 3 | `vault_archive_old_records()` ekle & çalıştır | ⏳ TODO | 2026-09-24T10:20Z | 2026-09-24T10:30Z |
| 4 | Cron job: `daily_vault_maintenance.py` | ⏳ TODO | 2026-09-24T10:30Z | 2026-09-24T11:00Z |

**Toplam:** 1 saat

---

## Sprint Sonu Kontrol Listesi (2026-09-28)

- [ ] ADMIN-UX-MENUTREE-01 bitti (Utku rapor yaz)
- [ ] TEST-8-KIRMA bitti (Salih rapor yaz)
- [ ] TEST-71-KAYIP bitti (Salih rapor yaz)
- [ ] ALTYAPI-CACHE-OPT-01 bitti (Yasu rapor yaz)
- [ ] GRAPH-FIX-02 bitti (Yasu rapor yaz)
- [ ] AGENTS.md UU merged (İhsan kontrol et)
- [ ] VAULT-CLEANUP-BATCH çalıştı (İhsan kontrol et)
- [ ] Tüm rapor dosyaları `data/orchestrator/` klasörüne kaydedildi
- [ ] task_board.json güncellendi
- [ ] Sonraki sprint planlanması yapıldı (2026-09-29)

---

## Tetik Sistemi (ORCH-08)

**Başlama Talimatı (D-87 tek komut):**

```bash
python scripts/gorev_atama_otomatis.py --task-id AGENTS-MERGE-UU --ajan ihsan
python scripts/gorev_atama_otomatis.py --task-id VAULT-CLEANUP-BATCH --ajan ihsan
```

**Tetik Dosyaları:**
- `data/orchestrator/triggers/utku.jsonl` — Utku'ya MENUTREE-01 ve SIDEBAR-TAB tetik
- `data/orchestrator/triggers/salih.jsonl` — Salih'e TEST-8/71 tetik devam
- `data/orchestrator/triggers/yasu.jsonl` — Yasu'ya CACHE/GRAPH işler tetik
- `data/orchestrator/triggers/ihsan.jsonl` — İhsan'a AGENTS-MERGE + VAULT-CLEANUP tetik

---

## Risk Analizi

| Risk | Olasılık | Etki | Mitigation |
|------|----------|------|-----------|
| Salih test köklendirme tıkanırsa | Yüksek (50%) | Yüksek (-2 gün) | Paralel test + Yasu/Utku yardımı (mapping/fix) |
| AGENTS.md merge karmaşık | Orta (30%) | Orta (-1 gün) | Git blame + manual merge |
| Vault cleanup script hata verirse | Düşük (10%) | Düşük (-30 min) | Dry-run önce, rollback ready |
| Prometheus timeout sorunu devam | Orta (40%) | Orta | D-123 spec'ine göz at (yeni tetikle) |

---

## Kaynaklar & İletişim

- **Task Board:** `data/orchestrator/task_board.json`
- **Brief Şablonu:** `plans/brief_{ajan}_{TASK-ID}.md`
- **Rapor Şablonu:** `data/orchestrator/{TASK-ID}_rapor_YYYY-MM-DD_{ajan}.md`
- **Tetik Kılavuzu:** AGENTS.md → D-68, D-87
- **Vault Mekanizması:** `src/company_master/orchestrator/trigger.py` (satır 121–601)

---

## Özet

**Yeşil durum** → işler sürüyor. **5 günlük sprint** sonunda kritik işler bitecek (MENUTREE, TEST-8/71, CACHE, GRAPH). **AGENTS.md merge** acil (P0 → 2 saat). **Vault cleanup** rutin (1 saat). **Paralel test** hızlandırması tavsiye (Salih yüklü).

**Başlangıç:** 2026-09-24T08:00Z (İhsan AGENTS.md merge başlat)  
**Kontrol:** 2026-09-28T16:00Z (Sprint sonu)  
**Sonraki Plan:** 2026-09-29T08:00Z

---

**Hazırlandı:** İhsan (Orkestratör)  
**Uygulanacak:** D-68 (tetik) + D-87 (atama)
