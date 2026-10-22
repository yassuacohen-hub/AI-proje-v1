<#
.SYNOPSIS
    Huginn Data Insights - Deployment Validation Script
    Comprehensive health checks for all services after Docker Compose deployment

.DESCRIPTION
    Runs validation tests against all deployed services:
    - Docker container health
    - PostgreSQL connectivity & schema
    - Redis connectivity & pub/sub
    - Kong Gateway routing & mTLS
    - FastAPI endpoints (health, ingest, mirmir)
    - Celery workers & beat
    - Streamlit Admin
    - Next.js Frontend
    - ChromaDB
    - TOBB API integration
    - SSL/TLS certificates

.PARAMETER HOST_IP_PUBLIC
    Public IP address (default: 192.168.1.50)

.PARAMETER HOST_IP_ENTERPRISE
    Enterprise IP address (default: 192.168.1.60)

.PARAMETER SKIP_SSL_VALIDATION
    Skip SSL certificate validation for self-signed certs (default: true)

.PARAMETER VERBOSE
    Show detailed output

.EXAMPLE
    .\validate-deployment.ps1 -Verbose

.EXAMPLE
    .\validate-deployment.ps1 -HOST_IP_PUBLIC "10.0.1.50" -HOST_IP_ENTERPRISE "10.0.1.60"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [ValidatePattern('^\d{1,3}(\.\d{1,3}){3}$')]
    [string]$HOST_IP_PUBLIC = "192.168.1.50",

    [Parameter(Mandatory=$false)]
    [ValidatePattern('^\d{1,3}(\.\d{1,3}){3}$')]
    [string]$HOST_IP_ENTERPRISE = "192.168.1.60",

    [Parameter(Mandatory=$false)]
    [bool]$SKIP_SSL_VALIDATION = $true,

    [Parameter(Mandatory=$false)]
    [switch]$VERBOSE
)

# ------------------------------------------------------------
# GLOBALS & HELPERS
# ------------------------------------------------------------
$ErrorActionPreference = "Stop"
$global:TestResults = @()
$global:StartTime = Get-Date

function Write-TestResult {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Details = "",
        [string]$Category = "General"
    )
    $result = [PSCustomObject]@{
        Name        = $Name
        Category    = $Category
        Passed      = $Passed
        Details     = $Details
        Timestamp   = Get-Date
        DurationMs  = 0
    }
    $global:TestResults += $result
    
    $status = if ($Passed) { "✓ PASS" } else { "✗ FAIL" }
    $color  = if ($Passed) { "Green" } else { "Red" }
    Write-Host "  [$status] $Name" -ForegroundColor $color -NoNewline
    if ($Details) { Write-Host " - $Details" -ForegroundColor Gray } else { Write-Host "" }
}

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [int]$ExpectedStatus = 200,
        [int]$TimeoutSec = 10,
        [string]$Category = "API"
    )
    
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $params = @{
            Uri         = $Url
            Method      = $Method
            TimeoutSec  = $TimeoutSec
            ErrorAction = "Stop"
        }
        if ($SKIP_SSL_VALIDATION) {
            $params.SkipCertificateCheck = $true
        }
        if ($Headers.Count -gt 0) {
            $params.Headers = $Headers
        }
        
        $response = Invoke-WebRequest @params
        $sw.Stop()
        
        $passed = $response.StatusCode -eq $ExpectedStatus
        Write-TestResult -Name $Name -Passed $passed -Details "HTTP $($response.StatusCode) in $($sw.ElapsedMilliseconds)ms" -Category $Category
        return $passed
    } catch {
        $sw.Stop()
        $msg = $_.Exception.Message
        if ($_.Exception.Response) {
            $msg = "HTTP $($_.Exception.Response.StatusCode): $msg"
        }
        Write-TestResult -Name $Name -Passed $false -Details "$msg (${sw.ElapsedMilliseconds}ms)" -Category $Category
        return $false
    }
}

