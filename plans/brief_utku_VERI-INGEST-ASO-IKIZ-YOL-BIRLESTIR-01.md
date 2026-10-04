# VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01 — Brief (utku)

**Başlık:** [VERİ-KİT] ASO ikiz ingest yolunu birleştir → tek kanonik dosya + tek yükleyici (3 saat)
**Öncelik:** P2 · **Kit:** `VERİ-KİT` (AGENTS.md D-196)
**Kilitli dosya:** `scripts/ingest_aso_data.py`, `src/company_master/etl/ingest_aso.py`, `scripts/refresh_pipeline.py`, `tests/test_ingest_aso_glob.py`
**Bağımlılık:** `VERI-INGEST-ASO-GLOB-01` (kapandı, 2026-10-03)
**Hub:** `hubs/VERI_KALITESI_HUB.md` — ZORUNLU (B-14). Görev kapanınca hub "Kapanan işler" bölümüne yazılır; yazılmazsa `teslim` reddedilir.

> **Tek brif kuralı (D-217):** Bağımsız iş. ADMIN zinciri (34-38) ile dosya çakışmaz.

## Neden
- Bulgu `data/orchestrator/bulgu_defteri.md:134` (utku, 🟡): iki ASO yükleyici var, farklı eşleşme mantığı:
  - `scripts/ingest_aso_data.py:70-134` — `unvan` okur, `LOWER(TRIM(legal_name))` eşleşmesi, `source_records` yazar.
  - `src/company_master/etl/ingest_aso.py` — SCRAPE-005'te yeniden yazıldı, `ON CONFLICT (legal_name) DO NOTHING`.
  - `refresh_pipeline.py:85-86` yalnız ikincisini çağırır → birincisi **çağrısız kod** (D-266).
- Üç aday veri dosyası: `data/aso/aso_full.jsonl` (1091 satır / 722 tekil), `aso_full_clean.jsonl` (785), `aso_full_filtered.jsonl`. Hangisi kanonik, karar yok. Geçmiş: `bulgu_defteri.md:111/114/116`.
- D-211 ikiz yasağı, D-212 tek adres, D-236 tüketicisi olmayan çıktı.

## Doğrulanacak varsayım
- `findstr /S /N /C:"ingest_aso_data" --> *.py *.md` ile çağıran listesi: beklenen yalnız `refresh_pipeline.py:85-86` + `ingest_aso.py` + raporlar/dokümanlar. Başka canlı çağıran varsa **dur**, chat.
- Üç dosyanın satır/tekil sayısı **yeniden ölçülür** (`python -c` ile, çıktı raporda) — 1091/722/785 beyan, kanıt değil (D-260).
- `source_records` yazımı ikinci yolda var mı? Yoksa birinci yolun bu kısmı korunur (veri kaybı yasağı).
- `tests/test_ingest_aso_glob.py` hangi modülü test ediyor? Test de taşınır.

## Adımlar
1. Ölç: üç dosya için `satır / tekil unvan / tekil vergi_no` tablosu; D-238 canlı DB'de `source_records WHERE source='aso'` sayısı.
2. Kanonik dosya kararı → `docs/VERI_KAYNAKLARI.md` (varsa) ya da hub'a tek satır: hangisi, neden. Diğer ikisi `data/aso/_eski/` altına taşınır (silinmez, D-231).
3. Eşleşme mantığı: `LOWER(TRIM(legal_name))` + `source_records` yazımı `etl/ingest_aso.py`'ye taşınır (doğru desen birincide). `ON CONFLICT` korunur.
4. `scripts/ingest_aso_data.py` **silinir** (çağrısız, D-266); dokümanlardaki referanslar `etl/ingest_aso.py`'ye çevrilir (`findstr` listesi raporda).
5. `refresh_pipeline.py` çağrısı değişmez; `python scripts/refresh_pipeline.py --dry-run` (varsa) çalışır.
6. Test: `tests/test_ingest_aso_glob.py`'ye assert — `scripts/ingest_aso_data.py` **yok** + `etl/ingest_aso.py` `source_records` yazıyor (mock engine ile).

## Kabul kriteri
- [ ] `python -m pytest -q tests/test_ingest_aso_glob.py tests/test_refresh_pipeline*.py` yeşil.
- [ ] `dir scripts\ingest_aso_data.py` → bulunamadı; `findstr /S /C:"ingest_aso_data" *.py` → yalnız `etl/ingest_aso.py` fonksiyon adı.
- [ ] Ölçüm tablosu (3 dosya + canlı DB) raporda; kanonik karar tek satırla hub'da.
- [ ] `bulgu_defteri.md:134` satırına `🟢 kapandı → VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01` eklenir.
- [ ] Hub "Kapanan işler".

## Kurallar (VERİ-KİT · D-196)
- Kanıtsız durum beyanı yasak (D-260).
- Veri silinmez, taşınır (D-231).
- Canlı DB ölçümü (D-238); yıkıcı iş yok (yalnız okuma + dosya taşıma).
- **Teslimden önce** hub satırı (B-14).

## Ajan chat zorunlu (D-210 · D-217)
- Varsayım tutmuyorsa → `ac`, uydurma.
- Tıkandıysa → sorun aç, sonraki adıma geç.
- @mention → P1 10-15 dk.

```bash
python scripts/ajan_chat.py ac utku VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01 "<sorun>" --cozum "<oneri>"
python scripts/ajan_chat.py oku --task-id VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01
python scripts/chat_gonder.py --to ihsan --type hata --task-id VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01 --mesaj "<metin>"
```

## Teslim

```bash
python scripts/gorev_kutusu.py teslim --ajan utku --task-id VERI-INGEST-ASO-IKIZ-YOL-BIRLESTIR-01 --ozet "<özet>"
```

**Teslimden sonra DURMAK YASAK (D-312 · D-335).**

```bash
python scripts/gorev_kutusu.py nobet --ajan utku
```

- Çıkış `0` = İŞ VAR → sıradaki görev.
- Çıkış `3` → ihsan'a kısa rapor, kapat.

## Ilgili Nodlar
- [[data/orchestrator/bulgu_defteri]] — :134 kaynak bulgu, :111/:114/:116 geçmiş
- [[Huginn Data Insights/hubs/VERI_KALITESI_HUB]]
- [[Huginn Data Insights/plans/brief_utku_VERI-INGEST-ASO-GLOB-01]] — öncül
- [[Huginn Data Insights/AGENTS]] — D-211, D-231, D-236, D-266
- [[plans/_brief_sablon]]
