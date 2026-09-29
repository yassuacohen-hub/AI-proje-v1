# Veri Yazma Kuralları (D-303)

Amaç: **sistem yalan söylemesin.** Bu belge kısa; zorlayan mandal
[`tests/test_yazma_kapisi.py`](../tests/test_yazma_kapisi.py), kapı
[`src/company_master/db/yazma_kapisi.py`](../src/company_master/db/yazma_kapisi.py).
Belge beyandır, kapı zorlayandır (D-261).

## Ölçüm (D-303, canlı DB)

| Ölçüm | Değer |
|---|---|
| `companies` | 9.412 |
| `source_records` | 10.601 |
| Şablon `website_domain` | **2.666** (devir notu 2.142 diyordu — yanlış) |
| Şablon kayıtların kaynağı | **%100 tek kaynak**: `ostim.org.tr` / `web_scrape` |
| Şablon e-posta / adres | 17 / 0 |
| `source_records.collected_at` NULL | 0 (iyi) |
| `companies.source_record_id` NULL | 3 |
| Bağımsız DB bağlantısı | 58 (27 `create_engine` + 17 `psycopg.connect` + 15 `sqlite3.connect`) |
| SQL yazan dosya | 79 |
| Kanonik listeyi kopyalayan dosya | **23** (5 ayrı isimle) |

**Kök sebep:** filtre eksikliği değil, **kanonik liste yokluğu**. Aynı şablon
listesi 23 dosyada `GENERIC`, `PLACEHOLDER_DOMAINS`, `skip_domains`,
`WEB_BLOCKLIST`, `_ALT_YAPI_WEB` adlarıyla kopyalanmış; kopyalar birbirinden sapmış.
Filtresiz kalan yol 2.666 kayıt yazmış.

## Kurallar

1. **Tek liste.** Yasak/şablon değerler yalnız `db/yazma_kapisi.py`'de tanımlanır.
   Yeni kod kopyalamaz, **import eder**. Mandal: kopya sayısı 23'ü aşamaz.
2. **Şablon değer yazılmaz.** `sablon_mu()` doğruysa alan `None` olur, kayıt
   yazılır ama alan boş kalır. Sebep raporlanır.
3. **Yokluk 0 değildir, boştur** (D-249). `0`, `-`, `yok`, `n/a`, `null` bilgi
   sayılmaz; `temizle()` bunları `None` yapar. Puanlamada "dolu" gibi görünmez.
4. **Köken zorunlu.** Her `companies` kaydı `source_record_id` taşır; köken
   zinciri `companies.source_record_id → source_records.source_id → sources`.
   `source_records.collected_at` toplanma zamanıdır. Kökensiz kayıt
   işaretlenir (D-287: tahmin, doğrulanmış gibi puanlanmaz).
   Not: `companies` üzerinde `source`, `collected_at`, `postal_code` kolonları
   **yoktur** — ölçüldü. Köken zincir üzerinden okunur.
5. **Veri silinmez.** Kapı yazmayı engeller, mevcut kaydı silmez.
   Silme yetkisi ürün sahibindedir.

## Kabul/ret kontrolü

```python
from company_master.db.yazma_kapisi import kabul
temiz, sebep = kabul(kayit)   # sebep boş değilse kayıt kirli girmiştir
```

Kapı kendini doğrular: `python src/company_master/db/yazma_kapisi.py`.

## Kapsam — kalan yollar (sıralı, tek turda birleştirilmez)

Bu tur **en çok yalan üreteni** kesti (şablon web, 2.666 kayıt, tek kaynak).
Kalan sıra, etkiye göre:

1. `src/company_master/etl/scrapers/ostim_scraper.py` + `ostim_detail_scraper.py`
   — 2.666 kaydı yazan yol; kanonik listeye bağlanacak.
2. `scripts/ingest_*` ailesi (4 dosya) — kendi `GENERIC` kopyaları var.
3. `scripts/p43_*`, `scripts/vkn_*` (4 dosya) — VKN yolu.
4. 15 `sqlite3.connect` — yasu'nun ayrı `company_master.db`'si; Postgres'le
   aynı kapıyı paylaşmıyor.
5. 17 `psycopg.connect` — `connection.py` atlayan doğrudan bağlantılar.

Borç kimliği: `BORC-YAZMA-KAPISI` (açık, bu turda daraltıldı).
