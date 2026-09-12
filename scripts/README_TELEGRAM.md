# Telegram Bot — Kurulum ve Kullanim Kilavuzu

## Genel Bakisim

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
TELEGRAM_CHAT_ID=801855376            # Yetkili chat ID
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
| `/status` | Proje durumu + aktif goresv | Herkese acik |
| `/gorev` | Task board'daki tum goresv | Herkese acik |
| `/rapor` | KPI raporu (`data/kpi_raporu.md`) | Herkese acik |
| `/wiki` | OSTIM kalite raporu | Herkese acik |
| `/restart_etl` | ETL pipeline yeniden baslat | Yetkili |
| `/degisiklik` | CHANGELOG.md | Herkese acik |
| `/gunluk` | Gunluk ozet | Herkese acik |
| `/izleme` | Kalite + proje izleme | Herkese acik |
| `/set_status <id> <durum>` | Gorev durumunu guncelle | Yetkili |

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

- Token ve chat_id **asla kodda saklanmaz**; `.env` dosyasindan okunur.
- Tum dinamik metin `html_escape()` ile sanitize edilir (Telegram HTML parse_mode).
- `requests.post/get` timeout ve `RequestException` ile guvenle güvenli.
- `/set_status` ve `/restart_etl` sadece yetkili chat_id'den gelen kullanicilara izin verir.
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
