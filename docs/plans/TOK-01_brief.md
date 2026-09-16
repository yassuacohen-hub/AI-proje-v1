# TOK-01 — Ajan Kural Dosyalarında Token Sıkıştırma (cline)

**Karar:** D-37 (batch tur + token verimliliği). **Kapsam:** yalnız `.md` / kural dosyaları; kod dosyasına dokunulmaz.

## Ölçüm (chars/4, her mesajda sabit yük)
| Dosya | Şimdi | Hedef |
|---|---|---|
| `AGENTS.md` | ~5.8K | ≤2.5K |
| `CLAUDE.md` | ~2.8K | ≤1.2K |
| `ANA_KURALLAR.md` | ~2.3K | ≤1.5K |
| `.roorules` | ~1.0K | ≤0.8K |
| **Toplam** | ~12K | **≤6K** |

## İş
1. `AGENTS.md` → **çekirdek** (zorunlu kurallar: koordinasyon, kilit, teslim→onay, ajan adları, proje sınırı, restart kuralları, dil) + ayrıntılar `docs/AJAN_DETAY.md`'ye taşınır (rol profilleri, ritüel/rotasyon ayrıntısı, harici ajan, versiyon hiyerarşisi, erişim matrisi, marka terminolojisi). Çekirdekte her taşınan bölüme tek satır link.
2. `CLAUDE.md` ve `ANA_KURALLAR.md`: `AGENTS.md` ile **çakışan/tekrar eden** bölümleri sil, tek yerden link ver. Yalnız o dosyaya özgü kurallar kalır.
3. `.roorules`: tekrarları at; 1-otonom-calisma.md ile çakışan satır kalmasın.
4. Kural **kaybı yok**: her silinen kural ya çekirdekte ya `AJAN_DETAY.md`'de bulunmalı. Teslim özetinde "taşınan bölüm → hedef" tablosu.
5. Ölçüm scripti çıktısı (önce/sonra) özete: `python -c "import sys;[print(f, len(open(f,encoding='utf-8').read())//4) for f in ['AGENTS.md','CLAUDE.md','ANA_KURALLAR.md','.roorules']]"`

## Kısıtlar
- UTF-8, BOM/NUL yok (`python scripts/kodlama_denetim.py`).
- `AGENTS.md` working tree'de değiştirilmiş (commitlenmemiş) — mevcut içerik üzerinden çalış, `git checkout` yapma.
- Commit atma. Teslim: `python scripts/gorev_kutusu.py teslim --ajan cline --task-id TOK-01 --ozet "..."`.
- BULGU NOTU: kapsam dışı sorun → `data/orchestrator/TOK-01_bulgular_<tarih>_cline.md`, düzeltme yapma.
