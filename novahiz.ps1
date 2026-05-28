$novahizDir = "$HOME\.opencode"
$cliScript = "$novahizDir\scripts\novahiz-cli.py"

$env:PYTHONIOENCODING = "utf-8"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

# ---- Auto-launch Chrome MCP (skip for stop commands) ----
$cmd = $args[0]
if ($cmd -ne "chrome-stop" -and $cmd -ne "chrome-start") {
    $bootFlag = "$novahizDir\data\.chrome-boot-done"
    if (-not (Test-Path $bootFlag)) {
        $null = & "$novahizDir\scripts\launch-chrome-mcp.ps1" -Quiet 2>&1
        $null = New-Item -ItemType File -Path $bootFlag -Force
    }
}

# ---- Chrome MCP commands handled natively ----
switch ($cmd) {
    "chrome-start" {
        if ($args.Count -gt 1) { & "$novahizDir\scripts\launch-chrome-mcp.ps1" $args[1..($args.Count - 1)] }
        else { & "$novahizDir\scripts\launch-chrome-mcp.ps1" }
        return
    }
    "chrome-stop" {
        if ($args.Count -gt 1) { & "$novahizDir\scripts\stop-chrome-mcp.ps1" $args[1..($args.Count - 1)] }
        else { & "$novahizDir\scripts\stop-chrome-mcp.ps1" }
        return
    }
    "chrome-status" {
        if ($args.Count -gt 1) { & "$novahizDir\scripts\chrome-status.ps1" $args[1..($args.Count - 1)] }
        else { & "$novahizDir\scripts\chrome-status.ps1" }
        return
    }
}

$pythonExe = $null
$pyCmd = Get-Command "python3" -ErrorAction SilentlyContinue
if (-not $pyCmd) { $pyCmd = Get-Command "python" -ErrorAction SilentlyContinue }
if (-not $pyCmd) { $pyCmd = Get-Command "py" -ErrorAction SilentlyContinue }
if ($pyCmd) { $pythonExe = $pyCmd.Source }

if (!$pythonExe) {
    Write-Host "Python not found. Install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

& $pythonExe -X utf8 $cliScript @args
