<#
.SYNOPSIS
    Windows Server 2022 Dual-IP Port Proxy Setup for Huginn Data Insights
    Configures netsh interface portproxy to bridge physical IPs to WSL2/Docker containers

.DESCRIPTION
    This script sets up the dual-IP architecture:
    - IP-1 (192.168.1.50): Public traffic -> Kong Gateway (ports 80/443)
    - IP-2 (192.168.1.60): Enterprise/mTLS traffic -> Kong Gateway (port 8443) + Streamlit Admin (port 8501)

    Run as Administrator on Windows Server 2022 host (NOT inside WSL/container).

.PARAMETER IP1_PUBLIC
    Primary public IP address (default: 192.168.1.50)

.PARAMETER IP2_ENTERPRISE
    Secondary enterprise IP address (default: 192.168.1.60)

.PARAMETER WSL2_HOST
    WSL2 localhost address (default: 127.0.0.1)

.PARAMETER KONG_HTTP_PORT
    Kong HTTP port inside container (default: 8000)

.PARAMETER KONG_HTTPS_PORT
    Kong HTTPS port inside container (default: 8443)

.PARAMETER ADMIN_PORT
    Streamlit Admin port inside container (default: 8501)

.EXAMPLE
    .\setup-dual-ip-portproxy.ps1 -IP1_PUBLIC "192.168.1.50" -IP2_ENTERPRISE "192.168.1.60"

.NOTES
    Requires: Windows Server 2022, Administrator privileges, netsh, IPv4 enabled
    Persistent across reboots (stored in Windows registry)
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidatePattern('^\d{1,3}(\.\d{1,3}){3}$')]
    [string]$IP1_PUBLIC = "192.168.1.50",

    [Parameter(Mandatory=$false)]
    [ValidatePattern('^\d{1,3}(\.\d{1,3}){3}$')]
    [string]$IP2_ENTERPRISE = "192.168.1.60",

    [Parameter(Mandatory=$false)]
    [ValidatePattern('^\d{1,3}(\.\d{1,3}){3}$')]
    [string]$WSL2_HOST = "127.0.0.1",

    [Parameter(Mandatory=$false)]
    [ValidateRange(1, 65535)]
    [int]$KONG_HTTP_PORT = 8000,

    [Parameter(Mandatory=$false)]
    [ValidateRange(1, 65535)]
    [int]$KONG_HTTPS_PORT = 8443,

    [Parameter(Mandatory=$false)]
    [ValidateRange(1, 65535)]
    [int]$ADMIN_PORT = 8501
)

# ------------------------------------------------------------
# VALIDATION: Administrator Check
# ------------------------------------------------------------
function Test-Administrator {
    $principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    Write-Error "Bu script YÖNETİCİ (Administrator) yetkileriyle çalıştırılmalıdır!"
    Write-Host "PowerShell'i 'Yönetici olarak çalıştır' ile açın ve tekrar deneyin." -ForegroundColor Red
    exit 1
}

# ------------------------------------------------------------
# VALIDATION: IP Addresses exist on interfaces
# ------------------------------------------------------------
function Test-IPOnInterface {
    param([string]$IP)
    $adapters = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue
    return ($adapters | Where-Object { $_.IPAddress -eq $IP }).Count -gt 0
}

Write-Host "=== HUGINN DATA INSIGHTS - Dual-IP Port Proxy Setup ===" -ForegroundColor Cyan
Write-Host "IP-1 (Public):  $IP1_PUBLIC" -ForegroundColor Yellow
Write-Host "IP-2 (Enterprise): $IP2_ENTERPRISE" -ForegroundColor Yellow
Write-Host "WSL2 Target: $WSL2_HOST" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-IPOnInterface -IP $IP1_PUBLIC)) {
    Write-Warning "IP-1 ($IP1_PUBLIC) bu sunucuda bulunamadı! Ağ adaptörünü kontrol edin."
    $continue = Read-Host "Yine de devam etmek istiyor musunuz? (E/H)"
    if ($continue -notmatch '^[Ee]') { exit 1 }
}

if (-not (Test-IPOnInterface -IP $IP2_ENTERPRISE)) {
    Write-Warning "IP-2 ($IP2_ENTERPRISE) bu sunucuda bulunamadı! Ağ adaptörünü kontrol edin."
    $continue = Read-Host "Yine de devam etmek istiyor musunuz? (E/H)"
    if ($continue -notmatch '^[Ee]') { exit 1 }
}

# ------------------------------------------------------------
# CLEANUP: Remove existing proxy rules for our ports
# ------------------------------------------------------------
Write-Host "Mevcut portproxy kuralları temizleniyor..." -ForegroundColor Yellow

