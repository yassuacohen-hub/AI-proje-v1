---
agent: harici_ajan
source: workspace\external\harici_ajan\output\sector_analysis.md
ingested: 2026-09-12T07:24:44.858430+00:00
type: task_output
task_id: unknown
updated_at: unknown
sahip: unknown
durum: unknown
---
# Sektor Analizi

## Kapsam
- sector_doldur.py - dosya bulunamadi
- data/nace_to_ostim_sektor.json - NACE kod -> sektor haritasi

## Durum
- sector_doldur.py dosyasi src/company_master/etl/ icinde bulunamadi
- Kilo Code tarafindan sektor_doldur.py: 8.313 firmaya NACE sektor atandi (%69.3 dolu) olarak raporlanmis
- NACE haritasi mevcut (data/nace_to_ostim_sektor.json), ancak kod dosyasi eksik

## Oneriler
- src/company_master/etl/sector_doldur.py dosyasi olusturulmalidir
- data/nace_to_ostim_sektor.json uzerinden NACE -> sektor esleme mantigi yazilmali
- Harita dosyasindaki _meta disi tum girisler sektor atamasi icin kullanilmalidir

*Bu içerik harici_ajan tarafından 2026-09-12 07:24:44 UTC'de ingest edildi.*
