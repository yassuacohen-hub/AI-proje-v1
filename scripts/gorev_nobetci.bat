@echo off
cd /d "C:\Huginn Data Projesi\Huginn Data Insights"
python scripts\gorev_nobetci.py nobet >> data\orchestrator\nobetci.log 2>&1
