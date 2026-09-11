@echo off
chcp 65001 >nul
setlocal

set "ROOT=%~dp0.."
cd /d "%ROOT%"

set "PYTHON=.venv\Scripts\pythonw.exe"
set "SCRIPT=scripts\server_watchdog.py"
set "LOG_DIR=logs"

if not exist "%PYTHON%" (
    echo HATA: %PYTHON% bulunamadi. 1>&2
    exit /b 1
)

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

:: Onceki kopyalari temizle (ayni port catsmasini onlemek icin)
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq Huginn Server Watchdog" >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Huginn Server Watchdog" >nul 2>&1

start "Huginn Server Watchdog" /MIN "%PYTHON%" "%SCRIPT%"
echo Watchdog baslatildi. Durum icin: scripts\watchdog_status.bat
