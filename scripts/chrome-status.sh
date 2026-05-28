#!/usr/bin/env bash
set -euo pipefail

NOVAHIZ_DIR="${NOVAHIZ_HOME:-${HOME}/.opencode}"
PID_FILE="${NOVAHIZ_DIR}/data/chrome-mcp.pid"
PROFILE_DIR="${NOVAHIZ_DIR}/chrome-profile-mcp"
JSON="${1:-}"

CHROME_OK=false
CHROME_PID=""
CHROME_BROWSER=""
CHROME_WS=""

if RAW=$(curl -sf "http://127.0.0.1:9222/json/version" 2>/dev/null); then
    CHROME_OK=true
    CHROME_BROWSER=$(echo "$RAW" | python3 -c "import sys,json; print(json.load(sys.stdin).get('Browser',''))" 2>/dev/null || true)
    CHROME_WS=$(echo "$RAW" | python3 -c "import sys,json; print(json.load(sys.stdin).get('webSocketDebuggerUrl',''))" 2>/dev/null || true)
fi

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null || true)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        CHROME_PID="$PID"
    fi
fi

if [ -z "$CHROME_PID" ] && $CHROME_OK; then
    CHROME_PID=$(pgrep -f "chrome.*${PROFILE_DIR}" 2>/dev/null | head -1 || true)
fi

if [ "$JSON" = "--json" ]; then
    echo "{\"running\":${CHROME_OK},\"pid\":\"${CHROME_PID}\",\"browser\":\"${CHROME_BROWSER}\",\"websocket\":\"${CHROME_WS}\",\"profile\":\"${PROFILE_DIR}\"}"
    exit 0
fi

if $CHROME_OK; then
    PID_STR="${CHROME_PID:+PID $CHROME_PID}"
    echo "[OK] Chrome MCP en marche - ${CHROME_BROWSER} (${PID_STR:-PID unknown})"
    echo "     WebSocket: ${CHROME_WS}"
else
    echo "[--] Chrome MCP arrete"
fi
