@echo off
cd /d "C:\Huginn Data Projesi\Huginn Data Insights"
python scripts\tetik_senk.py --gunluk >> data\orchestrator\tetik_senk_cikti.log 2>&1
