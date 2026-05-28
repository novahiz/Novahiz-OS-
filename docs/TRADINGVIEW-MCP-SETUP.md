# TradingView MCP - NovaHiz OS Integration

## ✅ Installation Complete

### Configuration

**File:** `~/.opencode/opencode.json`

```json
{
  "mcp": {
    "tradingview": {
      "type": "local",
      "command": "node",
      "args": ["/home/novahiz/.opencode/mcp/tradingview-mcp/versions/v1/src/server.js"],
      "enabled": true
    }
  }
}
```

### Files Installed

| File | Purpose |
|------|---------|
| `/home/novahiz/.opencode/mcp/tradingview-mcp/` | TradingView MCP server (81 tools) |
| `/home/novahiz/.opencode/bin/launch-tradingview.sh` | Launch script with CDP port 9222 |

### 81 MCP Tools Available

**Core Tools (78):**
- Chart control: `chart_save`, `chart_load`, `chart_reset`
- Indicators: `indicator_add`, `indicator_remove`, `indicator_config`
- Symbols: `symbol_search`, `symbol_set`, `symbol_info`
- UI: `ui_open_panel`, `ui_click`, `ui_type`
- Pine Script: `pine_create`, `pine_run`, `pine_compile`
- Alerts: `alert_create`, `alert_list`, `alert_delete`
- Screenshots: `screenshot_take`, `screenshot_save`

**Morning Brief Tools (3):**
- `morning_brief` - Scan watchlist, read indicators, generate session bias
- `session_save` - Save daily brief to `~/.tradingview-mcp/sessions/`
- `session_get` - Compare today vs yesterday

---

## 🚀 Usage

### 1. Launch TradingView Desktop with Debug Port

```bash
./home/novahiz/.opencode/bin/launch-tradingview.sh
```

Or manually:
```bash
/path/to/TradingView --remote-debugging-port=9222
```

### 2. Restart OpenCode

```bash
# OpenCode will auto-load MCP servers on restart
```

### 3. Use in Chat

```
List my TradingView watchlist
Add RSI indicator to current chart
Save current chart layout
Run morning brief
```

---

## ⚠️ Requirements

| Requirement | Status |
|-------------|--------|
| TradingView Desktop (paid subscription) | ✅ Installé (`/opt/TradingView/tradingview`) |
| Node.js 18+ | ✅ v22.22.1 |
| Port 9222 available | ✅ Ready |
| TradingView MCP server | ✅ Installed |
| GPU flags (Linux) | ✅ `--disable-gpu --no-sandbox` |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| `cdp_connected: false` | Run `launch-tradingview.sh` to start TV with debug port |
| `ECONNREFUSED` | TradingView not running or port 9222 blocked |
| MCP tools not showing | Restart OpenCode, check `opencode.json` syntax |
| Tools return stale data | Wait for TradingView to finish loading |
| Pine Editor tools fail | Open Pine Editor panel first |

---

## 📊 NovaHiz Agents Integration

| Agent | TradingView Use Case |
|-------|---------------------|
| `simon-data` | Market data analysis, screener |
| `kenzo-performance` | Portfolio performance, backtesting |
| `victor-strategy` | Trading strategies, risk management |
| `nexus-api` | Financial data streams |
| `phoenix-crisis` | Crash alerts, volatility spikes |

---

## Architecture

```
OpenCode (opencode.json)
    ↓
MCP Servers:
├── novahiz (stdio) → NovaHiz Router + 24 agents
├── tradingview (stdio) → 81 TradingView tools
└── supabase (stdio) → Database

TradingView Desktop (Electron)
    ↓
Chrome DevTools Protocol (port 9222)
    ↓
MCP Server (node server.js)
```

---

**Setup Date:** 2026-05-28
**Status:** ✅ Ready to use (pending TradingView Desktop installation)
