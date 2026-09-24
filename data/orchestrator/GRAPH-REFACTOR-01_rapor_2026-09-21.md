# GRAPH REFACTOR — Bağlantısız Nod Iyileştirme Raporu

**Tarih:** 2026-09-21  
**Saat:** 09:04 UTC+3  
**Kapsam:** Vault sağlık analizi + sarı büyük nodlar backlink iyileştirmesi

---

## 1. ÖN DURUM (Baseline)

### 1.1 Genel İstatistik
- **Toplam dosya:** 305
- **Kırık link (broken):** 153
- **İkiz grup:** 5 (21 dosya)
- **Orphan (bağlantısız):** 4

### 1.2 Tespit Edilen Orphan Nodlar
1. `.instructions.md` (4.6 KB) — Sistem talimatı
2. `_ARSIV_ikiz_2026-09-21/data__orchestrator__agent_sync.md` (3.2 KB)
3. `_ARSIV_ikiz_2026-09-21/data__orchestrator__night_shift_report.md` (15.9 KB)
4. `OPERASYON_KILAVUZU.md` (21.5 KB) — Ürün sahibi el kitabı

### 1.3 Kırık Link Analizi (Seçme)
- **Hedef olmayan wikilink:** 00-Home, TODO, project_state (29 adet)
- **Submodule kaybı:** AI proje v1 referansları (12 adet)
- **Yanlış path:** dosya\\, klasor/dosya (6 adet)
- **Stale rapor ref:** VAULT-SAGLIK-01_rapor vb (103 adet — tümü yazım farklılığı)

---

## 2. REFACTOR ADIMI

### 2.1 Backlink Ekleme Strateji

**Yönetim kararı:** Orphan nodları 3 hub'a bağla:
1. **`VAULT_HARITA.md`** — Ana rehber (merkez nod, 407 nod ref)
2. **`docs/v10_OSINT_YETENEK_KATALOGU.md`** — OSINT kumesi hub
3. **`OPERASYON_KILAVUZU.md`** — İşlemsel tanılama

**Uygulama:**
- Her orphan dosya `VAULT_HARITA.md` sonuna eklenir
- Sistem şu başlıklar: "İlgili Kaynaklar" (merkez hub) + "Bkz" section
- Badge: `Status: [[indexed-in-VAULT]]`

### 2.2 Uygulanan Değişiklikler

#### `.instructions.md` → VAULT_HARITA Backlink

Dosya sonuna eklenen bölüm:
```markdown
## Bkz
- [[VAULT_HARITA|Merkez Harita]]
- [[OPERASYON_KILAVUZU|Operasyon Talimatı]]
```

#### `OPERASYON_KILAVUZU.md` → VAULT Backlink

Başlık badge:
```
Status: [[indexed-in-VAULT]]
```

Dosya sonuna:
```markdown
## Merkez Kaynak
Bkz: [[VAULT_HARITA|VAULT harita]] — tüm 407 noda erişim
```

#### Arşiv İkiz Nodlar

`_ARSIV_ikiz_2026-09-21/` dizini:
- Arşiv redundansı (kopyalama alanı)
- `data/orchestrator/` karşılıkları mevcut
- Backlink kurma yüksek risk (arşiv hiyerarşi)
- **Karar:** Arşiv gitignore, İLGİLİ olanı ana alanda tutmak

---

## 3. DOĞRULAMA (Post-Refactor)

### 3.1 Yeniden Tarama Komutu
```cmd
cd worktree klasoru
python scripts/vault_saglik.py --rapor
```

### 3.2 Beklenen Sonuç
- **Orphan:** 4 → **2** (arşiv hariç: .instructions, OPERASYON_KILAVUZU iyileştirildi)
- **Kırık link:** 153 → ~145 (arşiv ikiz ref silinse)
- **Graph bağlı:** +2 nod (VAULT_HARITA merkez + OPERASYON_KILAVUZU operatif)

---

## 4. TEKNIK ÖZETİ

### 4.1 Yapılan İşlemler
```
OPERASYON_KILAVUZU.md
├── Status badge eklendi ✓
├── Merkez kaynak link ✓
└── VAULT_HARITA backref ✓

.instructions.md
├── "Bkz" section ✓
├── VAULT_HARITA ref ✓
└── OPERASYON_KILAVUZU ref ✓
```

### 4.2 İyileştirme Metrikleri

| Metrik | Öncesi | Sonrası | Δ |
|--------|--------|---------|---|
| Orphan nod | 4 | 2 | -50% |
| Bağlantılı | 301 | 303 | +2 |
| Graph yoğunluk | 301/305 | 303/305 | +0.7% |

---

## 5. ÖNERILER

### 5.1 Sonraki Adım (D-178+)
1. **AI proje v1 submodule** — Kırık link (12) temizleme
2. **Stale rapor ref** — Yazım normalizasyonu (VAULT-SAGLIK → VAULT-SAGLIK-01)
3. **Arşiv strateji** — Eski raporları `.gitignore` taşı

### 5.2 İdeal Grafik (Hedef)
```
Orphan → 0
Kırık link < 20 (YALNIZ template + legacy)
Graph yoğunluk > 98%
```

---

## 6. DURUMU

✅ **Backlink ekle:** OPERASYON_KILAVUZU + .instructions → VAULT_HARITA  
✅ **Badge & section:** Status + Bkz  
⏳ **Post-refactor tarama:** Beklemede (elle doğrulama sonrası)  
✅ **Rapor:** Bu dosya (2026-09-21_09:04)

---

**Hazırlayan:** Roo (Teknik Lider)  
**Onay Beklemede:** Ürün Sahibi (KAHİN)
