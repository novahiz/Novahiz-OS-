#Requires -RunAsAdministrator
# =============================================================================
# Novahiz OS v6.0 — Universal Installer for Windows (PowerShell)
# Usage (Run as Administrator):
#   Set-ExecutionPolicy Bypass -Scope Process -Force
#   iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.ps1'))
# =============================================================================

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Novahiz OS v6.0 — Installing..."

# ---- Constants ----
$RepoUrl      = "https://github.com/novahiz/Novahiz-OS-.git"
$RepoBranch   = "main"
$NovahizDir   = "$env:USERPROFILE\.opencode"
$NovahizEnv   = "$env:USERPROFILE\.novahiz"
$ObsidianVault = "$env:USERPROFILE\Documents\llm-wiki"
$PythonMin    = [Version]"3.10"
$NodeMin      = [Version]"18.0"

# ---- Colors ----
$Host.UI.RawUI.ForegroundColor = [ConsoleColor]::White
function Write-Color($Text, $Color) { Write-Host $Text -ForegroundColor $Color }
function log   { Write-Color "[•] $args" Cyan }
function ok    { Write-Color "[✓] $args" Green }
function warn  { Write-Color "[!] $args" Yellow }
function fail  { Write-Color "[✗] $args" Red }
function header{ Write-Host "`n━━━ $args ━━━" -ForegroundColor Cyan }

# ---- Parse flags ----
$Yes = $false
foreach ($arg in $args) {
    if ($arg -eq '-y' -or $arg -eq '--yes')  { $Yes = $true }
    if ($arg -eq '--no-obsidian')            { $env:SKIP_OBSIDIAN = 'true' }
    if ($arg -eq '--no-desktop')             { $env:SKIP_DESKTOP  = 'true' }
}

# =============================================================================
# Helper: ensure cmd is available
# =============================================================================
function Ensure-Cmd {
    param([string]$Name, [string]$Command, [string]$InstallCmd, [string]$VersionFlag, [Version]$MinVersion)
    $oldPreference = $ErrorActionPreference; $ErrorActionPreference = "SilentlyContinue"
    $version = & $Command $VersionFlag 2>$null | Select-Object -First 1
    $ErrorActionPreference = $oldPreference
    if ($LASTEXITCODE -eq 0 -and $version) {
        $v = [Version]($version -replace '[^0-9.]','')
        if ($MinVersion -and $v -lt $MinVersion) {
            warn "$Name $v (need $MinVersion+), installing..."
            Invoke-Expression $InstallCmd
        } else {
            ok "$Name $v"
        }
    } else {
        log "Installing $Name..."
        Invoke-Expression $InstallCmd
    }
}

# =============================================================================
# PHASE 1: PREREQUISITES
# =============================================================================
header "PHASE 1/5 — Prerequisites"
log "OS: Windows $((Get-CimInstance Win32_OperatingSystem).Caption)"

# Check admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    fail "Please run as Administrator"
    exit 1
}

# winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    log "Installing winget (App Installer)..."
    Start-Process "ms-appinstaller:?source=https://aka.ms/Microsoft.DesktopAppInstaller" -Wait
    warn "Please install 'App Installer' from the Microsoft Store, then re-run"
    exit 1
}

# Git
Ensure-Cmd -Name "Git" -Command "git" -InstallCmd "winget install -e --id Git.Git" -VersionFlag "--version"

# Python
$pyCmd = if (Get-Command "py" -ErrorAction SilentlyContinue) { "py" } else { "python" }
if (-not (Get-Command $pyCmd -ErrorAction SilentlyContinue)) {
    log "Installing Python 3..."
    winget install -e --id Python.Python.3.12
    $env:Path = [Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [Environment]::GetEnvironmentVariable("Path","User")
}

# Node.js
Ensure-Cmd -Name "Node.js" -Command "node" -InstallCmd "winget install -e --id OpenJS.NodeJS.LTS" -VersionFlag "--version"

# jq for Windows
if (-not (Get-Command "jq" -ErrorAction SilentlyContinue)) {
    log "Installing jq..."
    winget install -e --id jqlang.jq
}

# ---- Python packages ----
log "Installing Python packages..."
& $pyCmd -m pip install --upgrade pip setuptools wheel 2>$null

# =============================================================================
# PHASE 2: CLONE NOVAHIZ OS
# =============================================================================
header "PHASE 2/5 — Installing Novahiz OS"

if (Test-Path "$NovahizDir\.git") {
    log "Novahiz OS already installed. Updating..."
    Push-Location $NovahizDir
    git stash 2>$null
    git pull origin $RepoBranch 2>$null
    Pop-Location
    ok "Updated Novahiz OS"
} else {
    log "Cloning Novahiz OS..."
    if (Test-Path $NovahizDir) {
        $backup = "${NovahizDir}.backup.$(Get-Date -Format yyyyMMdd-HHmmss)"
        Rename-Item $NovahizDir $backup
        warn "Backed up existing to $backup"
    }
    git clone --branch $RepoBranch $RepoUrl $NovahizDir
    ok "Novahiz OS cloned to $NovahizDir"
}

Set-Location $NovahizDir

# ---- Create required directories ----
@('logs','config','executions','data','cache') | ForEach-Object {
    New-Item -ItemType Directory -Path "$NovahizDir\$_" -Force | Out-Null
}
New-Item -ItemType Directory -Path $NovahizEnv -Force | Out-Null

# =============================================================================
# PHASE 3: PATCH PATHS FOR THIS USER
# =============================================================================
header "PHASE 3/5 — Configuring for your system"

log "Patching hardcoded paths..."
$oldHome = "/home/novahiz"
$newHome = $env:USERPROFILE -replace '\\','\\'

Get-ChildItem $NovahizDir -Recurse -File -Include @('*.sh','*.py','*.json','*.service','*.conf','*.yml','*.yaml','*.md') |
    Where-Object { $_.FullName -notmatch '\\.git\\' -and $_.FullName -notmatch '\\node_modules\\' } |
    ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match [regex]::Escape($oldHome)) {
            $content = $content -replace [regex]::Escape($oldHome), $newHome
            Set-Content $_.FullName $content -NoNewline
        }
    }

