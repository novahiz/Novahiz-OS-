#!/bin/bash
# =============================================================================
# Novahiz OS — Component Setup Orchestrator
# Called by install.sh after clone + path patch
# =============================================================================
set -e
NOVAHIZ_DIR="${NOVAHIZ_DIR:-$HOME/.opencode}"
source "$NOVAHIZ_DIR/installers/lib/common.sh"
source "$NOVAHIZ_DIR/installers/lib/detect-os.sh"
detect_os

cd "$NOVAHIZ_DIR"
mkdir -p logs config executions data cache

header "Component: OpenCode CLI"
bash "$NOVAHIZ_DIR/installers/02-opencode-cli.sh" || warn "OpenCode CLI install failed"

header "Component: OpenCode Desktop"
bash "$NOVAHIZ_DIR/installers/03-opencode-desktop.sh" || warn "OpenCode Desktop skipped"

if [ "${SKIP_OBSIDIAN:-false}" != true ]; then
    header "Component: Obsidian"
    bash "$NOVAHIZ_DIR/installers/04-obsidian.sh" || warn "Obsidian install failed"
fi

header "Component: Chrome MCP"
bash "$NOVAHIZ_DIR/installers/05-chrome-mcp.sh" || warn "Chrome MCP config failed"

header "Component: Skills & Agents"
bash "$NOVAHIZ_DIR/installers/07-skills.sh" || warn "Skills setup failed"
bash "$NOVAHIZ_DIR/installers/08-agents.sh" || warn "Agents setup failed"

header "Component: MCP Servers"
bash "$NOVAHIZ_DIR/installers/09-mcp-servers.sh" || warn "MCP config failed"

header "Component: CLI Tools"
bash "$NOVAHIZ_DIR/installers/11-cli-tools.sh" || warn "CLI setup failed"

if [ "$OS" = "linux" ]; then
    header "Component: Systemd Services"
    bash "$NOVAHIZ_DIR/installers/12-systemd.sh" || warn "Systemd setup failed"
fi

header "Component: Dashboard"
bash "$NOVAHIZ_DIR/installers/13-dashboard.sh" || warn "Dashboard setup failed"

ok "All components installed"
