#Requires -RunAsAdministrator
# =============================================================================
# Novahiz OS v6.0 — Windows Installer (PowerShell)
# Usage (Run as Administrator):
#   powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Invoke-RestMethod 'https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.ps1'))"
# =============================================================================

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "Novahiz OS v6.0 — Installing..."

# ---- Constants ----
$RepoUrl       = "https://github.com/novahiz/Novahiz-OS-.git"
$RepoBranch    = "main"
$NovahizDir    = "$env:USERPROFILE\.opencode"
$NovahizEnv    = "$env:USERPROFILE\.novahiz"
$ObsidianVault = "$env:USERPROFILE\Documents\llm-wiki"
$OpenCodeVer   = "latest"

# ---- Colors ----
function wc($Text, $Color) { Write-Host $Text -ForegroundColor $Color }
function log   { wc "[•] $args" Cyan }
function ok    { wc "[✓] $args" Green }
function warn  { wc "[!] $args" Yellow }
function fail  { wc "[✗] $args" Red }
function header{ Write-Host "`n━━━ $args ━━━" -ForegroundColor Cyan }
function sub   { Write-Host "  → $args" -ForegroundColor Cyan }

# ---- Parse flags ----
$Yes = $false
foreach ($arg in $args) {
    if ($arg -in '-y','--yes')           { $Yes = $true }
    if ($arg -eq '--no-obsidian')        { $env:SKIP_OBSIDIAN = 'true' }
    if ($arg -eq '--no-desktop')         { $env:SKIP_DESKTOP = 'true' }
    if ($arg -eq '--verbose')            { $VerbosePreference = 'Continue' }
}

# ---- Refresh PATH from registry (after winget installs) ----
function Refresh-Path {
    $machine = [Environment]::GetEnvironmentVariable("Path","Machine")
    $user = [Environment]::GetEnvironmentVariable("Path","User")
    $env:Path = "$machine;$user"
}

# ---- Check if command exists ----
function Has-Command($cmd) { Get-Command $cmd -ErrorAction SilentlyContinue }

# ---- Install via winget with PATH refresh ----
function Install-WithWinget($Name, $WingetId) {
    log "Installing $Name..."
    winget install -e --id $WingetId --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        ok "$Name installed"
        Refresh-Path
    } else {
        warn "$Name install may have failed (winget exit: $LASTEXITCODE)"
    }
}

# =============================================================================
# PHASE 1: PREREQUISITES
# =============================================================================
header "PHASE 1/5 — Prerequisites"
$osInfo = Get-CimInstance Win32_OperatingSystem
log "OS: $($osInfo.Caption) | PowerShell: $($PSVersionTable.PSVersion)"

# Admin check
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    fail "Please run as Administrator"
    exit 1
}

# winget availability
if (-not (Has-Command winget)) {
    fail "winget not found. This installer requires Windows 10/11 or Windows Server 2022+."
    fail "Install 'App Installer' from the Microsoft Store, or install prerequisites manually."
    exit 1
}

# Git
if (-not (Has-Command git)) {
    Install-WithWinget "Git" "Git.Git"
    if (-not (Has-Command git)) { fail "Git required"; exit 1 }
} else { ok "Git $(git --version)" }

# Python 3
$pyCmd = $null
if (Has-Command py) { $pyCmd = "py" }
elseif (Has-Command python) { $pyCmd = "python" }
if (-not $pyCmd) {
    Install-WithWinget "Python 3" "Python.Python.3.12"
    if (Has-Command py) { $pyCmd = "py" } elseif (Has-Command python) { $pyCmd = "python" }
    if (-not $pyCmd) { fail "Python 3 required after install"; exit 1 }
}
try { $pyVer = & $pyCmd --version 2>&1 | Select-Object -First 1 } catch { $pyVer = "?" }
ok "Python $pyVer"

