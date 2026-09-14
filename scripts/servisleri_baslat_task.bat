@echo off
REM Huginn servis nobetcilerini oturum acilisinda penceresiz baslatir.
REM Task Scheduler kaydi: "Huginn Servisler" (/SC ONLOGON)
REM 2026-09-14: A5 — sabit yol yok, script konumuna gore kok kullanilir.

setlocal
cd /d "%~dp0.."

set "PYW=%CD%\.venv\Scripts\pythonw.exe"
if not exist "%PYW%" set "PYW=pythonw.exe"

start "" /b "%PYW%" "%CD%\scripts\servisleri_baslat.py" baslat --servis hepsi

endlocal
exit /b 0
