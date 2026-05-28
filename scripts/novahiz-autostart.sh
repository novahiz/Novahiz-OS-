#!/bin/bash
# =============================================================================
# novahiz-autostart.sh — Auto-start all Novahiz OS services v6.0
# Loads environment from ~/.novahiz/.env
# =============================================================================

NOVAHIZ_DIR="$HOME/.opencode"
SCRIPTS_DIR="$NOVAHIZ_DIR/scripts"
MCP_DIR="$NOVAHIZ_DIR/mcp"
RUNTIME_DIR="$NOVAHIZ_DIR/runtime"
LOGS_DIR="$NOVAHIZ_DIR/logs"
PIDS_DIR="$NOVAHIZ_DIR/pids"
ENV_FILE="$HOME/.novahiz/.env"

mkdir -p "$LOGS_DIR" "$PIDS_DIR"
LOG_FILE="$LOGS_DIR/autostart.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# =============================================================================
# LOAD ENVIRONMENT
# =============================================================================
if [ -f "$ENV_FILE" ]; then
    set -a  # Auto-export
    source "$ENV_FILE"
    set +a
    log "✓ Environment loaded from $ENV_FILE"
else
    log "⚠ WARNING: $ENV_FILE not found"
fi

# Verify API keys
if [ -z "$OPENROUTER_API_KEY" ]; then
    log "❌ ERROR: OPENROUTER_API_KEY not set"
    exit 1
fi
log "✓ OPENROUTER_API_KEY loaded"

# =============================================================================
# KILL EXISTING
# =============================================================================
pkill -f "novahiz-runtime.py" 2>/dev/null
pkill -f "opencode-bridge.py" 2>/dev/null
pkill -f "novahiz-mcp-http.py" 2>/dev/null
pkill -f "task-processor.py" 2>/dev/null
sleep 1

# =============================================================================
# START SERVICES
# =============================================================================
log "═══════════════════════════════════════════════════════════"
log "  NOVAHIZ OS v6.0 — AUTO-START"
log "═══════════════════════════════════════════════════════════"

# 1. Runtime Daemon
python3 "$RUNTIME_DIR/novahiz-runtime.py" daemon 3 > "$LOGS_DIR/runtime-daemon.log" 2>&1 &
RUNTIME_PID=$!
echo $RUNTIME_PID > "$PIDS_DIR/runtime.pid"
log "✓ Runtime started (PID: $RUNTIME_PID)"

# 2. Bridge Daemon
python3 "$MCP_DIR/opencode-bridge.py" daemon 2 > "$LOGS_DIR/opencode-bridge.log" 2>&1 &
BRIDGE_PID=$!
echo $BRIDGE_PID > "$PIDS_DIR/bridge.pid"
log "✓ Bridge started (PID: $BRIDGE_PID)"

# 3. MCP HTTP
python3 "$MCP_DIR/novahiz-mcp-http.py" > "$LOGS_DIR/mcp-http.log" 2>&1 &
MCP_PID=$!
echo $MCP_PID > "$PIDS_DIR/mcp-http.pid"
log "✓ MCP HTTP started (PID: $MCP_PID)"

# 4. Task Processor
python3 "$MCP_DIR/task-processor.py" daemon 5 > "$LOGS_DIR/task-processor.log" 2>&1 &
TASK_PID=$!
echo $TASK_PID > "$PIDS_DIR/task-processor.pid"
log "✓ Task Processor started (PID: $TASK_PID)"

sleep 3

log "═══════════════════════════════════════════════════════════"
log "  SUMMARY"
log "═══════════════════════════════════════════════════════════"
log "Services started: 4/4"
log "✅ NOVAHIZ OS v6.0 READY"
log ""
log "Environment: $ENV_FILE"
log "Use 'nv health' to verify"
log "Use 'novahiz-stop.sh' to stop"
log "═══════════════════════════════════════════════════════════"

exit 0
