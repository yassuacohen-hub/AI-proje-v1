@echo off
REM KILO Yedek Rotasyon - Windows Task Scheduler Kurulumu
REM Pazartesi 03:00'de haftada bir çalışacak
REM Yönetici olarak çalıştırılmalı

setlocal enabledelayedexpansion
cd /d "%~dp0.."

REM Mutlak yol: bu batch scripts/ dizininde, proje kökü parent directory
set PROJECT_ROOT=%~dp0..
set SCRIPT_PATH=%PROJECT_ROOT%\scripts\kilo_backup_rotate.py

echo.
echo ====================================================================
echo KILO Yedek Rotasyon Task Scheduler Kurulumu (D-176)
echo ====================================================================
echo.

REM Mevcut Python yolu bul
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_PATH=%%i

if "%PYTHON_PATH%"=="" (
    echo HATA: Python bulunamadı. Python kurulumu kontrol edin.
    exit /b 1
)

echo Kullanılan Python: %PYTHON_PATH%
echo Script yolu: %SCRIPT_PATH%
echo.

REM Task oluştur
echo [1/3] Task Scheduler kaydı oluşturuluyor...
schtasks /create /tn "Huginn-KILO-BackupRotate" ^
    /tr "%PYTHON_PATH% \"%SCRIPT_PATH%\"" ^
    /sc WEEKLY /d MON /st 03:00 /f

if %ERRORLEVEL% equ 0 (
    echo [OK] Task başarıyla oluşturuldu
) else (
    if %ERRORLEVEL% equ 1 (
        echo [!] Uyarı: Task zaten mevcut veya yönetici izni gerekli
    ) else (
        echo [HATA] Task oluşturulamadı (Hata: %ERRORLEVEL%)
        exit /b %ERRORLEVEL%
    )
)

echo.
echo [2/3] Task bilgileri gösteriliyor...
schtasks /query /tn "Huginn-KILO-BackupRotate" /v 2>nul | findstr /i "durum|schedule|next"

echo.
echo [3/3] Test çalıştırması yapılıyor...
python "%SCRIPT_PATH%"

echo.
echo ====================================================================
echo Kurulum tamamlandı!
echo ====================================================================
echo.
echo Bilgi:
echo - Task adı: Huginn-KILO-BackupRotate
echo - Zamanlama: Pazartesi 03:00 (haftada bir)
echo - Script: scripts\kilo_backup_rotate.py
echo - Log: data\orchestrator\.kilo_rotate_log.txt
echo.
echo Komut Satırında Manuel Test:
echo   python scripts\kilo_backup_rotate.py
echo.
echo Task Scheduler'da Manuel Test:
echo   schtasks /run /tn "Huginn-KILO-BackupRotate"
echo.
echo Task Silme (gerekirse):
echo   schtasks /delete /tn "Huginn-KILO-BackupRotate" /f
echo.
pause
