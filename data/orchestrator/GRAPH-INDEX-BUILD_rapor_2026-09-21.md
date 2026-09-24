# GRAPH-INDEX-BUILD — Tür-Bazlı Index Oluşturma (2026-09-21)

> **Plan C Tur 3, Seri**: 431 orphan dosyasını tür-bazlı index dosyalarına yerleştir.

## Ölçüm Özeti

| Metrik | Değer |
|--------|-------|
| Orphan (baseline, GRAPH-HUB-EXPAND sonrası) | 431 |
| **Orphan ÖNCE** (bu görev, backup hariç) | **374** |
| **Orphan SONRA** | **103** |
| **İyileşme** | **−271 (%72.5)** |
| Index oluşturulan | 4 |
| Sınıflandırılan dosya | 275 |
| Teknik Index | 96 |
| OSINT Index | 8 |
| Plan Index | 33 |
| Rapor Index | 138 |

## Oluşturulan Index Dosyaları

### OSINT
- **Yol**: `Huginn Data Insights/indexes/osint_index.md`
- **Dosya**: 8

### PLAN
- **Yol**: `Huginn Data Insights/indexes/plan_index.md`
- **Dosya**: 33

### RAPOR
- **Yol**: `Huginn Data Insights/indexes/rapor_index.md`
- **Dosya**: 138

### TEKNIK
- **Yol**: `Huginn Data Insights/indexes/teknik_index.md`
- **Dosya**: 96

## Teknik Notlar

- **Sınıflandırma**: Klasör pattern, dosya adı, YAML frontmatter tags
- **Wikilink**: Full path format: `[[Huginn Data Insights/path/to/file]]`
- **Atlanmış**: Canonical backup dosyaları (`.md.backup_YYYY-MM-DD`), worktree klasoru/
- **SSOT**: Huginn Data Insights/ (D-172, D-177)

**Oluşturulma**: 2026-09-21T10:45:47.302635Z
**Rapor**: data\orchestrator\GRAPH-INDEX-BUILD_rapor_2026-09-21.md