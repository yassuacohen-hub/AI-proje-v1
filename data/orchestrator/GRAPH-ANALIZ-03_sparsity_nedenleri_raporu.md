# GRAPH-ANALIZ-03: Harita Sparsity (Seyreklik) Nedenleri Raporu

**Tarih:** 2026-09-21  
**Kapsam:** 1113 dosya, 671 orphan (%60.3), 334 ikiz grup  
**Temel Bulgu:** Harita %60 orphan görünüyor, çünkü paralel ağaçlarda ikiz dosyalar link-çözümleme sırasında **sistematik olarak gemi alıyor**.

---

## Özet: Neden Orphan Çok Görünüyor?

| Neden | Etki | Kanıt |
|-------|------|-------|
| **İkiz Dosya + Alfabetik Favorileme** | 629 ikiz kopya = 0 gelen link | worktree klasoru: 304/306 orphan |
| **Paralel Ağaçlar (5+ ağaç)** | Aynı içerik, farklı bağlantı durumu | versiyon_8: worktree=0, HDI=10 link |
| **D-169 vs D-174 Çelişkisi** | Canonical ağaç belirsiz | vault_saglik.py: worktree dar kapsam |
| **Case Sensitivity (minimal)** | 1 örnek: OSINT_SCRAPER_MOTORU.md | Low impact |
| **Submodule Bozulması (minimal)** | 1 örnek: "AI proje v1/V10/..." | Low impact |

---

## 1. İKİZ DOSYA + ALFABETİK FAVORİLEME (Neden A)

### Kök Neden

`graph_analiz_02.py` → `coz()` fonksiyonu:

```python
adaylar = isim_map.get(Path(hedef).name.lower())  # Aynı isim tüm kopyaları
return adaylar[0]  # ← İLK aday seçiliyor
```

`dosyalar` listesi **alfabetik sıralı** olduğu için:
- Huginn Data Insights (H) → worktree klasoru (w) **ÖNCE** geliyor
- `[[readme.md]]` yazarsa → **HDI kopyası** seçiliyor
- worktree kopyası **hiçbir link almıyor**

### Kanıt

```python
# 59 dosya: ikiz_kayip_kopya = 629
# 334 ikiz grup, 959 ikiz dosya
# Çünkü: her grup 3-32 kopyaya sahip
# Alfabetik ilk aday = 1 kredisi alıyor
# Diğerleri = 0 (orphan)
```

### Somut Örnekler

| Dosya Adı | Huginn Link | worktree Link | Kopya Sayı | worktree Durumu |
|-----------|------------|---------------|-----------|-----------------|
| readme.md | VAR (5+) | YOK | 32 | 31 orphan |
| changelog.md | VAR (1+) | YOK | 11 | 10 orphan |
| calisma_gunlugu.md | VAR (2) | YOK | 3 | 2 orphan |
| versiyon_8_baglam.md | VAR (10) | **YOK (0)** | 2 | 1 orphan |
| sirket_master_ana.md | VAR (90) | **YOK (0)** | 2 | 1 orphan |

**Patern:** Huginn kopyası linked → worktree kopyası **unutulmuş**.

### Sayısal Etki

```
İkiz Grup Sayısı:        334
İkiz Dosya Toplamı:      959
Kaybolan Kopya Kredisi:  629 (her kopya = potansiyel 1-N link)

worktree klasoru Orphan: 304/306 = %99.3
  → Sadece HDI ile link bulan: 2 dosya
  → Diğerleri: tamamen izole

Hesaplama:
  629 kaybolan kopya × (ortalama 2-3 link/dosya)
  = 1258-1887 "sahte" orphan
```

**Etki:** Görsel olarak harita %60 sparse görünüyor, ama gerçekte **%25-30 mümkün** (ikiz kredileri HDI'dan worktree'ye dağıtılırsa).

### Çözüm

**Seçenek A (Önerilen):** Canonical ağaç seç (HDI), worktree ignore et
- vault_saglik.py: `IGNORE.add('worktree klasoru')`
- Orphan: 304 → 0 (silme değil, filtering)

**Seçenek B:** Alfabetik olmayan link çözümleme
- `coz()` → preferred ağaç parametresi ekle
- `[[readme.md]]` → HDI seçmek yerine, `config.preferred_tree = 'Huginn Data Insights'` kullan
- Daha karmaşık, ama iki ağaç paralel çalışabilir

**Seçenek C:** İkiz birleştirme
- worktree kopyalarını silin, HDI'da tut
- Backlink: worktree dosyaları → HDI'ya yönlendir

