#!/bin/bash
# Start NovaHiz API Server as daemon

NOVAHIZ_HOME="$HOME/.opencode"
PID_FILE="$NOVAHIZ_HOME/logs/api.pid"
LOG_FILE="$NOVAHIZ_HOME/logs/api-server.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "API server already running (PID: $PID)"
        exit 0
    fi
fi

# Start server
cd "$NOVAHIZ_HOME/api"
python3 -u server.py > "$LOG_FILE" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
echo "API server started (PID: $PID)"

# Wait and verify
sleep 2
if ps -p $PID > /dev/null 2>&1; then
    echo "✓ Server running"
else
    echo "✗ Server failed to start"
    exit 1
fi
