#Requires -RunAsAdministrator
# =============================================================================
# Novahiz OS v6.1 — WSL Installer Bootstrap (PowerShell)
# Usage (Run as Administrator):
#   powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Invoke-RestMethod 'https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.ps1'))"
# =============================================================================
# IMPORTANT: Novahiz OS requires WSL (Windows Subsystem for Linux).
# This script installs WSL + a Linux distro, then runs the Linux installer.
# It is NOT for direct Windows (native) installation.
# =============================================================================

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Novahiz OS v6.1 — WSL Bootstrap"

# ---- Colors ----
function wc($Text, $Color) { Write-Host $Text -ForegroundColor $Color }
function log   { wc "[•] $args" Cyan }
function ok    { wc "[✓] $args" Green }
function warn  { wc "[!] $args" Yellow }
function fail  { wc "[✗] $args" Red }
function header{ Write-Host "`n━━━ $args ━━━" -ForegroundColor Cyan }

Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║                    Novahiz OS v6.1                          ║
║            WSL Installer Bootstrap (PowerShell)              ║
╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# =============================================================================
# CHECK 1: Already in WSL?
# =============================================================================
$inWSL = ($env:WSL_DISTRO_NAME) -or (Test-Path "/proc/version" -ErrorAction SilentlyContinue)

if ($inWSL) {
    log "You are already inside WSL!"
    log "Running the Linux installer directly..."
    & bash -c "curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash"
    exit $LASTEXITCODE
}

# =============================================================================
# CHECK 2: WSL installed?
# =============================================================================
$wslExe = Get-Command "wsl.exe" -ErrorAction SilentlyContinue

if (-not $wslExe) {
    Write-Host @"

✗  WSL is not installed on this system.

   Novahiz OS requires WSL (Windows Subsystem for Linux) because:
   • All core scripts are Linux shell scripts (.sh)
   • System services use systemd (Linux init system)
   • MCP servers require native Linux paths and permissions
   • The agent runtime is optimized for Linux/POSIX environments

   Direct Windows (native) installation is NOT supported.

"@ -ForegroundColor Red

    header "How to install WSL"
    Write-Host @"
   1. Open PowerShell as Administrator

   2. Run:
         wsl --install

   3. Restart your computer when prompted

   4. After restart, WSL will open automatically.
      Set up your Linux username and password.

   5. Inside WSL, run:
         curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash

"@ -ForegroundColor White
    exit 1
}

# =============================================================================
# CHECK 3: WSL has a distro installed?
# =============================================================================
$distros = wsl.exe -l -v 2>$null | Select-Object -Skip 1
$hasDistro = $false
$runningDistro = $false

foreach ($line in $distros) {
    if ($line -match '^\s*(\S+)\s+.*\b(Running|Stopped)\b') {
        $hasDistro = $true
        if ($line -match 'Running') { $runningDistro = $true }
    }
}

if (-not $hasDistro) {
    fail "WSL is installed but no Linux distro is set up."
    Write-Host @"

   To install a default distro:
     wsl --install -d Ubuntu

   Then restart WSL and run:
     curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash

"@ -ForegroundColor Yellow
    exit 1
}

# =============================================================================
# Launch install inside WSL
# =============================================================================
header "Launching Novahiz OS Installer inside WSL"

if ($runningDistro) {
    log "WSL is running. Installing Novahiz OS..."
    wsl.exe bash -c "curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash"
} else {
    log "Starting WSL and installing Novahiz OS..."
    wsl.exe bash -c "curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash"
}

if ($LASTEXITCODE -eq 0) {
    Write-Host @"

╔══════════════════════════════════════════════════════════════╗
║  🚀 NOVAHIZ OS v6.1 — INSTALLED IN WSL SUCCESSFULLY!      ║
╚══════════════════════════════════════════════════════════════╝

   Quick start:
     wsl nv route "explore this project"
     wsl opencode

   Or open WSL and use directly:
     wsl ~

"@ -ForegroundColor Green
} else {
    fail "Installation failed."
    Write-Host @"
   Check WSL logs or try manually inside WSL:
     curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash
"@ -ForegroundColor Yellow
    exit 1
}
