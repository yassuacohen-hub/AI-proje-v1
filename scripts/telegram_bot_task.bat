@echo off
REM Telegram Bot — canonical long-polling (Windows Gorev Planlayicisi)
REM
REM Kullanim:
REM   1. .env dosyasini proje koklinde olusturun (token + chat_id)
REM   2. python.exe ve proje yolunu asagida duzeltin
REM   3. Bu .bat dosyasini Windows Gorev Planlayicisi'na ekleyin
REM      - Program: C:\Python312\python.exe
REM      - Arguman: "C:\Huginn Data Projesi\Huginn Data Insights\scripts\telegram_polling.py"
REM      - Baslangic klasoru: C:\Huginn Data Projesi\Huginn Data Insights

setlocal

REM --- Ayarlar (gerekirse duzeltin) ---
set PYTHON_EXE=C:\Python312\python.exe
set PROJECT_ROOT=C:\Huginn Data Projesi\Huginn Data Insights
set SCRIPT=%PROJECT_ROOT%\scripts\telegram_polling.py

REM --- .env yukle (varsa) ---
if exist "%PROJECT_ROOT%\.env" (
    for /f "usebackq tokens=*" %%a in ("%PROJECT_ROOT%\.env") do (
        echo %%a | findstr /r "^[A-Za-z]" >nul
        if not errorlevel 1 (
            for /f "tokens=1,* delims==" %%v in ("%%a") do (
                set "%%v=%%w"
            )
        )
    )
)

REM --- Token/chat_id kontrolu ---
if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo HATA: TELEGRAM_BOT_TOKEN .env veya ortam degiskeninde ayarlanmamissiniz.
    echo Lutfen .env dosyasini kontrol edin veya ortam degiskeni olarak set edin.
    exit /b 1
)
if "%TELEGRAM_CHAT_ID%"=="" (
    echo HATA: TELEGRAM_CHAT_ID .env veya ortam degiskeninde ayarlanmamissiniz.
    exit /b 1
)

echo Telegram bot polling baslatiliyor...
echo   Proje: %PROJECT_ROOT%
echo   Script: %SCRIPT%
echo   Bot token: **** (gizli)
echo   Chat ID: %TELEGRAM_CHAT_ID%
echo.

"%PYTHON_EXE%" "%SCRIPT%"
if errorlevel 1 (
    echo.
    echo HATA: Telegram bot calismasi sirinda hata olustu.
    echo Loglari kontrol edin.
    exit /b %errorlevel%
)

endlocal
