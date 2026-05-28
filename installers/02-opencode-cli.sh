#!/bin/bash
# =============================================================================
# Novahiz OS — OpenCode CLI Installer
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "OpenCode CLI"

if command -v opencode &>/dev/null; then
    log "OpenCode CLI already installed: $(opencode --version 2>/dev/null || true)"
    if confirm "Upgrade to latest?"; then
        npm install -g @opencode-ai/cli
        ok "OpenCode CLI upgraded"
    fi
else
    log "Installing OpenCode CLI..."
    npm install -g @opencode-ai/cli
    ok "OpenCode CLI installed: $(opencode --version 2>/dev/null || true)"
fi

# Verify
check "opencode command" "command -v opencode"
check "opencode version" "opencode --version"
summary
