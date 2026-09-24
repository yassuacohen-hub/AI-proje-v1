@echo off
REM Huginn otomatik git commit + push (Scheduler: Huginn Git Push, GUNDE 2x: 12:01 ve 00:01)
REM 2026-09-11: Yol duzeltildi (eski "C:\Projeler" yolu 0x80070002 hatasi veriyordu);
REM             push AKTIF dala yapiliyor; push 2 deneme + autostash eklendi (GIT-01).
setlocal
set LOG=logs\git_push.log
set GIT=%ProgramFiles%\Git\cmd\git.exe
if not exist "%GIT%" set GIT=git

cd /d "C:\Huginn Data Projesi\Huginn Data Insights"
if errorlevel 1 (
    echo [%DATE% %TIME%] cd HATA: proje klasoru bulunamadi >> %LOG%
    exit /b 1
)

echo [%DATE% %TIME%] otomatik push basli >> %LOG%

REM Aktif dali belirle
set BR=
for /f "usebackq delims=" %%b in (`"%GIT%" rev-parse --abbrev-ref HEAD`) do set BR=%%b
if "%BR%"=="" (
    echo [%DATE% %TIME%] dal belirlenemedi, main varsayildi >> %LOG%
    set BR=main
)

REM Degisiklik var mi?
"%GIT%" status --porcelain 2>&1 | findstr /r "." >nul
if errorlevel 1 (
    echo [%DATE% %TIME%] degisiklik yok >> %LOG%
    goto :push
)

"%GIT%" add -A >> %LOG% 2>&1

REM YA-01 (2026-09-24): ic ice depo korumasi. Calisma agacinda .gitmodules
REM eslemesi olmayan bir .git klasoru varsa "add -A" onu gitlink (160000) olarak
REM kaydeder ve taze klon o agaci BOS getirir. Belirti: submodule status "fatal:
REM no submodule mapping found" verir. Boyle bir durumda commit YAPILMAZ.
"%GIT%" submodule status >nul 2>>%LOG%
if errorlevel 1 (
    echo [%DATE% %TIME%] ESLEMESIZ GITLINK: commit iptal, elle temizle ^(YA-01^) >> %LOG%
    "%GIT%" reset >> %LOG% 2>&1
    exit /b 2
)

"%GIT%" -c user.name="Yasin" -c user.email="yasin@huginn.local" commit -m "Otomatik gunluk commit (%DATE% %TIME%)" >> %LOG% 2>&1

:push
set /a DENEME=1
:PUSH_DONGU
REM --autostash: kirli calisma agacinda rebase'in patlamasini engeller (GIT-01)
"%GIT%" pull --rebase --autostash origin %BR% >> %LOG% 2>&1
if errorlevel 1 (
    echo [%DATE% %TIME%] pull --rebase HATA (dal: %BR%) >> %LOG%
    exit /b 1
)
"%GIT%" push origin %BR% >> %LOG% 2>&1
if errorlevel 1 (
    if %DENEME% LSS 2 (
        echo [%DATE% %TIME%] push denemesi %DENEME% basarisiz, 5 sn sonra tekrar >> %LOG%
        set /a DENEME+=1
        timeout /t 5 /nobreak >nul
        goto :PUSH_DONGU
    )
    echo [%DATE% %TIME%] PUSH HATA (dal: %BR%, 2 deneme tukendi) >> %LOG%
    exit /b 1
)
echo [%DATE% %TIME%] push OK (dal: %BR%) >> %LOG%
exit /b 0

:err
echo [%DATE% %TIME%] git status hatasi >> %LOG%
exit /b 1
