#!/bin/bash
# Novahiz OS - Migrate to Unified Daemon
# Stops old daemons and starts unified daemon

set -e

echo "🔄 Novahiz OS — Migration vers Daemon Unifié"
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""

NOVAHIZ_DIR="$HOME/.opencode"
RUNTIME_DIR="$NOVAHIZ_DIR/runtime"
MCP_DIR="$NOVAHIZ_DIR/mcp"
LOGS_DIR="$NOVAHIZ_DIR/logs"

# =============================================================================
# STOP OLD DAEMONS
# =============================================================================
echo "🛑 Stopping old daemons..."

# Stop runtime daemon
if [ -f "$LOGS_DIR/novahiz-runtime.pid" ]; then
    PID=$(cat "$LOGS_DIR/novahiz-runtime.pid")
    kill $PID 2>/dev/null || true
    rm -f "$LOGS_DIR/novahiz-runtime.pid"
    echo "  ✓ Stopped novahiz-runtime (PID: $PID)"
fi

# Stop opencode-bridge
if [ -f "$LOGS_DIR/opencode-bridge.pid" ]; then
    PID=$(cat "$LOGS_DIR/opencode-bridge.pid")
    kill $PID 2>/dev/null || true
    rm -f "$LOGS_DIR/opencode-bridge.pid"
    echo "  ✓ Stopped opencode-bridge (PID: $PID)"
fi

# Kill any remaining daemon processes
pkill -f "novahiz-runtime.py" 2>/dev/null || true
pkill -f "opencode-bridge.py" 2>/dev/null || true
echo "  ✓ Cleaned up old processes"

# =============================================================================
# BACKUP OLD FILES
# =============================================================================
echo ""
echo "💾 Backing up old daemon scripts..."

BACKUP_DIR="$NOVAHIZ_DIR/backups/daemon_migration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

cp "$RUNTIME_DIR/novahiz-runtime.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "$MCP_DIR/opencode-bridge.py" "$BACKUP_DIR/" 2>/dev/null || true
cp "$MCP_DIR/supervisor.sh" "$BACKUP_DIR/" 2>/dev/null || true

echo "  ✓ Backup: $BACKUP_DIR"

# =============================================================================
# INSTALL UNIFIED DAEMON
# =============================================================================
echo ""
echo "📦 Installing unified daemon..."

# Create symlink for backward compatibility
ln -sf "$RUNTIME_DIR/novahiz-unified.py" "$RUNTIME_DIR/novahiz-runtime.py" 2>/dev/null || true
echo "  ✓ Created symlink: novahiz-runtime.py → novahiz-unified.py"

# Update supervisor script
cat > "$MCP_DIR/supervisor.sh" << 'SUPERVISOR_EOF'
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
SUPERVISOR_EOF

chmod +x "$MCP_DIR/supervisor.sh"
echo "  ✓ Updated supervisor.sh"

# =============================================================================
# START UNIFIED DAEMON
# =============================================================================
echo ""
echo "🚀 Starting unified daemon..."

cd "$RUNTIME_DIR"
nohup python3 novahiz-unified.py daemon 2 > "$LOGS_DIR/unified.log" 2>&1 &
UNIFIED_PID=$!
echo $UNIFIED_PID > "$LOGS_DIR/novahiz-unified.pid"

sleep 2

if ps -p $UNIFIED_PID > /dev/null 2>&1; then
    echo "  ✓ Unified daemon started (PID: $UNIFIED_PID)"
else
    echo "  ✗ Failed to start unified daemon"
    exit 1
fi

# =============================================================================
# VALIDATION
# =============================================================================
echo ""
echo "🔍 Validating installation..."

python3 "$RUNTIME_DIR/novahiz-unified.py" status

echo ""
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""
echo "✅ Migration completed!"
echo ""
echo "NEW COMMANDS:"
echo "  Start:  ~/.opencode/mcp/supervisor.sh start"
echo "  Stop:   ~/.opencode/mcp/supervisor.sh stop"
echo "  Status: ~/.opencode/mcp/supervisor.sh status"
echo ""
echo "BACKUP LOCATION:"
echo "  $BACKUP_DIR"
echo ""
echo "ROLLBACK (if needed):"
echo "  cp $BACKUP_DIR/novahiz-runtime.py $RUNTIME_DIR/"
echo "  cp $BACKUP_DIR/opencode-bridge.py $MCP_DIR/"
echo ""
