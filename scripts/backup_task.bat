@echo off
rem Huginn gunluk DB yedegi (P4-6) - Task Scheduler bu dosyayi cagirir
rem 2026-09-14: Sabit yol yerine script konumuna gore kok (tasinabilir).
cd /d "%~dp0.."
if not exist logs mkdir logs
python scripts\backup_db.py --keep 7 >> logs\backup.log 2>&1
