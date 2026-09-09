# Claude Code — Otomatik Görev Brief'i

> **Paket ID:** `EXT-CLAUDE_CODE-20260906`
> **Tarih:** 2026-09-06T11:42:20
> **Proje:** Huginn Data Insights — Ankara B2B Company Master
> **Rol:** Mimari dokümantasyon, güvenlik denetimi, teknik borç
> **Öncelik:** P0/P1/P2

---

## Görev: H002 — ETL mimarisi review + guncelle

**Açıklama:** AI proje v1/V10/03_mimari/01_etl_mimarisi.md dosyasini V9 baglam ile uyumlu hale getir.

### Beklenen Çıktı
- **Dosya:** `workspace/external/claude_code/output/docs/01_etl_mimarisi_review.md`
- **Bağımlılıklar:** Yok

### Kabul Kriterleri
- Görev dosyalarını oku, sadece izin verilen dosyaları değiştir.
- Çıktıyı `workspace/external/claude_code/output/` altına yaz.
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