# Node.js
if (-not (Has-Command node)) {
    Install-WithWinget "Node.js" "OpenJS.NodeJS.LTS"
    if (-not (Has-Command node)) { fail "Node.js required"; exit 1 }
} else { ok "Node.js $(node --version)" }

# jq
if (-not (Has-Command jq)) {
    log "Installing jq..."
    winget install -e --id jqlang.jq --accept-source-agreements 2>&1 | Out-Null
    Refresh-Path
    if (Has-Command jq) { ok "jq installed" } else { warn "jq not in PATH — some tools may not work" }
} else { ok "jq available" }

# ---- npm (comes with Node.js) ----
if (-not (Has-Command npm)) { warn "npm not found — OpenCode CLI may fail" }

# ---- Python packages ----
log "Installing Python packages..."
& $pyCmd -m pip install --upgrade pip setuptools wheel 2>&1 | Out-Null
ok "Python packages updated"

# =============================================================================
# PHASE 2: CLONE NOVAHIZ OS
# =============================================================================
header "PHASE 2/5 — Installing Novahiz OS"

if (Test-Path "$NovahizDir\.git") {
    log "Novahiz OS already installed. Updating..."
    Push-Location $NovahizDir
    git stash 2>$null; git pull origin $RepoBranch 2>$null
    Pop-Location
    ok "Updated Novahiz OS"
} else {
    log "Cloning Novahiz OS (this may take a minute)..."
    if (Test-Path $NovahizDir) {
        $backup = "${NovahizDir}.backup.$(Get-Date -Format yyyyMMdd-HHmmss)"
        Rename-Item $NovahizDir $backup
        warn "Backed up existing to $backup"
    }
    git clone --branch $RepoBranch $RepoUrl $NovahizDir 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { ok "Novahiz OS cloned" } else { fail "Clone failed"; exit 1 }
}

Set-Location $NovahizDir

# ---- Create required directories ----
foreach ($d in @('logs','config','executions','data','cache')) {
    New-Item -ItemType Directory -Path "$NovahizDir\$d" -Force | Out-Null
}
New-Item -ItemType Directory -Path $NovahizEnv -Force | Out-Null

# =============================================================================
# PHASE 3: CONFIGURE
# =============================================================================
header "PHASE 3/5 — Configuring for your system"

# ---- Patch hardcoded /home/novahiz paths -> Windows paths ----
log "Patching hardcoded paths..."
$oldHome = "/home/novahiz"
$newHome = $env:USERPROFILE

Get-ChildItem $NovahizDir -Recurse -File -Include @('*.sh','*.py','*.json','*.service','*.conf','*.yml','*.yaml','*.md') |
    Where-Object { $_.FullName -notmatch '\\.git\\' -and $_.FullName -notmatch '\\node_modules\\' -and $_.FullName -notmatch '\\__pycache__\\' } |
    ForEach-Object {
        $content = Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue
        if ($content -and $content -match [regex]::Escape($oldHome)) {
            $content = $content -replace [regex]::Escape($oldHome), $newHome
            Set-Content $_.FullName $content -NoNewline -Force
        }
    }
ok "Paths patched for user $env:USERNAME"

# ---- Python deps ----
log "Installing Python dependencies..."
& $pyCmd -m pip install --user -r "$NovahizDir\requirements.txt" 2>&1 | Out-Null
ok "Python dependencies installed"

# ---- TradingView MCP deps ----
if (Test-Path "$NovahizDir\mcp\tradingview-mcp\package.json") {
    log "Installing TradingView MCP dependencies..."
    Push-Location "$NovahizDir\mcp\tradingview-mcp"
    npm install --production 2>&1 | Out-Null
    Pop-Location
    ok "TradingView MCP ready"
}

# ---- Install OpenCode CLI ----
if (Has-Command npm) {
    log "Installing OpenCode CLI..."
    npm install -g @opencode-ai/cli 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { ok "OpenCode CLI installed" } else { warn "npm install failed" }
}