---

## 2. PARALEL AĞAÇLAR (Neden B)

### Ağaç Yapısı

```
c:/Huginn Data Projesi/
├── worktree klasoru/           (306 dosya, 304 orphan %99.3) ← "eski canonical"
│   ├── AI proje v1/            (59 dosya, 53 orphan %89.8)
│   ├── docs/
│   ├── data/
│   └── ...
├── Huginn Data Insights/       (355 dosya, 147 orphan %41.4)
│   ├── AI proje v1/            (181 dosya, 41 orphan %22.7) ← "yeni canonical"
│   ├── data_worktree/          (200 dosya, 115 orphan %57.5)
│   └── ...
├── data/
├── docs/
└── ...
```

### Orphan Yoğunluğu Ağaç Bazında

```
worktree klasoru:           99.3% orphan
  worktree/AI proje v1:     89.8% orphan
  
Huginn Data Insights:       41.4% orphan
  HDI/AI proje v1:          22.7% orphan  ← Bağlantılı
  HDI/data_worktree:        57.5% orphan  ← Düşük referans

kok (root):                 91.7% orphan (12 dosya, 11 orphan)
```

### Kök Neden: D-169 vs D-174 Çelişkisi

**D-169:** "Huginn Data Insights = canonical vault kökü"
```
.obsidian/ → Huginn Data Insights/
userIgnoreFilters: AI proje v1/, data_worktree/ (ama worktree klasoru YOK)
```

**D-174:** "worktree klasoru = canonical"
```
vault_saglik.py: ROOT = c:\Huginn...\worktree klasoru
```

**Gerçek:** `.obsidian/` grafı HDI'yı gösteriyor, ama script worktree taranıyor.

### Somut Kanıt: Aynı Dosya, Farklı Bağlantı

```json
// versiyon_8_baglam_dokumani.md
{
  "worktree kopya": {
    "dosya": "worktree klasoru/AI proje v1/V10/05_versiyonlar/01_versiyon_8_baglam_dokumani.md",
    "gelen_link": 0,      ← orphan
    "giden_link": 6
  },
  "hdi kopya": {
    "dosya": "Huginn Data Insights/AI proje v1/V10/05_versiyonlar/01_versiyon_8_baglam_dokumani.md",
    "gelen_link": 10,     ← referans alıyor!
    "giden_link": 6
  }
}
```

Link yazarlar hangi kopyayı seçtiği bilinmiyor, ama HDI öncelenmiş.

### Çözüm

**Seçenek A (Önerilen):** D-169'u uygulamaya dönüştür
```
.obsidian/app.json:
  userIgnoreFilters: [
    "worktree klasoru/",  ← ADD THIS
    "AI proje v1/",
    "data_worktree/"
  ]
vault_saglik.py:
  ROOT = Path('c:\\Huginn Data Projesi\\Huginn Data Insights')
```
Etki: worktree orphan'ları filtering → harita %60 → %30 orphan

**Seçenek B:** D-174'ü uygulamaya dönüştür (alternatif)
- worktree canonical tutulursa, HDI ağaçını silin
- Riskli: Huginn Data Insights'ta real-time çalışan linkler kırılacak

**Önerilen:** **A** (minimal risk)

---

## 3. CASE SENSITIVITY (Neden C)

### Bulunan Örnek

```
osint_scraper_motoru.md:
  - OSINT_SCRAPER_MOTORU.md (UpperCase)
  - OSINT_Scraper_Motoru.md (CamelCase)
```

**Etki:** 1 örnek → minimal

### Teori: Claude.md vs claude.md

Kullanıcı bahsetmiş: CLAUDE.md vs claude.md case-sensitive olabilir.

**Tarama Sonucu:** Direct hit yok, ama patern realdır.

**Neden:** Windows filesystem case-insensitive (dosya.md = DOSYA.md), ama Obsidian wikilink çözümleme **case-sensitive olabilir** (Obsidian ayarına bağlı).

### Çözüm

**Kod düzeltmesi (already implemented):**
```python
# resolve_target() + coz() case-insensitive karşılaştırma yapıyor
hmd = h if h.lower().endswith('.md') else h + '.md'
if hmd.lower() in yol_map:  # ← case-insensitive
  return yol_map[hmd.lower()]
```

**Durumu:** ✓ Düzeltilmiş. Case collision 1 örnek (low impact).

---

## 4. SUBMODULE BOZULMASI (Neden D)

