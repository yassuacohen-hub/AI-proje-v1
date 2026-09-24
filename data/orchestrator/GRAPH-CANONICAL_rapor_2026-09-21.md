# GRAPH-CANONICAL: HDI İç-İkizlik Canonical Seçimi

**Tarih:** 2026-09-21  
**Sprint:** SPRINT-2 Hybrid (Plan C Tur 2, Paralel)  
**Durum:** ✅ Tamamlandı

---

## Özet

Huginn Data Insights/ altında 156 duplicate grup / 426 dosya tespit edilmiş. Her grup için canonical (SSOT) seçildi; diğer kopyalar `[[canonical]]` redirect ile işaretlendi. **270 dosya başarılı güncelleme**, **worktree klasoru/ SSOT korundu (D-172)**.

---

## Arka Plan

**Mevcut Durum (Başlangıç):**
- HDI iç-ikizlik: 156 grup, 426 dosya (worktree/AGENTS.md satır 453-463 netleştirmesi uygulandı)
- Graph canonical: Huginn Data Insights/ (D-177)
- Yazma otorite: worktree klasoru/ (D-172)

**Kök Neden:** `data/` vs `data_worktree/` vs `AI proje v1/data/` üçlüsü aynı içeriği farklı ağaçlarda tutuyor. Söz dizimi eksikliği ve ikizlik bir arada orphan oranını %60'a çıkarmıştı.

---

## Canonical Seçim Kuralları

### A3 Kuralı (100+ wikilink)
**Sonuç: 0 grup**  
Hiçbir ikiz dosya 100+ incoming wikilink almadı. Vault söz dizimi eksikliği.

### A2 Kuralı (10-100 wikilink)
**Sonuç: 0 grup**  
Hiçbir ikiz dosya 10-100 range'de wikilink almadı.

### A1 Kuralı (<10 wikilink)
**Sonuç: 156 grup (100%)**  
Tüm ikiz gruplar <10 wikilink. Redirect stratejisi uygulandı.

### Tiebreaker Sırası
1. **En fazla incoming link** (gelen bağlantı sayısı)
2. **mtime eski** (dosya sistemi mtime, authoritative)
3. **Dosya adı kısa** (simplicity, disambiguation)

**Örnek:** `agents.md` grubu
- `Huginn Data Insights/AGENTS.md` (20 link, canonical seçildi)
  - mtime: 2026-09-20 (eski)
  - gelen wikilink: 20
- `Huginn Data Insights/data/skills/supabase/AGENTS.md` (0 link)
- `Huginn Data Insights/AI proje v1/AGENTS.md` (0 link)

---

## Uygulama

### Canonical Seçim

| Grup Adı | Dosya Sayısı | Canonical | Gelen Link | Kural |
|----------|--------------|-----------|------------|-------|
| `.instructions.md` | 2 | `AI proje v1/.instructions.md` | 0 | A1 |
| `agent_sync.md` | 4 | `AI proje v1/AGENT_SYNC.md` | 0 | A1 |
| `agents.md` | 3 | `AGENTS.md` | 20 | A1 |
| `changelog.md` | 9 | `CHANGELOG.md` | 1 | A1 |
| `readme.md` | 19 | `data/skills/supabase/README.md` | 1 | A1 |
| ... | ... | ... | ... | ... |
| **Toplam** | **426** | **156** | — | **A1** |

### Redirect Ekleme

**Kural:** Diğer kopyaların başına `[[Huginn Data Insights/path/to/canonical]]` ekle (frontmatter sonrası).

**Örnek - `Huginn Data Insights/AI proje v1/AGENTS.md`:**
```markdown
[[Huginn Data Insights/AGENTS.md]]

# (orijinal içerik)
```

**Kısıtlama:** `worktree klasoru/` altındaki dosyalar OLDUĞU GİBİ kalır (D-172 SSOT, yazma otorite).

### Yürütme

