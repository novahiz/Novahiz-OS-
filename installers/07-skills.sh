#!/bin/bash
# =============================================================================
# Novahiz OS — Skills Deploy
# Copies all 64 skills to .agents/skills/
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "Skills (64)"

AGENTS_SKILLS="$NOVAHIZ_DIR/.agents/skills"
mkdir -p "$AGENTS_SKILLS"

log "Deploying core skills..."
if [ -d "$NOVAHIZ_DIR/skills" ]; then
    for skill_dir in "$NOVAHIZ_DIR/skills"/*/; do
        name=$(basename "$skill_dir")
        target="$AGENTS_SKILLS/$name"
        if [ ! -d "$target" ]; then
            cp -r "$skill_dir" "$target"
            sub "$name"
        fi
    done
    ok "Core skills deployed"
fi

total=$(ls -d "$AGENTS_SKILLS"/*/ 2>/dev/null | wc -l)
ok "$total skills ready"
summary
