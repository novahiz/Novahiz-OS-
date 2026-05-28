#!/bin/bash
# =============================================================================
# novahiz-stop.sh — Stop all Novahiz OS services
# =============================================================================

NOVAHIZ_DIR="$HOME/.opencode"
PIDS_DIR="$NOVAHIZ_DIR/pids"
LOGS_DIR="$NOVAHIZ_DIR/logs"

LOG_FILE="$LOGS_DIR/autostart.log"

# Colors
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] $1" | tee -a "$LOG_FILE"
}

stop_by_name() {
    local name="$1"
    local pattern="$2"
    
    local pids=$(pgrep -f "$pattern" 2>/dev/null)
    if [ -n "$pids" ]; then
        for pid in $pids; do
            kill "$pid" 2>/dev/null
            sleep 0.5
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
            fi
            log "${YELLOW}⚠${NC} Stopped $name (PID: $pid)"
        done
    fi
}

# =============================================================================
# MAIN
# =============================================================================

log "═══════════════════════════════════════════════════════════"
log "  NOVAHIZ OS — STOPPING ALL SERVICES"
log "═══════════════════════════════════════════════════════════"

# Stop by PID files first (clean shutdown)
for pidfile in "$PIDS_DIR"/*.pid; do
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        local name=$(basename "$pidfile" .pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            sleep 1
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null
            fi
            log "${YELLOW}⚠${NC} Stopped $name (PID: $pid)"
        fi
        rm -f "$pidfile"
    fi
done

# Force kill any remaining by pattern
stop_by_name "novahiz-runtime" "novahiz-runtime.py"
stop_by_name "opencode-bridge" "opencode-bridge.py"
stop_by_name "novahiz-mcp-http" "novahiz-mcp-http.py"
stop_by_name "task-processor" "task-processor.py"
stop_by_name "auto-executor" "auto-executor-simple.py"

# Clean PID files
rm -f "$PIDS_DIR"/*.pid 2>/dev/null

log "${GREEN}✅ All Novahiz OS services stopped${NC}"
log "═══════════════════════════════════════════════════════════"

exit 0
