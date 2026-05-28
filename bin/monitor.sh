#!/bin/bash
# NovaHiz OS - System Monitor

NOVAHIZ_HOME="$HOME/.opencode"
API_URL="http://localhost:8080"
CHROME_PORT=9222

echo "╔════════════════════════════════════════════╗"
echo "║     NOVAHIZ OS - System Monitor v1.7      ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check API Server
if curl -s "$API_URL/api/health" | grep -q "healthy"; then
    echo "✓ API Server: Running ($API_URL)"
else
    echo "✗ API Server: DOWN"
fi

# Check Chrome MCP
if ps aux | grep -q "chrome-devtools-mcp"; then
    echo "✓ Chrome MCP: Running (port $CHROME_PORT)"
else
    echo "✗ Chrome MCP: DOWN"
fi

# Check processes
echo ""
echo "Active Processes:"
ps aux | grep -E "(server.py|chrome-devtools-mcp)" | grep -v grep | awk '{print "  └─ " $11 " (PID: " $2 ")"}'

# Disk usage
echo ""
echo "Storage:"
du -sh "$NOVAHIZ_HOME" 2>/dev/null | awk '{print "  └─ Novahiz Home: " $1}'

# Recent logs
echo ""
echo "Recent Activity:"
tail -3 "$NOVAHIZ_HOME/logs/novahiz.log" 2>/dev/null | sed 's/^/  └─ /'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
