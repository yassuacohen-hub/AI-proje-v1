@echo off
rem Huginn gunluk DB yedegi (P4-6) - Task Scheduler bu dosyayi cagirir
cd /d "C:\Projeler\Huginn Data Insights"
if not exist logs mkdir logs
python scripts\backup_db.py --keep 7 >> logs\backup.log 2>&1
