$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "== Sanat Cafe POS: Local Run ==" -ForegroundColor Cyan

if (!(Test-Path "backend/.env")) {
  Copy-Item "backend/.env.example" "backend/.env" -Force
  Write-Host "Created backend/.env from backend/.env.example" -ForegroundColor Yellow
}

Write-Host "Installing backend deps..." -ForegroundColor Cyan
python -m pip install -r backend/requirements.txt | Out-Null

Write-Host "Installing frontend deps..." -ForegroundColor Cyan
npm install | Out-Null

Write-Host "Seeding DB (safe)..." -ForegroundColor Cyan
python backend/scripts/seed.py | Out-Null

$backendCmd = "cd '$root'; python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"
$workerCmd = "cd '$root'; `$env:PYTHONPATH='backend'; python -m app.workers.print_worker"
$frontendCmd = "cd '$root'; npm run dev"

Start-Process -WindowStyle Minimized -FilePath powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command $backendCmd"
Start-Process -WindowStyle Minimized -FilePath powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command $workerCmd"
Start-Process -WindowStyle Minimized -FilePath powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command $frontendCmd"

Write-Host ""
Write-Host "Frontend: http://127.0.0.1:3000/#/" -ForegroundColor Green
Write-Host "Backend : http://127.0.0.1:8000/api/health" -ForegroundColor Green
Write-Host ""
Write-Host "Stop: run .\\stop-local.ps1" -ForegroundColor Yellow

