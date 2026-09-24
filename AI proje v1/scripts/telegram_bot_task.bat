@echo off
rem Huginn Telegram bot (long-polling, crash-restart dongusu).
rem Task Scheduler bu dosyayi cagirir: giris yapildiginda baslar, duserse yeniden baslatir.
chcp 65001 >nul
cd /d "C:\Projeler\Huginn Data Insights"
if not exist logs mkdir logs
:restart
echo [%date% %time%] Bot baslatiliyor... >> logs\telegram_bot.log 2>&1
python -u scripts\telegram_polling.py >> logs\telegram_bot.log 2>&1
echo [%date% %time%] Bot durdu (exit=%errorlevel%), 10 sn sonra yeniden... >> logs\telegram_bot.log 2>&1
timeout /t 10 /nobreak >nul
goto restart
