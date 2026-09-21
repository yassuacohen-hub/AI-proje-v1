[[Huginn Data Insights/data/orchestrator/ADMIN-HITAP-01_rapor_2026-09-18_roo.md]]

# ADMIN-HITAP-01 — Rapor (roo, 2026-09-18)

D-49 hitap kuralı uygulaması: "sahip" → `KAHİN (Ürün Sahibi)`.

## Düzeltilen satırlar
| Dosya:satır | Eski | Yeni |
|---|---|---|
| `AGENTS.md:12` | `(S-07, sahip kararı 2026-09-16)` | `(S-07, KAHİN kararı 2026-09-16)` |
| `AGENTS.md:38` | `(D-48, sahip kararı 2026-09-17)` | `(D-48, KAHİN kararı 2026-09-17)` |
| `AGENTS.md:138` | `Sabah roo/sahip` | `Sabah roo/KAHİN` |
| `docs/AJAN_DETAY.md:8` | `yalnızca sahibin sözüyle` | `yalnızca KAHİN'in (Ürün Sahibi) sözüyle` |
| `docs/AJAN_DETAY.md:14` | `\| Sahip cümlesi \|` | `\| KAHİN cümlesi \|` |
| `docs/AJAN_DETAY.md:24` | `rotasyon yalnızca sahip ritüeliyle` | `rotasyon yalnızca KAHİN ritüeliyle` |
| `docs/ARASTIRMA_API_PLAN_2026-09-17.md:142` | `### Sahip için adımlar` | `### KAHİN (Ürün Sahibi) için adımlar` |

## Kasten DOKUNULMAYAN (muaf)
| Yer | Gerekçe |
|---|---|
| `AGENTS.md:33` | D-49 kuralının kendi tanım metni: *"sahip", "kullanıcı", "efendim" kelimeleri YASAK* — kural silinemez |
| `docs/AJAN_DETAY.md:157`, `:159` | Kod parametresi: `gorev_ekle(task_id, baslik, sahip, ...)`, `lock_birak(dosya, sahip)` |
| `AGENT_SYNC.md:8`, `:27` | Otomatik üretilen tablo kolon başlığı (`task_board.sahip` alanı) — kaynak koddan gelir |
| `docs/GOREV_PANOSU_KULLANIM_KILAVUZU.md:32`, `:51` | Şema alan adı dokümantasyonu (`sahip` → str) |
| `docs/ISBIRLIGI.md:100` | Kod örneği çıktısı `{task_id, sahip, rol}` |

## Taranan ve temiz çıkanlar
`.clinerules`, `.roorules`, `.cursorrules`, `CLAUDE.md`, `ANA_KURALLAR.md`, `.instructions.md` — hitap ihlali yok.

## Kanıt
- `python scripts/kodlama_denetim.py` → `temiz: kodlama ihlali yok` / `allowlist disi ihlal yok`
- Tarama: `findstr /n /i "sahip karar sahibin sahip emri efendim roo/sahip" ...`

## Kapsam dışı bulgu
`sahip` kelimesi **kod alanı adı** olarak 20+ yerde geçiyor (`task_board.sahip`, `lock_birak(dosya, sahip)`).
Kod seviyesinde yeniden adlandırma D-49 kapsamı DEĞİL — ayrı görev gerektirir (geriye dönük uyumluluk + JSONL migrasyonu).
Öneri: yapılmasın (YAGNI); hitap kuralı insan metinlerine bakar.

## Sonraki
Zincir: `ADMIN-ROO-DENETIM-01`
