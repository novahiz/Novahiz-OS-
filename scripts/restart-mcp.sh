#!/bin/bash
# Restart Novahiz MCP Server

echo "🔄 Restarting Novahiz MCP..."

# Kill old processes
pkill -f "novahiz-mcp" 2>/dev/null
sleep 1

# Clear old logs
> ~/.opencode/logs/mcp-server-v4.log 2>/dev/null

# Test MCP startup
cd ~/.opencode
timeout 3 python3 mcp/novahiz-mcp.py --mcp 2>&1 | head -5

if [ $? -eq 124 ]; then
    echo "✅ MCP server starts correctly (timeout expected)"
else
    echo "❌ MCP server failed to start"
    cat ~/.opencode/logs/mcp-server-v4.log | tail -10
fi

echo ""
echo "Next: Restart opencode to reload MCP"
