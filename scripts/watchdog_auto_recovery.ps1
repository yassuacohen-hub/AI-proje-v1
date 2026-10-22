<# 
.SYNOPSIS
    Huginn Data Insights - Watchdog Auto-Recovery Script
    Runs every 5 minutes via Windows Task Scheduler
    Monitors: containers, services, queues, disk, quarantine, TOBB balance

.DESCRIPTION
    Otonom izleme ve onarma betiği. Kritik servisler down olduğunda yeniden başlatır,
    disk dolduğunda temizler, karantina backlog büyüdüğünde uyarır.

.NOTES
    Author: İhsan (Orchestrator)
    Schedule: Every 5 minutes (Task Scheduler)
    Logs: C:\Huginn\logs\watchdog_YYYYMMDD.log
#>

param(
    [switch]$VerboseOutput,
    [switch]$DryRun,
    [string]$LogPath = "C:\Huginn\logs"
)

# ============================================================
# CONFIGURATION
# ============================================================
$Config = @{
    # Docker Compose project
    ProjectName     = "hugin"
    ComposeFile     = "C:\Huginn\docker-compose.yml"
    
    # Service expectations
    ExpectedWorkers = 3
    MinWorkers      = 2
    
    # Thresholds
    DiskCriticalPercent    = 10
    DiskWarningPercent     = 15
    DockerVolumeWarningPct = 20
    QuarantineBacklogWarn  = 500
    QuarantineStuckHours   = 24
    TOBBBalanceCriticalTL  = 5000
    TOBBBalanceWarnTL      = 20000
    QueueBacklogWarn       = 100
    CPUWarningPercent      = 85
    MemoryWarningPercent   = 90
    
    # Notification
    TelegramBotToken = $env:TELEGRAM_BOT_TOKEN
    TelegramChatID   = $env:TELEGRAM_CHAT_ID_CRITICAL
    WebhookURL       = $env:ALERT_WEBHOOK_URL
}

# ============================================================
# LOGGING SETUP
# ============================================================
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $LogPath "watchdog_$(Get-Date -Format 'yyyyMMdd').log"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[{0}] [{1}] {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Level, $Message
    Add-Content -Path $logFile -Value $entry -Encoding UTF8
    if ($VerboseOutput -or $Level -ne "INFO") { Write-Host $entry }
}

function Send-TelegramAlert {
    param([string]$Message, [string]$ChatID = $Config.TelegramChatID)
    if (-not $Config.TelegramBotToken -or -not $ChatID) { return }
    try {
        $url = "https://api.telegram.org/bot$($Config.TelegramBotToken)/sendMessage"
        $body = @{ chat_id = $ChatID; text = $Message; parse_mode = "HTML" }
        Invoke-RestMethod -Uri $url -Method Post -Body $body -TimeoutSec 10 | Out-Null
    } catch {
        Write-Log "Telegram send failed: $($_.Exception.Message)" "ERROR"
    }
}

