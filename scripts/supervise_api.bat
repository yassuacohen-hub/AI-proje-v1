@echo off
REM Huginn API Supervisor - uvicorn web_app:app (port 8000)
REM Cokerse 10 sn icinde otomatik yeniden baslatir.
REM 2026-10-02: Kalici cozum (Task Scheduler "HuginnWebServices" ile baslatilir).
cd /d "%~dp0.."
set PYTHONPATH=src
if not exist logs mkdir logs
:loop
REM Port 8000 zaten dinleniyorsa (mesela el ile baslatilmis) bekleyip kontrol et
netstat -ano | findstr "LISTENING" | findstr ":8000 " >nul 2>&1
if %errorlevel%==0 (
    echo [%date% %time%] Port 8000 kullaniliyor, 30 sn bekleniyor >> logs\supervisor.log
    timeout /t 30 /nobreak >nul
    goto loop
)
echo [%date% %time%] uvicorn baslatiliyor >> logs\supervisor.log
python -m uvicorn web_app:app --host 0.0.0.0 --port 8000 >> logs\web_server.log 2>&1
echo [%date% %time%] uvicorn dustu, 10 sn icinde yeniden baslatiliyor >> logs\supervisor.log
timeout /t 10 /nobreak >nul
goto loop