$portsToClean = @(
    @{ ListenPort=80;  ListenAddress=$IP1_PUBLIC },
    @{ ListenPort=443; ListenAddress=$IP1_PUBLIC },
    @{ ListenPort=8443; ListenAddress=$IP1_PUBLIC },
    @{ ListenPort=8443; ListenAddress=$IP2_ENTERPRISE },
    @{ ListenPort=8501; ListenAddress=$IP2_ENTERPRISE }
)

foreach ($rule in $portsToClean) {
    try {
        netsh interface portproxy delete v4tov4 `
            listenport=$($rule.ListenPort) `
            listenaddress=$($rule.ListenAddress) 2>$null
        Write-Host "  Silindi: $($rule.ListenAddress):$($rule.ListenPort)" -ForegroundColor Gray
    } catch {
        # Rule might not exist, ignore
    }
}

# ------------------------------------------------------------
# CREATE: IP-1 (Public) -> Kong Gateway
# ------------------------------------------------------------
Write-Host "" -ForegroundColor Cyan
Write-Host "IP-1 (Public) kuralları oluşturuluyor..." -ForegroundColor Green

# HTTP 80 -> Kong 8000 (HTTP)
netsh interface portproxy add v4tov4 `
    listenport=80 `
    listenaddress=$IP1_PUBLIC `
    connectport=$KONG_HTTP_PORT `
    connectaddress=$WSL2_HOST
Write-Host "  [OK] $IP1_PUBLIC:80 -> $WSL2_HOST:$KONG_HTTP_PORT (HTTP)" -ForegroundColor Green

# HTTPS 443 -> Kong 8443 (HTTPS/SSL)
netsh interface portproxy add v4tov4 `
    listenport=443 `
    listenaddress=$IP1_PUBLIC `
    connectport=$KONG_HTTPS_PORT `
    connectaddress=$WSL2_HOST
Write-Host "  [OK] $IP1_PUBLIC:443 -> $WSL2_HOST:$KONG_HTTPS_PORT (HTTPS/SSL)" -ForegroundColor Green

# Kong HTTPS on IP-1 as well (for client-web-service on 8443)
netsh interface portproxy add v4tov4 `
    listenport=8443 `
    listenaddress=$IP1_PUBLIC `
    connectport=$KONG_HTTPS_PORT `
    connectaddress=$WSL2_HOST
Write-Host "  [OK] $IP1_PUBLIC:8443 -> $WSL2_HOST:$KONG_HTTPS_PORT (Kong HTTPS Alt)" -ForegroundColor Green

# ------------------------------------------------------------
# CREATE: IP-2 (Enterprise) -> Kong Gateway + Streamlit Admin
# ------------------------------------------------------------
Write-Host "" -ForegroundColor Cyan
Write-Host "IP-2 (Enterprise) kuralları oluşturuluyor..." -ForegroundColor Green

# Kong HTTPS 8443 -> Kong 8443 (mTLS Enterprise API)
netsh interface portproxy add v4tov4 `
    listenport=8443 `
    listenaddress=$IP2_ENTERPRISE `
    connectport=$KONG_HTTPS_PORT `
    connectaddress=$WSL2_HOST
Write-Host "  [OK] $IP2_ENTERPRISE:8443 -> $WSL2_HOST:$KONG_HTTPS_PORT (Enterprise mTLS API)" -ForegroundColor Green

# Streamlit Admin 8501 -> Admin 8501 (Muninn Admin Panel)
netsh interface portproxy add v4tov4 `
    listenport=8501 `
    listenaddress=$IP2_ENTERPRISE `
    connectport=$ADMIN_PORT `
    connectaddress=$WSL2_HOST
Write-Host "  [OK] $IP2_ENTERPRISE:8501 -> $WSL2_HOST:$ADMIN_PORT (Muninn Admin Panel)" -ForegroundColor Green

# ------------------------------------------------------------
# VERIFICATION: List all created rules
# ------------------------------------------------------------
Write-Host "" -ForegroundColor Cyan
Write-Host "Doğrulama: Oluşturulan tüm portproxy kuralları:" -ForegroundColor Yellow
Write-Host ""

netsh interface portproxy show v4tov4 | Where-Object { 
    $_ -match "$IP1_PUBLIC|$IP2_ENTERPRISE" 
} | ForEach-Object {
    Write-Host "  $_" -ForegroundColor White
}

# ------------------------------------------------------------
# FIREWALL RULES: Allow inbound on physical IPs
# ------------------------------------------------------------
Write-Host "" -ForegroundColor Cyan
Write-Host "Windows Firewall kuralları oluşturuluyor..." -ForegroundColor Yellow

