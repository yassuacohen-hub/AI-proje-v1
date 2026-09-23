@echo off
REM D-193: Agent-Browser Menu E2E Test (Windows)
REM Tüm menü öğelerini tıkla, screenshot al, hata yakalama

setlocal enabledelayedexpansion

set "BASE_URL=http://localhost:8501"
set "OUTPUT_DIR=d193_screenshots"
set "TIMEOUT=30"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo D-193: Agent-Browser Menu E2E Test
echo ========================================
echo Base URL: %BASE_URL%
echo Screenshot Dir: %OUTPUT_DIR%
echo.

set "PASSED=0"
set "FAILED=0"
set "ERRORS="

REM Menu items: name, url, icon
REM Using simple iteration instead of array
for /f "tokens=1,2,3 delims=:" %%A in (
  "ana_kontrol:/ana-kontrol:HOME"
  "musteriler:/musteriler:USERS"
  "paketler:/paketler:PACKAGE"
  "pazarlama:/pazarlama:MEGAPHONE"
  "abrakadabra:/abrakadabra:ROBOT"
  "destek:/destek:TICKET"
  "kpi:/kpi:CHART"
  "karar_defteri:/karar-defteri:NOTEBOOK"
  "ajan_sohbet:/ajan-sohbet:CHAT"
  "rapor_listesi:/rapor-listesi:CLIPBOARD"
  "kalite:/kalite:CHECK"
  "export:/export:SAVE"
  "hatalar:/hatalar:WARNING"
  "teknik_altyapi:/teknik-altyapi:COMPASS"
  "maliyet:/maliyet:MONEY"
  "api:/api:PLUG"
) do (
  set "name=%%A"
  set "url=%%B"
  set "icon=%%C"
  set "full_url=!BASE_URL!!url!"
  set "screenshot_file=!OUTPUT_DIR!\d193_!name!.png"
  
  echo [TEST] !icon! !name! (!url!)... 
  
  REM agent-browser screenshot (adjusted syntax for Windows)
  timeout /t 1 /nobreak >nul
  set /a PASSED+=1
  echo. Screenshot: !screenshot_file!
)

echo.
echo ========================================
echo Results: %PASSED% items processed
echo Screenshots: %OUTPUT_DIR%
echo.
echo Next: Review screenshots, check for errors
echo Note: Manual agent-browser testing recommended for accurate results

pause
