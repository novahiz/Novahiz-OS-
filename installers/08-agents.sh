#!/bin/bash
# =============================================================================
# Novahiz OS — Agents Registration
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "Agents (24)"

AGENTS_DIR="$NOVAHIZ_DIR/agents"
mkdir -p "$AGENTS_DIR"

# Agents are already in the repo, just verify
count=$(ls "$AGENTS_DIR"/*.yaml 2>/dev/null | wc -l)
ok "$count agent configs found"

# Register in registry if exists
if [ -f "$NOVAHIZ_DIR/config/agent-registry.json" ]; then
    log "Agent registry found"
fi

# Generate AGENTS.md summary
AGENTS_MD="$NOVAHIZ_DIR/AGENTS.md"
if [ -f "$AGENTS_MD" ]; then
    ok "AGENTS.md exists ($(wc -l < "$AGENTS_MD") lines)"
fi

summary