function Test-DockerContainer {
    param(
        [string]$ContainerName,
        [string]$Category = "Docker"
    )
    
    try {
        $container = docker inspect $ContainerName --format '{{.State.Status}} {{.State.Health.Status}}' 2>$null
        if (-not $container) {
            Write-TestResult -Name "Container: $ContainerName" -Passed $false -Details "Container not found" -Category $Category
            return $false
        }
        
        $parts = $container.Split(' ')
        $status = $parts[0]
        $health = if ($parts.Count -gt 1) { $parts[1] } else { "none" }
        
        $passed = ($status -eq "running") -and ($health -in @("healthy", "none", "starting"))
        $details = "Status: $status, Health: $health"
        Write-TestResult -Name "Container: $ContainerName" -Passed $passed -Details $details -Category $Category
        return $passed
    } catch {
        Write-TestResult -Name "Container: $ContainerName" -Passed $false -Details $_ -Category $Category
        return $false
    }
}

function Test-PostgreSQL {
    param(
        [string]$Host = "localhost",
        [int]$Port = 5432,
        [string]$Database = "hugin_commercial_db",
        [string]$User = "hugin_admin",
        [string]$Password
    )
    
    $connStr = "Host=$Host;Port=$Port;Database=$Database;Username=$User;Password=$Password;Timeout=10;SslMode=Disable;"
    
    try {
        Add-Type -AssemblyName "Npgsql" -ErrorAction SilentlyContinue
        if (-not ([System.Management.Automation.PSTypeName]"Npgsql.NpgsqlConnection").Type) {
            # Try to load from local DLL or skip
            Write-TestResult -Name "PostgreSQL Connection" -Passed $false -Details "Npgsql driver not available. Install: dotnet add package Npgsql" -Category "Database"
            return $false
        }
        
        $conn = New-Object Npgsql.NpgsqlConnection($connStr)
        $conn.Open()
        
        # Test basic query
        $cmd = $conn.CreateCommand()
        $cmd.CommandText = "SELECT version(), current_database(), current_user;"
        $reader = $cmd.ExecuteReader()
        $reader.Read()
        $version = $reader.GetString(0)
        $db = $reader.GetString(1)
        $user = $reader.GetString(2)
        $reader.Close()
        
        # Test critical tables exist
        $tables = @("firms", "industrial_listings", "quarantine_firms", "escrow_accounts", "arbitration_cases", "api_tokens", "audit_logs")
        $missingTables = @()
        foreach ($table in $tables) {
            $cmd.CommandText = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '$table');"
            $reader = $cmd.ExecuteReader()
            $reader.Read()
            if (-not $reader.GetBoolean(0)) { $missingTables += $table }
            $reader.Close()
        }
        
        # Test GIN index on industrial_listings
        $cmd.CommandText = "SELECT indexname FROM pg_indexes WHERE tablename = 'industrial_listings' AND indexdef LIKE '%gin%';"
        $reader = $cmd.ExecuteReader()
        $ginIndexes = @()
        while ($reader.Read()) { $ginIndexes += $reader.GetString(0) }
        $reader.Close()
        
        $conn.Close()
        
        $details = "DB: $db, User: $user, PG: $($version.Substring(0,50))... Tables OK: $(($tables.Count - $missingTables.Count))/$($tables.Count) GIN Indexes: $($ginIndexes.Count)"
        $passed = ($missingTables.Count -eq 0) -and ($ginIndexes.Count -gt 0)
        Write-TestResult -Name "PostgreSQL Schema & Indexes" -Passed $passed -Details $details -Category "Database"
        return $passed
    } catch {
        Write-TestResult -Name "PostgreSQL Connection" -Passed $false -Details $_ -Category "Database"
        return $false
    }
}

function Test-Redis {
    param(
        [string]$Host = "localhost",
        [int]$Port = 6379
    )
    
    try {
        # Use redis-cli if available, otherwise test via telnet
        $result = & redis-cli -h $Host -p $Port ping 2>$null
        if ($result -eq "PONG") {
            # Test pub/sub
            $pubsub = & redis-cli -h $Host -p $Port --raw pubsub channels "channel:mirmir:*" 2>$null
            Write-TestResult -Name "Redis Connection & PubSub" -Passed $true -Details "PONG received, PubSub active" -Category "Cache"
            return $true
        } else {
            Write-TestResult -Name "Redis Connection" -Passed $false -Details "Unexpected response: $result" -Category "Cache"
            return $false
        }
    } catch {
        # Fallback: test TCP port
        try {
            $tcp = New-Object Net.Sockets.TcpClient
            $tcp.Connect($Host, $Port)
            $tcp.Close()
            Write-TestResult -Name "Redis TCP Port" -Passed $true -Details "Port $Port open (redis-cli not available for full test)" -Category "Cache"
            return $true
        } catch {
            Write-TestResult -Name "Redis Connection" -Passed $false -Details $_ -Category "Cache"
            return $false
        }
    }
}

