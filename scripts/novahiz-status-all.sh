#!/bin/bash
# =============================================================================
# novahiz-status-all.sh — Show status of all Novahiz OS services
# =============================================================================

NOVAHIZ_DIR="$HOME/.opencode"
PIDS_DIR="$NOVAHIZ_DIR/pids"
LOGS_DIR="$NOVAHIZ_DIR/logs"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

check_service() {
    local name="$1"
    local pattern="$2"
    local pidfile="$3"
    
    local running=false
    local pid=""
    
    # Check PID file first
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            running=true
        fi
    fi
    
    # Fallback to pgrep
    if [ "$running" = false ]; then
        pid=$(pgrep -f "$pattern" | head -1)
        if [ -n "$pid" ]; then
            running=true
        fi
    fi
    
    if [ "$running" = true ]; then
        echo -e "${GREEN}●${NC} $name ${GREEN}running${NC} (PID: $pid)"
        return 0
    else
        echo -e "${RED}○${NC} $name ${RED}stopped${NC}"
        return 1
    fi
}

# =============================================================================
# MAIN
# =============================================================================

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  NOVAHIZ OS — SERVICE STATUS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

RUNNING=0
TOTAL=0

# Check each service
for service in \
    "Novahiz Runtime:novahiz-unified.py:$PIDS_DIR/runtime.pid" \
    "OpenCode Bridge:opencode-bridge.py:$PIDS_DIR/bridge.pid" \
    "MCP HTTP Server:novahiz-mcp-http.py:$PIDS_DIR/mcp-http.pid" \
    "Task Processor:task-processor.py:$PIDS_DIR/task-processor.pid"
do
    IFS=':' read -r name pattern pidfile <<< "$service"
    TOTAL=$((TOTAL + 1))
    if check_service "$name" "$pattern" "$pidfile"; then
        RUNNING=$((RUNNING + 1))
    fi
done

echo ""
echo -e "${CYAN}───────────────────────────────────────────────────────────${NC}"
echo -e "Services: ${GREEN}$RUNNING${NC}/${TOTAL} running"

if [ $RUNNING -eq $TOTAL ]; then
    echo -e "Status: ${GREEN}● All systems operational${NC}"
elif [ $RUNNING -ge $((TOTAL / 2)) ]; then
    echo -e "Status: ${YELLOW}● Partial service${NC}"
else
    echo -e "Status: ${RED}● Services down${NC}"
fi

echo ""

# Quick runtime status
echo -e "${CYAN}───────────────────────────────────────────────────────────${NC}"
echo -e "${CYAN}RUNTIME STATUS:${NC}"
python3 "$NOVAHIZ_DIR/runtime/novahiz-unified.py" status 2>/dev/null | grep -E "Active|Models:|Executions" | head -5

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "Quick commands:"
echo -e "  ${CYAN}nv status${NC}         — Runtime status"
echo -e "  ${CYAN}nv config models${NC}  — Model configuration"
echo -e "  ${CYAN}novahiz-stop.sh${NC}   — Stop all services"
echo -e "  ${CYAN}novahiz-autostart.sh${NC} — Start all services"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"

exit 0
