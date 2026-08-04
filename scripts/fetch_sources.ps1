# Скачивает все отчёты из data/sources_inventory.json в папку sources/.
# Запуск (из корня репозитория):  powershell -ExecutionPolicy Bypass -File scripts/fetch_sources.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$inv  = Join-Path $root "data/sources_inventory.json"
$dest = Join-Path $root "sources"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
$data = Get-Content $inv -Raw -Encoding UTF8 | ConvertFrom-Json
$ok = 0; $skip = 0; $fail = 0
foreach ($f in $data.files) {
  $out = Join-Path $dest $f.file
  if (Test-Path $out) { Write-Host "SKIP  $($f.file)"; $skip++; continue }
  if (-not $f.source_url) { Write-Host "NOURL $($f.file)"; $fail++; continue }
  try {
    Invoke-WebRequest -Uri $f.source_url -OutFile $out -UseBasicParsing -TimeoutSec 300
    Write-Host "OK    $($f.file)"; $ok++
  } catch {
    if (Test-Path $out) { Remove-Item $out -Force }
    Write-Host "FAIL  $($f.file)"; $fail++
  }
}
Write-Host "`nГотово: OK=$ok SKIP=$skip FAIL=$fail из $($data.total) (объём ~$($data.total_size_mb) МБ)"
