#!/bin/bash
# Novahiz Runtime Daemon Wrapper
# Ensures API key is set before starting daemon

NOVAHIZ_DIR="$HOME/.opencode"
LOGS_DIR="$NOVAHIZ_DIR/logs"
PIDS_DIR="$NOVAHIZ_DIR/pids"

mkdir -p "$LOGS_DIR" "$PIDS_DIR"

# Check if API key is set
if [ -z "$OPENROUTER_API_KEY" ]; then
    # Try to load from .bashrc
    source "$HOME/.bashrc" 2>/dev/null
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️  WARNING: OPENROUTER_API_KEY not set"
    echo "   Execution will fail without API key"
    echo "   Set it: export OPENROUTER_API_KEY=your_key"
    echo ""
fi

# Kill existing daemon
pkill -f "novahiz-unified.py daemon" 2>/dev/null || true
sleep 1

# Start daemon with environment
export PYTHONUNBUFFERED=1
export NOVAHIZ_MODE=production

nohup python3 "$NOVAHIZ_DIR/runtime/novahiz-unified.py" daemon 2 > "$LOGS_DIR/runtime-daemon.log" 2>&1 &
PID=$!
echo $PID > "$PIDS_DIR/runtime.pid"

sleep 2

if ps -p $PID > /dev/null 2>&1; then
    echo "✅ Runtime daemon started (PID: $PID)"
    echo "   Logs: tail -f $LOGS_DIR/runtime-daemon.log"
else
    echo "❌ Failed to start daemon"
    cat "$LOGS_DIR/runtime-daemon.log"
fi
