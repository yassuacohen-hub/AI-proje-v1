<#
.SYNOPSIS
    Huginn mTLS Certificate Expiry Check
    Checks all certificates in kong.yml volumes and alerts if < 30 days

.DESCRIPTION
    Scans certificate files and checks expiry dates.
    Sends Telegram alert if any certificate expires within 30 days.

.NOTES
    Scheduled: Daily 06:00 via Task Scheduler
    Author: İhsan (Orchestrator)
#>

param(
    [string]$CertDir = "C:\Huginn\certs",
    [int]$WarningDays = 30,
    [switch]$Verbose
)

# ============================================================
# LOAD ENV
# ============================================================
$TelegramBotToken = $env:TELEGRAM_BOT_TOKEN
$TelegramChatID   = $env:TELEGRAM_CHAT_ID_SECURITY

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $entry = "[{0}] [{1}] {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Level, $Message
    Write-Host $entry
    if ($Level -ne "INFO") {
        Add-Content -Path "C:\Huginn\logs\cert_check_$(Get-Date -Format 'yyyyMMdd').log" -Value $entry -Encoding UTF8
    }
}

function Send-TelegramAlert {
    param([string]$Message)
    if (-not $TelegramBotToken -or -not $TelegramChatID) { return }
    try {
        $url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage"
        $body = @{ chat_id = $TelegramChatID; text = $Message; parse_mode = "HTML" }
        Invoke-RestMethod -Uri $url -Method Post -Body $body -TimeoutSec 10 | Out-Null
    } catch {
        Write-Log "Telegram send failed: $($_.Exception.Message)" "ERROR"
    }
}

# ============================================================
# MAIN
# ============================================================
Write-Log "Starting certificate expiry check..."
$alerts = @()

if (-not (Test-Path $CertDir)) {
    Write-Log "Certificate directory not found: $CertDir" "WARN"
    exit 0
}

# Find all .crt and .pem files
$certFiles = Get-ChildItem -Path $CertDir -Recurse -Filter "*.crt", "*.pem" -ErrorAction SilentlyContinue
if (-not $certFiles) {
    Write-Log "No certificate files found in $CertDir" "WARN"
    exit 0
}

foreach ($certFile in $certFiles) {
    try {
        # Use openssl to get expiry
        $openssl = "C:\Program Files\OpenSSL-Win64\bin\openssl.exe"
        if (-not (Test-Path $openssl)) {
            $openssl = "openssl.exe"  # Try PATH
        }
        
        $cmd = "& '$openssl' x509 -in '$($certFile.FullName)' -noout -enddate -subject"
        $result = Invoke-Expression $cmd -ErrorAction Stop
        
        # Parse: notAfter=Oct 13 06:00:00 2026 GMT
        if ($result -match 'notAfter=(.+)') {
            $expiryStr = $matches[1].Trim()
            $expiry = [datetime]::ParseExact($expiryStr, "MMM dd HH:mm:ss yyyy 'GMT'", [System.Globalization.CultureInfo]::InvariantCulture)
            
            # Parse subject for CN
            $subject = ""
            if ($result -match 'subject=(.+)') {
                $subject = $matches[1].Trim()
            }
            
            $daysLeft = [math]::Floor(($expiry - (Get-Date)).TotalDays)
            $status = if ($daysLeft -lt 0) { "EXPIRED" } elseif ($daysLeft -le $WarningDays) { "EXPIRING SOON" } else { "OK" }
            
            Write-Log "$($certFile.Name): $daysLeft days left ($status) - $subject" "INFO"
            
            if ($daysLeft -le $WarningDays) {
                $alerts += @{
                    File      = $certFile.Name
                    Path      = $certFile.FullName
                    Subject   = $subject
                    Expiry    = $expiry.ToString("yyyy-MM-dd")
                    DaysLeft  = $daysLeft
                    Status    = $status
                }
            }
        }
    } catch {
        Write-Log "Failed to check $($certFile.Name): $($_.Exception.Message)" "ERROR"
    }
}

# Send alerts
if ($alerts.Count -gt 0) {
    $msg = "🔐 <b>HUGINN CERTIFICATE EXPIRY ALERT</b> 🔐`n"
    $msg += "`n<b>Check Time:</b> $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
    $msg += "<b>Warning Threshold:</b> $WarningDays days`n`n"
    
    foreach ($a in $alerts) {
        $icon = if ($a.DaysLeft -lt 0) { "🔴" } else { "🟡" }
        $msg += "$icon <b>$($a.File)</b>`n"
        $msg += "  Subject: $($a.Subject)`n"
        $msg += "  Expires: $($a.Expiry) ($($a.DaysLeft) days)`n"
        $msg += "  Path: <code>$($a.Path)</code>`n`n"
    }
    
    $msg += "<b>Action Required:</b> Renew certificates and reload Kong`n"
    $msg += "<code>docker-compose -p hugin exec kong kong reload</code>"
    
    Write-Log "CERT ALERTS: $($alerts.Count)" "WARN"
    Send-TelegramAlert -Message $msg
} else {
    Write-Log "All certificates valid (> $WarningDays days)" "INFO"
}

Write-Log "Certificate check complete."
exit 0