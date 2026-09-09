# GitHub Copilot — Otomatik Görev Brief'i

> **Paket ID:** `EXT-COPILOT-20260906`
> **Tarih:** 2026-09-06T11:42:20
> **Proje:** Huginn Data Insights — Ankara B2B Company Master
> **Rol:** CI/CD, test, deploy, operasyon otomasyonu
> **Öncelik:** P0/P1/P2

---

## Görev: H001 — ASO verisini ingest et

**Açıklama:** data/aso/aso_full.jsonl (488KB) dosyasini DB'ye yaz. Ingestion scripti yok, uret.

### Beklenen Çıktı
- **Dosya:** `scripts/aso_ingest.py`
- **Bağımlılıklar:** Yok

### Kabul Kriterleri
- Görev dosyalarını oku, sadece izin verilen dosyaları değiştir.
- Çıktıyı `workspace/external/copilot/output/` altına yaz.
- Tamamlanınca `harici_ajan_sonuc_topla.py` çalıştır.


## Görev: H004 — Telegram bot systemd servisini test et

**Açıklama:** scripts/telegram_bot_systemd.service dosyasini test et, duzelt ve dokumantasyon yaz.

### Beklenen Çıktı
- **Dosya:** `workspace/external/copilot/output/scripts/telegram_bot_systemd.service`
- **Bağımlılıklar:** Yok

### Kabul Kriterleri
- Görev dosyalarını oku, sadece izin verilen dosyaları değiştir.
- Çıktıyı `workspace/external/copilot/output/` altına yaz.
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