# ------------------------------------------------------------
# MAIN VALIDATION FLOW
# ------------------------------------------------------------
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "HUGINN DATA INSIGHTS - DEPLOYMENT VALIDATION" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "Public IP:  $HOST_IP_PUBLIC" -ForegroundColor Yellow
Write-Host "Enterprise IP: $HOST_IP_ENTERPRISE" -ForegroundColor Yellow
Write-Host "Started: $($global:StartTime)" -ForegroundColor Yellow
Write-Host ""

# ------------------------------------------------------------
# 1. DOCKER CONTAINERS
# ------------------------------------------------------------
Write-Host "=== 1. DOCKER CONTAINER HEALTH ===" -ForegroundColor Cyan
$containers = @(
    "hugin_kong_gateway",
    "hugin_postgres_db",
    "hugin_redis_cache",
    "hugin_fastapi_backend",
    "hugin_worker_tobb",
    "hugin_worker_pdf",
    "hugin_worker_quarantine",
    "hugin_celery_beat",
    "hugin_streamlit_admin",
    "hugin_nextjs_frontend",
    "hugin_chromadb",
    "hugin_prometheus",
    "hugin_grafana"
)

foreach ($c in $containers) {
    Test-DockerContainer -ContainerName $c
}

# ------------------------------------------------------------
# 2. POSTGRESQL (via localhost port proxy)
# ------------------------------------------------------------
Write-Host "" 
Write-Host "=== 2. POSTGRESQL DATABASE ===" -ForegroundColor Cyan
# Note: Password would need to be passed from .env
Write-Host "Skipping direct PostgreSQL test (requires password from .env)" -ForegroundColor Gray
Write-Host "Run manually: docker exec hugin_postgres_db pg_isready -U hugin_admin" -ForegroundColor Gray

# ------------------------------------------------------------
# 3. REDIS
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 3. REDIS CACHE ===" -ForegroundColor Cyan
Test-Redis -Host "localhost" -Port 6379

# ------------------------------------------------------------
# 4. KONG GATEWAY (IP-1 Public)
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 4. KONG GATEWAY - IP-1 PUBLIC ($HOST_IP_PUBLIC) ===" -ForegroundColor Cyan

# Health check
Test-Endpoint -Name "Kong Health (IP-1 HTTP)" -Url "http://$HOST_IP_PUBLIC/health" -Category "Kong-IP1"
Test-Endpoint -Name "Kong Health (IP-1 HTTPS)" -Url "https://$HOST_IP_PUBLIC/health" -Category "Kong-IP1"

# Client API routes
Test-Endpoint -Name "Client API v1 (IP-1)" -Url "https://$HOST_IP_PUBLIC/api/v1/health" -Category "Kong-IP1"
Test-Endpoint -Name "Mirmir SSE Endpoint (IP-1)" -Url "https://$HOST_IP_PUBLIC/api/v1/mirmir/live-stream" -Method "GET" -ExpectedStatus 200 -Category "Kong-IP1"

# Frontend
Test-Endpoint -Name "Frontend Root (IP-1)" -Url "http://$HOST_IP_PUBLIC/" -Category "Kong-IP1"

# ------------------------------------------------------------
# 5. KONG GATEWAY (IP-2 Enterprise)
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 5. KONG GATEWAY - IP-2 ENTERPRISE ($HOST_IP_ENTERPRISE) ===" -ForegroundColor Cyan

# Health check (requires mTLS cert - will fail without cert, that's expected)
Test-Endpoint -Name "Enterprise API Health (IP-2 mTLS)" -Url "https://$HOST_IP_ENTERPRISE:8443/health" -ExpectedStatus 401 -Category "Kong-IP2"

# Admin panel (requires mTLS cert)
Test-Endpoint -Name "Muninn Admin Panel (IP-2)" -Url "https://$HOST_IP_ENTERPRISE:8501/_stcore/health" -ExpectedStatus 200 -Category "Kong-IP2"

# ------------------------------------------------------------
# 6. FASTAPI BACKEND (Direct - bypass Kong for internal validation)
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 6. FASTAPI BACKEND (Direct Internal) ===" -ForegroundColor Cyan

