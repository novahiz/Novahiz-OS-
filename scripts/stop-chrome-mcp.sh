#!/usr/bin/env bash
set -euo pipefail

NOVAHIZ_DIR="${NOVAHIZ_HOME:-${HOME}/.opencode}"
PID_FILE="${NOVAHIZ_DIR}/data/chrome-mcp.pid"
PROFILE_DIR="${NOVAHIZ_DIR}/chrome-profile-mcp"
KILLED=false

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null || true)
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null || true
        sleep 1
        kill -9 "$PID" 2>/dev/null || true
        echo "Chrome MCP (PID $PID) stopped via PID file"
        KILLED=true
    fi
    rm -f "$PID_FILE"
fi

if ! $KILLED; then
    PIDS=$(pgrep -f "chrome.*${PROFILE_DIR}" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        for P in $PIDS; do
            kill "$P" 2>/dev/null || true
        done
        sleep 1
        for P in $PIDS; do
            kill -9 "$P" 2>/dev/null || true
        done
        echo "Chrome MCP instances stopped (profile-based)"
        KILLED=true
    fi
fi

if ! $KILLED; then
    echo "No Chrome MCP instance found running"
fi
exit 0
