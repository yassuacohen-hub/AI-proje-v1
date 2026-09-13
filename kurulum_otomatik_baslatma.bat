@echo off
REM -*- coding: utf-8 -*-
REM Huginn Data Insights — Otomatik başlatma (Görev Zamanlayıcı kaydı)
REM 
REM Kullanım: Windows Görev Zamanlayıcı'da yeni görev oluştur:
REM   Tetikleyici: Sistem başlatılırken
REM   İşlem: "C:\Windows\System32\cmd.exe" /c "%~dp0kurulum_otomatik_baslatma.bat"
REM   Çalış dizini: "%~dp0"
REM

setlocal enabledelayedexpansion

REM Proje kökü
set ROOTDIR=%~dp0
cd /d %ROOTDIR%

REM .venv kontrolü
if not exist .venv (
    echo [%DATE% %TIME%] HATA: .venv bulunamadi
    exit /b 1
)

REM Loglar klasörü oluştur
if not exist logs mkdir logs

REM 1. PostgreSQL + Docker servisleri başlat (eğer gerekli)
echo [%DATE% %TIME%] Docker servisleri başlatılıyor...
docker compose up -d api db 2>>logs\startup.log
timeout /t 5 /nobreak

REM 2. Watchdog başlat (çift port izleme + Telegram)
REM    Watchdog, FastAPI (8000) ve Streamlit (8501) başlatacak ve izleyecek
echo [%DATE% %TIME%] Watchdog başlatılıyor (dual-port: 8000 + 8501)...
start "Huginn Watchdog" "%ROOTDIR%.venv\Scripts\python.exe" "%ROOTDIR%scripts\server_watchdog_v2.py" --interval 30

REM 3. Tarayıcı aç (opsiyonel)
timeout /t 10 /nobreak
echo [%DATE% %TIME%] Admin paneli açılıyor (Streamlit 8501)...
start "Huginn Admin Panel" "http://localhost:8501"

REM 4. Tamamlandı
echo [%DATE% %TIME%] Huginn başlatıldı (watchdog monitor edecek)
exit /b 0
