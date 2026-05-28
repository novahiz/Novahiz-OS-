# 🚀 NOVAHIZ OS v5.2 — INSTALLATION & AUTO-START GUIDE

**Version:** 5.2.0  
**Date:** 2026-05-27  
**Status:** ✅ Production Ready

---

## 📋 TABLE DES MATIÈRES

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Auto-Start Configuration](#auto-start-configuration)
4. [OpenCode Desktop Integration](#opencode-desktop-integration)
5. [Commandes Utiles](#commandes-utiles)
6. [Troubleshooting](#troubleshooting)

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    OPENCODE DESKTOP                        │
│         (Plugin Novahiz OS + MCP Server)                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ MCP Protocol
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   NOVAHIZ SERVICES                         │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Runtime Daemon  │  │ Bridge Daemon   │                  │
│  │ (LLM Executor)  │→ │ (MCP Execution) │                  │
│  └─────────────────┘  └─────────────────┘                  │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ MCP HTTP Server │  │ Task Processor  │                  │
│  │ (Port 8765)     │  │ (Fallback)      │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Multi-Provider LLM
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   LLM PROVIDERS                            │
│  • OpenRouter (Primary) — 356 modèles                      │
│  • OpenCode Zen (Fallback) — Local server                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 INSTALLATION

### Prérequis

- Python 3.10+
- OpenCode Desktop (optionnel, pour UI)
- API keys configurées

### 1. Vérifier Installation

```bash
# Vérifier scripts
ls -la ~/.opencode/scripts/novahiz-*.sh

# Vérifier MCP
ls -la ~/.opencode/mcp/*.py

# Vérifier plugin
ls -la ~/.opencode/plugins/novahiz-plugin/
```

### 2. Configurer API Keys

```bash
# Les keys sont dans ~/.opencode/runtime/config.json
# Export automatique via setup-env.sh
source ~/.opencode/scripts/setup-env.sh
```

### 3. Tester Installation

```bash
# Démarrer tous les services
~/.opencode/scripts/novahiz-autostart.sh

# Vérifier status
~/.opencode/scripts/novahiz-status-all.sh

# Ou via CLI
nv status
```

---

## ⚡ AUTO-START CONFIGURATION

### Method 1: Bash Hook (Recommandé)

Déjà configuré dans `~/.bashrc`:

```bash
# Novahiz OS Auto-Start
if [ -f ~/.opencode/scripts/novahiz-autostart.sh ]; then
    if ! pgrep -f 'novahiz-runtime.py' > /dev/null 2>&1; then
        ~/.opencode/scripts/novahiz-autostart.sh > /dev/null 2>&1 &
    fi
fi
```

**Comportement:**
- ✅ Démarre automatiquement à l'ouverture d'un terminal
- ✅ Vérifie si services déjà running (évite doublons)
- ✅ Silencieux (logs dans `~/.opencode/logs/autostart.log`)

### Method 2: OpenCode Startup Hook

Dans `~/.opencode/opencode.json`:

```json
{
  "plugins": {
    "novahiz-os": {
      "name": "Novahiz OS",
      "enabled": true,
      "autoStart": true
    }
  }
}
```

### Method 3: Systemd (Linux)

```bash
# Créer service systemd
sudo nano /etc/systemd/system/novahiz-os.service
```

```ini
[Unit]
Description=Novahiz OS Services
After=network.target

[Service]
Type=forking
User=novahiz
ExecStart=/home/novahiz/.opencode/scripts/novahiz-autostart.sh
ExecStop=/home/novahiz/.opencode/scripts/novahiz-stop.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Activer
sudo systemctl enable novahiz-os
sudo systemctl start novahiz-os
```

---

## 🖥️ OPENCODE DESKTOP INTEGRATION

### 1. MCP Server Configuration

Dans `~/.opencode/opencode.json`:

```json
{
  "mcp": {
    "novahiz": {
      "type": "local",
      "command": "python3",
      "args": ["/home/novahiz/.opencode/mcp/novahiz-mcp.py", "--mcp"],
      "enabled": true
    },
    "novahiz-http": {
      "type": "sse",
      "url": "http://127.0.0.1:8765/sse",
      "enabled": true
    }
  }
}
```

### 2. Plugin Installation

Le plugin est dans `~/.opencode/plugins/novahiz-plugin/`

**Structure:**
```
novahiz-plugin/
├── package.json       # Plugin manifest
├── index.js          # Main plugin code
└── icons/
    └── novahiz-icon.svg
```

### 3. Activer dans OpenCode Desktop

1. Ouvrir OpenCode Desktop
2. Settings → Plugins
3. Chercher "Novahiz OS"
4. Click "Enable"
5. Redémarrer OpenCode

### 4. Commands Disponibles

| Command | Description |
|---------|-------------|
| `Novahiz: Route task to optimal agent` | Route vers le meilleur agent |
| `Novahiz: Auto-route and execute` | Route + exécute automatiquement |
| `Novahiz: Execute with specific agent` | Exécute avec agent spécifique |
| `Novahiz: List all agents` | Liste les 22 agents |
| `Novahiz: Search agents` | Recherche par keyword |
| `Novahiz: System health check` | Check santé système |
| `Novahiz: Show service status` | Status des services |

---

## 💻 COMMANDES UTILES

### CLI Commands

```bash
# Démarrer tous les services
~/.opencode/scripts/novahiz-autostart.sh

# Arrêter tous les services
~/.opencode/scripts/novahiz-stop.sh

# Voir status
~/.opencode/scripts/novahiz-status-all.sh

# Via nv CLI
nv status              # Runtime status
nv config models       # Model configuration
nv config providers    # Provider configuration
nv run "task"          # Route + execute
nv agents              # List agents
```

### Direct Commands

```bash
# Runtime
python3 ~/.opencode/runtime/novahiz-runtime.py status
python3 ~/.opencode/runtime/novahiz-runtime.py daemon 3

# Bridge
python3 ~/.opencode/mcp/opencode-bridge.py daemon 2

# MCP HTTP
python3 ~/.opencode/mcp/novahiz-mcp-http.py

# Task Processor
python3 ~/.opencode/mcp/task-processor.py daemon 5
```

### Logs

```bash
# Voir logs en temps réel
tail -f ~/.opencode/logs/autostart.log
tail -f ~/.opencode/logs/runtime-daemon.log
tail -f ~/.opencode/logs/opencode-bridge.log
tail -f ~/.opencode/logs/mcp-http.log
```

---

## 🐛 TROUBLESHOOTING

### Services ne démarrent pas

```bash
# 1. Vérifier processes existants
ps aux | grep novahiz | grep -v grep

# 2. Kill tous les processes
pkill -f novahiz-runtime
pkill -f opencode-bridge
pkill -f novahiz-mcp

# 3. Nettoyer PID files
rm ~/.opencode/pids/*.pid

# 4. Redémarrer
~/.opencode/scripts/novahiz-autostart.sh
```

### MCP not responding

```bash
# Check HTTP server
curl http://127.0.0.1:8765/health

# Restart MCP
pkill -f novahiz-mcp-http
python3 ~/.opencode/mcp/novahiz-mcp-http.py &
```

### Executions sans provider/model

**Problème:** Bridge daemon ne tourne pas

```bash
# Vérifier
ps aux | grep opencode-bridge

# Si pas running
python3 ~/.opencode/mcp/opencode-bridge.py daemon 2 > ~/.opencode/logs/opencode-bridge.log 2>&1 &
```

### API Keys missing

```bash
# Re-export
source ~/.opencode/scripts/setup-env.sh

# Vérifier
echo $OPENROUTER_API_KEY
echo $OPENCODE_ZEN_API_KEY
```

---

## 📊 SERVICE STATUS

### Expected State

```
● Novahiz Runtime     running (PID: XXXXX)
● OpenCode Bridge     running (PID: XXXXX)
● MCP HTTP Server     running (PID: XXXXX)
● Task Processor      running (PID: XXXXX)

Services: 4/4 running
Status: ● All systems operational
```

### Check Commands

```bash
# Quick check
~/.opencode/scripts/novahiz-status-all.sh

# Detailed
ps aux | grep -E "novahiz|opencode" | grep -v grep

# PID files
cat ~/.opencode/pids/*.pid
```

---

## 🎯 PRODUCTION CHECKLIST

- [ ] API keys configurées dans `config.json`
- [ ] Auto-start hook dans `.bashrc`
- [ ] MCP configuré dans `opencode.json`
- [ ] Plugin installé dans `plugins/`
- [ ] Services démarrent automatiquement
- [ ] Logs surveillés (`logs/` directory)
- [ ] PID files propres (`pids/` directory)
- [ ] Test exécution réelle fait

---

## 📞 SUPPORT

- **Logs:** `~/.opencode/logs/`
- **Config:** `~/.opencode/runtime/config.json`
- **Scripts:** `~/.opencode/scripts/`
- **Plugin:** `~/.opencode/plugins/novahiz-plugin/`

---

[Executed by: Novahiz Router]
[Agent: novahiz-router]
[Timestamp: 02:26:00]
