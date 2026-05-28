# 🚀 NOVAHIZ OS v6.0

**Long Term Stability Release**  
**Version:** 6.0.0  
**Status:** ✅ Production Ready

---

## 📋 TABLE DES MATIÈRES

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [Architecture](#architecture)
5. [Maintenance](#maintenance)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 INSTALLATION

### Prérequis

- Python 3.10+
- OpenCode (optional, for desktop integration)
- API keys (OpenRouter, OpenCode Zen)

### Quick Start

```bash
# 1. Clone/setup
cd ~/.opencode

# 2. Configure environment
cp ~/.opencode/.env.example ~/.novahiz/.env
# Edit ~/.novahiz/.env with your API keys

# 3. Install dependencies (optional)
pip install -r requirements.txt

# 4. Start services
./scripts/novahiz-autostart.sh

# 5. Verify
nv health
```

---

## ⚙️ CONFIGURATION

### Environment Variables

**File:** `~/.novahiz/.env`

```bash
# API Keys (required)
OPENROUTER_API_KEY="sk-or-..."
OPENCODE_ZEN_API_KEY="sk-..."

# Optional
NOVAHIZ_LOG_LEVEL="INFO"
NOVAHIZ_MAX_CONCURRENT="5"
NOVAHIZ_TIMEOUT="120"
```

### Config Files

| File | Purpose |
|------|---------|
| `~/.novahiz/.env` | Environment variables (secrets) |
| `~/.opencode/runtime/config.json` | Runtime configuration |
| `~/.config/opencode/opencode.jsonc` | OpenCode integration |

---

## 💻 USAGE

### CLI Commands

```bash
# Health & Status
nv health              # System health check
nv status              # Runtime status
nv metrics             # Usage statistics
nv metrics today       # Last 24h
nv metrics week        # Last 168h

# Execution
nv run "task"          # Route + execute
nv agents              # List all agents
nv search "keyword"    # Search agents

# Configuration
nv config models       # Model configuration
nv config providers    # Provider configuration

# Services
novahiz-autostart.sh   # Start all services
novahiz-stop.sh        # Stop all services
```

### OpenCode Desktop

After configuration, use in chat:
```
@novahiz_list_agents
@novahiz_auto task="Build API"
```

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                    OPENCODE DESKTOP                     │
│              (MCP Client + Plugin UI)                   │
└─────────────────────────────────────────────────────────┘
                            │
                            │ MCP Protocol
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   NOVAHIZ SERVICES                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Runtime   │  │   Bridge    │  │  MCP HTTP   │     │
│  │   Daemon    │  │   Daemon    │  │   Server    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│  ┌─────────────┐  ┌─────────────┐                       │
│  │    Task     │  │   Metrics   │                       │
│  │  Processor  │  │  Collector  │                       │
│  └─────────────┘  └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
                            │
                            │ Multi-Provider LLM
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   LLM PROVIDERS                         │
│  • OpenRouter (Primary) — 356+ modèles                  │
│  • OpenCode Zen (Fallback) — Local server               │
└─────────────────────────────────────────────────────────┘
```

### Components

| Component | File | Purpose |
|-----------|------|---------|
| Runtime | `runtime/novahiz-runtime.py` | LLM execution with fallbacks |
| Bridge | `mcp/opencode-bridge.py` | MCP ↔ Runtime bridge |
| MCP HTTP | `mcp/novahiz-mcp-http.py` | HTTP API server |
| MCP Server | `mcp/novahiz-mcp.py` | MCP protocol server |
| Metrics | `metrics/metrics.py` | Usage tracking |
| CLI | `bin/novahiz` | Command-line interface |

---

## 🔧 MAINTENANCE

### Daily Operations

```bash
# Check health
nv health

# View metrics
nv metrics today

# Check logs
tail -f ~/.opencode/logs/opencode-bridge.log
```

### Weekly Maintenance

```bash
# Rotate logs
logrotate -f ~/.opencode/logs/logrotate.conf

# Clear old executions
find ~/.opencode/executions -name "exec_*.json" -mtime +7 -delete

# Update metrics backup
cp ~/.opencode/metrics/usage.json ~/.opencode/metrics/usage.json.backup
```

### Monthly Maintenance

```bash
# Run full test suite
cd ~/.opencode/tests && python3 test_novahiz.py && ./run-integration-tests.sh

# Check for updates
git pull origin main  # If using git

# Review error logs
grep "ERROR" ~/.opencode/logs/*.log | tail -50
```

### Systemd Services (Production)

```bash
# Install services
sudo cp ~/.opencode/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable novahiz-runtime novahiz-bridge
sudo systemctl start novahiz-runtime novahiz-bridge

# Check status
systemctl status novahiz-runtime
systemctl status novahiz-bridge

# View logs
journalctl -u novahiz-runtime -f
journalctl -u novahiz-bridge -f
```

---

## 🐛 TROUBLESHOOTING

### Services Not Starting

```bash
# Check if running
ps aux | grep novahiz

# Stop all
novahiz-stop.sh

# Start all
novahiz-autostart.sh

# Check logs
tail -100 ~/.opencode/logs/autostart.log
```

### API Key Issues

```bash
# Verify .env exists
ls -la ~/.novahiz/.env

# Source environment
source ~/.novahiz/.env

# Verify keys loaded
echo $OPENROUTER_API_KEY | cut -c1-20
```

### MCP Not Appearing in OpenCode

1. Check config: `cat ~/.config/opencode/opencode.jsonc`
2. Verify MCP server: `python3 ~/.opencode/mcp/novahiz-mcp.py --mcp`
3. Restart OpenCode Desktop

### High Memory Usage

```bash
# Check memory
ps aux | grep novahiz | awk '{print $6/1024 " MB - " $11}'

# Restart services
novahiz-stop.sh && novahiz-autostart.sh

# Clear metrics cache
rm ~/.opencode/metrics/usage.json
```

---

## 📞 SUPPORT

**Documentation:** `~/.opencode/README.md`  
**Logs:** `~/.opencode/logs/`  
**Tests:** `~/.opencode/tests/`  
**Version:** See `~/.opencode/VERSION`

---

[Novahiz OS v6.0 — Long Term Stability]

---

## 🔧 OPTIONAL: Install Linters

**Note:** Linters are optional for development. Novahiz OS runs without them.

```bash
# Install pip if missing
sudo apt-get install -y python3-pip  # Debian/Ubuntu

# Install linters
pip3 install black flake8 pylint coverage

# Run linters
cd ~/.opencode
black mcp/*.py runtime/*.py --check
flake8 mcp/*.py runtime/*.py

# Run coverage
cd tests
./run-coverage.sh
```

---

