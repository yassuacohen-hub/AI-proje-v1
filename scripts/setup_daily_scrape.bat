@echo off
REM Company Master - Daily Scrape Scheduler
REM Windows Task Scheduler ile calistirin

echo ========================================
echo Company Master Daily Scrape Scheduler
echo ========================================
echo.
echo Bu script, Windows Task Scheduler'da gunluk scrape gorevi olusturacak.
echo.
echo Gorev detaylari:
echo   - Ad: CompanyMaster_DailyScrape
echo   - Zaman: Her gun 02:00
echo   - Komut: python scripts/scheduled_scrape.py --once
echo   - Working Directory: C:\Projeler\Huginn Data Insights
echo.

set TASK_NAME=CompanyMaster_DailyScrape
set PYTHON_PATH=python
set SCRIPT_PATH=scripts\scheduled_scrape.py
set WORKING_DIR=C:\Projeler\Huginn Data Insights

echo.
echo Yeni gorev olusturuluyor...

schtasks /create /tn "%TASK_NAME%" /tr "%PYTHON_PATH% %SCRIPT_PATH% --once" /sc daily /st 02:00 /f /ru "%USERNAME%" /rp *

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Gorev basariyla olusturuldu!
    echo.
    echo Gorev durumu:
    schtasks /query /tn "%TASK_NAME%" /fo list
    echo.
    echo Manuel calistirmak icin:
    echo   schtasks /run /tn "%TASK_NAME%"
    echo.
    echo Gorev silmek icin:
    echo   schtasks /delete /tn "%TASK_NAME%" /f
) else (
    echo.
    echo [HATA] Gorev olusturulamadi. Yonetici yetkisi ile calistirdiginizdan emin olun.
)

pause
