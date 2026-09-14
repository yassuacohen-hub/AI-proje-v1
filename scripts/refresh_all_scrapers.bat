@echo off
chcp 65001 >nul
setlocal

REM 2026-09-14: Sabit yol yerine script konumuna gore kok (tasinabilir).
cd /d "%~dp0.."

echo [%date% %time%] Scrape refresh basliyor... >> logs\refresh_all_scrapers.log

"C:\Users\yasin\AppData\Local\Programs\Python\Python312\python.exe" scripts\refresh_all_scrapers.py >> logs\refresh_all_scrapers.log 2>&1

echo [%date% %time%] Scrape refresh bitti. >> logs\refresh_all_scrapers.log

endlocal
