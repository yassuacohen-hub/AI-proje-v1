@echo off
chcp 65001 >nul
echo Huginn watchdog ve web sunucusu durduruluyor...
taskkill /F /FI "WINDOWTITLE eq Huginn Server Watchdog" /IM pythonw.exe >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Huginn Server Watchdog" /IM python.exe >nul 2>&1
:: Ayrica 8000 portundaki tum python sureclerini kapat
taskkill /F /IM python.exe /FI "COMMANDLINE eq *web_app.py*" >nul 2>&1
echo Tamamlandi.
