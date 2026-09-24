@echo off
REM YASU_4GOREV_KOMUT.bat — Yasu'nun 4 görevinin brieflerini sırayla göster
REM Windows cmd.exe uyumlu version
REM Kullanım: YASU_4GOREV_KOMUT.bat

echo.
echo ========================================
echo YASU — 4 GOREV BRIEFLERI
echo ========================================
echo.

REM Görev 1: API-KVKK-KONTROL-25
echo [1/4] API-KVKK-KONTROL-25 — Kontör Entegrasyonu
echo ----------------------------------------
type "plans\brief_yasu_API-KVKK-KONTROL-25.md"
echo.
echo.

REM Görev 2: TEST-VISIBILITY-ENTEGRASYON-27
echo [2/4] TEST-VISIBILITY-ENTEGRASYON-27 — E2E Test Suite
echo ----------------------------------------
type "plans\brief_yasu_TEST-VISIBILITY-ENTEGRASYON-27.md"
echo.
echo.

REM Görev 3: API-LAYER2-DINAMIK-YÜKLEME-30
echo [3/4] API-LAYER2-DINAMIK-YÜKLEME-30 — Layer 2 Dinamik Yükleme
echo ----------------------------------------
type "plans\brief_yasu_API-LAYER2-DINAMIK-YÜKLEME-30.md"
echo.
echo.

REM Görev 4: KONTROL-KVKK-MASKELEME-31
echo [4/4] KONTROL-KVKK-MASKELEME-31 — Admin Mode E2E Test
echo ----------------------------------------
type "plans\brief_yasu_KONTROL-KVKK-MASKELEME-31.md"
echo.

echo.
echo ========================================
echo TAMAMLANDI — Task board'dan durum oku
echo ========================================
echo.
pause
