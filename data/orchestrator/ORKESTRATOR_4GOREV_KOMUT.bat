@echo off
REM ORKESTRATOR_4GOREV_KOMUT.bat — Orkestrator'un 4 görevinin brieflerini sırayla göster
REM Windows cmd.exe uyumlu version
REM Kullanım: ORKESTRATOR_4GOREV_KOMUT.bat

echo.
echo ========================================
echo ORKESTRATOR — 4 GOREV BRIEFLERI
echo ========================================
echo.

REM Görev 1: UI-ADMIN-FEATURE-FLAG-25
echo [1/4] UI-ADMIN-FEATURE-FLAG-25 — Feature Flag Yönetim Paneli
echo ----------------------------------------
type "plans\brief_orkestrator_UI-ADMIN-FEATURE-FLAG-25.md"
echo.
echo.

REM Görev 2: API-ADMIN-MFA-26
echo [2/4] API-ADMIN-MFA-26 — Multi-Factor Authentication (TOTP)
echo ----------------------------------------
type "plans\brief_orkestrator_API-ADMIN-MFA-26.md"
echo.
echo.

REM Görev 3: UI-ADMIN-LTV-CAC-27
echo [3/4] UI-ADMIN-LTV-CAC-27 — LTV/CAC Analiz Panosu
echo ----------------------------------------
type "plans\brief_orkestrator_UI-ADMIN-LTV-CAC-27.md"
echo.
echo.

REM Görev 4: DOC-ADMIN-MULTITENANT-KARAR-28
echo [4/4] DOC-ADMIN-MULTITENANT-KARAR-28 — Multi-Tenant Mimarı Karar Belgesi
echo ----------------------------------------
type "plans\brief_orkestrator_DOC-ADMIN-MULTITENANT-KARAR-28.md"
echo.

echo.
echo ========================================
echo TAMAMLANDI — Task board'dan durum oku
echo ========================================
echo.
pause