function Invoke-DockerCompose {
    param([string]$Command, [switch]$CaptureOutput = $true)
    $cmd = "docker-compose -p $($Config.ProjectName) -f $($Config.ComposeFile) $Command"
    if ($DryRun) { Write-Log "[DRYRUN] $cmd" "DEBUG"; return @() }
    try {
        if ($CaptureOutput) {
            return Invoke-Expression $cmd
        } else {
            Invoke-Expression $cmd | Out-Null
            return $true
        }
    } catch {
        Write-Log "Docker compose command failed: $cmd | $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# ============================================================
# MAIN EXECUTION
# ============================================================
Write-Log "===== WATCHDOG START =====" "INFO"
$alerts = @()
$actionsTaken = @()

# ---- 1. CONTAINER HEALTH CHECK ----
Write-Log "Checking container health..." "DEBUG"
$containers = Invoke-DockerCompose "ps --format json"
if ($containers) {
    $healthy = 0
    $unhealthy = @()
    foreach ($c in $containers | ConvertFrom-Json) {
        $status = $c.State
        $name = $c.Name
        if ($status -eq "running") {
            $healthy++
        } else {
            $unhealthy += @{ Name = $name; Status = $status }
            $alerts += "Container DOWN: $name ($status)"
        }
    }
    Write-Log "Containers: $healthy healthy, $($unhealthy.Count) unhealthy"
    
    # Auto-restart unhealthy containers
    foreach ($u in $unhealthy) {
        if (-not $DryRun) {
            Write-Log "Attempting restart: $($u.Name)" "WARN"
            Invoke-DockerCompose "restart $($u.Name)" -CaptureOutput:$false
            $actionsTaken += "Restarted container: $($u.Name)"
        }
    }
}

# ---- 2. SERVICE ENDPOINT HEALTH ----
Write-Log "Checking service endpoints..." "DEBUG"
$endpoints = @(
    @{ Name = "Kong Gateway (IP-1)"; URL = "http://192.168.1.50/health"; Expect = 200 },
    @{ Name = "Kong Gateway (IP-2 mTLS)"; URL = "https://192.168.1.60:8443/health"; Expect = 200; SkipCert = $true },
    @{ Name = "FastAPI Backend"; URL = "http://localhost:8000/health"; Expect = 200 },
    @{ Name = "Streamlit Admin"; URL = "http://localhost:8501/_stcore/health"; Expect = 200 },
    @{ Name = "Next.js Frontend"; URL = "http://localhost:3000/api/health"; Expect = 200 },
    @{ Name = "Prometheus"; URL = "http://localhost:9090/-/healthy"; Expect = 200 },
    @{ Name = "Grafana"; URL = "http://localhost:3001/api/health"; Expect = 200 }
)

foreach ($ep in $endpoints) {
    try {
        $params = @{ Uri = $ep.URL; Method = "GET"; TimeoutSec = 5 }
        if ($ep.SkipCert) { $params.SkipCertificateCheck = $true }
        $resp = Invoke-WebRequest @params -ErrorAction Stop
        if ($resp.StatusCode -ne $ep.Expect) {
            $alerts += "$($ep.Name) returned HTTP $($resp.StatusCode)"
        } else {
            Write-Log "$($ep.Name): OK" "DEBUG"
        }
    } catch {
        $alerts += "$($ep.Name) UNREACHABLE: $($_.Exception.Message)"
    }
}

# ---- 3. REDIS CONNECTIVITY ----
Write-Log "Checking Redis..." "DEBUG"
try {
    $redis = Invoke-DockerCompose "exec -T hugin-cache redis-cli ping"
    if ($redis -notmatch "PONG") {
        $alerts += "Redis PING failed: $redis"
    } else {
        Write-Log "Redis: OK" "DEBUG"
    }
} catch {
    $alerts += "Redis connection error: $($_.Exception.Message)"
}

# ---- 4. POSTGRESQL CONNECTIVITY ----
Write-Log "Checking PostgreSQL..." "DEBUG"
try {
    $pg = Invoke-DockerCompose "exec -T hugin-db pg_isready -U hugin_admin -d hugin_commercial_db"
    if ($pg -notmatch "accepting connections") {
        $alerts += "PostgreSQL not accepting connections: $pg"
    } else {
        Write-Log "PostgreSQL: OK" "DEBUG"
    }
} catch {
    $alerts += "PostgreSQL connection error: $($_.Exception.Message)"
}

# ---- 5. CELERY QUEUE MONITORING ----
Write-Log "Checking Celery queues..." "DEBUG"
try {
    $queueInfo = Invoke-DockerCompose "exec -T hugin-worker celery -A app.workers.celery_app inspect active_queues"
    # Parse queue lengths from flower or redis directly
    $queueLengths = Invoke-DockerCompose "exec -T hugin-cache redis-cli LLEN celery"
    $queueLen = [int]($queueLengths.Trim())
    if ($queueLen -gt $Config.QueueBacklogWarn) {
        $alerts += "Celery queue backlog: $queueLen tasks (warn > $($Config.QueueBacklogWarn))"
    }
    Write-Log "Celery queue length: $queueLen" "DEBUG"
} catch {
    Write-Log "Queue check failed: $($_.Exception.Message)" "WARN"
}

# Worker count check
try {
    $workers = Invoke-DockerCompose "exec -T hugin-worker celery -A app.workers.celery_app inspect ping"
    $workerCount = ($workers | Select-String "pong").Matches.Count
    if ($workerCount -lt $Config.MinWorkers) {
        $alerts += "Celery workers below minimum: $workerCount/$($Config.ExpectedWorkers)"
        if (-not $DryRun) {
            Write-Log "Scaling up workers..." "WARN"
            Invoke-DockerCompose "up -d --scale hugin-worker=$($Config.ExpectedWorkers)" -CaptureOutput:$false
            $actionsTaken += "Scaled workers to $($Config.ExpectedWorkers)"
        }
    }
    Write-Log "Active Celery workers: $workerCount" "DEBUG"
} catch {
    Write-Log "Worker count check failed: $($_.Exception.Message)" "WARN"
}

# ---- 6. QUARANTINE BACKLOG ----
Write-Log "Checking quarantine backlog..." "DEBUG"
try {
    $sql = "SELECT COUNT(*) FROM quarantine_firms WHERE resolved_status = FALSE;"
    $count = Invoke-DockerCompose "exec -T hugin-db psql -U hugin_admin -d hugin_commercial_db -t -c `"$sql`""
    $unresolved = [int]($count.Trim())
    
    # Stuck records (>24h)
    $sqlStuck = "SELECT COUNT(*) FROM quarantine_firms WHERE resolved_status = FALSE AND created_at < NOW() - INTERVAL '24 hours';"
    $stuck = Invoke-DockerCompose "exec -T hugin-db psql -U hugin_admin -d hugin_commercial_db -t -c `"$sqlStuck`""
    $stuckCount = [int]($stuck.Trim())
    
    if ($unresolved -gt $Config.QuarantineBacklogWarn) {
        $alerts += "Quarantine backlog: $unresolved unresolved (warn > $($Config.QuarantineBacklogWarn))"
    }
    if ($stuckCount -gt 0) {
        $alerts += "Quarantine stuck >24h: $stuckCount records"
    }
    Write-Log "Quarantine: $unresolved unresolved, $stuckCount stuck >24h" "DEBUG"
} catch {
    Write-Log "Quarantine check failed: $($_.Exception.Message)" "WARN"
}

# ---- 7. DISK SPACE CHECK ----
Write-Log "Checking disk space..." "DEBUG"
$disks = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
foreach ($disk in $disks) {
    $freePct = [math]::Round(($disk.FreeSpace / $disk.Size) * 100, 1)
    $drive = $disk.DeviceID
    if ($freePct -lt $Config.DiskCriticalPercent) {
        $alerts += "DISK CRITICAL: $drive has $freePct% free (< $($Config.DiskCriticalPercent)%)"
    } elseif ($freePct -lt $Config.DiskWarningPercent) {
        $alerts += "DISK WARNING: $drive has $freePct% free (< $($Config.DiskWarningPercent)%)"
    }
    Write-Log "Disk $drive: $freePct% free" "DEBUG"
}

# Docker volume specific
try {
    $dockerVol = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "C:" }
    if ($dockerVol) {
        $freePct = [math]::Round(($dockerVol.FreeSpace / $dockerVol.Size) * 100, 1)
        if ($freePct -lt $Config.DockerVolumeWarningPct) {
            $alerts += "Docker volume (C:\) low: $freePct% free"
            if (-not $DryRun) {
                Write-Log "Running docker system prune..." "WARN"
                Invoke-DockerCompose "system prune -f --volumes" -CaptureOutput:$false
                $actionsTaken += "Docker system prune executed"
            }
        }
    }
} catch {
    Write-Log "Docker volume check failed: $($_.Exception.Message)" "WARN"
}

# ---- 8. TOBB BALANCE CHECK ----
Write-Log "Checking TOBB balance..." "DEBUG"
try {
    # This would call a FastAPI endpoint that checks TOBB balance
    $resp = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/admin/tobb-balance" -TimeoutSec 10 -ErrorAction Stop
    $balance = $resp.Content | ConvertFrom-Json
    $balanceTL = $balance.balance_tl
    
    if ($balanceTL -lt $Config.TOBBBalanceCriticalTL) {
        $alerts += "TOBB BALANCE CRITICAL: $balanceTL TL (< $($Config.TOBBBalanceCriticalTL) TL)"
    } elseif ($balanceTL -lt $Config.TOBBBalanceWarnTL) {
        $alerts += "TOBB BALANCE WARNING: $balanceTL TL (< $($Config.TOBBBalanceWarnTL) TL)"
    }
    Write-Log "TOBB Balance: $balanceTL TL" "DEBUG"
} catch {
    Write-Log "TOBB balance check failed: $($_.Exception.Message)" "WARN"
}

# ---- 9. SYSTEM RESOURCES (CPU/MEM) ----
Write-Log "Checking system resources..." "DEBUG"
$cpu = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average | Select-Object -ExpandProperty Average
$cpu = [math]::Round($cpu, 1)
if ($cpu -gt $Config.CPUWarningPercent) {
    $alerts += "HOST CPU HIGH: $cpu% (> $($Config.CPUWarningPercent)%)"
}

$mem = Get-CimInstance Win32_OperatingSystem
$memUsedPct = [math]::Round((1 - $mem.FreePhysicalMemory / $mem.TotalVisibleMemorySize) * 100, 1)
if ($memUsedPct -gt $Config.MemoryWarningPercent) {
    $alerts += "HOST MEMORY HIGH: $memUsedPct% (> $($Config.MemoryWarningPercent)%)"
}
Write-Log "Host CPU: $cpu%, Memory: $memUsedPct%" "DEBUG"

# ---- 10. SEND ALERTS IF ANY ----
if ($alerts.Count -gt 0) {
    $msg = "🚨 <b>HUGINN WATCHDOG ALERTS</b> 🚨`n"
    $msg += "`n<b>Time:</b> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
    $msg += "<b>Host:</b> $env:COMPUTERNAME`n`n"
    foreach ($a in $alerts) { $msg += "• $a`n" }
    if ($actionsTaken.Count -gt 0) {
        $msg += "`n<b>Actions Taken:</b>`n"
        foreach ($act in $actionsTaken) { $msg += "✅ $act`n" }
    }
    $msg += "`n<a href='https://grafana.huginn.local'>📊 Open Grafana</a>"
    
    Write-Log "ALERTS TRIGGERED: $($alerts.Count)" "WARN"
    Send-TelegramAlert -Message $msg
    
    # Also write to alert log
    $alertLog = Join-Path $LogPath "alerts_$(Get-Date -Format 'yyyyMMdd').log"
    $alerts | ForEach-Object { Add-Content -Path $alertLog -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $_" -Encoding UTF8 }
} else {
    Write-Log "All checks passed. No alerts." "INFO"
}

# ---- 11. LOG ROTATION (keep 30 days) ----
$oldLogs = Get-ChildItem -Path $LogPath -Name "watchdog_*.log" | Where-Object {
    $_ -match "watchdog_(\d{8})\.log" -and [datetime]::ParseExact($matches[1], "yyyyMMdd", $null) -lt (Get-Date).AddDays(-30)
}
foreach ($old in $oldLogs) {
    Remove-Item -Path (Join-Path $LogPath $old) -Force
    Write-Log "Rotated old log: $old" "DEBUG"
}

Write-Log "===== WATCHDOG END =====" "INFO"
exit 0