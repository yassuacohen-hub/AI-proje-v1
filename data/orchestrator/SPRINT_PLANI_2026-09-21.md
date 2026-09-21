# Sprint Planı — 2026-09-21
**Orkestratör:** Roo (Claude Code)  
**Dönem:** 2026-09-21 → 2026-09-28 (1 hafta)

---

## I. Hedefler
1. ✅ PROFILMENU-01 kapatma (tamamlandı)
2. ⚠️ 6 blocked görevdeki tutarsızlıkları temizle
3. **🎯 Paralel track başlat:** UTKU (UX) + İHSAN (belge/copilot)
4. **D-85 uygulaması:** DASH-UX serial (02a → 02b)
5. D-67 haftalık özeleştiri (orkestratör)

---

## II. Görev Seçimi (Öncelik → Sahip → Çakışma)

### P0 (Acil)
- ✅ ADMIN-UX-PROFILMENU-01 → DONE
- ⏭ UI-AYARLAR-SAYFA-01 (tetiklendi, zincir devamı)

### P1 (Bu Sprint)

#### Track A: UTKU (UX Zinciri + DASH-UX Seri)
1. **ADMIN-UX-MENUTREE-01** (P1, sol menü ağacı gruplandırması)
   - Brief: `plans/brief_utku_UX-ZINCIR-01.md` (ortak)
   - Tetik: `al utku ADMIN-UX-MENUTREE-01`
   - Durum: `plan` → `aktif`
   - Tahmini: 5h
   - Dosyalar: `web_dashboard/tabs/__init__.py`

2. **DASH-UX-02a.v1** (P1, sistem sekmelerini dosyada yaz — SECTIONS kayıtsız)
    - Brief: `plans/brief_utku_DASH-UX-02a-v1.md` (D-185 split)
    - Tetik: `al utku DASH-UX-02a` (D-85 seri başlangıcı)
    - Durum: `plan` → `aktif`
    - Tahmini: 5h (K1 kalibrasyonu tanımı)
    - Dosyalar: `web_dashboard/tabs/admin_sistem.py` (cost/perf/api/dlq/webhook)
    - **Kritik:** `web_dashboard/tabs/__init__.py`'ye **DOKUNMAZ** (v2'de yapılacak)
    - **K1 kalibrasyonu** bu görevde tanımlanır, raporda detaylandırılır

2b. **DASH-UX-02a.v2** (P1, admin_sistem SECTIONS kaydı) — v1 + MENUTREE **SONRASI**
    - Brief: `plans/brief_utku_DASH-UX-02a-v2.md` (D-185 split)
    - Tetik: Zincir otomatik (v1 onay + MENUTREE done olunca)
    - Blokaj: `["DASH-UX-02a", "ADMIN-UX-MENUTREE-01"]`
    - Durum: `plan` → `aktif`
    - Tahmini: 2h (kayıt + full regresyon test)
    - Dosyalar: `web_dashboard/tabs/__init__.py`
    - **K1 reuse:** v1 raporundan alınır

3. **DASH-UX-02b** (P1, yönetim sekmeleri birleştirme) — 02a **SONRASI**
   - Brief: `plans/brief_utku_DASH-UX-02a.md` (ortak, K1 kalibasyonu referansı)
   - Tetik: Zincir otomatik (02a tamamlandığında)
   - Durum: `blocked` → (02a done olunca) `aktif`
   - Tahmini: 5h (K1 reuse, K2/K3/K5 paralel)
   - Dosyalar: `web_dashboard/tabs/admin_yonetim.py` (extras/audit/panel/export)

**UTKU İş Yükü:** MENUTREE (5h) + 02a.v1 (5h) + 02a.v2 (2h) + 02b (5h) = **17h** (kapasitesi ~20h/hafta) ✅ **kabul edilebilir**

---

#### Track B: İHSAN (Copilot + Belge + Copilot Yönetimi)
1. **V10-BELGE-01** (P1, dokümantasyon düzeltmeleri)
   - Brief: `plans/brief_ihsan_V10-BELGE-01.md` (kontrol gerek)
   - Tetik: `al ihsan V10-BELGE-01`
   - Durum: `plan` → `aktif`
   - Tahmini: 4h
   - Dosyalar: `AI proje v1/V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md`

