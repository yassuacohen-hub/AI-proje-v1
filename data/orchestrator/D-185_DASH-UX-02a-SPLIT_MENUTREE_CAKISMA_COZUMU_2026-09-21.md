# D-185: DASH-UX-02a Split & MENUTREE Çakışma Çözümü

**Tarih:** 2026-09-21  
**Karar Veren:** Orkestratör (Roo)  
**Karar ID:** D-185  
**Kapsam:** DASH-UX-02a / ADMIN-UX-MENUTREE-01 dosya çakışması — `web_dashboard/tabs/__init__.py`

---

## 1. Problem

### Tanımlanan Çakışma

| Görev | Hedef | Dosya Dokunuş | Etki |
|-------|-------|-------|------|
| **DASH-UX-02a** | 5 sistem sekmesini `admin_sistem.py`'ye birleştir | `admin_sistem.py` (yeni) + `__init__.py` (SECTIONS düzelt) | SECTIONS: 5 eski giriş sil, 1 yeni giriş ekle |
| **ADMIN-UX-MENUTREE-01** | Menüyü yeniden grupla (veri/analiz/yönetim) | `__init__.py` (SECTIONS düzenle) | Grupları yeniden sırala, "Ayarlar" sekmesi çıkar |
| **Overlap** | — | **`web_dashboard/tabs/__init__.py`** | **Aynı dosyada ciddi düzenleme = merge çatışması riski yüksek** |

### Gerekçe

- `web_dashboard/tabs/__init__.py` = **navigasyon SSOT (Single Source of Truth)**: `SECTIONS` tuple tüm menü yapısını, sekmeler arası ilişkileri, URL yönlendirmelerini sürüyor.
- D-85 kararında DASH-UX-02a ve 02b seri yapılması kararlaştırılmıştı, ancak **MENUTREE-01'in tasarısı, 02a'nın SECTIONS düzenlemesini gerektirdiği fark edilmemişti**.
- D-66 guard (brifsiz atama yasağı) muhasebesi = brif uzunluğu, ama **dosya kilit muhasebesi yoktur**.
- Sprint planı (SPRINT_PLANI_2026-09-21.md) "❌ Çakışma yok" iddeasıyla yanlış tasarlanmıştı.

---

## 2. Karar: DASH-UX-02a Split (v1 / v2)

### Strateji

**DASH-UX-02a'yı iki alt görev olarak split et:**

#### **DASH-UX-02a.v1** (İlk Aşama — MENUTREE ile paralel)
- **Sahibi:** UTKU
- **Hedef:** `web_dashboard/tabs/admin_sistem.py` oluştur
  - 5 sekmeyi (Cost/Performance/API Analytics/DLQ/Webhook) Streamlit container içinde aç
  - Her sekme: veri kaynağı + placeholder + açıklama (K2/K3)
  - K1 kalibrasyonu tanımı (yapı, ölçümler, limitler) — **raporda detaylandır**
  - Durum management + animasyon
- **Testler:** Local render testleri (`pytest tests/test_dash_ux_tabs.py`)
  - **Kısıt:** `SECTIONS` kaydı yapılmaz. `__init__.py`'ye hiç dokunmaz.
  - v1 test'leri `from web_dashboard.tabs import admin_sistem` + mock render'la çalışır.
