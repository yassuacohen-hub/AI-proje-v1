# H004 — Telegram Bot systemd Servisi: Test Raporu ve Kurulum Dokümantasyonu

**Tarih:** 2026-09-06
**Görev:** `scripts/telegram_bot_systemd.service` dosyasını test et, düzelt ve
dokümantasyon yaz.
**Orkestratör notu:** Dosya ilk üretimde mevcut değildi; bu teslimatla birlikte
oluşturuldu (`scripts/telegram_bot_systemd.service` + bu doküman).

---

## 1. Tespit Edilen Durum (Başlangıç)

| Kontrol | Sonuç |
|---|---|
| `scripts/telegram_bot_systemd.service` var mı? | **YOK** (görev boş başladı) |
| `scripts/telegram_polling.py` derleniyor mu? | Aşağıda test edildi |
| `.env` gerekli anahtarlar | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `DATABASE_URL` |

## 2. Yapılan Testler (Windows geliştirme makinesi)

systemd yalnızca Linux'ta çalıştığı için Windows üzerinde unit dosyası
çalıştırılamaz; bunun yerine aşağıdaki doğrulamalar yapılmıştır:

1. **Python script derleme testi:** `python -m py_compile scripts/telegram_polling.py`
   → Başarılı (sözdizimi hatası yok).
2. **Unit dosyası yapı testi:** INI bölümleri (`[Unit]`, `[Service]`, `[Install]`)
   ve zorunlu anahtarlar (`ExecStart`, `WorkingDirectory`, `Restart`,
   `WantedBy`) programatik olarak doğrulandı → Başarılı.
3. **Ortam değişkeni testi:** `.env` içinde `TELEGRAM_BOT_TOKEN` ve
   `TELEGRAM_CHAT_ID` anahtarlarının varlığı doğrulandı (değerler okunmadı —
   secret kuralı). → Başarılı.
4. **Canlı servis testi:** Linux sunucu gerektirir; aşağıdaki kurulum adımları
   ile hedef ortamda yapılmalıdır.

## 3. Düzeltmeler (Üretim sırasında uygulanan)

- `Restart=always` + `RestartSec=15`: long-polling sessiz kalan bot için güvenli
  varsayılan.
- `WorkingDirectory` proje köküne ayarlandı: `telegram_polling.py` başındaki
  `load_dotenv()` proje kökündeki `.env` dosyasını bulur.
- `EnvironmentFile=/opt/huginn/.env`: token'lar unit dosyasına gömülmez
  (secret kuralı: gizli bilgi koda yazılmaz).
- `After=network-online.target`: açılışta ağ hazır olmadan başlamayı önler.
- Kullanıcı/grup `huginn` olarak ayrıldı (root koşturma yok).

## 4. Kurulum (Linux)

```bash
# 0) Proje yolu /opt/huginn değilse unit dosyasındaki 3 yolu güncelleyin:
#    WorkingDirectory, EnvironmentFile, ExecStart

# 1) Unit dosyasını kur
sudo cp scripts/telegram_bot_systemd.service /etc/systemd/system/

# 2) Servis kullanıcısını hazırla (ilk kurulumda)
sudo useradd -r -s /usr/sbin/nologin huginn || true
sudo chown -R huginn:huginn /opt/huginn

# 3) Yeniden yükle ve başlat
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-bot

# 4) Doğrula
systemctl status telegram-bot --no-pager
journalctl -u telegram-bot -f          # canlı log
```

## 5. Bakım Komutları

| İşlem | Komut |
|---|---|
| Yeniden başlat | `sudo systemctl restart telegram-bot` |
| Durdur | `sudo systemctl stop telegram-bot` |
| Otomatik başlatmayı kapat | `sudo systemctl disable telegram-bot` |
| Son hatalar | `journalctl -u telegram-bot -n 100 --no-pager` |

## 6. Bilinen Sınırlar / Sonraki Adımlar

- Windows geliştirme makinesinde systemd olmadığından canlı test Linux ortamına
  kaldı (P1-6 kapsamındaki pm2 alternatifi de mevcut).
- Telegram API erişimi VPN'e bağlı olabilir; bağlantı hatalarında önce VPN
  durumunu kontrol edin (VPN kuralı: `10_vpn_kurali.md`).
- Timer/cron tabanlı günlük scrape ile entegrasyon P2-3 kapsamındadır.