2. **BRIF-03** (P1, copilot brifi — Sahipsiz → İHSAN atama)
   - Brief: `plans/brief_ihsan_BRIF-03.md` (var)
   - Tetik: `al ihsan BRIF-03`
   - Durum: `blocked` → (kontrol sonrası) `aktif`
   - Tahmini: 6h
   - Dosyalar: `AI proje v1/V10/03_mimari/brifler/brif_copilot.md`
   - **Not:** D-62 copilot legacy (ajan değil, gözlemci)

**İHSAN İş Yükü:** V10-BELGE (4h) + BRIF-03 (6h) = **10h** ✅ **rahat**

---

#### Track C: Cleanup (Pano Tutarsızlıkları)
1. **COP-26 Durum Güncelleme** (blokaj kaldır, `plan` yap)
   - Tetik: COP-25 archive → COP-26 blokaj kaldır
   - Sonra: `al ihsan COP-26` (P1, müşteri ekranı)
   - Tahmini: 0.5h (otomatik script)

2. **FMT-01 / GUARD-ENC-02 Sınıflandırması** (archive veya wontfix)
   - Durum: D-48 ref (ADMIN-AYAR-01 priorite)
   - Tahmini: 0.5h

3. **WK-01 / WK-02 / WK-03 Archive Taşıması** (park görevler)
   - Tahmini: 0.5h

---

## III. Parallelism & Conflict Avoidance

### Sahip Dağılımı
| Sahip | Görev | Saat | Engel Riski |
|-------|-------|------|-----------|
| UTKU | MENUTREE + DASH-UX-02a + DASH-UX-02b | 18h | Seri (02a → 02b), UX zinciri paralel |
| İHSAN | V10-BELGE + BRIF-03 + COP-26 | 10h | COP-26 blokajı kaldırıldıktan sonra |
| Orkestratör | Cleanup + D-67 haftalık özeleştiri | 2h | — |

### Dosya Kilitleri (D-185 düzeltmesi)
- `web_dashboard/tabs/admin_sistem.py` ← UTKU (02a.v1, paralel)
- `web_dashboard/tabs/admin_yonetim.py` ← UTKU (02b, 02a.v2 sonrası)
- `web_dashboard/tabs/__init__.py` ← **MENUTREE (1h) → DASH-UX-02a.v2 (1h), SERİ** — tek dosya, iki görev, çakışma noktası
- `AI proje v1/V10/00_ana_belgeler/01_sirket_master_ana_belgesi.md` ← İHSAN (V10-BELGE)
- `AI proje v1/V10/03_mimari/brifler/brif_copilot.md` ← İHSAN (BRIF-03)
- `web_dashboard/tabs/admin_musteriler.py` ← (COP-26, hazır ama blokaj kaldırıldıktan sonra)

