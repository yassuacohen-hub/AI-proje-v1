# Telegram Bot Rehberi

Bağlantılar: [[00-Home]] · [[10_ankara_osb_sentez]] · [[project_state]] · [[CHANGELOG]]

**Tarih:** 2026-09-01
**Sürüm:** 1.0
**Bot:** [@Huginn_Insights_Bot](https://t.me/Huginn_Insights_Bot)
**Karar referansı:** [[10_ankara_osb_sentez]] Karar 13

---

## 1. Bot Bilgileri

| Alan | Değer |
|---|---|
| Bot adı | Huginn Insights Bot |
| Username | [@Huginn_Insights_Bot](https://t.me/Huginn_Insights_Bot) |
| Token | `.env` dosyasında (`TELEGRAM_BOT_TOKEN`) |
| Chat ID | `.env` dosyasında (`TELEGRAM_CHAT_ID`) |
| Polling script | `scripts/telegram_polling.py` |
| Bildirim modülü | `src/company_master/utils/telegram_bot.py` |

---

## 2. Güvenlik

- **Token saklama:** `TELEGRAM_BOT_TOKEN` yalnızca `.env` dosyasında tutulur.
- **Git:** `.env` dosyası `.gitignore`'da listelenmiştir; asla commit yapılmaz.
- **Log:** Token'lar loglarda maskelenir (`8603398149:****c2M`).
- **Paylaşım:** Token'ı kimseyle paylaşmayın; Product Owner ile Koordinatör arasında kalmalıdır.

---

## 3. Botu Çalıştırma

### Başlat
```powershell
cd "C:\Projeler\Huginn Data Insights"
$env:TELEGRAM_BOT_TOKEN = (Get-Content .env | Where-Object { $_ -match "TELEGRAM_BOT_TOKEN" }).Split("=")[1]
$env:TELEGRAM_CHAT_ID = (Get-Content .env | Where-Object { $_ -match "TELEGRAM_CHAT_ID" }).Split("=")[1]
python scripts/telegram_polling.py
```

### Arka planda başlat (Windows)
```powershell
Start-Process -FilePath "python" -ArgumentList "scripts\telegram_polling.py" -NoNewWindow -WorkingDirectory "C:\Projeler\Huginn Data Insights"
```

### Durdur
```powershell
Get-Process python | Where-Object { $_.CommandLine -like "*telegram_polling*" } | Stop-Process -Force
```

---

## 4. Komutlar

| Komut | Açıklama | Örnek Çıktı |
|---|---|---|
| `/start` | Bot tanıtımı | Proje adı, amaç |
| `/help` | Komut listesi | Tüm komutlar |
| `/status` | Proje durumu | Canlı kayıt sayısı, sürüm, arayüz URL |
| `/gorev` | Aktif görevler | 5 başlık halinde görev listesi |
| `/rapor` | Son kalite raporu | Toplam, ortalama kalite, yüksek sayısı |
| `/wiki` | Wiki sayfaları | 7 önemli sayfa |

---

## 5. Otomatik Bildirimler

Aşağıdaki olaylar otomatik Telegram mesajı gönderir:

| Olay | Fonksiyon | Örnek |
|---|---|---|
| Yeni görev başladı | `send_task_started(task, agent)` | "🚀 Yeni Görev Başladı — Geliştirici" |
| Görev tamamlandı | `send_task_completed(task, agent, summary)` | "✅ Görev Tamamlandı — 300 firma" |
| Kritik hata | `send_alert(title, message)` | "⚠️ Scraper Hatası" |
| Günlük özet | `send_daily_summary(stats)` | "📊 Günlük Özet" |

---

## 6. Geliştirici Kullanımı

```python
from src.company_master.utils.telegram_bot import (
    send_message,
    send_task_started,
    send_task_completed,
    send_alert,
)

# Basit mesaj
send_message("<b>Test</b> mesaji")

# Görev bildirimleri
send_task_started("OSTİM scrape", "Geliştirici Ajan")
send_task_completed("OSTİM scrape", "Geliştirici Ajan", "300 firma parse edildi")

# Hata bildirimi
send_alert("Scraper Hatası", "Selector bulunamadi: div.col-lg-4.mb-3")
```

---

## 7. Sorun Giderme

| Sorun | Çözüm |
|---|---|
| Bot cevap vermiyor | Polling çalışıyor mu? `Get-Process python` kontrol et |
| "TOKEN not set" hatası | `.env` yüklenmemiş; ortam değişkenlerini ayarla |
| Emoji bozuk | `PYTHONIOENCODING=utf-8` ayarla |
| Rate limit | Telegram limit: saniyede 30 mesaj; aşma durumunda bekle |

---

## 8. İlgili Wiki

- [[10_ankara_osb_sentez]] Karar 13 — Telegram bot entegrasyon kararı
- [[project_state]] — Proje durumu
- [[00-Home]] — Ana sayfa