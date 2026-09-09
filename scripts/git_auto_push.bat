@echo off
REM Huginn gunluk otomatik git commit + push (Scheduler: Huginn Git Push, 04:00)
setlocal
cd /d "C:\Projeler\Huginn Data Insights"
set LOG=logs\git_push.log
set GIT=%ProgramFiles%\Git\cmd\git.exe
if not exist "%GIT%" set GIT=git

echo [%DATE% %TIME%] otomatik push basli >> %LOG%

REM Degisiklik var mi?
"%GIT%" status --porcelain > nul 2>&1
if errorlevel 1 goto :err
for /f %%i in ('"%GIT%" status --porcelain ^| find /c /v ""') do set N=%%i
if "%N%"=="0" (
    echo [%DATE% %TIME%] degisiklik yok >> %LOG%
    goto :push
)

"%GIT%" add -A >> %LOG% 2>&1
"%GIT%" -c user.name="Yasin" -c user.email="yasin@huginn.local" commit -m "Otomatik gunluk commit (%DATE% %TIME%)" >> %LOG% 2>&1

:push
"%GIT%" pull --rebase origin main >> %LOG% 2>&1
"%GIT%" push origin main >> %LOG% 2>&1
if errorlevel 1 (
    echo [%DATE% %TIME%] PUSH HATA >> %LOG%
    exit /b 1
)
echo [%DATE% %TIME%] push OK >> %LOG%
exit /b 0

:err
echo [%DATE% %TIME%] git status hatasi >> %LOG%
exit /b 1
