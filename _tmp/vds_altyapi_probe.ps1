$ErrorActionPreference = "SilentlyContinue"
"== WHERE_PYTHON =="; (Get-Command python).Source
"== WHERE_PY =="; (Get-Command py).Source
"== WHERE_SQLITE =="; (Get-Command sqlite3).Source
"== DB_YOLLARI =="
foreach ($p in @(
  "C:\Users\Administrator\AppData\Roaming\9router\db\data.sqlite",
  "C:\Users\ihsan\AppData\Roaming\9router\db\data.sqlite",
  "C:\ProgramData\9router\db\data.sqlite"
)) {
  if (Test-Path $p) { $f = Get-Item $p; "VAR: $p | $($f.Length) bayt | $($f.LastWriteTime)" }
}
"== REPO_YOLU =="
foreach ($r in @(
  "C:\Hugin_insights\Apps\hugin-infra",
  "C:\Hugin_insights\Apps\huginn-data-insights",
  "C:\hugin-infra"
)) { if (Test-Path $r) { "VAR: $r" } }
"== GIT_PULL_ZAMANLAYICI =="
Get-ScheduledTask -TaskName "*git*pull*" | Select-Object TaskName,State | Format-Table -AutoSize | Out-String
"== 9ROUTER_CALISANI =="
(Get-Process | Where-Object { $_.ProcessName -match "9router|node" } | Select-Object -First 5 ProcessName,Id | Format-Table -AutoSize | Out-String)