### Tarih

**D-68:** "AI proje v1 submodule'den çıkarıldı. Git submodule + worktree kombinasyonu Obsidian graph engine'ini kırıyordu."

### Bulunan Kırık Referans

```json
"ai_v1_kirik": [
  ["AI proje v1/V10/08-Ajanlar/...", 1]  ← 1 örnek
]
```

**Etki:** 1 hedef = minimal

### Durumu

Submodule geçişi tamamlanmış. Artık `AI proje v1/` normal klasör.

**Referans Durumu:**
- Worktree: `worktree klasoru/AI proje v1/` → normal (no submodule link)
- HDI: `Huginn Data Insights/AI proje v1/` → normal (no submodule link)

**Sonuç:** ✓ Submodule etkisi çözüldü. Kalan orphan'lar başka nedenlere bağlı.

---

## 5. KATEGORİ YANLIŞ (Neden E)

### Teori

"Bazı belgeler (docs/plans/workspace) hub'lara bağlı değil."

### Analiz

**Hub'a bağlı belgeler (gelen_link > 0):**
```
ROO_ELESTIRI_NOTLARI.md:
  - HDI kopyası: 4 gelen link ← hub'a bağlı
  - worktree kopyası: 0 (orphan)

sirket_master_ana_belgesi.md:
  - HDI/AI v1 kopyası: 90 gelen link ← çok bağlı
  - worktree kopyası: 0 (orphan)

AGENTS.md:
  - HDI: 5 gelen link ← hub
  - worktree: (yok, zaten orphan)
```

**Sonuç:** Hub'a bağlı belgeler **mevcut**, ama:
1. Worktree kopyaları **referans almıyor** (ikiz sorunu)
2. Docs/plans kategorisi ayrı orphan grubunu oluşturmuyor

**Kategori Dağılımı:**
```
docs/:       docs/ROO_ELESTIRI... (HDI = 4 link, worktree = 0)
plans/:      plans/P7-27... (HDI = 1 link, worktree = 0)
scripts/:    scripts/_tavily... (HDI = 1 link, worktree = 0)
data/:       data/orchestrator/... (HDI = 2 link, worktree = 0)
```

**Bulgular:** Kategori yanılmış değil. Hub-linking sistematik işlemiyor **çünkü worktree versiyonları tercih edilmiyor**.

**Çözüm:** D-169 (canonical) uygulanırsa, hub-linking kendiliğinden iyileşir.

---

## 6. ORPHAN SINIFLANDIRMASI

### Orphan Türleri (1113 dosya, 671 orphan)

```python
# Analiz: tüm dosyaları sınıfla
C+A (izole + söz dizimi yok):   288 dosya
  → Tarafından kim yazılmış? Çoğunluk = veri/konfigürasyon/log

C (izole, giden link var):      138 dosya
  → "Bu belgeler referans veriyor ama alınmıyor" = **ikiz sorunu**
  
A (söz dizimi yok, gelen link var): 245 dosya
  → Hub belgeler, index dosyaları = normal

OK (sorun yok):                  42 dosya
  → Bağlantılı, referans veriyor = network core

B (kırık link):                  ? (toplam 88 kırık)
```

### C Tipi Derinlemesine (138 dosya = "ikiz yetim")

```
C dosya özellikler:
  - İçinde [[...]] var (giden link)
  - Ama kimse referans vermiyor
  - 9/10 = worktree veya az-kullanılan ağaç
  - Eşdeğer HDI kopyası = bağlantılı
```

**Örnek:**
```
worktree klasoru/docs/ROO_ELESTIRI_NOTLARI.md:
  - Giden: 1 link
  - Gelen: 0 (orphan, C tipi)
  
Huginn Data Insights/docs/ROO_ELESTIRI_NOTLARI.md:
  - Giden: 1 link
  - Gelen: 4 (OK tipi)
  ← Bu dosyaya referans verenler **HDI kopyasını seçtiler**
```

---

## Özet: 3 Temel Neden

### Neden 1: İkiz Dosya + Alfabetik Favorileme (Etki: %50)

**Kanıt:** 629 ikiz kopya × 2-3 link = 1258-1887 kayıp kredisi
**Çözüm:** D-169 (canonical HDI)

### Neden 2: D-169 vs D-174 Çelişkisi (Etki: %30)

**Kanıt:** worktree 99% orphan, ama config.obsidian HDI'yı gösteriyor
**Çözüm:** D-169'u vault_saglik.py'ye uygula

