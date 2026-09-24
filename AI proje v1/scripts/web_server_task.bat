@echo off
REM Huginn Web Server - otomatik yeniden baslatma dongusu
REM Sunucu herhangi bir sebeple cokerse 10 saniye icinde yeniden baslar
cd /d "C:\Projeler\Huginn Data Insights"
set PYTHONPATH=src
if not exist logs mkdir logs
echo [%date% %time%] Web Server supervisor basladi >> logs\web_server.log
:loop
echo [%date% %time%] uvicorn baslatiliyor >> logs\web_server.log
python -m uvicorn web_app:app --host 0.0.0.0 --port 8000 >> logs\web_server.log 2>&1
echo [%date% %time%] uvicorn dusti, 10 sn icinde yeniden baslatiliyor >> logs\web_server.log
timeout /t 10 /nobreak >nul
goto loop