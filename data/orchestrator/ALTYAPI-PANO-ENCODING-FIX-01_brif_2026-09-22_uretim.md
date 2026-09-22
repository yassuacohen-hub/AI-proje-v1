# ALTYAPI-PANO-ENCODING-FIX-01 — Üretim Brief

**Görev:** Task board encoding hatalarını düzelt  
**Ajan:** utku (Üretim)  
**Öncelik:** P1  
**Tarih:** 2026-09-22  
**Blokaj:** ORKESTRA-NAMING-AUDIT-02 (task_board.json kilit çakışması)

## Özet

Board'da (~284) başlık mojibake hataları (UTF-8 kontaminasyonu): "Ã…Â", "â€™", "dÃƒÂ¼", vb. Python JSON okurken bu karakterler kalıyor. Board'ı temiz UTF-8'e çevir, başlıkları düzelt.

## Adımler

1. **Scan:** `task_board.json` dosyasını oku, mojibake karakterleri bul (regex: `Ã|â|ÃƒÂ|â€|™`).
2. **Fix script:** Python UTF-8 encoding düzeltme script yaz veya manual düzelt.
   - Seçenek A: `chardet` ile dosya encoding'i tespit et, CP-1252 → UTF-8 dönüşüm yap.
   - Seçenek B: JSON'u oku, başlık alanlarını normalize et, yeniden yaz.
3. **Doğrula:** 284 hata sayısı azalıyor mu?
4. **Test:** `gorev_kutusu.py bak` ile panoya bak, başlıklar temiz görülüyor mu?
5. **Teslim Not:** Bulunan/düzeltilen hata sayısı, yöntem, doğrulama.

## Dosyalar

- `data/orchestrator/task_board.json` — **kilitli** (blokaj nedeniyle ORKESTRA-NAMING-AUDIT-02 tamamlanana kadar beklemeli)

## Gözlemler

- Windows'ta JSON yazarken veya önceki agentler tarafından yanlış encoding yapılmış olabilir.
- `iconv` veya Python `chardet` + encoding dönüşümü etkili olabilir.
- Blokaj: İHSAN'ın ORKESTRA-NAMING-AUDIT-02 görevinde board dosyası kullanılıyor, aynı anda düzenlenemez.

**Teslim:** task_board.json temiz UTF-8, mojibake yok, başlıklar doğru.
