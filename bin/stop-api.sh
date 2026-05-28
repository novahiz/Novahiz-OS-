#!/bin/bash
# Stop NovaHiz API Server

NOVAHIZ_HOME="$HOME/.opencode"
PID_FILE="$NOVAHIZ_HOME/logs/api.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "API server stopped (PID: $PID)"
    else
        echo "Server not running (stale PID file)"
    fi
    rm "$PID_FILE"
else
    pkill -f "python3 server.py"
    echo "API server stopped"
fi
