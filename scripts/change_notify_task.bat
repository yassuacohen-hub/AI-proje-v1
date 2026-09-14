@echo off
rem Y14 degisiklik bildirimi (gunluk, backup sonrasi). Task Scheduler bu dosyayi cagirir.
rem 2026-09-14: Sabit yol yerine script konumuna gore kok (tasinabilir).
cd /d "%~dp0.."
if not exist logs mkdir logs
python scripts\change_notify.py --check >> logs\change_notify.log 2>&1
