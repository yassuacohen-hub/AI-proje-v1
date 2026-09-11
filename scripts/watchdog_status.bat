@echo off
chcp 65001 >nul
cd /d "%~dp0.."

set "LOG_FILE=logs\server_watchdog.jsonl"

echo Son izleme kayitlari (%LOG_FILE%):
echo ---------------------------------
if exist "%LOG_FILE%" (
    powershell -NoProfile -Command "Get-Content '%LOG_FILE%' -Tail 10 | ForEach-Object { Write-Host $_ }"
) else (
    echo Henuz log yok.
)

echo.
echo Mevcut saglik kontrolu:
curl -sS http://127.0.0.1:8000/api/health 2>&1
if errorlevel 1 (
    echo.
    echo Sunucu su an erisilemiyor.
)
echo.
