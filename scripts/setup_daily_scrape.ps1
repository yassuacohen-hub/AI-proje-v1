#!/usr/bin/env pwsh
# Company Master - Daily Scrape Scheduler (PowerShell)
# Windows Task Scheduler ile gunluk scrape gorevi olusturur.

$TaskName = "CompanyMaster_DailyScrape"
$PythonPath = "python"
$ScriptPath = "scripts\scheduled_scrape.py"
$WorkingDir = "C:\Projeler\Huginn Data Insights"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Company Master Daily Scrape Scheduler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Gorev detaylari:" -ForegroundColor Yellow
Write-Host "  - Ad: $TaskName"
Write-Host "  - Zaman: Her gun 02:00"
Write-Host "  - Komut: $PythonPath $ScriptPath --once"
Write-Host "  - Working Directory: $WorkingDir"
Write-Host ""

# Check if task already exists
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[UYARI] Gorev zaten mevcut: $TaskName" -ForegroundColor Yellow
    Write-Host "Mevcut gorev kaldiriliyor..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create task action
$action = New-ScheduledTaskAction -Execute $PythonPath -Argument "$ScriptPath --once" -WorkingDirectory $WorkingDir

# Create daily trigger at 02:00
$trigger = New-ScheduledTaskTrigger -Daily -At 02:00

# Create settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest -LogonType S4U

# Register task
try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Company Master daily scrape and workflow" -Force
    Write-Host ""
    Write-Host "[OK] Gorev basariyla olusturuldu!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Gorev durumu:" -ForegroundColor Yellow
    Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, LastRunTime, NextRunTime
    Write-Host ""
    Write-Host "Manuel calistirmak icin:" -ForegroundColor Yellow
    Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host "Gorev silmek icin:" -ForegroundColor Yellow
    Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
} catch {
    Write-Host ""
    Write-Host "[HATA] Gorev olusturulamadi: $_" -ForegroundColor Red
    Write-Host "Yonetici yetkisi ile calistirdiginizdan emin olun."
}
