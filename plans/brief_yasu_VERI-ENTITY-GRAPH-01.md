# VERI-ENTITY-GRAPH-01 — Brief (yasu)

**Başlık:** [VERI] Firma ilişki ağı v0 yaz → 0047_entity_graph.sql (4s)
**Öncelik:** P1 · **Kit:** `VERI` (AGENTS.md D-196)
**Kilitli dosya:** `src/company_master/schema/migrations/0047_entity_graph.sql`
**Hub:** `hubs/OSINT_VERI_TOPLAMA_HUB.md` — ZORUNLU (B-14). Görev kapanınca bu hub'ın "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Fazlar aşağıda `## Faz A/B/C` olarak yazılı.

## Neden

SSOT yol haritasının **Faz 3 — Entity Graph** adımı. Amacı SSOT'ta tek cümleyle yazılı:
*"Şirket ekosistemini görselleştirmek."* Bugün ne tablo ne de kenar üretici var.

| Kanıt | Yer |
|---|---|
| Entity Graph düğüm türleri (Şube, Marka, Grup Şirketleri dahil 10 tür) | `yedekler/Huginn Data Insights (HUGIns).txt:760-779` |
| Nihai çıktı listesinde "Entity Graph (şirket ağ haritası)" | `yedekler/Huginn Data Insights (HUGIns).txt:824-849` |
| Faz 3 = Entity Graph | `yedekler/Huginn Data Insights (HUGIns).txt:850-873` |

**v0 kapsamı dar tutulur.** İlk sürümde yalnız **elde veri olan 2 kenar türü** üretilir:

| Kenar türü | Kaynak | Neden bu ikisi |
|---|---|---|
| `same_osb` (aynı OSB'de komşu) | mevcut OSB verisi | ölçülmüş, elde var |
| `nace_complementary` (NACE tamamlayıcılığı) | `company_industries` | ölçülmüş, elde var |

Kalan 8 düğüm türü (ortaklık, grup şirketi, marka, şube...) **bu görevin kapsamı değildir**;
kaynağı yok. Tablo onları taşıyacak şekilde açılır ama **boş bırakılır** (D-249: boş ≠ yok sayılmış).

## Doğrulanacak varsayım

- Son göç numarası **0047** varsayıldı (0046 `VERI-RISK-MOTORU-01` tarafından alınıyor). 0047 diskte varsa **dur**, sorun aç.
- `company_industries` tablosu ve `is_primary` kolonu var varsayıldı. Yoksa **dur** — `VERI-NACE-COKLU-01` bu alanı dolduruyor, bağımlılık olabilir.
- OSB bilgisinin firma kaydında bir kolonda tutulduğu varsayıldı. **Kolon adını ölçerek bul**, tahmin etme (D-245: kolon adı veri türünü garanti etmez).
- `companies.id` birincil anahtar varsayıldı.
- Kenar yönsüzdür varsayıldı → `(a_id, b_id)` çiftinde `a_id < b_id` kısıtı konur, çift kayıt engellenir.

## Faz A — Şema (en riskli, ilk sırada)

1. `0047_entity_graph.sql` yaz: `company_edges` tablosu.
   - `company_a_id`, `company_b_id` (FK), `edge_type TEXT`, `strength NUMERIC(5,2) NULL`, `evidence TEXT`, `source TEXT`, `created_at`.
   - `CHECK (company_a_id < company_b_id)` — yönsüz kenarın tek temsili.
   - `UNIQUE (company_a_id, company_b_id, edge_type)`.
   - `edge_type` için `CHECK`: 10 düğüm/ilişki türünün kanonik listesi; v0'da yalnız 2'si doldurulur.
2. Her kolona `COMMENT`: SSOT satır referansı.
3. `down/0047_entity_graph.sql` yaz.
4. `schema_versions.json`'a satır ekle.

## Faz B — Kenar üretici

5. `src/company_master/graph/kenarlar.py` yaz: `osb_komsulari()` ve `nace_tamamlayici()` — ikisi de **liste döner, DB'ye yazmaz**.
6. Tek yazma kapısı: `kenarlari_yaz()` — `ON CONFLICT DO NOTHING` ile idempotent.
7. `evidence` alanına kenarın **neden** kurulduğu yazılır (örn. "aynı OSB: Başkent OSB"). Boş `evidence` ile kenar yazmak yasak (D-260: kanıtsız iddia yok).
8. `strength` ölçülemiyorsa **NULL** yazılır, 0 yazılmaz (D-249).

## Faz C — Mandal (D-256/4: kırılarak doğrulanır)

9. `tests/test_entity_graph.py` yaz. En az 5 assert:
    - `(b, a)` sırası ters verilirse üretici normalize ediyor (a<b).
    - aynı kenar iki kez yazılırsa tablo tek satır tutuyor.
    - `evidence` boşsa yazıcı hata veriyor.
    - ölçülemeyen `strength` → `None`, 0 değil.
    - `edge_type` kanonik liste dışıysa hata veriyor.
10. Mandalı **kır**, kırmızıyı teslim özetine yaz, yeşili geri al.

## Kabul kriteri

- [ ] `0047_entity_graph.sql` + `down/` eşi + `schema_versions.json` güncel.
- [ ] `python -m pytest tests/test_schema_validation.py tests/test_entity_graph.py` yeşil.
- [ ] v0'da üretilen kenar türü **yalnız 2**; kalan türler şemada var ama boş.
- [ ] `strength` kolonunda `DEFAULT 0` yok.
- [ ] Yazıcı tek: grep ile ikinci `INSERT INTO company_edges` yok.
- [ ] Mandal kırılarak doğrulandı.

## Kurallar (VERI-KİT · D-196)

- **Görev başında** SSOT oku: `yedekler/Huginn Data Insights (HUGIns).txt:755-850`.
- Kanıtsız durum beyanı yasak: her "yapıldı" satırı `dosya:satır` gösterir (D-260).
- Canlı DB'ye toplu kenar yazımı **bu görevin kapsamı değil** (D-238); şema + üretici + mandal ile biter.
- Yeni bağımlılık ekleme (networkx vb. **yok**); saf SQL + stdlib.
- **Teslimden önce** `hubs/OSINT_VERI_TOPLAMA_HUB.md` "Kapanan işler" bölümüne `VERI-ENTITY-GRAPH-01` satırı yaz (B-14).

## Ajan chat zorunlu (D-210 · D-217)

```bash
python scripts/ajan_chat.py ac yasu VERI-ENTITY-GRAPH-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-ENTITY-GRAPH-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id VERI-ENTITY-GRAPH-01 --mesaj "<metin>"
```

OSB kolonunu bulamazsan **dur ve yaz** — kolon adı uydurmak D-245 ihlalidir.

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan yasu --task-id VERI-ENTITY-GRAPH-01 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312).**

```bash
python scripts/gorev_kutusu.py bak --ajan yasu
python scripts/ajan_chat.py oku --son 10
```

## Ilgili Nodlar

- [[Huginn Data Insights/AGENTS]] (D-238, D-245, D-249, D-260)
- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
- [[plans/_brief_sablon]]