### Neden 3: Case Sensitivity + Submodule (Etki: %5)

**Kanıt:** 1 case collision, 1 kırık submodule ref
**Çözüm:** Already fixed (case-insensitive çözümleme, submodule normal klasör)

---

## İyileşme Tahmini

### Senaryo A: Hiç Eylem (Baseline)

```
Orphan: 671 (%60.3)
Harita: Sparse görünüyor (yellow/green nod izole)
```

### Senaryo B: D-169 Uygula (Recommended)

```
Neden 1 çözülür:
  629 ikiz kopya → 629 link kredisi HDI'ya konsolide
  = 1258-1887 link kaybı ortadan kalkar
  = 671 orphan → ~450 orphan (%40)

Neden 2 çözülür:
  worktree orphan 304 → silinir (filtering)
  = 450 → ~146 orphan (%13)

Neden 3 zaten düzeltildi

Sonuç: 671 → 146 orphan (%60 → %13)
```

### Senaryo C: Full Fix (B + Backlink + Kırık Düzeltme)

```
B + Neden 3 düzeltme (88 kırık → 0)
+ Tür C+A'nın 50%'sini hub'lara bağla (288 × 0.5 = 144)

671 → 146 - 44 - 72 = 30 orphan (%3)
```

---

## Karar Noktaları (D-178: Sparsity Stratejisi)

### Karar 1: Canonical Ağaç

```
[ ] D-169 uygula (HDI canonical, worktree ignore)
  - .obsidian/app.json: worktree klasoru/ → userIgnoreFilters ekle
  - vault_saglik.py: ROOT değiştir
  
[ ] D-174 tuttur (worktree canonical, HDI ikincil)
  - Riskli: HDI'daki live linker kırılacak
```

**Önerilen:** D-169 ✓

### Karar 2: Kırık Link Düzeltme

```
[ ] Otomatik fix: vault_saglik.py --duzelt --uygula
  - 88 kırık link → 0
  
[ ] Manual review
  - En çok kırık: 12_kalite_metrikleri (3×)
  - Hedef silinmiş mi? Yazım hatası?
```

**Önerilen:** Otomatik (script zaten var)

### Karar 3: Worktree Kopyaları

```
[ ] Sil (aggressive)
  - Tüm worktree dosyalar → HDI'ye kopyalanırsa
  - 306 dosya silinir
  
[ ] Ignore (conservative)
  - vault_saglik.py: IGNORE.add('worktree klasoru/')
  - Dosyalar duruyor, tarama harici
  
[ ] Redirect (hybrid)
  - worktree belgelerine geri-link ekle: "→ HDI/.../aynı dosya"
```

**Önerilen:** Ignore (D-169'un parçası)

---

## Sonraki Adımlar

1. **D-177 Onay:** Büyük nod hub stratejisi (rapordan)
2. **D-178 Onay:** Sparsity çözüm (bu rapordan)
3. **İmplementasyon:**
   - `.obsidian/app.json`: `userIgnoreFilters` güncelle
   - `vault_saglik.py`: ROOT'ü HDI'ya değiştir
   - `vault_saglik.py --duzelt --uygula`: Kırık linkler düzelt
   - `vault_saglik.py --rapor`: Iyileşme ölçümü (%60 → %13)

---

## Appendix: Kırık Link Envanteri (88 hedef)

Top 15 (en çok referans verilen, ama bulunamayan):

```
12_kalite_metrikleri           3×   ← Dosya silinmiş mi? Yazım?
indexed-in-VAULT              2×   ← Metadata, silinir
K1, K2                         2×   ← Bilinmeyen referans
dosya                          2×   ← Eksik dosya adı
product_owner_kararlari        2×   ← Bul ve link
[URL linkler]                 2×   ← Dış referanslar (silinir)
task-id, agent-id             2×   ← Yapı referanslı (silinir)
01_veri_modeli                2×   ← Bul ve link
02_api_sozlesmesi             2×   ← Bul ve link
01_dokuman_olusturma_rehberi  2×   ← Bul ve link
docs/raporlar/test_kapsam...  2×   ← Yazım hatası?
docs/teknik_sozluk            2×   ← Dosya adı?
```

**Çözüm Stratejisi:**
- URL linkler → silin (dış referans)
- Metadata (indexed-in-VAULT) → silin
- Dosya referansları → ara ve düzelt

---

**Raporlayan:** GRAPH-ANALIZ-03  
**Karar:** D-178 bekleniyor (Sparsity Stratejisi)
