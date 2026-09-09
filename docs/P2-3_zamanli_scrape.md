# P2-3: Zamanlanmış Scrape (Günlük Refresh)

> **Durum:** Plan → Aktif  
> **Sahip:** web_kazima  
> **Amaç:** OSB scraper'larını günlük otomatik çalıştırmak.

## 1. Linux (systemd timer — önerilen)

`scripts/refresh_all_scrapers.service` ve `scripts/refresh_all_scrapers.timer` dosyalarını
kullanarak her gün 03:00'te tüm scraper'ları çalıştırır.

### Kurulum
```bash
sudo cp scripts/refresh_all_scrapers.service /etc/systemd/system/
sudo cp scripts/refresh_all_scrapers.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now refresh_all_scrapers.timer
```

### Doğrula
```bash
systemctl list-timers refresh_all_scrapers.timer
journalctl -u refresh_all_scrapers.service -f
```

## 2. Windows (Görev Zamanlayıcı)

`scripts/refresh_all_scrapers.bat` dosyasını Windows Görev Zamanlayıcı ile günlük çalıştırın.

### Kurulum (PowerShell — yönetici)
```powershell
$action = New-ScheduledTaskAction -Execute "C:\Projeler\Huginn Data Insights\scripts\refresh_all_scrapers.bat"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
Register-ScheduledTask -TaskName "Huginn_ScrapeRefresh" -Action $action -Trigger $trigger -Description "Huginn Data Insights - Gunluk OSB scraper refresh"
```

### Doğrula
```powershell
Get-ScheduledTask -TaskName "Huginn_ScrapeRefresh" | Get-ScheduledTaskInfo
```

## 3. İçerik: `refresh_all_scrapers.py`

Tüm scraper'ları sırayla çalıştırır, loglar, hata durumunda bildirir.
- `ostim_scraper.py` (OSTİM detay)
- `ivedik_scraper.py` (İvedik OSB)
- `baskent_scraper.py` (Başkent OSB)
- `aso_scraper.py` (ASO)

Not: Scraper'lar VPN gerektirebilir; VPN kuralı `10_vpn_kurali.md` geçerlidir.
