# GRAPH-KOPRU-01 — Karar ↔ Kod ↔ Test Çapraz Link Planlaması

**Tarih:** 2026-09-21 · **Hazırlayan:** KAHİN (orkestratör analizi) · **Durum:** Planı yapılıyor

---

## 1. Mevcut Durum

**Tamamlanan:** (AGENTS.md satır 480-511)
- ✅ GRAPH-FIX-02 — 8 büyük izole nod backlink'leri
- ✅ GRAPH-HUB-EXPAND — 5 kategori hub + 200 orphan bağlantı
- ✅ GRAPH-INDEX-BUILD — 4 tür-bazlı index + 319 orphan bağlantı

**Sorunu:** decision_log.jsonl kaydında bir D-XXX (örn. D-182) yazılıysa, şu dosyalar bağlantısız duruyor:
- `worktree klasoru/src/company_master/ai_chat.py` (implementasyon)
- `worktree klasoru/tests/test_d182_mimir.py` (test)
- `worktree klasoru/AGENTS.md` bölümü (kural)

Graph'ta **D-182** hub olmadığı için orphan nod'lar bağlantıya bir köprü yok. Hub'lar (TECHNICAL_DOCS_HUB, plan_index, vs.) bu dosyaları zaten alıyor ama **karar → kod → test** zincir görünmüyor.

---

## 2. Amaç (GRAPH-KOPRU-01)

Bir karar kaydı (D-XXX) yazıldığında, **karar ↔ implementasyon ↔ test** arasında çapraz wikilink oluştur. Böylece Obsidian'da:
- D-182 nodu → ai_chat.py (kodlama)
- ai_chat.py → test_d182_mimir.py (doğrulama)
- test_d182_mimir.py → D-182 (gerekçelendirme)

**Çıktı:** Karar başına ortalama 3 nod, ~50 karar × 3 = ~150 yeni backlink, orphan oranı %60'tan %40'a düşer.

---

## 3. Teknik Tasarım

### 3.1 Adlandırma Kuralı
Karar kaydındaki `id` alanı örn. "D-182" ise:

1. **Kod dosyası** — `src/` veya `worktree klasoru/scripts/` altında:
   - Pattern: `*_d182_*` veya `*_D182_*` (case-insensitive)
   - Örn: `ai_chat.py` içinde `# D-182:` yorum
   - Örn: `gorev_at.py` içinde `# cmd_abrakadabra: D-182'ye referans`

2. **Test dosyası** — `tests/` altında:
   - Pattern: `test_d182_*.py` veya `*_d182_test.py`
   - Örn: `tests/test_d182_mimir.py`

3. **Karar belgesi** — `data/orchestrator/`:
   - Pattern: `D-182_*.md` veya `D-182_*.jsonl`
   - Örn: `D-182_mimir_anahtar_donusumu_raporu.md`

4. **AGENTS.md** — Kural bölümü:
   - Başlık: `## [ALAN] [FIIL] (D-182 — ...)`
   - Örn: `## MIMIR — Orkestratör Asistanı, İki Seviye (D-182 — ...)`

### 3.2 Wikilink Eklemesi (Elle veya Script)

**Seçenek A — Elle (ilk tur, sağlam):**
Karar yazıldıktan sonra ilgili dosyalar bulunup, içine wikilink eklenir.

Örn. `ai_chat.py` satır 30-35 başında:
```python
"""
AI Chat asistanı (MIMIR).

Karar: [[D-182]] (Orkestratör Asistanı İki Seviye)
Kural: Seviye 0 = MIMIR, Seviye 1 = ODIN
Test: [[tests/test_d182_mimir.py]]
"""
```

Örn. `tests/test_d182_mimir.py` başında:
```python
"""
Test: MIMIR iki seviye mekanizması doğrulaması.

Karar: [[D-182]] (Orkestratör Asistanı İki Seviye)
Implementasyon: [[ai_chat.py]]
"""
```

Örn. `D-182_mimir_anahtar_donusumu_raporu.md` başında:
```markdown
# D-182 — MIMIR Anahtar Dönüşümü Raporu

**Referanslar:**
- Kod: [[src/company_master/ai_chat.py]]
- Test: [[tests/test_d182_mimir.py]]
- Kural: [[AGENTS.md#MIMIR]] (D-182 bölümü)
```

**Seçenek B — Script (gelecek tur, ölçeklendirme):**
`scripts/graph_kopru_kaydetci.py` — decision_log.jsonl'daki yeni D-XXX'leri okur, ilgili dosyaları bulur, wikilink kodu enjekte eder (regex ile, docstring başına).

---

## 4. Sprint Taksı (BATCH-GRAPH-01 tamamlama)

| Görev | Ajan | Tahmini | Dosyalar |
|---|---|---|---|
| GRAPH-KOPRU-01-ELLE | utku | 4 saat | ai_chat.py, gorev_at.py, trigger.py, test_d182_mimir.py, D-182_*.md, AGENTS.md |
| GRAPH-ARSIV-01 | ihsan | 0.5 saat | .obsidian/app.json (userIgnoreFilters) |
| TEST-GRAPH-KOPRU | salih | 2 saat | Obsidian CLI ile backlink sayımı doğrulaması |

**Sıra:** GRAPH-KOPRU-01 → TEST-GRAPH-KOPRU → GRAPH-ARSIV-01

---

## 5. Karar Önerisi (D-184)

Karar yazılmadan önce ajan + sahip onayı gerekliyor. Burada taslak:

| Alan | Değer |
|---|---|
| **ID** | D-184 |
| **Tarih** | 2026-09-21 |
| **Başlık** | Graph Köprü Kuralı: Karar ↔ Kod ↔ Test Wikilink'leri |
| **Karar** | Her karar kaydı (D-XXX) yazıldıktan sonra, ilgili kod dosyaları (`*_dXXX_*` pattern) ve test dosyaları (`test_dXXX_*.py` pattern) içine docstring/başında wikilink eklenir: `[[D-XXX]] - [başlık]`. Karar belgesi de kod ve test dosyalarına backlink içerir. Wikilink'ler Obsidian graph'ta karar nodu'nu hub olarak oluşturur; orphan oranı azalır. |
| **Kapsam** | Yeni kararlar (D-XXX); eski kararlar (D-1…D-183) geriye dönük wikilink eklemesi ADLANDIRMA-GERIYE-01 ile birleştirilir (isteğe bağlı, düşük öncelik). |
| **Yürürlük** | Derhal (yeni karar yazıldığında) |
| **Karar Veren** | KAHİN |

---

## 6. Bağlantılar

- **Karar:** `data/orchestrator/D-184_graph_kopru_kurali_karar.jsonl` (yazılacak)
- **Brief:** `worktree klasoru/plans/BATCH_GRAPH_01_brief.md` (yazılacak)
- **Referans:** AGENTS.md satır 480-511 (GRAPH-FIX-02, GRAPH-HUB-EXPAND, GRAPH-INDEX-BUILD)
