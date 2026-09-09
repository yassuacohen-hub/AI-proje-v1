#!/usr/bin/env pwsh
# PostgreSQL Backup Scheduler (PowerShell)
# Windows Task Scheduler ile otomatik yedekleme gorevi olusturur.
#
# Kullanim (PowerShell yonetici olarak):
#     powershell -ExecutionPolicy Bypass -File scripts\backup\setup_backup_scheduler.ps1

$TaskName = "Huginn_Postgres_Backup"
$PythonPath = "python"
$ScriptPath = "scripts\backup\pg_backup.py"
$WorkingDir = "C:\Projeler\Huginn Data Insights"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Huginn PostgreSQL Backup Scheduler" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Gorev detaylari:" -ForegroundColor Yellow
Write-Host "  - Ad: $TaskName"
Write-Host "  - Zaman: Her gun 03:00"
Write-Host "  - Komut: $PythonPath $ScriptPath"
Write-Host "  - Working Directory: $WorkingDir"
Write-Host ""

$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "[UYARI] Gorev zaten mevcut: $TaskName" -ForegroundColor Yellow
    Write-Host "Mevcut gorev kaldiriliyor..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

$action = New-ScheduledTaskAction -Execute $PythonPath -Argument "$ScriptPath" -WorkingDirectory $WorkingDir

$trigger = New-ScheduledTaskTrigger -Daily -At 03:00

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest -LogonType S4U

try {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Huginn Data Insights - Daily PostgreSQL backup" -Force
    Write-Host ""
    Write-Host "[OK] Gorev basariyla olusturuldu!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Gorev durumu:" -ForegroundColor Yellow
    Get-ScheduledTask -TaskName $TaskName | Format-List TaskName, State, LastRunTime, NextRunTime
    Write-Host ""
    Write-Host " Manuel calistirmak icin:" -ForegroundColor Yellow
    Write-Host "   Start-ScheduledTask -TaskName '$TaskName'"
    Write-Host ""
    Write-Host " Gorevi silmek icin:" -ForegroundColor Yellow
    Write-Host "   Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
    Write-Host ""
    Write-Host "Yedekleri test etmek icin:" -ForegroundColor Yellow
    Write-Host "   python scripts\backup\pg_restore.py scripts\backup\pg_*.dump"
    Write-Host ""
    Write-Host "Eski yedekleri temizlemek icin:" -ForegroundColor Yellow
    Write-Host "   python scripts\backup\pg_cleanup.py --days 30 --keep 14"
} catch {
    Write-Host ""
    Write-Host "[HATA] Gorev olusturulamadi: $_" -ForegroundColor Red
    Write-Host "Yonetici yetkisi ile calistirdiginizdan emin olun."
}
