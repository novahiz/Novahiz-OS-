<div align="center">
  <h1>🚀 Novahiz OS v6.1</h1>
  <p><strong>Multi-Agent Orchestration System for AI Development</strong></p>
  <p>
    <a href="https://github.com/novahiz/Novahiz-OS-">
      <img src="https://img.shields.io/badge/version-6.1.0-blue?style=flat-square" alt="Version">
    </a>
    <a href="https://github.com/novahiz/Novahiz-OS-/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
    </a>
    <img src="https://img.shields.io/badge/status-production%20grade-success?style=flat-square" alt="Status">
    <img src="https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20WSL-orange?style=flat-square" alt="Platform">
    <img src="https://img.shields.io/badge/runtime-OpenCode%20Only-7c5cfc?style=flat-square" alt="Runtime">
    <img src="https://img.shields.io/badge/agents-24-orange?style=flat-square" alt="Agents">
    <img src="https://img.shields.io/badge/skills-76-purple?style=flat-square" alt="Skills">
  </p>
</div>

---

## ⚡ One-Line Install

### Linux / macOS

```bash
# Clone and install
git clone https://github.com/novahiz/Novahiz-OS- ~/.opencode && ~/.opencode/installers/01-install-deps.sh
```

### Windows (WSL Required)

Novahiz OS requires WSL. You have two options:

**Option 1: PowerShell Bootstrap (Recommended)**
```powershell
# Run as Administrator — installs WSL + Novahiz OS automatically
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((Invoke-RestMethod 'https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.ps1'))"
```

**Option 2: Manual WSL Setup**
```powershell
# 1. Install WSL (restart required)
wsl --install

# 2. After restart, open WSL and run:
curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash
```

> Detects your OS, installs prerequisites (Python 3.10+, Node.js 18+, Git), clones the system, patches paths, and runs the interactive config wizard.
>
> Note: The `curl | bash` one-liner is for published releases. For local development, use `git clone` or copy the `installers/` directory.

---

## ✨ Overview

Novahiz OS turns **any AI coding agent** into a coordinated multi-agent workforce. It provides 24 specialized agents, 76+ skills, and 6 MCP servers that work together — routing tasks to the right expert agent automatically.

> **⚠️ Important Requirements:**
> - **Runtime:** Novahiz OS is **OpenCode Only** — requires the OpenCode framework
> - **Windows:** Requires **WSL (Windows Subsystem for Linux)** — native Windows is not supported
> - **Linux/macOS:** Works natively

### What makes it different?

| Feature | Description |
|---------|-------------|
| **Smart Router** | Routes each task to the optimal agent based on domain, complexity, and budget |
| **24 Specialized Agents** | From architecture (Arthur) to security (Neo) to design (Luna) |
| **76+ Skills** | Reusable capabilities from brainstorming to deployment |
| **6 MCP Servers** | Chrome DevTools, Novahiz OS, Obsidian wiki, Google Stitch, TradingView, Supabase |
| **Self-Healing** | Auto-detects and fixes engine errors at runtime |
| **Cross-Platform** | Linux, macOS, Windows — same experience everywhere |
| **One Command Install** | `curl | bash` or `iex ((Invoke-RestMethod ...))` |
| **CI/CD Ready** | GitHub Actions, pre-commit hooks, health checks built in |

---

## 🧠 Agent Roster (24)

| Agent | Domain | Model |
|-------|--------|-------|
| Arthur | Architecture | Claude 3.5 Sonnet |
| Athena | Initialization | Claude 3.5 Sonnet |
| Atlas | Memory | Claude 3.5 Sonnet |
| Elias | Marketing | Claude 3.5 Sonnet |
| Kenzo | Performance | Claude 3.5 Sonnet |
| Luna | Design | Claude 3.5 Sonnet |
| Malik | Database | Claude 3.5 Sonnet |
| Neo | Security | Claude 3.5 Sonnet |
| Ralph | Browser/Execution | Claude 3.5 Sonnet |
| Sarah | Quality/Testing | Claude 3.5 Sonnet |
| Victor | Strategy | Claude 3.5 Sonnet |
| Cipher | Cryptography | Qwen 3.6 Plus |
| Forge | CI/CD | Qwen 3.5 Plus |
| Ghost | Stealth | Qwen 3.5 Plus |
| Nexus | API | Qwen 3.5 Plus |
| Orion | DevOps | Qwen 3.5 Plus |
| Phoenix | Crisis | Qwen 3.5 Plus |
| Pulse | Realtime | Qwen 3.5 Plus |
| Ryu | Design | Qwen 3.5 Plus |
| Samuel | Legal | Qwen 3.5 Plus |
| Simon | Data | Qwen 3.5 Plus |
| Vega | Legal | Qwen 3.5 Plus |
| Novahiz | Router (primary) | Claude 3.5 Sonnet |

---

## 🛠️ MCP Servers

| Server | Purpose |
|--------|---------|
| `novahiz-mcp.py` | Core MCP — agent routing, task execution |
| `novahiz-mcp-http.py` | HTTP transport layer |
| `opencode-bridge.py` | OpenCode ↔ Novahiz bridge |
| `monitoring-mcp.py` | Health monitoring & metrics |
| `stitch-mcp-wrapper.py` | Google Stitch UI generation |
| `task-processor.py` | Async task queue |
| `tradingview-mcp/` | TradingView chart automation |

---

## 📦 Project Structure

```
~/.opencode/
├── agents/          # 24 agent YAML configs + markdown docs
├── bin/             # CLI tools (nv, nv-route, nv-exec, ...)
├── config/          # model-router.json, agent-registry.json, scoreboard.json
├── config-wizard/   # Interactive API key + model setup
├── engine/          # Router, executor, registry, scoring, learning
├── installers/      # 13 modular component installers
├── mcp/             # 7 MCP servers + TradingView MCP
├── memory/          # Context, sessions, agent logs, decisions
├── plugins/         # Plugin system (novahiz-plugin, auto-executor)
├── runtime/         # Unified runtime, daemon, rate limiter
├── scripts/         # 60+ utility scripts
├── skills/          # 64 reusable skill packages
├── systemd/         # Service files for Linux
├── docs/            # Full documentation
└── install.sh       # Entry point (curl | bash)
```

---

## 🚦 Quick Start

```bash
# After installation, use the CLI:
nv route "explore this project"    # Route a task to the right agent
nv health                          # System health check
nv agents                          # List all agents
nv doctor                          # Diagnostics
opencode                           # Launch OpenCode with Novahiz
```

### Configure API Keys

```bash
# Interactive wizard:
nv config

# Or manually:
nano ~/.novahiz/.env
# Add: OPENROUTER_API_KEY=sk-or-...
```

---

## 📚 Documentation

| Resource | Link |
|----------|------|
| Full Documentation | `~/.opencode/docs/INSTALL.md` |
| Architecture Guide | `~/.opencode/docs/ARCHITECTURE.md` |
| API Reference | `~/.opencode/docs/API.md` |
| Deployment Guide | `~/.opencode/docs/DEPLOYMENT.md` |
| Recovery Guide | `~/.opencode/docs/RECOVERY.md` |

---

## 🤝 Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

All contributors must sign the [CLA](./docs/legal/CLA_TEMPLATE.md).

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](./LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ by the Novahiz team</sub>
</div>
