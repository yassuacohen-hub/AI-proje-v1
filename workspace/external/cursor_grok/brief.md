# Cursor Grok — Otomatik Görev Brief'i

> **Paket ID:** `EXT-CURSOR_GROK-20260906`
> **Tarih:** 2026-09-06T11:42:20
> **Proje:** Huginn Data Insights — Ankara B2B Company Master
> **Rol:** Code review, refactor, test üretme
> **Öncelik:** P0/P1/P2

---

## Görev: H003 — Ostim scraper code review

**Açıklama:** src/company_master/etl/scrapers/ostim_scraper.py dosyasini gozden gecir, iyilestirme oner.

### Beklenen Çıktı
- **Dosya:** `workspace/external/cursor_grok/output/code_review.md`
- **Bağımlılıklar:** Yok

### Kabul Kriterleri
- Görev dosyalarını oku, sadece izin verilen dosyaları değiştir.
- Çıktıyı `workspace/external/cursor_grok/output/` altına yaz.
- Tamamlanınca `harici_ajan_sonuc_topla.py` çalıştır.


## Kısıtlar
1. Proje kökü DEĞİŞTİRİLEMEZ.
2. Harici ajan `workspace/external/{ajan}/output/` dışına dosya yazamaz.
3. `.env` / secret / KVKK verisine erişim YOK.
4. Üretim veritabanına erişim YOK.
5. Kod değişikliği yalnızca görevle ilgili dosyalara yapılır.


## Bağlam Dosyaları
- `AI proje v1/V10/05_versiyonlar/01_versiyon_9_baglam_dokumani.md`
- `AI proje v1/V10/TODO.md`
- `data/orchestrator/task_board.json`
- `AGENT_SYNC.md`
