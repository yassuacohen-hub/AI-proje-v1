<#
.SYNOPSIS
    Remove Huginn Data Insights Dual-IP Port Proxy Rules
    Cleans up all netsh portproxy and firewall rules created by setup script

.DESCRIPTION
    Run as Administrator on Windows Server 2022 host.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidatePattern('^\d{1,3}(\.\d{1,3}){3}$')]
    [string]$IP1_PUBLIC = "192.168.1.50",

    [Parameter(Mandatory=$false)]
    [ValidatePattern('^\d{1,3}(\.\d{1,3}){3}$')]
    [string]$IP2_ENTERPRISE = "192.168.1.60"
)

# Administrator check
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Bu script YÖNETİCİ (Administrator) yetkileriyle çalıştırılmalıdır!"
    exit 1
}

Write-Host "=== HUGINN Dual-IP Port Proxy Temizleme ===" -ForegroundColor Cyan

# Remove portproxy rules
$portsToClean = @(
    @{ ListenPort=80;  ListenAddress=$IP1_PUBLIC },
    @{ ListenPort=443; ListenAddress=$IP1_PUBLIC },
    @{ ListenPort=8443; ListenAddress=$IP1_PUBLIC },
    @{ ListenPort=8443; ListenAddress=$IP2_ENTERPRISE },
    @{ ListenPort=8501; ListenAddress=$IP2_ENTERPRISE }
)

Write-Host "Portproxy kuralları siliniyor..." -ForegroundColor Yellow
foreach ($rule in $portsToClean) {
    netsh interface portproxy delete v4tov4 `
        listenport=$($rule.ListenPort) `
        listenaddress=$($rule.ListenAddress) 2>$null
    Write-Host "  Silindi: $($rule.ListenAddress):$($rule.ListenPort)" -ForegroundColor Green
}

# Remove firewall rules
$firewallNames = @(
    "Huginn IP-1 HTTP 80",
    "Huginn IP-1 HTTPS 443",
    "Huginn IP-1 Kong 8443",
    "Huginn IP-2 Kong 8443",
    "Huginn IP-2 Admin 8501"
)

Write-Host "" -ForegroundColor Cyan
Write-Host "Firewall kuralları siliniyor..." -ForegroundColor Yellow
foreach ($name in $firewallNames) {
    Remove-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue
    Write-Host "  Silindi: $name" -ForegroundColor Green
}

# Verification
Write-Host "" -ForegroundColor Cyan
Write-Host "Kalan portproxy kuralları:" -ForegroundColor Yellow
netsh interface portproxy show v4tov4 | Where-Object { 
    $_ -match "$IP1_PUBLIC|$IP2_ENTERPRISE" 
} | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Red
}

Write-Host "" -ForegroundColor Green
Write-Host "Temizleme tamamlandı." -ForegroundColor Green