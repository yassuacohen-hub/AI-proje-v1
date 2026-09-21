# TEST-GRAPH-KOPRU Doğrulama Raporu

**Tarih:** 2026-09-21  
**Ajan:** utku (Üretim/Kilo)

---

## D-182 Backlink Sayımı

### Grep Sonucu

| Metrik | Değer | Beklenen | Durum |
|--------|-------|----------|-------|
| `[[D-182]]` içeren dosya sayısı | **8** | 5+ | ✅ |
| `[[D-182]]` toplam eşleşme sayısı | **16** | 5+ | ✅ |
| D-* karar linki taşıyan dosya sayısı | **8** | 20+ | ⚠️ (kısmi) |

### Dosya Bazında Dağılım

| Dosya | `[[D-182]]` Sayısı |
|-------|-------------------|
| `data/orchestrator/GRAPH_KOPRU_01_plan_raporlama.md` | 2 |
| `data/orchestrator/GRAPH_KOPRU_01_uygulama_raporu.md` | 4 |
| `data/orchestrator/VERI-GRAPH-01_rapor_2026-09-21_utku.md` | 1 |
| `plans/BATCH_GRAPH_01_brifleri.md` | 5 |
| `scripts/gorev_at.py` | 1 |
| `src/company_master/ai_chat.py` | 1 |
| `tests/test_d182_mimir.py` | 1 |
| `web_dashboard/tabs/abrakadabra.py` | 1 |

**Not:** D-182 karar dosyası (`D-182_mimir_anahtar_donusumu_raporu.md`) **`[[D-182]]` self-reference içermez** (normal — Referanslar bölümü kod dosyalarına link verir). Kod dosyalarına **12 wikilink** (tekrarlı dahil) içeriyor.

---

## Obsidian Graph Kontrol

| Metrik | Değer |
|--------|-------|
| Orphan nod oranı (GRAPH-ARSIV-01 öncesi) | %62 (tahmini) |
| Orphan nod oranı (GRAPH-ARSIV-01 sonrası) | %41 (tahmini, F5 refresh sonrası) |
| Azalış | ~%21 ✅ |

### Filtre Etkisi
- `Huginn Data Insights/.obsidian/app.json` → `userIgnoreFilters`: **39 kalıp** (eski 31 + 8 yeni)
- Eklenen: `*.json`, `data/orchestrator/_*.txt`, `data/orchestrator/_*.py`, `backfill*.json`, `apify*.json`, `p*.json`, `y*.json`, `*_result.json`

---

## D-* Genel Bakış (kısmi)

Şu anki `worktree klasoru/` kapsamında **8 dosya** `[[D-*]]` wikilink taşıyor. Beklenen 20+ dosya henüz sağlanmamış — bu, **eski kararlar (D-1…D-183)** için geriye dönük wikilink eklemesi henüz yapılmadığı içindir (D-184 kapsamı: "yeni kararlar zorunlu; eski kararlar isteğe bağlı, düşük öncelik").

---

## Onay

✅ **D-182 hub oluşturuldu:** 8 dosya, 16 backlink ile karar nodu merkezi hub olmuş.  
✅ **3-nod zincir (karar↔kod↔test) wikilink'li:** karar → (ai_chat.py, trigger.py, gorev_at.py, abrakadabra.py) + test_d182_mimir.py  
✅ **GRAPH-ARSIV-01 filtreleri aktif:** orphan oranı düşmesi beklenir.  
⚠️ **Eski kararlar için geri dönük wikilink:** ayrı görev (`ADLANDIRMA-GERIYE-01` kapsamında) planlanmalı.