- **Teslim:** D-55 rapor + files, `teslim` komutu ile review statüsüne geç
- **Onay:** Kontrolör onaylaması (SALIH/KAHİN)
- **Duration:** ~4–5h (orijinal 02a'nın 8h tahmini, kayıt işi çıkarıldı)

#### **DASH-UX-02a.v2** (İkinci Aşama — MENUTREE sonra)
- **Sahibi:** UTKU
- **Bağımlılık:** `ADMIN-UX-MENUTREE-01` `done` durumuna geçince (v1 onayı bittikten sonra)
- **Hedef:** v1'in `admin_sistem.py` + MENUTREE'nin yeni SECTIONS yapısı üstüne SECTIONS kaydını yaz
  - MENUTREE'nin 5 sekme giriş silmesi + 1 yeni "sistem" giriş ekleme komutunu al
  - Uyumlu K1 yapısıyla SECTIONS kaydını yap (veri kaynağı, roles, URL pattern)
  - Tüm test'leri çalıştır (K5 = test birlikte gelsin)
- **Testler:** `pytest tests/` full regresyon
- **Teslim:** v2 rapor (v1'i referans) + files
- **Duration:** ~1–2h

### Avantajlar

1. **Merge riski = 0**: v1 `__init__.py`'ye hiç dokunmaz → MENUTREE paralel yapılabilir.
2. **Parallelism sağlanır**: v1 (MENUTREE sırasında) + MENUTREE (aynı anda) + COP-26 (ayrı dosya, paralel) = 3 görev hızlı ilerler.
3. **D-85 seri kuralı korunur**: UTKU v1 → v2 sırasıyla yapıyor = seri.
4. **Kod temiz kalır**: v1 Local-self-contained, v2 registry-aware.
5. **Test geçişleri aşamalı**: v1 yeşil → v2 yeşil → hata varsa izole edilebilir.

### Dezavantajlar

- v2 brifi yeni yazılmalı (v1'e bağımlılık, ufak taalimat)
- v2 görev ID'si nedir? → **DASH-UX-02a.v2 yoksa DASH-UX-02a-SECTIONS** (daha açık)

---

## 3. Uygulama Talimatı

### 3.1 Board Değişiklikleri

1. **DASH-UX-02a** — Mevcut görev dosyaları güncelle:
   ```json
   "dosyalar": ["web_dashboard/tabs/admin_sistem.py"],
   "not": "D-185 split: v1 (admin_sistem.py, __init__.py'ye dokunmaz) -> v2 (SECTIONS kaydı MENUTREE sonra). v1 4-5h, v2 1-2h. Brifler: brief_utku_DASH-UX-02a-v1.md, brief_utku_DASH-UX-02a-v2.md"
   ```

2. **Yeni görev: DASH-UX-02a-SECTIONS** (v2 görev)
   ```json
   {
     "task_id": "DASH-UX-02a-SECTIONS",
     "baslik": "[DASH-UX] DASH-UX-02a-SECTIONS: admin_sistem.py sekmesini SECTIONS'a kaydet",
     "sahip": "utku",
     "oncelik": "P1",
     "durum": "plan",
     "blokaj": ["DASH-UX-02a", "ADMIN-UX-MENUTREE-01"],
     "dosyalar": ["web_dashboard/tabs/__init__.py"],
     "not": "D-185 split v2: DASH-UX-02a.v1 onaylandıktan + MENUTREE bitince yapılır. SECTIONS kaydı + full test.",
     "talimat": "admin_sistem sekmesini SECTIONS'a ekle. MENUTREE'nin Ayarlar çıkarma ve grup düzenlemesinin üstüne yap. K1 kalibrasyonu v1 raporundan al. `pytest tests/` full yeşil.",
     "brief": "plans/brief_utku_DASH-UX-02a-v2.md"
   }
   ```

### 3.2 Yeni Brifler

**plans/brief_utku_DASH-UX-02a-v1.md** — (orijinal brief'den ayır)
```markdown
# DASH-UX-02a.v1: Sistem Sekmelerini Dosyada Yaz (SECTIONS Kayıtsız)

[... orijinal içerik ...]

## Kısıt
- `web_dashboard/tabs/__init__.py`'ye **DOKUNMA**.
- Local render testleri, import testleri, K1 tanımı = v1'de.
- SECTIONS kaydı = v2'de (MENUTREE bitince).

## Rapor Zorunluluğu
- K1 kalibrasyonu detayları (yapı, eşikler, yapılan seçimler) — v2 referans alacak.
```

**plans/brief_utku_DASH-UX-02a-v2.md** — (yeni)
```markdown
# DASH-UX-02a.v2: Sistem Sekmesi SECTIONS Kaydını Yap

## Bağımlılıklar
- DASH-UX-02a.v1 = done
- ADMIN-UX-MENUTREE-01 = done

## Ne yapılacak
- v1'in admin_sistem.py + MENUTREE'nin yeni SECTIONS yapısı üstüne SECTIONS kaydını yaz
- K1 kalibrasyonu v1 raporundan al, uyumlu hale getir
- `pytest tests/` full regresyon

## Testler
- `pytest tests/ -q` hepsi yeşil
```

### 3.3 Sprint Planı Güncelleme

**SPRINT_PLANI_2026-09-21.md** dosya kilidi tablosu:
```markdown
| Dosya | Görev | Sahibi | Sıra | Not |
|-------|-------|--------|------|-----|
| web_dashboard/tabs/admin_sistem.py | DASH-UX-02a.v1 | UTKU | Paralel MENUTREE | 4-5h, test local |
| web_dashboard/tabs/__init__.py | ADMIN-UX-MENUTREE-01 | UTKU | Paralel v1 | 1h, SECTIONS yeniden grupla + Ayarlar çıkar |
| web_dashboard/tabs/__init__.py | DASH-UX-02a.v2 | UTKU | Seri: MENUTREE sonra | 1-2h, v1 + MENUTREE üstüne SECTIONS kaydı |
| web_dashboard/tabs/admin_yonetim.py | DASH-UX-02b | UTKU | Seri: v2 sonra | 5h |
| web_dashboard/tabs/admin_musteriler.py | COP-26 | İHSAN | Paralel | 2-3h, SECTIONS giriş minimal |
```

**Düzeltme: Çakışma VAR ama split ve seri ile çözüldü:**
```markdown
## File Lock Analiz

**❌ Çakışma: `web_dashboard/tabs/__init__.py`** — ADMIN-UX-MENUTREE-01 + DASH-UX-02a  
→ **Çözüm: DASH-UX-02a split (v1/v2), v2 MENUTREE sonra seri yapılır (D-185)**

| Dosya | Görev | Sıra |
|-------|-------|------|
| **__init__.py** | MENUTREE (1h) → DASH-UX-02a.v2 (1h) | Seri |
| admin_sistem.py | DASH-UX-02a.v1 | Paralel (MENUTREE ile) |
| admin_yonetim.py | DASH-UX-02b (5h, v2 sonra) | Seri |
| admin_musteriler.py | COP-26 | Paralel |

→ **Parallelism korunur, merge riski 0**
```

---

## 4. Tetik Zinciri (D-79)

```
DASH-UX-02a.v1 teslim → onay → DASH-UX-02a.v2 tetikle (blocked duruma geç, MENUTREE bitmesini bekle)

ADMIN-UX-MENUTREE-01 teslim → onay → DASH-UX-02a.v2 otomatik başlasın (blokaj çözül)

DASH-UX-02a.v2 teslim → onay → DASH-UX-02b tetikle
```

---

## 5. Risk Değerlendirmesi

| Risk | Düzey | Azaltma |
|------|-------|---------|
| v1 local testleri yeterli değilse v2'de hata bulunur | Düşük | v1 test setini geniş tutmak (snapshot, render mock) |
| MENUTREE'nin SECTIONS yapısı değişirse v2 fail olur | Orta | MENUTREE → v2 arasında communication (brief) |
| v2'nin ufak olması nedeni ile adım atlanabilir | Düşük | Brief özel, task_board.json açık kısıtlar |

---

## 6. Karar Özetleri

**D-185 Karar:**
- ✅ DASH-UX-02a split v1/v2 → merge riski = 0
- ✅ MENUTREE paralel yapılabilir → sprint 3–4 gün kazanır
- ✅ COP-26 paralel → toplam parallelism artır
- ✅ D-85 seri kuralı korunur (UTKU, v1→v2→02b)
- ✅ Board ve brifler güncellenecek (aşağıda)

**Etkilenen Dosyalar:**
- `data/orchestrator/task_board.json` — DASH-UX-02a güncelle, DASH-UX-02a-SECTIONS ekle
- `plans/brief_utku_DASH-UX-02a-v1.md` — oluştur (orijinal brief'den ayır)
- `plans/brief_utku_DASH-UX-02a-v2.md` — oluştur (yeni)
- `data/orchestrator/SPRINT_PLANI_2026-09-21.md` — çakışma raporu düzelt, seri sıra belir
- `data/orchestrator/decision_log.jsonl` — D-185 kaydı ekle

---

## 7. Next Step

1. Board (`task_board.json`) güncellemesi
2. Yeni brifler yazılması
3. Sprint planı düzeltilmesi
4. Commit
5. UTKU: v1 başlama (paralel MENUTREE ile)
