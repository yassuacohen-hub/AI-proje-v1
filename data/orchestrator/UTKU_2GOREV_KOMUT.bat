@echo off
REM UTKU_2GOREV_KOMUT.bat — Utku'nun 2 görevinin brieflerini sırayla göster
REM Windows cmd.exe uyumlu version
REM Kullanım: UTKU_2GOREV_KOMUT.bat

echo.
echo ========================================
echo UTKU — 2 GOREV BRIEFLERI
echo ========================================
echo.

REM Görev 1: UI-ADMIN-KVKK-MODU-26
echo [1/2] UI-ADMIN-KVKK-MODU-26 — Admin KVKK Mode Toggle (P1)
echo ----------------------------------------
type "plans\brief_utku_UI-ADMIN-KVKK-MODU-26.md"
echo.
echo.

REM Görev 2: UI-ADMIN-KVKK-RAPOR-28
echo [2/2] UI-ADMIN-KVKK-RAPOR-28 — KVKK Maskeleme Raporu (P2)
echo ----------------------------------------
type "plans\brief_utku_UI-ADMIN-KVKK-RAPOR-28.md"
echo.

echo.
echo ========================================
echo TAMAMLANDI — Task board'dan durum oku
echo ========================================
echo.
pause
