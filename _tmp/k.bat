@echo off
set SYSPY=C:\Users\yasin\AppData\Local\Programs\Python\Python312\python.exe
set TARGET=C:\Projeler\Huginn Data Insights\.venv\Lib\site-packages
@echo off
set SYSPY=C:\Users\yasin\AppData\Local\Programs\Python\Python312\python.exe
set TARGET=C:\Projeler\Huginn Data Insights\.venv\Lib\site-packages
rmdir /s /q "%TARGET%\numpy"
rmdir /s /q "%TARGET%\pandas"
"%SYSPY%" -m pip install --target "%TARGET%" --quiet numpy pandas
echo PIP=%ERRORLEVEL% > c:\Users\yasin\k.log
cd /d "c:\Huginn Data Projesi\Huginn Data Insights"
python -c "import numpy,pandas;print('NP_PD_OK',numpy.__version__,pandas.__version__)" >> c:\Users\yasin\k.log 2>&1
echo IMP=%ERRORLEVEL% >> c:\Users\yasin\k.log
exit
if exist "%TARGET%\pygments" (echo PYGMENTS_VAR) else (echo PYGMENTS_YOK)