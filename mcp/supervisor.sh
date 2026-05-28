#!/bin/bash
# Novahiz OS — Unified Supervisor
# Manages unified daemon

NOVAHIZ_DIR="$HOME/.opencode"
RUNTIME_DIR="$NOVAHIZ_DIR/runtime"
LOGS_DIR="$NOVAHIZ_DIR/logs"

case "$1" in
    start)
        echo "Starting Novahiz Unified Daemon..."
        cd "$RUNTIME_DIR"
        nohup python3 novahiz-unified.py daemon 2 > "$LOGS_DIR/unified.log" 2>&1 &
        echo $! > "$LOGS_DIR/novahiz-unified.pid"
        echo "✓ Started (PID: $!)"
        ;;
    stop)
        if [ -f "$LOGS_DIR/novahiz-unified.pid" ]; then
            PID=$(cat "$LOGS_DIR/novahiz-unified.pid")
            kill $PID 2>/dev/null || true
            rm -f "$LOGS_DIR/novahiz-unified.pid"
            echo "✓ Stopped (PID: $PID)"
        else
            pkill -f "novahiz-unified.py" 2>/dev/null || true
            echo "✓ Stopped (by pattern)"
        fi
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    status)
        python3 "$RUNTIME_DIR/novahiz-unified.py" status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
