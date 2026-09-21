[[Huginn Data Insights/AI proje v1/scripts/README_TELEGRAM.md]]

# Telegram Bot — Kurulum ve Kullanim Kilavuzu

## Genel Bakış

Bu Telegram botu **canonical long-polling** motoru ile çalistirilir;
`python-telegram-bot` veya benzeri bir framework kullanmaz. Doğrudan
[Telegram Bot API](https://core.telegram.org/bots/api)'ye HTTP istekleri
gönderir (`getUpdates` long-polling).

## Dosyalar

| Dosya | Aciklama |
|-------|----------|
| `scripts/telegram_polling.py` | Ana bot motoru (getUpdates long-polling + komut parsing) |
| `scripts/telegram_periodic.py` | Periodik durum bildirimi (gunluk ozet gibi) |
| `src/company_master/utils/telegram_bot.py` | Ortak yardimci: send_message, html_escape, parse_command, get_updates |
| `src/company_master/telegram/bot_service.py` | Servis wrapper (subprocess polling baslatir) |
| `scripts/test_telegram.py` | Entegre test (mock + --live modu) |
| `scripts/test_telegram_simple.py` | Basit mock test |

## Ortam Degiskenleri (.env)

```
TELEGRAM_BOT_TOKEN=123456:ABC-...     # @BotFather'dan alinir (gizli!)
TELEGRAM_CHAT_ID=801855376            # Birincil yetkili chat ID
TELEGRAM_ALLOWED_CHAT_IDS=            # Opsiyonel; virgulle ek yetkili chat ID'ler
TELEGRAM_BOT_USERNAME=                # Opsiyonel; @BotName komut parsing icin
ETL_RESTART_CMD=python scripts/refresh_pipeline.py  # Opsiyonel
TELEGRAM_PERIODIC_INTERVAL_SECONDS=3600
TELEGRAM_PERIODIC_ENABLED=1
```

## Komutlar

| Komut | Aciklama | Yetki |
|-------|----------|-------|
| `/start` | Hos gelesme | Herkese acik |
| `/help` | Yardim metni | Herkese acik |
| `/status` | Proje durumu + aktif görevler | Herkese açık |
| `/durum` | Proje durumu + aktif görevler (`/status` alias'ı) | Herkese açık |
| `/gorev` | Task board'daki tüm görevler | Herkese açık |
| `/menu` | Etkileşimli ana menü | Herkese açık |
| `/rapor` | KPI raporu (`data/kpi_raporu.md`) | Herkese açık |
| `/wiki` | V10 wiki sayfaları | Herkese açık |
| `/restart_etl` | ETL pipeline yeniden başlat | Yetkili |
| `/degisiklik` | CHANGELOG.md | Herkese açık |
| `/gunluk` | Günlük özet | Herkese açık |
| `/izleme` | Kalite + proje izleme | Herkese açık |
| `/set_status <mesaj>` | `project_state.md` içine tarihli not ekle | Yetkili |
| `/set_task_status <id> <durum>` | Task board durumunu güncelle | Yetkili |
| `/gorev-durum <id> <durum>` | Task board durumunu güncelle (`/set_task_status` alias'ı) | Yetkili |
| `/gorev-ekle <id> <ajan> <baslik>` | Panoya görev ekle ve tetik at | Yetkili |
| `/at <id> <ajan> <baslik>` | Panoya görev ekle (`/gorev-ekle` alias'ı) | Yetkili |
| `/pano` | Bekleyen tetik ve onay özeti | Yetkili |
| `/onaylar` | Onay bekleyen teslimleri listele | Yetkili |
| `/onayla <id>` | Görevi onayla (`done`) | Yetkili |
| `/reddet <id> <neden>` | Görevi reddet (`aktif`) | Yetkili |
| `/teslim <id> <ozet>` | Görevi incelemeye gönder (`review`) | Yetkili |
| `/nobet` | Nöbetçi turunu çalıştır | Yetkili |
| `/nobet-ayar <sn>` | Nöbet alarm süresini güncelle | Yetkili |
| `/nobet_ayar <sn>` | Nöbet alarm süresini güncelle (`/nobet-ayar` alias'ı) | Yetkili |

## Calistirma

### Yerel (Windows)

```bat
set TELEGRAM_BOT_TOKEN=123456:ABC-...
set TELEGRAM_CHAT_ID=801855376
python scripts/telegram_polling.py
```

Otomatik baslatmak icin: `scripts\telegram_bot_task.bat` (gorev planlayici / cron karsiligi).

### Docker Compose

```bash
# profil: telegram servislerini baslatir (bot + periodik)
docker compose --profile telegram up -d --build telegram-bot telegram-periodic
```

### Windows Gorev Planlayicisi

`telegram_bot_task.bat` dosyasini Gorev Planlayicisi'na ekleyin:
- Program/Komut: `C:\Python312\python.exe`
- Arguman: `C:\path\to\scripts\telegram_polling.py`
- Baslangic klasoru: proje root

## Guvenlik

- `TELEGRAM_CHAT_ID` birincil yetkili chat'tir; `TELEGRAM_ALLOWED_CHAT_IDS` virgülle ayrılmış ek yetkili kimlikleri destekler.
- Token ve chat_id **asla kodda saklanmaz**; `.env` dosyasindan okunur.
- Tum dinamik metin `html_escape()` ile sanitize edilir (Telegram HTML parse_mode).
- `requests.post/get` timeout ve `RequestException` ile guvenle güvenli.
- `/restart_etl`, `/set_status`, `/set_task_status`, `/gorev-ekle`, `/onayla`, `/reddet`, `/teslim` ve `/nobet-ayar` yalnızca yetkili chat_id'den gelen kullanıcılara izin verir.
- `set_task_status` task_board.py'nin atomik `gorev_guncelle()` fonksiyonunu kullanir.

## Test

```bash
# Mock test (ag cagrisi yapmaz)
python scripts/test_telegram.py

# Canli test (gercek Telegram API; .env gerekir)
python scripts/test_telegram.py --live

# Basit test
python scripts/test_telegram_simple.py

# pytest
pytest tests/test_telegram_bot.py tests/test_telegram_polling.py -v
```

## restart_etl

`/restart_etl` komutu veya `telegram_periodic.py` icin:

```
ETL_RESTART_CMD=python scripts/refresh_pipeline.py
```

komutunu .env'e ekleyin. Bot bu komutu `subprocess.Popen` ile `cwd=ROOT`
(proje kokeli) olarak calistirir.