**✅ Çakışma çözüldü: `__init__.py`** (D-185 split) → MENUTREE (seri) + DASH-UX-02a.v1 (paralel)
- DASH-UX-02a.v1 (dosya yaz, `__init__.py`'ye dokunma) → **paralel** MENUTREE ile
- MENUTREE (`__init__.py` düzenle) → biter → DASH-UX-02a.v2 (`SECTIONS` kaydı) tetiklenir → **seri**
- ADMIN-AYAR-01: pano taramasında `done` bulundu (2026-09-17) → bu sprint dışı, listeden çıkarıldı

### Seri Bağımlılıklar (D-85 + D-185)
```
MENUTREE ━━┓
            ┃ (__init__.py düzenle, 1h)
            ┃
            ├─→ DASH-02a.v2 ━━━━┓
                (SECTIONS, 1h)   ┃
                                 ┣━ DASH-02b (seri, 5h)
DASH-02a.v1 ━━━━━━━━━━━━━━━━━━━━┛
(dosya yaz, 5h, paralel MENUTREE ile)

COP-26 ━━━━━━━━━━━━━━━━━━━━━━━━━ (paralel, ayrı dosya)
```

---

## IV. Aksiyon Planı (Sıra)

### Gün 1 (2026-09-21, bugün 17:56)
1. ✅ PROFILMENU-01 teslim + onayla → DONE
2. 📋 Pano taraması + tutarsızlık raporu yazma
3. 📋 Sprint planı yazma (bu belge)
4. 🔧 **Cleanup başlat:**
   - COP-26 blokajı kaldır
   - FMT-01 / GUARD-ENC-02 archive taşı
   - WK-01/02/03 archive taşı
5. 📧 **Tetikleri gönder:**
   - `al utku ADMIN-UX-MENUTREE-01`
   - `al utku DASH-UX-02a`
   - `al ihsan V10-BELGE-01`
   - `al ihsan BRIF-03`
6. 💾 Commit: "Sprint 2026-09-21: PROFILMENU done, 4 görev aktif, pano temiz"

### Gün 2-5 (2026-09-22 → 2026-09-25)
- UTKU: MENUTREE + DASH-UX-02a paralel çalış
- İHSAN: V10-BELGE + BRIF-03 paralel çalış
- MENUTREE veya 02a bitmek üzere → teslim + kontrolörün onay + done
- 02b tetiklenmesi otomatik (02a done olunca)

### Gün 6-7 (2026-09-26 → 2026-09-27)
- UTKU: 02b bitirme
- İHSAN: COP-26 başlama (blokaj kaldırıldıktan sonra)
- Teslimler başlanıyor

### Gün 7 Sonunda (2026-09-28 pazar)
- D-67 haftalık özeleştiri (orkestratör)
- Sonraki sprint planlama

---

## V. Risk & Kontrol Noktaları

### 🔴 Riskler
1. **UTKU overload** — 18h sıkı ama planlandığı gibi seri + paralel = OK
2. **COP-26 blocker** — COP-25 archive kontrol gerek (durum kontrol: ✅ archive)
3. **K1 kalibrasyonu** — 02a'da bir kez, 02b'de reuse → koordinasyon gerek

### 🟡 Kontrol Noktaları
- **02a bitmeden 02b açma** (blokaj guard's)
- **BRIF-03 copilot legacy check** (D-62 referansı) — brief'te açık mı?
- **COP-26 blokaj kaldırma** (otomatik script + manuel kontrol)

---

## VI. Sonraki Sprint (2026-09-28 +)

Eğer bu sprint süreli biterse:
1. **COP-26 devamı** (müşteri ekranı, P1)
2. **V1-ARGE görevler** (plan durumunda, 12 görev)
3. **FMT-01 / GUARD-ENC-02** (archive → wontfix, P3)

*Not: ADMIN-AYAR-01 pano taramasında `done` (2026-09-17) bulundu → kaldırıldı.*

---

## VII. Karşılaştırma: Önceki Durum vs Yeni Sprint

| Metrik | Önceki | Yeni |
|--------|-------|-----|
| Aktif görev | 1 (PROFILMENU) | 4 (MENUTREE + 02a + BRIF-03 + V10-BELGE) |
| Blocked | 6 (tutarsız) | 1 (COP-26, cleanup sonrası) |
| Done | 246 | 247 |
| Sahip parallelism | Tek (UTKU UX) | İki track (UTKU + İHSAN) |
| Deadlock riski | YOK (ama DASH-02a sahipsiz) | MINIMAL (seri D-85) |

---

## VIII. Approval & Commit

**User onayı gerekli:**
- [ ] MENUTREE + DASH-UX-02a + V10-BELGE + BRIF-03 tetikleme
- [ ] COP-26 blokaj kaldırma
- [ ] FMT-01/GUARD-ENC-02 cleanup
- [ ] WK-01/02/03 archive taşı

**Commit metin:**
```
Sprint 2026-09-21: PROFILMENU kapatıldı (247/247), 4 görev tetiklendi
- PROFILMENU-01 done (teslim → onayla, test 10/10 geçti)
- MENUTREE (UTKU, P1, UX zinciri) tetiklendi
- DASH-UX-02a (UTKU, P1, K1 kalibasyonu) tetiklendi
- V10-BELGE-01 (İHSAN, P1) tetiklendi
- BRIF-03 (İHSAN, P1, copilot brifi) tetiklendi
- Pano tutarsızlığı raporu yazıldı (cleanup tasviyesi)
- Sprint planı yazıldı (18h UTKU + 10h İHSAN paralel)
```

---

## IX. Hazırlık Checklist

- [ ] Temp dosyaları temizle: `_pano_tarama.py`, `_pano.txt`, `_mark_done.py` vb.
- [ ] Commit git add -A
- [ ] Push
- [ ] İHSAN/UTKU'ya bilgilendir

