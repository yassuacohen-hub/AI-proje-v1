## Gorev Brief: Y2

**Gorev:** Ivedik + Baskent OSB verilerini ingest et (scraper kodu hazir)
**Sahip:** gelistirici
**Oncelik:** P0
**Durum:** aktif

### Dosyalar (sadece bunlari ac)
  - src/company_master/etl/scrapers/ivedik_scraper.py
  - src/company_master/etl/scrapers/baskent_scraper.py

### Aktif Lock'lar
  - src/company_master/etl/scrapers/ivedik_scraper.py (gelistirici)
  - src/company_master/schema/migrations/0007_osb.sql (mimar)
  - scripts/vkn_web_scraper.py (web_kazima)
  - AI proje v1/V10/07_referanslar/vkn_bulma_stratejisi.md (web_kazima)

### Kurallar
- Sadece yukaridaki dosyalari ac ve degistir
- Baska dosya acma (exploration yasak)
- Gorev bitince: gorev-guncelle Y2 --durum done
- Basarisiz olursa: gorev-guncelle Y2 --durum blocked --not "hata_aciklamasi"
