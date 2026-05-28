# NovaHiz OS — Port Registry

**Last Updated:** 2026-05-27  
**Purpose:** Single source of truth for all port assignments to prevent conflicts

---

## Port Assignments

| Port | Service | Protocol | Status | Notes |
|------|---------|----------|--------|-------|
| `3000` | Vite Dev Server | HTTP | Optional | Odjuayé frontend dev |
| `5173` | Vite Default | HTTP | Available | Fallback if 3000 busy |
| `8080` | NovaHiz API Server | HTTP | Reserved | Main API endpoint |
| `8765` | NovaHiz MCP HTTP | HTTP | **ACTIVE** | Primary MCP REST API |
| `8766` | NovaHiz MCP WebSocket | WS | **ACTIVE** | WebSocket MCP server |
| `9080` | Log Aggregator | HTTP | Reserved | Centralized logging |
| `9222` | Chrome Debugging | CDP | Optional | Remote debugging port |

---

## Current Status

```bash
# Check all NovaHiz ports
$ netstat -tlnp | grep -E "3000|5173|8080|8765|8766|9080|9222"

# Expected output (when all services running):
LISTEN  0  511  127.0.0.1:8765  0.0.0.0:*  users:(("python3",pid=XXXX,fd=X))  # MCP HTTP
LISTEN  0  511  127.0.0.1:8766  0.0.0.0:*  users:(("python3",pid=XXXX,fd=X))  # MCP WS
```

---

## Service Scripts

### MCP HTTP Server
```bash
python3 ~/.opencode/mcp/novahiz-mcp-http.py
# Port: 8765
# Health: curl http://127.0.0.1:8765/health
```

### MCP WebSocket Server
```bash
python3 ~/.opencode/mcp/novahiz-mcp-ws.py
# Port: 8766
# Health: curl http://127.0.0.1:8766/health
```

### MCP Stdio (for OpenCode)
```bash
python3 ~/.opencode/mcp/novahiz-mcp.py --mcp
# No network port (stdio transport)
```

### Monitoring MCP
```bash
python3 ~/.opencode/mcp/monitoring-mcp.py
# No network port (stdio transport)
```

### API Server
```bash
python3 ~/.opencode/scripts/python/novahiz-api.py
# Port: 8080
# Health: curl http://127.0.0.1:8080/api/health
```

### Chrome MCP
```bash
./bin/monitor.sh start
# Port: 9222 (Chrome remote debugging)
```

---

## Conflict Resolution

### If port conflict detected:

1. **Check what's using the port:**
   ```bash
   lsof -i :<PORT>
   # or
   netstat -tlnp | grep <PORT>
   ```

2. **Kill the conflicting process:**
   ```bash
   kill <PID>
   # or force kill
   kill -9 <PID>
   ```

3. **Restart the service:**
   ```bash
   # Example for MCP HTTP
   python3 ~/.opencode/mcp/novahiz-mcp-http.py &
   ```

---

## Configuration Files

| File | Port Config |
|------|-------------|
| `~/.opencode/mcp/novahiz-mcp-http.py` | `PORT = 8765` |
| `~/.opencode/mcp/novahiz-mcp-ws.py` | `PORT = 8766` |
| `~/.opencode/scripts/python/novahiz-api.py` | `"port": 8080` |
| `~/.opencode/bin/monitor.sh` | `CHROME_PORT=9222` |
| `~/.opencode/scripts/autoheal.py` | `CHROME_PORT = 9222` |
| `~/.opencode/opencode.json` | MCP config (stdio) |

---

## Environment Variables

```bash
# Add to ~/.opencode/.env or .env.local
NOVAHIZ_MCP_HTTP_PORT=8765
NOVAHIZ_MCP_WS_PORT=8766
NOVAHIZ_API_PORT=8080
CHROME_DEBUG_PORT=9222
```

---

## Firewall Rules (if needed)

```bash
# Allow local MCP connections
sudo ufw allow from 127.0.0.1 to any port 8765
sudo ufw allow from 127.0.0.1 to any port 8766
sudo ufw allow from 127.0.0.1 to any port 8080
```

---

## Quick Health Check Script

```bash
#!/bin/bash
# ~/.opencode/bin/check-ports.sh

echo "=== NovaHiz Port Health Check ==="

check_port() {
    local port=$1
    local name=$2
    if lsof -i :$port > /dev/null 2>&1; then
        echo "✓ $name (:$port) - RUNNING"
    else
        echo "✗ $name (:$port) - NOT RUNNING"
    fi
}

check_port 8765 "MCP HTTP"
check_port 8766 "MCP WebSocket"
check_port 8080 "API Server"
check_port 9222 "Chrome Debug"
check_port 3000 "Vite Dev"
```

---

## Change History

| Date | Change | Reason |
|------|--------|--------|
| 2026-05-27 | WS port 8765 → 8766 | Resolve conflict with HTTP server |

---

**NOTE:** Any new service MUST register its port here before deployment to prevent conflicts.
