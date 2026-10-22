$ErrorActionPreference = "SilentlyContinue"
$key = "sk-e0fc29ccfd4fd5f6-fj938x-b30e5a44"
$h = @{ Authorization = "Bearer $key" }
try {
  $r = Invoke-WebRequest -Uri "http://127.0.0.1:20128/v1/models" -Headers $h -UseBasicParsing -TimeoutSec 30
  $js = $r.Content | ConvertFrom-Json
  $ids = @($js.data | ForEach-Object { $_.id })
  "VDS_MODEL_SAYISI=" + $ids.Count
  "VDS_KOMBOLAR=" + (($ids | Where-Object { $_ -match "^(yasu-9router|claude-claudecombo|claude_sadece|fullclaude|mimir-dis|fetch-combo|search-combo)$" }) -join ",")
  "VDS_SAMPLE=" + (($ids | Select-Object -First 8) -join ",")
} catch {
  "VDS_HATA=" + $_.Exception.Message
}