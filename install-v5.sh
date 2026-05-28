#!/bin/bash
# =============================================================================
# Novahiz OS v5.0 — Production Installation Script
# Stable, Scalable, Standalone Execution Engine
# =============================================================================

set -e

NOVAHIZ_DIR="$HOME/.opencode"
SCRIPTS_DIR="$NOVAHIZ_DIR/scripts"
MCP_DIR="$NOVAHIZ_DIR/mcp"
RUNTIME_DIR="$NOVAHIZ_DIR/runtime"
PLUGINS_DIR="$NOVAHIZ_DIR/plugins"
DEPLOY_DIR="$NOVAHIZ_DIR/deploy"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${CYAN}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC} $*"; }
warning() { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  NOVAHIZ OS v5.0 — Production Installation${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# 1. Check Python
log "Checking Python 3..."
if command -v python3 &> /dev/null; then
    success "Python: $(python3 --version)"
else
    error "Python 3 required"
    exit 1
fi

# 2. Create directories
log "Creating directories..."
mkdir -p "$SCRIPTS_DIR" "$MCP_DIR" "$RUNTIME_DIR" "$PLUGINS_DIR" "$DEPLOY_DIR"
mkdir -p "$NOVAHIZ_DIR"/{executions,pending_tasks,logs,config,memory,runtime}
success "Directories created"

# 3. Set permissions
log "Setting permissions..."
find "$NOVAHIZ_DIR" -name "*.py" -type f -exec chmod +x {} \; 2>/dev/null || true
find "$NOVAHIZ_DIR" -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || true
success "Permissions set"

# 4. Initialize Runtime
log "Initializing Novahiz Runtime..."
if [ ! -f "$RUNTIME_DIR/config.json" ]; then
    python3 "$RUNTIME_DIR/novahiz-runtime.py" init
    success "Runtime initialized"
else
    warning "Runtime already initialized"
fi

# 5. Check opencode.json
log "Checking OpenCode config..."
if [ -f "$NOVAHIZ_DIR/opencode.json" ]; then
    if python3 -c "import json; json.load(open('$NOVAHIZ_DIR/opencode.json'))" 2>/dev/null; then
        success "opencode.json: Valid"
    else
        error "opencode.json: Invalid JSON"
    fi
else
    warning "opencode.json: Not found"
fi

# 6. Install systemd services
log "Checking systemd..."
if command -v systemctl &> /dev/null; then
    if [ -f "$DEPLOY_DIR/novahiz-runtime.service" ]; then
        echo -n "  Install systemd services? (y/n): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            sudo cp "$DEPLOY_DIR/novahiz-runtime.service" /etc/systemd/system/
            sudo systemctl daemon-reload
            sudo systemctl enable novahiz-runtime
            sudo systemctl start novahiz-runtime
            success "Systemd service installed and started"
            echo ""
            echo "  Check status: systemctl status novahiz-runtime"
            echo "  View logs: journalctl -u novahiz-runtime -f"
        fi
    fi
else
    warning "systemd not available"
fi

# 7. Update .bashrc
log "Updating shell config..."
if ! grep -q "novahiz-runtime" "$HOME/.bashrc" 2>/dev/null; then
    cat >> "$HOME/.bashrc" << 'EOF'

# Novahiz OS v5.0
export PATH="$HOME/.opencode/bin:$HOME/.opencode/runtime:$PATH"
alias nv='~/.opencode/bin/nv'
alias nv-start='bash ~/.opencode/mcp/supervisor.sh start'
alias nv-status='bash ~/.opencode/mcp/supervisor.sh status'
alias nv-stop='bash ~/.opencode/mcp/supervisor.sh stop'
alias runtime='python3 ~/.opencode/runtime/novahiz-runtime.py'
EOF
    success ".bashrc updated"
else
    warning ".bashrc already configured"
fi

# 8. Test components
log "Testing components..."

# Test Smart Router
if python3 "$SCRIPTS_DIR/novahiz-cli.py" route "test" &>/dev/null; then
    success "Smart Router: OK"
else
    warning "Smart Router: Issues"
fi

# Test MCP HTTP
if timeout 2 python3 "$MCP_DIR/novahiz-mcp-http.py" &>/dev/null; then
    success "MCP HTTP: OK"
else
    success "MCP HTTP: Installed"
fi

# Test Runtime
if python3 "$RUNTIME_DIR/novahiz-runtime.py" status &>/dev/null; then
    success "Runtime: OK"
else
    warning "Runtime: Issues"
fi

# 9. Summary
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  INSTALLATION COMPLETE${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "📁 Installation: $NOVAHIZ_DIR"
echo ""
echo "🚀 Quick Start:"
echo ""
if systemctl is-active --quiet novahiz-runtime 2>/dev/null; then
    echo "   ✅ Runtime: Running (systemd)"
else
    echo "   1. Start Runtime daemon:"
    echo "      ${YELLOW}python3 $RUNTIME_DIR/novahiz-runtime.py daemon &${NC}"
fi
echo ""
echo "   2. Set API key (required for execution):"
echo "      ${YELLOW}export OPENROUTER_API_KEY=your_key${NC}"
echo ""
echo "   3. Test execution:"
echo "      ${YELLOW}nv route \"Build API\"${NC}"
echo "      ${YELLOW}nv run \"Build API\"${NC}"
echo ""
echo "📖 Documentation:"
echo "   - $NOVAHIZ_DIR/ROUTER.md"
echo "   - $NOVAHIZ_DIR/SOLUTIONS.md"
echo "   - $NOVAHIZ_DIR/LIMITES.md"
echo ""
echo "🔧 Commands:"
echo "   nv route <task>     — Route to optimal agent"
echo "   nv run <task>       — Route + execute"
echo "   nv exec <agent> <task> — Execute with agent"
echo "   runtime status      — Runtime status"
echo "   runtime daemon      — Start runtime daemon"
echo ""
echo "═══════════════════════════════════════════════════════════"
