# P2/P5 İş Dağıtımı Planı — 2026-09-23

## 📊 Koordinasyon Matrisi

| # | Task ID | Sahip | Öncelik | Durum | Süre | Kategori | Başla Komutu | Notlar |
|---|---------|-------|---------|-------|------|----------|--------------|--------|
| 1 | ALTYAPI-KILIT-TEMIZLE-01 | Yasu | P2 | aktif ✅ | 1s | Altyapı | *Rapor mevcut* | Tamamlandı — task_board güncellemesi |
| 2 | ORKESTRA-VAULT-TEKRAR-01 | İhsan | P2 | plan | 2s | Orkestrasyon | `npx --yes n8nac workflow present` | Brief mevcut — başlayabilir |
| 3 | ORKESTRA-BRIEF-TALIMAT-01 | Yasu | P2 | plan | 1s | Orkestrasyon | `cat data/orchestrator/ORKESTRA-BRIEF-TALIMAT-01_brif_2026-09-20_denetim.md` | 4 brife talimat yaz |
| 4 | DASH-UX-02a-SECTIONS | Utku | P1 | blocked | 3s | UI | *Blokaj: DASH-UX-02a, ADMIN-UX-MENUTREE-01* | Duplike kayıt — temizleme sonra başla |
| 5 | AGENTS.md UU merge | Orkestratör | Yönetim | Pending | — | Git/Yönetim | `git status` | Kullanıcı onayı gerekli |
| 6 | Geçici dosya temizliği | Orkestratör | P5 | — | 30s | Temizlik | `del _task_analiz.py _aktif_sonuc.txt` | Analiz dosyaları |
| 7 | Duplike kayıt temizliği | Orkestratör | P5 | — | 1m | JSON | *apply_diff* | task_board.json satır 6578-6600 |

---

## 🎯 İş Atama Kararları

### Uzun İşler → Utku (Yüksek Oran)
- **DASH-UX-02a-SECTIONS** (P1, 3s): Blokaj kaldırıldıktan sonra
  - admin_sistem sekmesi SECTIONS'a taşı
  - web_dashboard/tabs/__init__.py

### Plan İşleri → Yasu (Altyapı)
- **ORKESTRA-BRIEF-TALIMAT-01** (P2, 1s): 4 brife talimat dosyası yaz
  - Brief mevcut: `data/orchestrator/ORKESTRA-BRIEF-TALIMAT-01_brif_2026-09-20_denetim.md`
  - Çıktı: 4 talimat dosyası

### Plan İşleri → İhsan (UI/Yönetim)
- **ORKESTRA-VAULT-TEKRAR-01** (P2, 2s): Vault isim tekrarları denetleme
  - Brief: `data/orchestrator/ORKESTRA-VAULT-TEKRAR-01_brif_2026-09-22_orkestrator.md`
  - Zincir parçası (sira=4/4, son): ORKESTRA-DECISION-LOG-03 → sonraki=null

### Orkestratör (Sen) — P5 Temizlik
- **Geçici dosya temizliği**: `_task_analiz.py`, `_aktif_sonuc.txt` vb.
- **DASH-UX-02a-SECTIONS duplike kaydı**: task_board.json satır 6578-6600 silinecek
- **AGENTS.md UU merge**: Kullanıcı onayı → git conflict çözümü

---

## 🚀 Görev Başlama Komutları (D-87)

### Yasu → ORKESTRA-BRIEF-TALIMAT-01
```bash
python scripts/gorev_atama_otomatis.py --task-id ORKESTRA-BRIEF-TALIMAT-01 --ajan yasu
```
**Brief:** `data/orchestrator/ORKESTRA-BRIEF-TALIMAT-01_brif_2026-09-20_denetim.md`
**Çıktı:** 4 talimat dosyası (data/orchestrator/ dizinine)