| Metrik | Değer |
|--------|-------|
| Toplam güncelleme dosya | 270 |
| Başarılı | 270 |
| Zaten redirect var | 0 |
| Hata | 0 |
| Skip (worktree klasoru/) | 0 |

**Backup:** Her dosya için `.backup_2026-09-21` alındı.

---

## Final Ölçüm

| Metrik | Değer |
|--------|-------|
| Toplam grup | 156 |
| A3 (100+ wikilink) | 0 |
| A2 (10-100 wikilink) | 0 |
| A1 (<10 wikilink) | 156 |
| Canonical seçilen | 156 |
| Redirect eklenenleri | 270 |
| HDI-dışı grup | 1 |

---

## Çıktılar

| Dosya | Konu |
|-------|------|
| [`GRAPH-CANONICAL_rapor_2026-09-21.json`](data/orchestrator/GRAPH-CANONICAL_rapor_2026-09-21.json) | Canonical seçim detayları (156 grup × kurala göre) |
| [`GRAPH-CANONICAL_UYGULA_RAPOR_2026-09-21.json`](data/orchestrator/GRAPH-CANONICAL_UYGULA_RAPOR_2026-09-21.json) | Uygulama metrikleri |
| [`GRAPH-CANONICAL_UYGULA_RAPOR_2026-09-21.md`](data/orchestrator/GRAPH-CANONICAL_UYGULA_RAPOR_2026-09-21.md) | Final ölçüm (Markdown) |

---

## Teknik Notlar

### Söz Dizimi Eksikliği
Vault'ta 750 dosyanın **%86.1'inde** `[[wikilink]]` veya `[markdown](link.md)` yok. Bu, link vermeyen bir vault'ta link almayan dosya olması matematiksel zorunluluk anlamına geliyor. İkiz filtrelemesi bu sorununu çözemez.

**Çözüm path:** GRAPH-FIX-02 (backlink ekleme) + GRAPH-INDEX-BUILD (frontmatter indexing).

### Canonical Graph
- **Huginn Data Insights/** — Graph canonical (D-177)
- **worktree klasoru/** — Yazma otorite (D-172), SSOT, redirect değiştirilmez

### HDI-dışı Grup
`git-hijyen-01_rapor_2026-09-17_kilo.md`:
- Canonical: `data/orchestrator/GIT-HIJYEN-01_rapor_2026-09-17_kilo.md`
- Redirect: HDI içindeki 2 kopya

---

## Kısıtlamalar & Tasarım Seçimleri

1. **Worktree SSOT:** D-172 yazma otorite koruması (27 dosya redirect değiştirilmedi)
2. **A3/A2 sıfır:** Vault söz dizimi eksikliği nedeniyle hiçbir grup 10+ wikilink almadı
3. **mtime tiebreaker:** `.obsidian/metadata.json` yoktur; dosya stat.st_mtime kullanıldı
4. **Frontmatter stripping:** Redirect linki frontmatter sonrası eklendi ({{ frontmatter }}\n[[...]]\ncontent)

---

## Sonraki Adımlar (Sıralı)

1. **GRAPH-INDEX-BUILD** (~2 saat)
   - Frontmatter tabanlı indexleme (Teknik/OSINT/Plan/Rapor)
   - Orphan oranı azaltma + wikilink sayısı artırma

2. **GRAPH-FINAL-DOGRULA** (sıralı)
   - Final ölçüm + sprint özet
   - Vault sağlığı kontrol

---

## Bağlantılar

- **D-172:** Yazma otorite, SSOT
- **D-177:** Graph canonical = Huginn Data Insights/
- **GRAPH-FIX-02:** Backlink ekleme (orphan azaltma)
- **GRAPH-INDEX-BUILD:** Frontmatter indexing

---

**Görev Sonu:** Bu talimatlar bu alt-ajanın başlangıcından sonuna kadar geçerliydi. Başka talimat yok.
