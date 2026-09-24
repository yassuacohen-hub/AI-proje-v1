# GRAPH-CANONICAL-SECER-02 Raporu

- **Sahip**: Yasu
- **Tarih**: 2026-09-23T07:40:09.959040+00:00
- **Kaynak**: `data\orchestrator\GRAPH-CANONICAL_rapor_2026-09-21.json`
- **Durum**: ⚠️ Bulgular var (aşağıda)

## Özet
| Metrik | Değer |
|--------|-------|
| Grup sayısı | 156 |
| Canonical (seçili) | 156 |
| Canonical eksik | 0 |
| Kırık redirect | 8 |
| SSOT ihlali | 0 |
| İçeriği boşalan redirect dosyası | 0 |

## Bulgular

**Kök neden (13 bulgunun 13'ü):** `AI proje v1/` altındaki 11 ikiz dosya (AGENTS.md,
CHANGELOG.md, CLAUDE.md, AGENT_SYNC.md, ANA_KURALLAR.md, .instructions.md,
PROJECT_ROADMAP.md, README_ARAYUZ.md, Kimlik Doğrulama Sistemi.md, Kullanıcı
Yönetimi.md, Mimari Kararlar.md) ve `src/company_master/orchestrator/README.md`
çalışma dizininden **silinmiş** (backup'ları ve `.backup_2026-09-21` kopyaları duruyor).

- Git durumu: `AI proje v1` repo'sunda bu dosyalar `D` (deleted, unstaged) —
  **HEAD'de hâlâ mevcutlar**, `git checkout -- <dosya>` ile geri getirilebilir.
- Bu silme, GRAPH-CANONICAL-UYGULA (2026-09-21) redirect uygulamasından sonra
  gerçekleşmiş; redirect backlink'leri silinen kopyalardaydı → kırık redirect.
- Canonical'lar (ör. `Huginn Data Insights/AGENTS.md`, `Huginn Data Insights/CHANGELOG.md`)
  **sağlam ve erişilebilir** — SSOT zarar görmedi (D-172/D-177 korunuyor).

**⚠️ Orkestratör kararı bekliyor (müdahale YAPILMADI):**
Silinen 11 dosya çoğunlukla canonical'a redirect edilmiş ikizlerdi; silinmeleri
bilinçli bir temizlik olabilir. Geri getirme kararı orkestratöre/ihsan'a ait:
`git -C "AI proje v1" checkout -- AGENTS.md ...` ile restore edilebilir.

**Bulgu listesi:**
- **CANONICAL_KAYIP** — .instructions.md: Huginn Data Insights/AI proje v1/.instructions.md
- **CANONICAL_KAYIP** — agent_sync.md: Huginn Data Insights/AI proje v1/AGENT_SYNC.md
- **REDIRECT_KIRIK** — agents.md: Huginn Data Insights/AI proje v1/AGENTS.md
- **CANONICAL_KAYIP** — ana_kurallar.md: Huginn Data Insights/AI proje v1/ANA_KURALLAR.md
- **REDIRECT_KIRIK** — changelog.md: Huginn Data Insights/AI proje v1/CHANGELOG.md
- **CANONICAL_KAYIP** — claude.md: Huginn Data Insights/data/skills/supabase/CLAUDE.md
- **REDIRECT_KIRIK** — claude.md: Huginn Data Insights/AI proje v1/CLAUDE.md
- **REDIRECT_KIRIK** — readme.md: Huginn Data Insights/src/company_master/orchestrator/README.md
- **REDIRECT_KIRIK** — kimlik doğrulama sistemi.md: Huginn Data Insights/AI proje v1/Kimlik Doğrulama Sistemi.md
- **REDIRECT_KIRIK** — kullanıcı yönetimi.md: Huginn Data Insights/AI proje v1/Kullanıcı Yönetimi.md
- **REDIRECT_KIRIK** — mimari kararlar.md: Huginn Data Insights/AI proje v1/Mimari Kararlar.md
- **CANONICAL_KAYIP** — project_roadmap.md: Huginn Data Insights/AI proje v1/PROJECT_ROADMAP.md
- **REDIRECT_KIRIK** — readme_arayuz.md: Huginn Data Insights/AI proje v1/README_ARAYUZ.md

## Bağlantılar
- [[Karar: Graph canonical]] (D-177: Huginn Data Insights/ = graph canonical)
- D-172: worktree klasoru/ = yazma otorite, SSOT
- Önceki: [[GRAPH-CANONICAL_UYGULA_RAPOR_2026-09-21]]