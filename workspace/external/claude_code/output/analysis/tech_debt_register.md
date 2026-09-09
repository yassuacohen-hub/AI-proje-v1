# Teknik Borc Kaydi

**Tarih:** 2026-09-02
**Analizci:** Claude Code

## Kritik (P0)

| # | Borc | Dosya | Satir | Tahmini Efor |
|---|------|------|-------|-------------|
| 1 | OSTIM detay scraper eksikligi | src/company_master/etl/scrapers/ostim_scraper.py | - | 6-8 saat |
| 2 | sector_doldur.py dosyasi yok | src/company_master/etl/ | - | 2-3 saat |
| 3 | ingest_ostim_detail.py dosyasi yok | scripts/ | - | 1-2 saat |

## Yuksek (P1)

| # | Borc | Dosya | Satir | Tahmini Efor |
|---|------|------|-------|-------------|
| 4 | Retry mekanizmasi eksik | src/company_master/etl/pipeline.py | 85-143 | 4-6 saat |
| 5 | Connection pooling ayarlaniyor | src/company_master/db/connection.py | - | 2-3 saat |
| 6 | Structured JSON log formati yok | src/company_master/etl/pipeline.py | - | 3-4 saat |
| 7 | Observability (metrics/tracing) eksik | tum proje | - | 8-10 saat |

## Orta (P2)

| # | Borc | Dosya | Satir | Tahmini Efor |
|---|------|------|-------|-------------|
| 8 | _similarity fonksiyonu SequenceMatcher kullanir | src/company_master/etl/entity_resolution.py | 26-27 | 2-3 saat |
| 9 | Fuzzy threshold 0.85 cok yuksek | src/company_master/etl/entity_resolution.py | 100 | 1-2 saat |
| 10 | data_quality_score formulu basit | src/company_master/etl/normalize.py | 50 | 3-4 saat |
| 11 | Dead code: _sample_df fonksiyonu kullanilmiyor | app.py | 181-189 | 0.5-1 saat |

## Dusuk (P3)

| # | Borc | Dosya | Satir | Tahmini Efor |
|---|------|------|-------|-------------|
| 12 | Kullanilmayan importlar | app.py | 1-10 | 0.5-1 saat |
| 13 | Test coverage dusuk alanlar | tests/ | - | 4-6 saat |

## Toplam

- Kritik: 3
- Yuksek: 4
- Orta: 4
- Dusuk: 2
- Toplam: 13
- Tahmini Toplam Efor: 38-52 saat
