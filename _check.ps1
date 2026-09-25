$task='TEST-BLOKE-FAKTOR-ARASTIRMA-01'
$path='C:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator'
$board=Get-Content "$path/task_board.json" -Raw | ConvertFrom-Json
$taskData=$board | Where-Object { $_.id -eq $task } | Select-Object -First 1
Write-Host "Task found: $(if($taskData) { 'YES' } else { 'NO' })"
Write-Host "Status: $($taskData.durum)"
Write-Host "Report exists: $(Test-Path "$path/${task}_rapor_*.md")"
Get-ChildItem "$path" -Filter "${task}_rapor_*.md" | Select-Object Name
Write-Host "Bulgu exists: $(Test-Path "$path/${task}_bulgular_*.md")"