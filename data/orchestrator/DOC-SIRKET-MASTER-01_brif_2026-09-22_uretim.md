# DOC-SIRKET-MASTER-01 — Üretim Brief

**Görev:** Şirket Master ana belgesi düzelt  
**Ajan:** utku (Üretim)  
**Öncelik:** P1  
**Tarih:** 2026-09-22

## Özet

`01_sirket_master_ana_belgesi.md` belgesinde UTF-8 encoding hatası veya yapisal sorun var (board'da mojibake görünüyor: "Ã…Â", "dÃƒÂ¼zelt"). Belgeyi temizle, encoding düzelt, tüm linkler doğru olana kadar kontrol et.

## Adımlar

1. **Dosya bul:** `data/` veya `docs/` altında `*sirket_master*` dosyasını ara.
2. **Encoding taraması:** UTF-8 uyumluluğunu kontrol et. Mojibake karakterleri tespit et (Ã, â€, ™, vb.).
3. **Düzelt:** Belgeyi temiz UTF-8'de yeniden yaz veya dönüştür.
4. **Yapı kontrol:** İç linkler (`[[...]]`, `[link](...)`) doğru mu?
5. **Task board:** İlgili panodaki başlık temiz görülüyor mu?
6. **Teslim Not:** Sorun türü, çözüm yöntemi, doğrulama sonucu.

## Dosyalar

- `01_sirket_master_ana_belgesi.md` — **kilitli** (düzenle)
- `Huginn Data Insights/data/orchestrator/task_board.json` — doğru başlık görünsün

## Gözlemler

- Board'daki başlık mojibake: "Ã…Âirket Master ana belgesi dÃƒÂ¼zelt". Bu Windows-1252 veya CP-1251 kontaminasyonu olabilir.
- Dosya yok mu, kilitli mi, veya gerçekten encoding sorunu mu test et.

**Teslim:** Belgeyi temiz ve linkler doğru halde, başlık board'da düzgün.
