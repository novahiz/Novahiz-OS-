#!/bin/bash
# NovaHiz OS — Port Conflict Verification

echo "=== NovaHiz Port Verification ==="
echo "Date: $(date)"
echo ""

CONFLICTS=0

# Check for duplicate port definitions
echo "1. Checking for port conflicts in MCP files..."
HTTP_PORT=$(grep "^PORT\s*=" ~/.opencode/mcp/novahiz-mcp-http.py | awk -F= '{print $2}' | tr -d ' ')
WS_PORT=$(grep "^PORT\s*=" ~/.opencode/mcp/novahiz-mcp-ws.py | awk -F= '{print $2}' | tr -d ' ')

if [ "$HTTP_PORT" = "$WS_PORT" ]; then
    echo "   ❌ CONFLICT: HTTP and WS both use port $HTTP_PORT"
    CONFLICTS=$((CONFLICTS + 1))
else
    echo "   ✓ HTTP: $HTTP_PORT, WS: $WS_PORT (no conflict)"
fi

# Check what's actually listening
echo ""
echo "2. Checking active listeners..."
for port in 8765 8766 8080 9222 3000; do
    if lsof -i :$port > /dev/null 2>&1; then
        PID=$(lsof -i :$port -t)
        echo "   ✓ Port $port: IN USE (PID: $PID)"
    else
        echo "   - Port $port: FREE"
    fi
done

# Verify config consistency
echo ""
echo "3. Verifying config consistency..."
if grep -q "localhost:8765" ~/.opencode/mcp/novahiz-mcp-ws.py; then
    echo "   ⚠ Warning: WS file still references 8765 in comments/docs"
else
    echo "   ✓ WS file references correct port"
fi

echo ""
echo "=== Summary ==="
if [ $CONFLICTS -eq 0 ]; then
    echo "✓ No port conflicts detected"
else
    echo "❌ $CONFLICTS conflict(s) found"
fi

exit $CONFLICTS
