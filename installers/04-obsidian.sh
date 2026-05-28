#!/bin/bash
# =============================================================================
# Novahiz OS — Obsidian Installer + Vault Setup
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "Obsidian"

if [ "${SKIP_OBSIDIAN:-false}" = true ]; then
    warn "Skipping Obsidian (--no-obsidian)"
    exit 0
fi

OBSIDIAN_VAULT="$HOME/Documents/llm-wiki"

# ---- Install Obsidian ----
install_obsidian() {
    case "$OS" in
        linux)
            if command -v obsidian &>/dev/null; then
                ok "Obsidian already installed"
                return 0
            fi
            log "Installing Obsidian via flatpak..."
            flatpak install -y flathub md.obsidian.Obsidian 2>/dev/null && {
                alias obsidian="flatpak run md.obsidian.Obsidian"
                return 0
            }
            warn "Flatpak install failed. Try: https://obsidian.md/download"
            return 1
            ;;
        macos)
            if [ -d "/Applications/Obsidian.app" ]; then
                ok "Obsidian already installed"
                return 0
            fi
            brew install --cask obsidian
            ;;
        windows)
            winget install -e --id Obsidian.Obsidian 2>/dev/null || warn "Install from: https://obsidian.md"
            ;;
    esac
}

install_obsidian || true

# ---- Create vault ----
header "Obsidian Vault Setup"
mkdir -p "$OBSIDIAN_VAULT"

# Copy wiki content from Novahiz
if [ -d "$NOVAHIZ_DIR/memory/05_Context" ]; then
    log "Setting up vault structure..."
    mkdir -p "$OBSIDIAN_VAULT/wiki/agents" "$OBSIDIAN_VAULT/wiki/skills" "$OBSIDIAN_VAULT/raw"

    cp "$NOVAHIZ_DIR/AGENTS.md" "$OBSIDIAN_VAULT/AGENTS.md" 2>/dev/null || true
    cp -r "$NOVAHIZ_DIR/memory/05_Context"/*.md "$OBSIDIAN_VAULT/" 2>/dev/null || true
    ok "Vault content copied"
fi

# ---- Create index ----
if [ ! -f "$OBSIDIAN_VAULT/index.md" ]; then
    cat > "$OBSIDIAN_VAULT/index.md" << 'EOF'
# Novahiz OS — LLM Wiki

Welcome to your personal LLM wiki. This vault is auto-configured for use with AI agents.

## Navigation

- [[AGENTS.md|Registered Agents]] — 24 agents available
- [[wiki/index|Wiki Home]]
- [[log|Activity Log]]

## Quick Start

```
nv route "explore this project"
nv agents
nv health
```

_Last updated: {{DATE}}_
EOF
    sed -i "s/{{DATE}}/$(date '+%Y-%m-%d')/" "$OBSIDIAN_VAULT/index.md"
    ok "index.md created"
fi

# ---- Configure Obsidian plugins ----
OBSIDIAN_CONFIG="$OBSIDIAN_VAULT/.obsidian"
mkdir -p "$OBSIDIAN_CONFIG"

cat > "$OBSIDIAN_CONFIG/app.json" << 'EOF'
{
  "promptDelete": false,
  "alwaysUpdateLinks": true,
  "newFileLocation": "current",
  "attachmentFolderPath": "./attachments",
  "spellcheck": true,
  "showLineNumber": true,
  "vimMode": false
}
EOF

cat > "$OBSIDIAN_CONFIG/core-plugins.json" << 'EOF'
{
  "file-explorer": true,
  "global-search": true,
  "switcher": true,
  "graph": true,
  "backlink": true,
  "canvas": true,
  "outgoing-link": true,
  "tag-pane": true,
  "page-preview": true,
  "daily-notes": true,
  "templates": true,
  "note-composer": true,
  "command-palette": true,
  "editor-status": true,
  "starred": true,
  "markdown-importer": true,
  "outline": true,
  "word-count": true,
  "slides": true,
  "workspaces": true,
  "file-recovery": true,
  "publish": false,
  "sync": false
}
EOF

cat > "$OBSIDIAN_CONFIG/community-plugins.json" << 'EOF'
["dataview", "templater-obsidian", "obsidian-kanban"]
EOF

ok "Obsidian config created at $OBSIDIAN_CONFIG"

# ---- Validate ----
if command -v obsidian &>/dev/null || [ -d "/Applications/Obsidian.app" ]; then
    ok "Obsidian ready"
else
    warn "Obsidian binary not found in PATH. Launch manually."
fi
check "Obsidian vault" "[ -d '$OBSIDIAN_VAULT/.obsidian' ]"
summary
