# Unified script to run Doc Assistant with all services
# Usage: .\scripts\run_dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Starting Doc Assistant Development Environment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Function to start a service in a new PowerShell window
function Start-Service {
    param(
        [string]$Name,
        [string]$Command,
        [int]$Port,
        [int]$WaitSeconds = 5
    )
    
    Write-Host "Starting $Name..." -ForegroundColor Yellow
    
    # Check if port is already in use
    $existing = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "$Name already running on port $Port (PID: $($existing.OwningProcess))" -ForegroundColor Green
        return $null
    }
    
    # Start the service in a new PowerShell window
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "powershell.exe"
    $processInfo.Arguments = "-NoExit -Command `"$Command`""
    $processInfo.WorkingDirectory = $PSScriptRoot | Split-Path -Parent
    $processInfo.RedirectStandardOutput = $false
    $processInfo.RedirectStandardError = $false
    $processInfo.UseShellExecute = $true
    $processInfo.CreateNoWindow = $false
    
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $processInfo
    $process.Start() | Out-Null
    
    # Wait for service to start
    Start-Sleep -Seconds $WaitSeconds
    
    Write-Host "$Name started successfully (PID: $($process.Id))" -ForegroundColor Green
    return $process
}

# Function to kill a process and all its children
function Stop-ProcessTree($process) {
    if ($process -and !$process.HasExited) {
        try {
            # Kill child processes first
            $children = Get-WmiObject Win32_Process | Where-Object { $_.ParentProcessId -eq $process.Id }
            foreach ($child in $children) {
                Stop-Process -Id $child.ProcessId -Force -ErrorAction SilentlyContinue
            }
            $process.Kill()
        } catch {
            # Process may have already exited
        }
    }
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

# Wait for frontend to be ready
Write-Host "Waiting for frontend to be ready..." -ForegroundColor Yellow
$frontendReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:1420" -TimeoutSec 1 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Frontend ready" -ForegroundColor Green
            $frontendReady = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $frontendReady) {
    Write-Host "ERROR: Frontend failed to start within 30 seconds" -ForegroundColor Red
    exit 1
}

# Start Tauri Desktop App (if Rust is available)
if ($TAURI_ENABLED) {
    Write-Host ""
    Write-Host "Step 3/3: Starting Tauri Desktop App" -ForegroundColor Cyan
    Write-Host "-----------------------------------------" -ForegroundColor Cyan
    
    # Tauri doesn't listen on a port - launch directly
    Write-Host "Starting Tauri..." -ForegroundColor Yellow
    
    $tauriProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
    $tauriProcessInfo.FileName = "powershell.exe"
    $tauriProcessInfo.Arguments = "-NoExit -Command `"cd src-tauri; cargo tauri dev`""
    $tauriProcessInfo.WorkingDirectory = $PSScriptRoot | Split-Path -Parent
    $tauriProcessInfo.UseShellExecute = $true
    $tauriProcessInfo.RedirectStandardOutput = $false
    $tauriProcessInfo.RedirectStandardError = $false
    $tauriProcessInfo.CreateNoWindow = $false
    
    $tauriProcess = [System.Diagnostics.Process]::Start($tauriProcessInfo)
    
    Write-Host "Tauri started successfully (PID: $($tauriProcess.Id))" -ForegroundColor Green
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
    
    # Stop process trees
    if ($backendProcess) { Stop-ProcessTree $backendProcess }
    if ($tauriProcess) { Stop-ProcessTree $tauriProcess }
    
    Write-Host "All services stopped." -ForegroundColor Green
}
