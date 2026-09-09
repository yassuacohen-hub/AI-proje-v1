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