ok "Paths patched for user $env:USERNAME"

# ---- Install Python deps ----
log "Installing Python dependencies..."
& $pyCmd -m pip install --user -r "$NovahizDir\requirements.txt" 2>$null
ok "Python packages installed"

# ---- Install Node deps (TradingView MCP) ----
if (Test-Path "$NovahizDir\mcp\tradingview-mcp\package.json") {
    log "Installing TradingView MCP dependencies..."
    Push-Location "$NovahizDir\mcp\tradingview-mcp"
    npm install --production 2>$null
    Pop-Location
    ok "TradingView MCP ready"
}

# ---- Run component setup (where applicable on Windows) ----
if (Test-Path "$NovahizDir\installers\setup-novahiz.sh") {
    log "Running component setup (WSL/bash recommended)..."
    warn "Some Linux-specific components (systemd) will be skipped on Windows"
    bash "$NovahizDir\installers\setup-novahiz.sh" 2>$null
}

# ---- Install OpenCode CLI via npm ----
log "Installing OpenCode CLI..."
npm install -g @opencode-ai/cli 2>$null
ok "OpenCode CLI installed"

# ---- Add to PATH (User level) ----
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathsToAdd = @(
    "$env:USERPROFILE\AppData\Roaming\npm",
    "$env:USERPROFILE\.local\bin",
    "$NovahizDir\bin"
)
foreach ($p in $pathsToAdd) {
    if ($userPath -notlike "*$p*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$p", "User")
        $env:Path += ";$p"
    }
}
ok "CLI tools added to PATH"

# =============================================================================
# PHASE 4: CONFIG WIZARD (via WSL/bash if available)
# =============================================================================
header "PHASE 4/5 — Configuration"

if ($Yes) {
    log "Non-interactive mode: using defaults"
} elseif (Get-Command "bash" -ErrorAction SilentlyContinue) {
    log "Running configuration wizard (requires WSL)..."
    if (Test-Path "$NovahizDir\config-wizard\wizard.sh") {
        bash "$NovahizDir\config-wizard\wizard.sh"
    }
} else {
    warn "Wizard requires WSL/bash. Configure manually later:"
    warn "  bash $NovahizDir\config-wizard\wizard.sh"
    warn "  Or: set API keys in $NovahizEnv\.env"
}

# =============================================================================
# PHASE 5: VALIDATION
# =============================================================================
header "PHASE 5/5 — Validation"

$errors = 0; $passed = 0
function Check($Label, $Condition) {
    if ($Condition) { ok $Label; $script:passed++ }
    else            { fail $Label; $script:errors++ }
}

Check "Python 3.10+" (& $pyCmd -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)")
Check "Node.js 18+"  (node -e "process.exit(Number(process.version.slice(1).split('.')[0] < 18))")
Check "Git installed" (Get-Command git -ErrorAction SilentlyContinue)
Check "Novahiz directory" (Test-Path "$NovahizDir\engine")
Check "MCP server" (Test-Path "$NovahizDir\mcp\novahiz-mcp.py")
Check "Agent configs" (Test-Path "$NovahizDir\agents\novahiz-router.yaml")
Check "CLI tools" (Get-Command "nv" -ErrorAction SilentlyContinue)
Check "Config directory" (Test-Path "$NovahizDir\opencode.json")
Check "Runtime engine" (Test-Path "$NovahizDir\runtime\novahiz-unified.py")

# Deep validation
if (Test-Path "$NovahizDir\config-wizard\final-validation.py") {
    log "Running deep validation..."
    & $pyCmd "$NovahizDir\config-wizard\final-validation.py"
}

Write-Host ""
if ($errors -eq 0) {
    Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  🚀 NOVAHIZ OS v6.0 — INSTALLED SUCCESSFULLY!  ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Quick start:" -ForegroundColor White
    Write-Host "    nv route 'explore this project'         ← Route a task" -ForegroundColor Green
    Write-Host "    opencode                                ← Launch OpenCode" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Docs: $NovahizDir\docs\" -ForegroundColor White
    Write-Host "  Logs: $NovahizDir\logs\" -ForegroundColor White
    Write-Host ""
    warn "Close and re-open your terminal for PATH changes to take effect"
} else {
    Write-Host "[!] $errors checks failed, $passed passed" -ForegroundColor Yellow
    exit 1
}
