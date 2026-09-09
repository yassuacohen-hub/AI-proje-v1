# Ingest Detail Analizi

## Kapsam
- scripts/ingest_ostim_detail.py - kaynak kod bulunamadi
- logs/ingest_ostim_detail.log - hata kaydi mevcut

## Durum
- scripts/ingest_ostim_detail.py dosyasi bulunamadi
- AGENT_SYNC.md: scripts/ingest_ostim_detail.py mevcut (vergi_no 11 hane regex + parsel adres fallback) olarak raporlanmis
- logs/ingest_ostim_detail.log dosyasi mevcut ancak icerigi okunamadi (log formati)

## Oneriler
- scripts/ingest_ostim_detail.py dosyasi yeniden olusturulmalidir veya scripts/ klasorunden silinmelidir
- Detay scrape eksik (sektor, adres, web_sitesi liste sayfasinda yok) - OSTIM detay sayfasi scraped edilmelidir
