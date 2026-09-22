# P7-6 Kariyer.net Scraper MVP

## Durum: Tamamlandı

## Özet
Kariyer.net firma listesi için MVP scraper yazıldı.

## Dosyalar
- `src/company_master/scrapers/kariyernet.py` — `fetch()`, `parse()`, `save()` metodları ile `KariyerNetScraper` sınıfı
- `tests/test_kariyernet.py` — 2 test (fetch başarı, parse firma çıkarımı)
- `data/kariyernet_firmalar.jsonl` — JSONL çıktı (tekrar eden firma adları yok)

## Uygulanan Kısıtlar
- Pagination / JS / proxy: **defer**
- Encoding: **UTF-8, BOM yok**
- Hedef süre: **<20 dk**

---

## Ilgili Nodlar

- [[Huginn Data Insights/hubs/OSINT_VERI_TOPLAMA_HUB]]
