$ErrorActionPreference = "SilentlyContinue"

Write-Host "Stopping local processes..." -ForegroundColor Cyan

$procs = Get-CimInstance Win32_Process | Where-Object {
  $_.Name -in @("python.exe","node.exe","cmd.exe","powershell.exe") -and (
    $_.CommandLine -match "uvicorn app\\.main:app" -or
    $_.CommandLine -match "app\\.workers\\.print_worker" -or
    $_.CommandLine -match "\\bvite\\b" -or
    $_.CommandLine -match "npm run dev"
  )
}

foreach ($p in $procs) {
  try { Stop-Process -Id $p.ProcessId -Force } catch {}
}

Write-Host "Done." -ForegroundColor Green

