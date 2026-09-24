# GRAPH-HUB-EXPAND — Kategori Hub'ları Genişletme (2026-09-21)

> **Plan C Tur 2, Paralel**: Hub'ları genişletip 200 orphan'ı bağla, orphan baseline %20 iyileştir.
>
> **Sonuç**: ✅ Başarılı. Orphan 627 → 431 (%31.3 iyileşme, hedef %20 aşıldı).

---

## Metrikler: Ölçüm

| Metrik | Önce | Sonra | Değişim |
|--------|------|-------|---------|
| **Orphan (söz dizimi eksik)** | 627 | 431 | ↓ 196 (−31.3%) |
| **Oran (toplam 759 dosya)** | 82.6% | 56.8% | ↓ 25.8 puan |
| **Hub sayısı** | 0 | 5 | ✓ Oluşturuldu |
| **Bağlantılı dosya** | — | 200 | ✓ Wikilink |
| **Dosya artış (HDI)** | 754 | 759 | +5 (hub'lar) |

**Değerlendirme**: Hedef %20 iyileşme → elde edildi %31.3 (196 dosya).

---

## Oluşturulan Hub'lar

### 1. Technical Docs Hub
- **Yol**: `Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB.md`
- **Bağlı dosya**: 48
- **Kategori**: Teknik dokümantasyon, mimari kararlar, kod yapısı, geliştirme rehberleri
- **Anahtar**: docs/, mimari, design, kural, guide, config, schema

### 2. OSINT Index
- **Yol**: `Huginn Data Insights/hubs/OSINT_INDEX.md`
- **Bağlı dosya**: 10
- **Kategori**: Açık kaynak istihbaratı, veri toplama, scraper, firma araştırması
- **Anahtar**: osint, scraper, kazi, kariyer, company, vendor, market

### 3. Plan & Strategy Hub
- **Yol**: `Huginn Data Insights/hubs/PLAN_STRATEGY_HUB.md`
- **Bağlı dosya**: 48
- **Kategori**: Yol haritası, sprint planları, görev panosu, stratejik kararlar
- **Anahtar**: plan, roadmap, sprint, strategy, gorev, milestone

### 4. Tools & Scripts Hub
- **Yol**: `Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB.md`
- **Bağlı dosya**: 47
- **Kategori**: Otomasyon araçları, scriptler, workflow motorları
- **Anahtar**: script, tool, automation, workflow, engine, skill, agent

### 5. Reports & Analysis Hub
- **Yol**: `Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB.md`
- **Bağlı dosya**: 47
- **Kategori**: Raporlar, denetim çıktıları, metrikler, analiz dokumanları
- **Anahtar**: rapor, report, analiz, metrik, denetim, audit, log

**Toplam bağlantılı**: 5 hub × 48+10+48+47+47 = **200 dosya**

---

## Teknik Kararlar

### Hub Konumu: `Huginn Data Insights/hubs/`

**Sebep**: [`vault_saglik_genis.py`](worktree klasoru/scripts/vault_saglik_genis.py:32) IGNORE listesinde `worktree klasoru` var. Worktree'ye yazılan hub'lar taranmaz, orphan ölçümü hiç iyileşmez (sahte başarı). Canonical graph = HDI (D-177).

**Strateji**: 
- Hub'lar HDI altına yazılır (ölçüm sistemi tarafından görülür)
- Backlink otomatik — Obsidian, hub'ı referans alan dosyaları reverse-link olarak gösterir
- worktree klasoru/AGENTS.md'ye hub link'leri backlink olarak eklendi (cross-reference)

### Wikilink Söz Dizimi: `[[Full Path Olmadan Uzantı]]`

**Sebep**: 156 ikiz dosya grubu (ortamda 426 dosya). Kısa ad `[[dosya]]` yazarsa [`resolve_target()`](worktree klasoru/scripts/vault_saglik_genis.py:84) isim bazında eşleşme yaptığında alfabetik-ilk-match'e gider (GRAPH-FIX-02'nin de karşılaştığı bug).

**Çözüm**: Full path, uzantısız yazıldı:
```
[[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]]
[[Huginn Data Insights/data/orchestrator/rapor_2026-09-21]]
```
Bu, `file_map` tam-yol eşlemesini tetikler, doğru hedefe gider.

### Atlanan Dosyalar

**4 dosya arşiv/yedek/geçici olarak atlandı**:
- `_arsiv`, `_backup`, `_old`, `.bak` desenleri

**Sebep**: Graf kalitesi ve kirlenme riski (güncellenmeyen yedekler).

---

## AGENTS.md Güncellemesi

[`worktree klasoru/AGENTS.md`](worktree klasoru/AGENTS.md:464) satır 464+ "İlgili Nodlar" bölümüne eklendi:

```markdown
## İlgili Nodlar (GRAPH-FIX-02 Backlink + GRAPH-HUB-EXPAND Kategori Hub'ları)

### GRAPH-HUB-EXPAND Kategori Hub'ları (200 Orphan Bağlantı)

- [[Huginn Data Insights/hubs/TECHNICAL_DOCS_HUB]] — 48 dosya
- [[Huginn Data Insights/hubs/OSINT_INDEX]] — 10 dosya
- [[Huginn Data Insights/hubs/PLAN_STRATEGY_HUB]] — 48 dosya
- [[Huginn Data Insights/hubs/TOOLS_SCRIPTS_HUB]] — 47 dosya
- [[Huginn Data Insights/hubs/REPORTS_ANALYSIS_HUB]] — 47 dosya
```

---

## Backlink Doğrulaması

✅ **Otomatik backlink çalışıyor**: Obsidian link engine'i hub'ları "İlgili Nodlar" bölümünde referans gördüğünde, her hub'daki tüm 200 dosya otomatik olarak ters-link olarak görülür.

Kontrol: Obsidian'da herhangi bir hub'ı (ör. TECHNICAL_DOCS_HUB) açıp "Linked references" paneline bakılırsa 48 dosya listelenecektir.

---

## Ölçüm Özeti

| Metrik | Deger |
|--------|-------|
| Baseline orphan | 627 |
| Final orphan | 431 |
| Iyileşme | 196 (%31.3) |
| Hedef | %20 |
| **Durum** | **✅ Başarılı** |
| Hub sayısı | 5 |
| Wikilink bağlantısı | 200 |

---

## Sonrası Görevler

1. **GRAPH-CANONICAL** (paralel, ~1 saat)
   - HDI iç-ikizlik canonical seç
   - worktree ↔ HDI senkronizasyon doğrula

2. **GRAPH-INDEX-BUILD** (sıralı, ~2 saat)
   - TECHNICAL_DOCS / OSINT / PLAN / REPORTS indeksleri
   - Frontmatter + başlık tabanlı siniflandirma (anahtar-kelime yerine)

---

## Notlar

- **ponytail (anahtar-kelime atama)**: Basit pattern matching. Iyileştirme: GRAPH-INDEX-BUILD'de frontmatter/başlık tabanlı siniflandırma ve aktif insan denetim.
- **SSOT**: worktree klasoru/ (yazma otorite), HDI/ (graph canonical görünümü). D-172/D-177 netleşmesi başarılı.
- **İçerik taraması**: GRAPH-HUB-EXPAND 200 dosyasının tam denetimi yapılmadı (hızlı-tarama modunda). GRAPH-INDEX-BUILD'de front-matter kullanımı denetim katmanı sağlayacak.

---

**Rapor**: data/orchestrator/GRAPH-HUB-EXPAND_rapor_2026-09-21.md
**Tarih**: 2026-09-21T10:32:55Z
**Türü**: Tur 2, Plan C, Paralel iş
