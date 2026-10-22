<#
.SYNOPSIS
    Huginn Data Insights - Windows Task Scheduler Setup
    Registers all scheduled tasks for the watchdog and maintenance

.DESCRIPTION
    Creates the following scheduled tasks:
    1. Huginn-Watchdog - Runs every 5 minutes (auto-recovery)
    2. Huginn-PortProxy-Startup - Runs at system startup (netsh portproxy)
    3. Huginn-PortProxy-NetworkChange - Runs on network change event
    4. Huginn-LogCleanup - Runs daily at 03:00 (log rotation)
    5. Huginn-DockerPrune - Runs weekly Sunday 04:00 (docker cleanup)
    6. Huginn-CertRenewal-Check - Runs daily at 06:00 (mTLS cert check)

.NOTES
    Must run as Administrator
    Author: İhsan (Orchestrator)
#>

param(
    [switch]$Force,
    [switch]$Remove,
    [string]$HuginnRoot = "C:\Huginn",
    [string]$LogPath = "C:\Huginn\logs"
)

# ============================================================
# CHECK ADMIN RIGHTS
# ============================================================
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator!"
    Write-Host "Right-click PowerShell -> 'Run as Administrator'" -ForegroundColor Red
    exit 1
}

# ============================================================
# CONFIGURATION
# ============================================================
$Tasks = @(
    @{
        Name        = "Huginn-Watchdog"
        Description = "Huginn auto-recovery watchdog - runs every 5 minutes"
        Script      = Join-Path $HuginnRoot "scripts\watchdog_auto_recovery.ps1"
        Trigger     = @{
            Type       = "Once"
            Repetition = @{ Interval = "5 minutes"; Duration = "([TimeSpan]::MaxValue)" }
            At         = (Get-Date).AddMinutes(1).ToString("yyyy-MM-ddTHH:mm:ss")
        }
        User        = "SYSTEM"
        RunLevel    = "Highest"
        Enabled     = $true
    },
    @{
        Name        = "Huginn-PortProxy-Startup"
        Description = "Configure netsh portproxy for dual-IP at system startup"
        Script      = Join-Path $HuginnRoot "scripts\setup-dual-ip-portproxy.ps1"
        Trigger     = @{
            Type = "AtStartup"
            Delay = "00:02:00"  # Wait 2 min for network stack
        }
        User        = "SYSTEM"
        RunLevel    = "Highest"
        Enabled     = $true
    },
    @{
        Name        = "Huginn-PortProxy-NetworkChange"
        Description = "Re-apply portproxy on network configuration change (Event ID 4001/4002)"
        Script      = Join-Path $HuginnRoot "scripts\setup-dual-ip-portproxy.ps1"
        Trigger     = @{
            Type        = "OnEvent"
            Log         = "System"
            Source      = "Microsoft-Windows-NetworkProfile"
            EventID     = 10000  # Network change event
        }
        User        = "SYSTEM"
        RunLevel    = "Highest"
        Enabled     = $true
    },
    @{
        Name        = "Huginn-LogCleanup"
        Description = "Daily log rotation and cleanup (keep 30 days)"
        Script      = "powershell.exe"
        Arguments   = "-NoProfile -ExecutionPolicy Bypass -Command `"Get-ChildItem '$LogPath\*.log' | Where-Object { `$_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item -Force`""
        Trigger     = @{
            Type = "Daily"
            At   = "03:00"
        }
        User        = "SYSTEM"
        RunLevel    = "Highest"
        Enabled     = $true
    },
    @{
        Name        = "Huginn-DockerPrune"
        Description = "Weekly Docker system prune (remove unused images/volumes/networks)"
        Script      = "docker.exe"
        Arguments   = "system prune -af --volumes --filter until=168h"
        Trigger     = @{
            Type       = "Weekly"
            DaysOfWeek = "Sunday"
            At         = "04:00"
        }
        User        = "SYSTEM"
        RunLevel    = "Highest"
        Enabled     = $true
    },
    @{
        Name        = "Huginn-CertRenewal-Check"
        Description = "Daily mTLS certificate expiry check (alert if < 30 days)"
        Script      = "powershell.exe"
        Arguments   = "-NoProfile -ExecutionPolicy Bypass -File `"$HuginnRoot\scripts\check_cert_expiry.ps1`""
        Trigger     = @{
            Type = "Daily"
            At   = "06:00"
        }
        User        = "SYSTEM"
        RunLevel    = "Highest"
        Enabled     = $true
    }
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
function New-ScheduledTaskTriggerFromConfig {
    param($TriggerConfig)
    switch ($TriggerConfig.Type) {
        "Once" {
            $trigger = New-ScheduledTaskTrigger -Once -At $TriggerConfig.At
            if ($TriggerConfig.Repetition) {
                $trigger.RepetitionInterval = $TriggerConfig.Repetition.Interval
                $trigger.RepetitionDuration = $TriggerConfig.Repetition.Duration
            }
            return $trigger
        }
        "Daily" {
            return New-ScheduledTaskTrigger -Daily -At $TriggerConfig.At
        }
        "Weekly" {
            return New-ScheduledTaskTrigger -Weekly -DaysOfWeek $TriggerConfig.DaysOfWeek -At $TriggerConfig.At
        }
        "AtStartup" {
            $trigger = New-ScheduledTaskTrigger -AtStartup
            if ($TriggerConfig.Delay) {
                $trigger.Delay = $TriggerConfig.Delay
            }
            return $trigger
        }
        "OnEvent" {
            return New-ScheduledTaskTrigger -OnEvent -Log $TriggerConfig.Log -Source $TriggerConfig.Source -EventId $TriggerConfig.EventID
        }
        default {
            Write-Error "Unknown trigger type: $($TriggerConfig.Type)"
            return $null
        }
    }
}

function Register-HuginnTask {
    param($TaskConfig)
    
    $taskName = $TaskConfig.Name
    
    # Check if exists
    $existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existing -and -not $Force) {
        Write-Warning "Task '$taskName' already exists. Use -Force to overwrite."
        return $false
    }
    
    if ($existing -and $Force) {
        Write-Host "Removing existing task: $taskName" -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    }
    
    if ($Remove) {
        Write-Host "Removing task: $taskName" -ForegroundColor Red
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        return $true
    }
    
    # Create trigger
    $trigger = New-ScheduledTaskTriggerFromConfig -TriggerConfig $TaskConfig.Trigger
    if (-not $trigger) { return $false }
    
    # Create action
    if ($TaskConfig.Arguments) {
        $action = New-ScheduledTaskAction -Execute $TaskConfig.Script -Argument $TaskConfig.Arguments
    } else {
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$($TaskConfig.Script)`""
    }
    
    # Create principal (run as SYSTEM with highest privileges)
    $principal = New-ScheduledTaskPrincipal -UserId $TaskConfig.User -LogonType ServiceAccount -RunLevel $TaskConfig.RunLevel
    
    # Settings
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 5) `
        -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
        -Hidden $false
    
    # Register
    try {
        Register-ScheduledTask `
            -TaskName $taskName `
            -Description $TaskConfig.Description `
            -Trigger $trigger `
            -Action $action `
            -Principal $principal `
            -Settings $settings `
            -Force:$Force `
            -ErrorAction Stop
        
        if ($TaskConfig.Enabled) {
            Enable-ScheduledTask -TaskName $taskName -ErrorAction Stop
        }
        
        Write-Host "✅ Registered: $taskName" -ForegroundColor Green
        return $true
    } catch {
        Write-Error "Failed to register $taskName: $($_.Exception.Message)"
        return $false
    }
}

function Verify-Tasks {
    Write-Host "`n=== TASK VERIFICATION ===" -ForegroundColor Cyan
    $allGood = $true
    foreach ($t in $Tasks) {
        $task = Get-ScheduledTask -TaskName $t.Name -ErrorAction SilentlyContinue
        if ($task) {
            $state = $task.State
            $nextRun = $task.NextRunTime
            $status = if ($state -eq "Ready") { "✅ Ready" } elseif ($state -eq "Running") { "🔄 Running" } else { "⚠️ $state" }
            Write-Host "$($t.Name): $status | Next: $nextRun"
            if ($state -notin @("Ready", "Running")) { $allGood = $false }
        } else {
            Write-Host "$($t.Name): ❌ NOT FOUND" -ForegroundColor Red
            $allGood = $false
        }
    }
    return $allGood
}

