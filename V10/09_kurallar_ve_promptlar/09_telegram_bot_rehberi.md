# Telegram Bot Rehberi

Bağlantılar: [[00-Home]] · [[10_ankara_osb_sentez]] · [[project_state]] · [[CHANGELOG]]

**Tarih:** 2026-09-13
**Sürüm:** 2.0
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
| Ek yetkili chat ID'leri | `.env` dosyasında (`TELEGRAM_ALLOWED_CHAT_IDS`, opsiyonel) |
| Polling script | `scripts/telegram_polling.py` |
| Bildirim modülü | `src/company_master/utils/telegram_bot.py` |

---

## 2. Güvenlik

- **Token saklama:** `TELEGRAM_BOT_TOKEN` yalnızca `.env` dosyasında tutulur.
- **Git:** `.env` dosyası `.gitignore`'da listelenmiştir; asla commit yapılmaz.
- **Log:** Token'lar loglarda maskelenir (`8603398149:****c2M`).
- **Yetkili chat:** `TELEGRAM_CHAT_ID` birincil kimliktir; `TELEGRAM_ALLOWED_CHAT_IDS` ile virgülle ayrılmış ek yetkili chat'ler tanımlanabilir.
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

### 4.1 Başlangıç ve Yardım

| Komut | Açıklama | Örnek |
|---|---|---|
| `/start` | Bot başlangıç mesajı | Proje amacı ve kategoriler |
| `/help` | Kategorize komut listesi ve örnekler | Tüm komutlar |
| `/menu` | Etkileşimli ana menü | Numbered menü |

### 4.2 Görev Yönetimi

| Komut | Alias | Kullanım | Açıklama |
|---|---|---|---|
| `/gorev-ekle` | `/at` | `/gorev-ekle &lt;id&gt; &lt;ajan&gt; &lt;baslik&gt;` | Panoya görev ekle ve ajan postasına tetik at |
| `/gorev` | — | `/gorev` | Tüm görevleri duruma göre listele |
| `/gorev-durum` | `/set_task_status` | `/gorev-durum &lt;id&gt; &lt;durum&gt;` | Görev durumunu güncelle |

**Örnek:**
```
/gorev-ekle TASK-01 kilo "Firma scrape"
```

### 4.3 Onay ve İnceleme

| Komut | Alias | Kullanım | Açıklama |
|---|---|---|---|
| `/onaylar` | — | `/onaylar` | Onay bekleyen teslimleri listeler |
| `/onayla` | — | `/onayla &lt;id&gt;` | Görevi onayla (done) |
| `/reddet` | — | `/reddet &lt;id&gt; &lt;neden&gt;` | Görevi reddet (aktife geri dönder) |
| `/teslim` | — | `/teslim &lt;id&gt; &lt;ozet&gt;` | Görevi incelemeye gönder |

**Örnek:**
```
/teslim TASK-01 Parse tamamlandi
/reddet TASK-01 Gereksiz duzeltme
```

### 4.4 Durum ve Raporlama

| Komut | Alias | Açıklama |
|---|---|---|
| `/durum` | `/status` | Proje durumu + aktif görevler |
| `/pano` | — | Bekleyen tetik ve onay özeti |
| `/rapor` | — | KPI raporu |
| `/wiki` | — | V10 wiki sayfalarını listele |
| `/gunluk` | — | Günlük özet |
| `/izleme` | — | Kalite + proje izleme |
| `/degisiklik` | — | CHANGELOG.md |

### 4.5 Nöbetçi

| Komut | Alias | Kullanım | Açıklama |
|---|---|---|---|
| `/nobet` | — | `/nobet` | Nöbetçi turu attırır (geciken tetikler) |
| `/nobet-ayar` | `/nobet_ayar` | `/nobet-ayar &lt;kademe_sn&gt;` | Alarm süresini saniye olarak güncelle |

---

## 5. Komut Akışı (ORCH-08)

```
/gorev-ekle (veya /at)
   ↓ Görev panoya eklendi (plan)
Agent çalışır ve görevi teslim eder
   ↓ /teslim
   ↓ Onay kuyruğuna eklendi (review)
/onaylar  →  İnceleme bekleyenleri görüntüle
   ↓
/onayla   →  Onay → done (kilitler bırakılır)
/reddet   →  Reddet → aktif (agent düzeltir)
```

---

## 6. Otomatik Bildirimler

Aşağıdaki olaylar otomatik Telegram mesajı gönderir:

| Olay | Fonksiyon | Örnek |
|---|---|---|
| Yeni görev başladı | `send_task_started(task, agent)` | "🚀 Yeni Görev Başladı — Geliştirici" |
| Görev tamamlandı | `send_task_completed(task, agent, summary)` | "✅ Görev Tamamlandı — 300 firma" |
| Kritik hata | `send_alert(title, message)` | "⚠️ Scraper Hatası" |
| Günlük özet | `send_daily_summary(stats)` | "📊 Günlük Özet" |

---

## 7. Geliştirici Kullanımı

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
send_alert("Scraper Hatası", "Selector bulunamadi: div.col-lg-4.mb_3")
```

---

## 8. Sorun Giderme

| Sorun | Çözüm |
|---|---|
| Komut cevap vermiyor | Bot polling çalışıyor mu? `Get-Process python` kontrol et |
| "Yetkisiz" mesajı | Komut yetkili chat ID'den gönderilmeli. `.env` `TELEGRAM_CHAT_ID` kontrol edilebilir |
| "Bilinmeyen komut" | Bot yeniden başlatılmalı (eskiden kod güncellendi) |
| "TOKEN not set" hatası | `.env` yüklenmemiş; ortam değişkenlerini ayarla |
| Emoji bozuk | `PYTHONIOENCODING=utf-8` ayarla |
| Rate limit | Telegram limit: saniyede 30 mesaj; aşma durumunda bekle |

---

## 9. İlgili Wiki

- [[10_ankara_osb_sentez]] Karar 13 — Telegram bot entegrasyon kararı
- [[project_state]] — Proje durumu
- [[00-Home]] — Ana sayfa