# ---- OpenCode Desktop (Windows native) ----
if ($env:SKIP_DESKTOP -ne 'true') {
    $desktopPath = "$env:LOCALAPPDATA\Programs\opencode-desktop"
    if (-not (Test-Path "$desktopPath\opencode-desktop.exe")) {
        log "Installing OpenCode Desktop..."
        $msiUrl = "https://github.com/opencodelabs/opencode-desktop/releases/latest/download/opencode-desktop-x86_64.msi"
        $msiPath = "$env:TEMP\opencode-desktop.msi"
        try {
            $null = Invoke-WebRequest -Uri $msiUrl -OutFile $msiPath -UseBasicParsing -TimeoutSec 60
            Start-Process msiexec -ArgumentList "/i `"$msiPath`" /quiet /norestart" -Wait
            ok "OpenCode Desktop installed"
        } catch {
            warn "OpenCode Desktop download/install failed: $_"
        }
    } else { ok "OpenCode Desktop already installed" }
}

# ---- Obsidian via winget ----
if ($env:SKIP_OBSIDIAN -ne 'true' -and (Has-Command winget)) {
    if (-not (Test-Path "$env:LOCALAPPDATA\Obsidian\Obsidian.exe")) {
        log "Installing Obsidian..."
        winget install -e --id Obsidian.Obsidian --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) { ok "Obsidian installed" } else { warn "Obsidian install skipped (install manually)" }
    } else { ok "Obsidian already installed" }
}

# ---- Obsidian vault setup ----
if (-not (Test-Path "$ObsidianVault\.obsidian\app.json")) {
    log "Setting up Obsidian vault..."
    New-Item -ItemType Directory -Path "$ObsidianVault\.obsidian" -Force | Out-Null
    $obsidianConfig = @{
        vaultName = "llm-wiki"
        showLineNumbers = $true
        newFileLocation = "current"
        alwaysUpdateLinks = $true
        attachmentFolderPath = "./assets"
    }
    $obsidianConfig | ConvertTo-Json | Set-Content "$ObsidianVault\.obsidian\app.json" -Force
    ok "Obsidian vault configured"
}

# ---- Chrome MCP shortcut for Windows ----
$chromeMcpShortcut = "$env:USERPROFILE\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\chrome-mcp.bat"
if (-not (Test-Path $chromeMcpShortcut)) {
    $chromePath = "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"
    if (-not (Test-Path $chromePath)) {
        $chromePath = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    }
    if (Test-Path $chromePath) {
        $batContent = @"
@echo off
start "" "$chromePath" --remote-debugging-port=9222 --user-data-dir="$env:USERPROFILE\.opencode\chrome-profile-mcp"
"@
        Set-Content $chromeMcpShortcut $batContent -Force
        ok "Chrome MCP startup shortcut created"
    } else { warn "Chrome not found — install Chrome manually for MCP support" }
}

# ---- Add to PATH ----
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathsToAdd = @(
    "$env:APPDATA\npm",
    "$env:USERPROFILE\.local\bin",
    "$NovahizDir\bin"
)
foreach ($p in $pathsToAdd) {
    if ($userPath -notlike "*$p*") {
        $newVal = if ($userPath.EndsWith(';')) { "$userPath$p" } else { "$userPath;$p" }
        [Environment]::SetEnvironmentVariable("Path", $newVal, "User")
    }
}
Refresh-Path
ok "CLI tools added to PATH"

# =============================================================================
# PHASE 4: CONFIG (API keys)
# =============================================================================
header "PHASE 4/5 — Configuration"

if ($Yes) {
    log "Non-interactive mode — using defaults"
    warn "Set API keys later: opencode.json or $NovahizEnv\.env"
} else {
    $envFile = "$NovahizEnv\.env"
    if (-not (Test-Path $envFile) -or (Get-Item $envFile).Length -eq 0) {
        Write-Host ""
        wc "  Do you want to configure your OpenRouter API key now?" Yellow
        wc "  (Without it, you can still explore but agents won't run)" Yellow
        Write-Host "  Enter API key (or press Enter to skip):" -ForegroundColor Cyan
        $apiKey = Read-Host "  OpenRouter API key"

        if ($apiKey) {
            @"
# Novahiz OS — API Keys
# Generated by install.ps1 on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
OPENROUTER_API_KEY=$apiKey
"@ | Set-Content $envFile -Force
            ok "OpenRouter API key saved to $envFile"

            # Also inject into opencode.json if it exists
            $ocFile = "$NovahizDir\opencode.json"
            if (Test-Path $ocFile) {
                $oc = Get-Content $ocFile -Raw | ConvertFrom-Json
                if ($oc.api -and $oc.api.providers) {
                    foreach ($prov in $oc.api.providers) {
                        if ($prov.id -eq 'openrouter' -and -not $prov.apiKey) {
                            $prov.apiKey = "`${OPENROUTER_API_KEY}"
                        }
                    }
                    $oc | ConvertTo-Json -Depth 10 | Set-Content $ocFile -Force
                }
            }
        } else {
            warn "No API key configured — run 'nv config' later"
        }
    } else {
        ok "API keys already present"
    }
}