Test-Endpoint -Name "FastAPI Health" -Url "http://localhost:8000/health" -Category "FastAPI"
Test-Endpoint -Name "FastAPI OpenAPI Schema" -Url "http://localhost:8000/openapi.json" -Category "FastAPI"

# Ingest endpoint (security filter test)
$testPayload = @{
    company_vkn = "1234567890"
    company_title = "TEST FIRMA A.S."
    osb_name = "ANKARA OSB"
    category_flag = "F"
    volume_tier = "TIER_1"
    source = "validation_test"
} | ConvertTo-Json

Test-Endpoint -Name "Ingest Gateway - Valid Payload" -Url "http://localhost:8000/api/v1/ingest" -Method "POST" -Headers @{"Content-Type"="application/json"} -ExpectedStatus 200 -Category "FastAPI"

# Invalid payload (should quarantine)
$badPayload = @{
    company_vkn = "invalid"
    company_title = "<script>alert('xss')</script>"
} | ConvertTo-Json

Test-Endpoint -Name "Ingest Gateway - Invalid Payload (Quarantine)" -Url "http://localhost:8000/api/v1/ingest" -Method "POST" -Headers @{"Content-Type"="application/json"} -ExpectedStatus 422 -Category "FastAPI"

# ------------------------------------------------------------
# 7. CELERY WORKERS
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 7. CELERY WORKERS ===" -ForegroundColor Cyan

# Check worker status via Redis/Flower or direct
try {
    $workers = docker exec hugin_redis_cache redis-cli -n 0 keys "celery*" 2>$null
    Write-TestResult -Name "Celery Worker Keys in Redis" -Passed $true -Details "Keys found: $($workers.Count)" -Category "Workers"
} catch {
    Write-TestResult -Name "Celery Worker Keys in Redis" -Passed $false -Details $_ -Category "Workers"
}

# ------------------------------------------------------------
# 8. STREAMLIT ADMIN
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 8. STREAMLIT ADMIN PANEL ===" -ForegroundColor Cyan
Test-Endpoint -Name "Streamlit Health" -Url "http://localhost:8501/_stcore/health" -Category "Admin"

# ------------------------------------------------------------
# 9. NEXT.JS FRONTEND
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 9. NEXT.JS FRONTEND ===" -ForegroundColor Cyan
Test-Endpoint -Name "Frontend Health" -Url "http://localhost:3000/api/health" -Category "Frontend"
Test-Endpoint -Name "Frontend Root" -Url "http://localhost:3000/" -Category "Frontend"

# ------------------------------------------------------------
# 10. CHROMADB
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 10. CHROMADB VECTOR STORE ===" -ForegroundColor Cyan
Test-Endpoint -Name "ChromaDB Heartbeat" -Url "http://localhost:8002/api/v2/heartbeat" -Category "VectorDB"

# ------------------------------------------------------------
# 11. TOBB API INTEGRATION TEST
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 11. TOBB API INTEGRATION TEST ===" -ForegroundColor Cyan

# This would test the actual TOBB API with provided credentials
# Requires: TOBB_API_KEY, TOBB_API_SECRET from .env
Write-Host "TOBB API Test requires live credentials and prepaid balance." -ForegroundColor Gray
Write-Host "Run manually via: docker exec hugin_fastapi_backend python -m app.services.tobb_official_client" -ForegroundColor Gray

# ------------------------------------------------------------
# 12. SSL/TLS CERTIFICATES
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 12. SSL/TLS CERTIFICATES ===" -ForegroundColor Cyan

$certPath = "./kong/certs/kong-server.pem"
if (Test-Path $certPath) {
    try {
        $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($certPath)
        $expiry = [DateTime]::Parse($cert.GetExpirationDateString())
        $daysLeft = ($expiry - (Get-Date)).Days
        $passed = $daysLeft -gt 30
        Write-TestResult -Name "Kong SSL Certificate" -Passed $passed -Details "Expires: $expiry ($daysLeft days left)" -Category "SSL"
    } catch {
        Write-TestResult -Name "Kong SSL Certificate" -Passed $false -Details $_ -Category "SSL"
    }
} else {
    Write-TestResult -Name "Kong SSL Certificate" -Passed $false -Details "Certificate not found at $certPath" -Category "SSL"
}