$firewallRules = @(
    @{ Name="Huginn IP-1 HTTP 80";  LocalPort=80;  Protocol="TCP"; LocalIP=$IP1_PUBLIC; Description="Huginn Public HTTP (IP-1)" },
    @{ Name="Huginn IP-1 HTTPS 443"; LocalPort=443; Protocol="TCP"; LocalIP=$IP1_PUBLIC; Description="Huginn Public HTTPS (IP-1)" },
    @{ Name="Huginn IP-1 Kong 8443";  LocalPort=8443; Protocol="TCP"; LocalIP=$IP1_PUBLIC; Description="Huginn Kong Alt HTTPS (IP-1)" },
    @{ Name="Huginn IP-2 Kong 8443";  LocalPort=8443; Protocol="TCP"; LocalIP=$IP2_ENTERPRISE; Description="Huginn Enterprise mTLS API (IP-2)" },
    @{ Name="Huginn IP-2 Admin 8501"; LocalPort=8501; Protocol="TCP"; LocalIP=$IP2_ENTERPRISE; Description="Huginn Muninn Admin Panel (IP-2)" }
)

foreach ($rule in $firewallRules) {
    # Remove existing
    Remove-NetFirewallRule -DisplayName $rule.Name -ErrorAction SilentlyContinue
    
    # Create new
    New-NetFirewallRule `
        -DisplayName $rule.Name `
        -Description $rule.Description `
        -Direction Inbound `
        -Action Allow `
        -Protocol $rule.Protocol `
        -LocalPort $rule.LocalPort `
        -LocalAddress $rule.LocalIP `
        -Profile Domain,Private,Public `
        -Enabled True `
        -ErrorAction Stop
    
    Write-Host "  [OK] Firewall: $($rule.Name) ($($rule.LocalIP):$($rule.LocalPort))" -ForegroundColor Green
}

# ------------------------------------------------------------
# WSL2 CONFIGURATION: Ensure WSL2 forwards to Windows host
# ------------------------------------------------------------
Write-Host "" -ForegroundColor Cyan
Write-Host "WSL2 .wslconfig kontrolü..." -ForegroundColor Yellow

$wslConfigPath = "$env:USERPROFILE\.wslconfig"
if (Test-Path $wslConfigPath) {
    $content = Get-Content $wslConfigPath -Raw
    if ($content -notmatch '\[wsl2\]') {
        Write-Warning ".wslconfig dosyasında [wsl2] bölümü yok. Ağ ayarları eklenmeli."
    } elseif ($content -notmatch 'networkingMode=mirrored') {
        Write-Warning "WSL2 'mirrored' networking mode önerilir (Windows 11/Server 2022+)."
    } else {
        Write-Host "  [OK] WSL2 mirrored networking mode aktif" -ForegroundColor Green
    }
} else {
    Write-Warning ".wslconfig dosyası bulunamadı ($wslConfigPath)."
    Write-Host "  Önerilen içerik:" -ForegroundColor Gray
    Write-Host @"
[wsl2]
networkingMode=mirrored
dnsProxy=true
autoProxy=true
memory=12GB
processors=6
"@ -ForegroundColor Gray
}

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------
Write-Host "" -ForegroundColor Cyan
Write-Host "=== KURULUM TAMAMLANDI ===" -ForegroundColor Green
Write-Host ""
Write-Host "Traffic Flow:" -ForegroundColor Yellow
Write-Host "  Internet/Clients  -> $IP1_PUBLIC:80/443    -> Kong (8000/8443) -> FastAPI/Frontend" -ForegroundColor White
Write-Host "  Enterprise Clients -> $IP2_ENTERPRISE:8443 -> Kong (8443 mTLS) -> Enterprise API" -ForegroundColor White
Write-Host "  Admins            -> $IP2_ENTERPRISE:8501  -> Streamlit (8501) -> Muninn Admin" -ForegroundColor White
Write-Host ""
Write-Host "Sonraki adımlar:" -ForegroundColor Yellow
Write-Host "  1. Docker Compose'ı başlatın: docker-compose up -d" -ForegroundColor White
Write-Host "  2. Kong'un ayağa kalmasını bekleyin (30-60 sn)" -ForegroundColor White
Write-Host "  3. Test: curl -k https://$IP1_PUBLIC/health" -ForegroundColor White
Write-Host "  4. Test: curl -k --cert client.pem --key client.key https://$IP2_ENTERPRISE:8443/health" -ForegroundColor White
Write-Host ""
Write-Host "Kuralları silmek için: .\remove-dual-ip-portproxy.ps1" -ForegroundColor Gray