# ============================================================
# MAIN
# ============================================================
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  HUGINN TASK SCHEDULER SETUP" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Root: $HuginnRoot"
Write-Host "Logs: $LogPath"
Write-Host "Force: $Force"
Write-Host "Remove: $Remove"
Write-Host ""

# Ensure log directory exists
if (-not (Test-Path $LogPath)) {
    New-Item -Path $LogPath -ItemType Directory -Force | Out-Null
    Write-Host "Created log directory: $LogPath"
}

# Ensure scripts directory exists
$scriptsDir = Join-Path $HuginnRoot "scripts"
if (-not (Test-Path $scriptsDir)) {
    New-Item -Path $scriptsDir -ItemType Directory -Force | Out-Null
}

# Process each task
$success = 0
$failed = 0
foreach ($task in $Tasks) {
    if (Register-HuginnTask -TaskConfig $task) { $success++ } else { $failed++ }
}

Write-Host ""
Write-Host "Summary: $success registered, $failed failed" -ForegroundColor Cyan

if (-not $Remove) {
    Verify-Tasks
    Write-Host ""
    Write-Host "To manually run watchdog now:" -ForegroundColor Yellow
    Write-Host "  powershell -NoProfile -ExecutionPolicy Bypass -File `"$scriptsDir\watchdog_auto_recovery.ps1`" -VerboseOutput"
    Write-Host ""
    Write-Host "To view watchdog logs:" -ForegroundColor Yellow
    Write-Host "  Get-Content $LogPath\watchdog_$(Get-Date -Format 'yyyyMMdd').log -Tail 50"
}

Write-Host "Done." -ForegroundColor Cyan