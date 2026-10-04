# VERI-INGEST-ASO-GLOB-01 — Brief (utku)

**Hub:** [[hubs/ADMIN_DASHBOARD_HUB]]
**Öncelik:** P1 · **Sahip:** utku · **Açan:** ihsan (bulgu #105, 2026-10-03 19:50)
**Kilitli dosya:** `src/company_master/etl/ingest_aso.py`
**Ön koşul:** SCRAPE-005 teslim edilmeden başlama (aynı ajan, sıra: önce SCRAPE-005).

## Neden

`[3/4] ingest` adımı `data/aso/` klasöründeki **rapor/özet dosyalarını** da firma kaydı sanıp okuyor.
Ölçülen: [`ingest_aso.py:19`](../src/company_master/etl/ingest_aso.py:19) `glob("*.csv")` + `glob("*.json")`, [`:31`](../src/company_master/etl/ingest_aso.py:31) `read_json(lines=True)`.
Sonuç: SCRAPE-005 kabul şartı 2 (4/4 adım) bu kapanmadan ölçülemez.

## Doğrulanacak varsayım

"Rapor dosyası `data/aso/` kökünde durduğu sürece `glob("*.json*")` onu firma kaydı sanır."
Ölçüm: ingest öncesi klasör listesi + `aso_full.jsonl` kayıt sayısı; rapor dosyası eklenince sayı değişiyorsa varsayım doğru.

## ŞART (patch öncesi — D-67)

Kod yazmadan **önce** `ajan_chat.py` ile ihsan'a 2 seçenekli çözüm önerisi yaz; onay sonrası patch:

| Seçenek | Ne yapar | Risk |
|---|---|---|
| A | glob'u `firmalar*.jsonl` / `aso_full.jsonl` ile daralt, rapor dosyalarını dışla | Yeni dosya adı çıkınca sessiz atlanır |
| B | Ham kayıtlar `data/aso/ham/` alt klasöre, rapor kökte kalır | Mevcut yolları kullanan 3+ script değişir |

Üçüncü seçeneğin varsa yaz. Karar chat'e `kapat --karar` ile düşer.

## Adımlar

1. `python scripts/gorev_kutusu.py al utku VERI-INGEST-ASO-GLOB-01`
2. Çözüm önerisi → chat (yukarıdaki şart). Cevap bekle.
3. Patch + test: `tests/test_ingest_aso_glob.py` — rapor dosyası varken ingest kayıt sayısı değişmez (sahte klasör, `tmp_path`).
4. Canlı: `python scripts/refresh_pipeline.py` → `[3/4] ingest` yeşil; `aso_full.jsonl` kayıt sayısı önce/sonra chat'e.
5. `python -m pytest tests/test_ingest_aso_glob.py tests/test_scrape005_kabul_sartlari.py -q`

## Kabul kriteri

- Chat'te öneri + ihsan kararı var (şart).
- `[3/4] ingest` canlıda hatasız; rapor dosyası okunmuyor (log'da dosya listesi).
- Yeni test dosyası yeşil; mevcut 36 test yeşil.
- SCRAPE-005 karar belgesi §Kabul 3b → "4/4 ikinci koşu" burada ölçülür.

## Kurallar (ADMIN-KİT · D-196)

- Yalnız `ingest_aso.py` + yeni test dosyası. Başka dosyaya dokunmak = ayrı görev.
- `data/aso/*.jsonl` üretim verisi; silme/yeniden adlandırma yok (seçenek B seçilirse ihsan onayıyla taşıma).

## Ajan chat zorunlu (D-210 · D-217)

- Başlangıç: `python scripts/ajan_chat.py ac ihsan VERI-INGEST-ASO-GLOB-01 "oneri: A/B/C ..." --kimden utku`
- Bitiş: kayıt sayısı önce/sonra + test çıktısı.

## Teslim

`python scripts/gorev_kutusu.py teslim utku VERI-INGEST-ASO-GLOB-01 --sonuc "ingest_aso glob daraltildi; N kayit; tests yesil"` → `bulgu_defteri.py ekle` (varsa yeni bulgu) → `utku_project_context.md` Tuzaklar.

## Ilgili Nodlar

- [[hubs/ADMIN_DASHBOARD_HUB]]
- [[data/orchestrator/SCRAPE-005-KAZIMA-DOCKER-INTEGRATION_karar_2026-10-03]]
- [[plans/brief_utku_SCRAPE-005-KAZIMA-DOCKER-INTEGRATION]]
