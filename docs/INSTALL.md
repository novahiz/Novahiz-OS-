# Novahiz OS — Installation Guide

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash
```

### Non-interactive mode (no API key prompt)

```bash
curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash -s -- --yes
```

### Skip optional components

```bash
curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash -s -- --no-obsidian --no-desktop
```

---

## Prerequisites (auto-installed)

The installer will **automatically** install any missing:

| Software | Min version | Installed via |
|----------|-------------|--------------|
| Python 3 | 3.10 | apt/dnf/pacman/brew/winget |
| Node.js | 18 | apt/dnf/pacman/brew/winget |
| Git | latest | apt/dnf/pacman/brew/winget |
| curl | latest | apt/dnf/pacman/brew/winget |

---

## What gets installed

| Component | Details |
|-----------|---------|
| **OpenCode CLI** | `@opencode-ai/cli` global npm package |
| **OpenCode Desktop** | GUI application for your OS |
| **Obsidian** | Note-taking app + 3 plugins (Dataview, Templater, Kanban) |
| **Chrome MCP** | Browser automation via DevTools protocol |
| **Novahiz Engine** | 12 modules: routing, scoring, execution, plugin system, learning |
| **Novahiz Runtime** | Daemon, rate limiter, observer, state management |
| **MCP Servers** | 7 servers: novahiz, obsidian, tradingview, stitch, supabase, monitoring, bridge |
| **64 Skills** | Browser automation, API design, canvas, SEO, security, testing, etc. |
| **24 Agents** | Architecture, design, security, database, marketing, etc. |
| **CLI Tools** | 15 commands: `nv`, `novahiz`, `nv-route`, `nv-exec`, etc. |
| **Systemd Services** | Auto-start at boot (Linux only) |
| **Dashboard** | Status page + daily metrics |
| **Obsidian Vault** | Pre-configured LLM wiki at `~/Documents/llm-wiki/` |

---

## Configuration Wizard

During install, you'll be prompted for:

1. **OpenRouter API Key** (REQUIRED) — [Get one free](https://openrouter.ai/keys)
2. **OpenCode Zen API Key** (optional)
3. **Supabase Access Token** (optional)
4. **GitHub Token** (optional)

Keys are stored encrypted at `~/.novahiz/.env` (chmod 600).

---

## After Installation

```bash
# Route a task to the best agent
nv route "explore this project"

# List all 24 agents
nv agents

# System health check
nv health

# Launch OpenCode
opencode

# Launch Obsidian vault
obsidian ~/Documents/llm-wiki/
```

---

## Flags

| Flag | Description |
|------|-------------|
| `--yes` / `-y` | Non-interactive, skip prompts |
| `--quiet` / `-q` | Minimal output |
| `--no-obsidian` | Skip Obsidian installation |
| `--no-desktop` | Skip OpenCode Desktop |
| `--verbose` / `-v` | Detailed logs |

---

## Windows

On Windows 10/11, run **PowerShell as Administrator**:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
iex ((New-Object System.Net.WebClient).DownloadString("https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.ps1"))
```

---

## Troubleshooting

### Install fails
```bash
# Retry with verbose logs
curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash -s -- --verbose

# Check install log
cat ~/.opencode/logs/install.log
```

### MCP not connecting
```bash
# Verify MCP server
python3 ~/.opencode/mcp/novahiz-mcp.py --mcp

# Check opencode.json
cat ~/.opencode/opencode.json | python3 -m json.tool
```

### Re-run config wizard
```bash
bash ~/.opencode/config-wizard/wizard.sh
```

### Uninstall
```bash
rm -rf ~/.opencode ~/.novahiz ~/Documents/llm-wiki
# Remove from ~/.bashrc lines containing .local/bin and novahiz
```
