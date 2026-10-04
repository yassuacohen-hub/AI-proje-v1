@echo off
REM Huginn Streamlit Supervisor - streamlit app.py (port 8501)
REM Cokerse 10 sn icinde otomatik yeniden baslatir.
REM 2026-10-02: Kalici cozum (Task Scheduler "HuginnWebServices" ile baslatilir).
cd /d "%~dp0.."
set PYTHONPATH=src
if not exist logs mkdir logs
:loop
REM Port 8501 zaten dinleniyorsa (mesela el ile baslatilmis) bekleyip kontrol et
netstat -ano | findstr "LISTENING" | findstr ":8501 " >nul 2>&1
if %errorlevel%==0 (
    echo [%date% %time%] Port 8501 kullaniliyor, 30 sn bekleniyor >> logs\supervisor.log
    timeout /t 30 /nobreak >nul
    goto loop
)
echo [%date% %time%] streamlit baslatiliyor >> logs\supervisor.log
python -m streamlit run app.py --server.port 8501 --server.headless true >> logs\streamlit.log 2>&1
echo [%date% %time%] streamlit dustu, 10 sn icinde yeniden baslatiliyor >> logs\supervisor.log
timeout /t 10 /nobreak >nul
goto loop
