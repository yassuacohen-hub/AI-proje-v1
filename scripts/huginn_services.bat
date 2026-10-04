@echo off
REM Huginn Hizmetleri Baslatici - API (8000) + Streamlit (8501)
REM Her supervisor kendi servisini cokme durumunda otomatik yeniden baslatir.
REM Task Scheduler gorevi "HuginnWebServices" bu betigi kullanir.
start "Huginn-API-Supervisor" /min cmd /c ""%~dp0supervise_api.bat""
start "Huginn-Streamlit-Supervisor" /min cmd /c ""%~dp0supervise_streamlit.bat""
exit
