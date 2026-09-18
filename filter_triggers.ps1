$lines = Get-Content "C:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\triggers\roo.jsonl" -Encoding UTF8

$filtered = @()
$removed = 0

foreach ($line in $lines) {
    $trimmed = $line.Trim()
    if (-not $trimmed) { continue }
    
    $taskId = $null
    $durum = $null
    
    if ($trimmed -match '"task_id"\s*:\s*"([^"]+)"') {
        $taskId = $matches[1]
    }
    if ($trimmed -match '"durum"\s*:\s*"([^"]+)"') {
        $durum = $matches[1]
    }
    
    if ($taskId -in @('ADMIN-MODAL-STIL-01', 'ADMIN-SIFRE-RESET-FLOW-01', 'ADMIN-LOGIN-FIX-01') -and $durum -eq 'bekliyor') {
        $removed++
        continue
    }
    
    $filtered += $trimmed
}

$filtered | Set-Content "C:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\triggers\roo.jsonl" -Encoding UTF8
Write-Host "Removed $removed bekliyor entries"