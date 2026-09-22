# ALTYAPI-KILIT-YOL-FIX-01 — Üretim Brief

**Görev:** Kilit yolu konfigürasyonunu düzelt  
**Ajan:** utku (Üretim)  
**Öncelik:** P1  
**Tarih:** 2026-09-22

## Özet

`data/orchestrator/file_locks.json` dosyasında eski/stale yollar var — bunlar panoya gelen görevlerin dosya kilitlemesine engel oluyor. Stale kilitler temizle, kilit mekanizmasını test et.

## Adımlar

1. **Audit:** `file_locks.json` aç, tüm yolları oku. Hangi görevlere ait olduğunu kontrol et.
2. **Stale tespit:** Ilgili görev done mi veya silinmiş mi? Dosya gerçekten hala kilitli mi (sistem kontrol et)?
3. **Temizle:** Done görevlerin ve yok olan görevlerin kilitlerini düşür.
4. **Yeniden test:** `gorev_at.py at` ile test görev ekle, otomatik kilit kontrol et (`tb.gorev_ekle` dosya kilitlemeli).
5. **Teslim Not:** Temizlenen kilit sayısı, test sonucu, kilit mekanizması doğrulandı.

## Dosyalar

- `data/orchestrator/file_locks.json` — **kilitli** (düzenle)
- `Huginn Data Insights/src/company_master/orchestrator/task_board.py` (kilit kodu referans)

## Gözlemler

- Kilitler hangi dosyalara ait? `ALTYAPI-*`, `TEST-*` görevleri mi?
- Batch kilitlemesi çalışıyor mu (dosya listesi kommayla ayrılmış)?

**Teslim:** file_locks.json temiz, kilit mekanizması test edildi ve doğrulandı.