# =============================================================================
# PHASE 5: VALIDATION
# =============================================================================
header "PHASE 5/5 — Validation"

$errors = 0; $passed = 0
function Check($Label, $Condition) {
    if (& $Condition) { ok $Label; $script:passed++ }
    else { fail $Label; $script:errors++ }
}

Check "Python 3.10+"    { & $pyCmd -c "import sys; exit(0 if sys.version_info>=(3,10) else 1)" 2>$null }
Check "Node.js 18+"     { node -e "process.exit(Number(process.version.slice(1).split('.')[0]<18))" 2>$null }
Check "Git installed"   { (Get-Command git -ErrorAction SilentlyContinue) -ne $null }
Check "Novahiz engine"  { Test-Path "$NovahizDir\engine\__init__.py" }
Check "MCP server"      { Test-Path "$NovahizDir\mcp\novahiz-mcp.py" }
Check "Agent configs"   { Test-Path "$NovahizDir\agents\novahiz-router.yaml" }
Check "OpenCode config" { Test-Path "$NovahizDir\opencode.json" }
Check "Runtime engine"  { Test-Path "$NovahizDir\runtime\novahiz-unified.py" }
Check "Skills dir"      { (Test-Path "$NovahizDir\.agents\skills") -or (Test-Path "$NovahizDir\skills") }
Check "CLI tools"       { Test-Path "$NovahizDir\bin\nv" }
Check "OpenCode CLI"    { (Get-Command opencode -ErrorAction SilentlyContinue) -ne $null }
Check "API key file"    { (Test-Path "$NovahizEnv\.env") -and ((Get-Item "$NovahizEnv\.env").Length -gt 0) }

# Deep validation
if (Test-Path "$NovahizDir\config-wizard\final-validation.py") {
    log "Running deep validation..."
    & $pyCmd "$NovahizDir\config-wizard\final-validation.py" 2>&1
}

Write-Host ""
if ($errors -eq 0) {
    Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║  🚀 NOVAHIZ OS v6.0 — INSTALLED SUCCESSFULLY!  ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Quick start:" -ForegroundColor White
    Write-Host "    nv route 'explore this project'" -ForegroundColor Green
    Write-Host "    opencode" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Docs: $NovahizDir\docs\" -ForegroundColor White
    Write-Host "  Logs: $NovahizDir\logs\" -ForegroundColor White
    Write-Host ""
    warn "Close and re-open your terminal for PATH changes"
} else {
    Write-Host "[!] $errors checks failed, $passed passed" -ForegroundColor Yellow
    exit 1
}
