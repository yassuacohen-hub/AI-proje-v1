@echo off
cd /d "C:\Huginn Data Projesi\Huginn Data Insights"
python scripts\ajan_nobet_kosucusu.py --ajan yasu >> data\orchestrator\ajan_nobet_yasu.log 2>&1
