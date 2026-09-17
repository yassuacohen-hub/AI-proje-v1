@echo off
REM Haftalik ucretsiz model taramasi (Windows Zamanlanmis Gorev icin).
REM Kurulum (yonetici gerekmez):
REM   schtasks /Create /TN "Huginn-Continue-Tarama" /TR "\"%~f0\"" /SC WEEKLY /D MON /ST 09:00 /F
REM Rapor: docs\raporlar\continue\tarama_<tarih>.md
cd /d "%~dp0.."
python scripts\continue_config_kur.py --tara >> "data\_tmp\continue_tarama.log" 2>&1
exit /b %ERRORLEVEL%