### İhsan → ORKESTRA-VAULT-TEKRAR-01
```bash
python scripts/gorev_atama_otomatis.py --task-id ORKESTRA-VAULT-TEKRAR-01 --ajan ihsan
```
**Brief:** `data/orchestrator/ORKESTRA-VAULT-TEKRAR-01_brif_2026-09-22_orkestrator.md`
**Çıktı:** Rapor (ORKESTRA-VAULT-TEKRAR-01_rapor_2026-09-23_ihsan.md)

### Utku → DASH-UX-02a-SECTIONS (Sonra)
```bash
python scripts/gorev_atama_otomatis.py --task-id DASH-UX-02a-SECTIONS --ajan utku
```
**Bloklama:** Önce DASH-UX-02a ve ADMIN-UX-MENUTREE-01 tamamlanmalı
**Brief:** `plans/brief_utku_DASH-UX-02a-v2.md`

---

## 📋 Blokaj & Bağımlılıklar

```
DASH-UX-02a-SECTIONS (blocked)
  ├─ DASH-UX-02a (parent task) — STATUS?
  └─ ADMIN-UX-MENUTREE-01 (parent task) — STATUS?
```
Blokaj kaldırıldıktan sonra Utku başlayabilir.

---

## ✅ Yönetim İşleri (Orkestratör)

### 1. AGENTS.md UU merge çakışması
**Durumu:** Kullanıcı onayı gerekli
**Aksiyon:** 
```bash
git status
# Conflict dosyalarını listele
git show HEAD:AGENTS.md > /tmp/HEAD_AGENTS.md
git show MERGE_HEAD:AGENTS.md > /tmp/MERGE_AGENTS.md
# Karşılaştır ve karar ver
```

### 2. Geçici Dosya Temizliği
```bash
del c:\Huginn Data Projesi\_task_analiz.py
del c:\Huginn Data Projesi\_aktif_sonuc.txt
del c:\Huginn Data Projesi\_utku_check.py  (varsa)
del c:\Huginn Data Projesi\_dash_check.py  (varsa)
```

### 3. DASH-UX-02a-SECTIONS Duplike Kaydı Temizliği
**Dosya:** `Huginn Data Insights/data/orchestrator/task_board.json`
**Satırlar:** 6578-6600 (silinecek)
**Not:** UI-ADOPT-01 (satır 6602) başlamış — duplike hemen sonra gelir.

---

## 📊 İş Koordinasyon Özeti

| Kişi | Görev | Başlama Komutu | Bağımlılık | Rapor |
|------|-------|---------------|-----------|-------|
| Yasu | ORKESTRA-BRIEF-TALIMAT-01 | `gorev_atama_otomatis.py --task-id ORKESTRA-BRIEF-TALIMAT-01 --ajan yasu` | Yok | 4 talimat dosyası |
| İhsan | ORKESTRA-VAULT-TEKRAR-01 | `gorev_atama_otomatis.py --task-id ORKESTRA-VAULT-TEKRAR-01 --ajan ihsan` | Yok (zincir sonu) | ORKESTRA-VAULT-TEKRAR-01_rapor_2026-09-23_ihsan.md |
| Utku | DASH-UX-02a-SECTIONS | `gorev_atama_otomatis.py --task-id DASH-UX-02a-SECTIONS --ajan utku` | DASH-UX-02a, ADMIN-UX-MENUTREE-01 temizlenmeli | pytest tests/ -q yeşil |
| Orkestratör | Temizlik + Merge | `apply_diff` + `git` | — | — |

---

## 🔄 Zincir Yapısı

```
ORKESTRA-VAULT-TEKRAR-01 (zincir sira=4/4)
  onceki: ORKESTRA-DECISION-LOG-03
  sonraki: null (SON)
```

---

## 💡 Notlar

- **ALTYAPI-KILIT-TEMIZLE-01** (Yasu, aktif): Rapor mevcut → status "done" olarak işaretle
- **DASH-UX-02a-SECTIONS** (duplike): Temizlemeden sonra Utku'ya verilecek
- **AGENTS.md UU merge**: Kullanıcı git conflict'i onaylayana kadar bekleme

---

**Plan Tarihi:** 2026-09-23 06:59  
**Versiyon:** 1.0  
**Durum:** Onay Bekliyor