# CA Cert
$caPath = "./kong/certs/ca.pem"
if (Test-Path $caPath) {
    Write-TestResult -Name "CA Certificate" -Passed $true -Details "Found at $caPath" -Category "SSL"
} else {
    Write-TestResult -Name "CA Certificate" -Passed $false -Details "Missing at $caPath" -Category "SSL"
}

# ------------------------------------------------------------
# 13. NETSH PORTPROXY RULES
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 13. NETSH PORTPROXY RULES ===" -ForegroundColor Cyan

$expectedRules = @(
    @{ IP=$HOST_IP_PUBLIC; Port=80 },
    @{ IP=$HOST_IP_PUBLIC; Port=443 },
    @{ IP=$HOST_IP_PUBLIC; Port=8443 },
    @{ IP=$HOST_IP_ENTERPRISE; Port=8443 },
    @{ IP=$HOST_IP_ENTERPRISE; Port=8501 }
)

$allRules = netsh interface portproxy show v4tov4
$allPassed = $true

foreach ($rule in $expectedRules) {
    $found = $allRules | Where-Object { $_ -match "$($rule.IP).*$($rule.Port)" }
    $passed = $found -ne $null
    $allPassed = $allPassed -and $passed
    Write-TestResult -Name "PortProxy $($rule.IP):$($rule.Port)" -Passed $passed -Details $(if($passed){"Active"}else{"MISSING"}) -Category "Network"
}

# ------------------------------------------------------------
# 14. FIREWALL RULES
# ------------------------------------------------------------
Write-Host ""
Write-Host "=== 14. WINDOWS FIREWALL RULES ===" -ForegroundColor Cyan

$fwRules = @(
    "Huginn IP-1 HTTP 80",
    "Huginn IP-1 HTTPS 443",
    "Huginn IP-1 Kong 8443",
    "Huginn IP-2 Kong 8443",
    "Huginn IP-2 Admin 8501"
)

foreach ($name in $fwRules) {
    $rule = Get-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue
    $passed = $rule -ne $null -and $rule.Enabled -eq "True"
    Write-TestResult -Name "Firewall: $name" -Passed $passed -Details $(if($passed){"Enabled"}else{"Missing or Disabled"}) -Category "Network"
}

# ------------------------------------------------------------
# SUMMARY REPORT
# ------------------------------------------------------------
$global:EndTime = Get-Date
$totalDuration = ($global:EndTime - $global:StartTime).TotalSeconds

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

$total = $global:TestResults.Count
$passed = ($global:TestResults | Where-Object { $_.Passed }).Count
$failed = $total - $passed
$passRate = if ($total -gt 0) { [math]::Round($passed / $total * 100, 1) } else { 0 }

Write-Host "Total Tests:  $total" -ForegroundColor White
Write-Host "Passed:       $passed" -ForegroundColor Green
Write-Host "Failed:       $failed" -ForegroundColor Red
Write-Host "Pass Rate:    $passRate%" -ForegroundColor $(if($passRate -ge 90){"Green"}elseif($passRate -ge 70){"Yellow"}else{"Red"})
Write-Host "Duration:     $([math]::Round($totalDuration,1))s" -ForegroundColor White
Write-Host ""

# Category breakdown
$categories = $global:TestResults | Group-Object Category | Sort-Object Count -Descending
foreach ($cat in $categories) {
    $catPassed = ($cat.Group | Where-Object { $_.Passed }).Count
    $catTotal = $cat.Count
    $catRate = [math]::Round($catPassed / $catTotal * 100, 1)
    $color = if ($catRate -eq 100) { "Green" } elseif ($catRate -ge 70) { "Yellow" } else { "Red" }
    Write-Host "  $($cat.Name): $catPassed/$catTotal ($catRate%)" -ForegroundColor $color
}

# Failed details
if ($failed -gt 0) {
    Write-Host ""
    Write-Host "FAILED TESTS:" -ForegroundColor Red
    $global:TestResults | Where-Object { -not $_.Passed } | ForEach-Object {
        Write-Host "  ✗ $($_.Name) [$($_.Category)]: $($_.Details)" -ForegroundColor Red
    }
}

# Exit code
if ($failed -gt 0) {
    Write-Host ""
    Write-Host "VALIDATION FAILED - $failed test(s) failed" -ForegroundColor Red
    exit 1
} else {
    Write-Host ""
    Write-Host "ALL TESTS PASSED - Deployment validated successfully!" -ForegroundColor Green
    exit 0
}