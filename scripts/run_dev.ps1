# Unified script to run Doc Assistant with all services
# Usage: .\scripts\run_dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Starting Doc Assistant Development Environment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Function to start a service
function Start-Service {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port,
        [int]$WaitSeconds = 5
    )
    
    Write-Host "Starting $Name..." -ForegroundColor Yellow
    
    # Check if port is already in use
    $process = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "$Name already running on port $Port (PID: $($process.OwningProcess))" -ForegroundColor Green
        return
    }
    
    # Start the service
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "cmd.exe"
    $processInfo.Arguments = "/c $Command"
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false
    $processInfo.CreateNoWindow = $true
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo
    $process.Start() | Out-Null
    
    # Wait for service to start
    Start-Sleep -Seconds $WaitSeconds
    
    Write-Host "$Name started successfully" -ForegroundColor Green
    return $process
}

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Node.js
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python is not installed. Please install Python first." -ForegroundColor Red
    exit 1
}

# Check Rust (for Tauri)
if (-not (Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "WARNING: Rust/Cargo is not installed. Tauri desktop app will not work." -ForegroundColor Yellow
    Write-Host "Install Rust from https://rustup.rs/ to enable the desktop app." -ForegroundColor Yellow
    $TAURI_ENABLED = $false
} else {
    $TAURI_ENABLED = $true
}

Write-Host ""

# Start Backend
Write-Host "Step 1/3: Starting Backend Service" -ForegroundColor Cyan
Write-Host "-----------------------------------------" -ForegroundColor Cyan
$backendProcess = Start-Service -Name "Backend" -Command "cd backend; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -Port 8000 -WaitSeconds 3

# Start Frontend Dev Server
Write-Host ""
Write-Host "Step 2/3: Starting Frontend Dev Server" -ForegroundColor Cyan
Write-Host "-----------------------------------------" -ForegroundColor Cyan
$frontendProcess = Start-Service -Name "Frontend" -Command "cd frontend; npm run dev" -Port 1420 -WaitSeconds 5

# Start Tauri Desktop App (if Rust is available)
if ($TAURI_ENABLED) {
    Write-Host ""
    Write-Host "Step 3/3: Starting Tauri Desktop App" -ForegroundColor Cyan
    Write-Host "-----------------------------------------" -ForegroundColor Cyan
    
    # Check if frontend is built
    if (-not (Test-Path "frontend/dist")) {
        Write-Host "Building frontend for Tauri..." -ForegroundColor Yellow
        Push-Location frontend
        npm run build
        Pop-Location
    }
    
    $tauriProcess = Start-Service -Name "Tauri" -Command "cd src-tauri; cargo tauri dev" -Port 1420 -WaitSeconds 10
} else {
    Write-Host ""
    Write-Host "Step 3/3: Tauri Desktop App (Skipped - Rust not installed)" -ForegroundColor Gray
    Write-Host "You can access the web version at: http://localhost:1420" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "All services started successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Services running:" -ForegroundColor White
Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - Frontend Web: http://localhost:1420" -ForegroundColor Cyan
if ($TAURI_ENABLED) {
    Write-Host "  - Tauri Desktop App: Running" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

# Wait for user interruption
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
catch {
    Write-Host ""
    Write-Host "Shutting down services..." -ForegroundColor Yellow
    
    # Stop processes
    if ($backendProcess) { $backendProcess.Kill() }
    if ($frontendProcess) { $frontendProcess.Kill() }
    if ($tauriProcess) { $tauriProcess.Kill() }
    
    Write-Host "All services stopped." -ForegroundColor Green
}