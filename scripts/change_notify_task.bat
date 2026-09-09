@echo off
rem Y14 degisiklik bildirimi (gunluk, backup sonrasi). Task Scheduler bu dosyayi cagirir.
cd /d "C:\Projeler\Huginn Data Insights"
if not exist logs mkdir logs
python scripts\change_notify.py --check >> logs\change_notify.log 2>&1
