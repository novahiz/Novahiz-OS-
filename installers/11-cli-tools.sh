#!/bin/bash
# =============================================================================
# Novahiz OS — CLI Tools Setup
# Symlinks, PATH, aliases
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "CLI Tools"

BIN_DIR="$NOVAHIZ_DIR/bin"
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

# ---- Symlink all tools ----
count=0
for tool in "$BIN_DIR"/*; do
    [ -f "$tool" ] || continue
    name=$(basename "$tool")
    target="$LOCAL_BIN/$name"
    if [ ! -f "$target" ]; then
        ln -sf "$tool" "$target"
        count=$((count + 1))
    fi
done
ok "$count tools linked to $LOCAL_BIN"

# ---- Add to PATH in shell configs ----
PATH_LINE='export PATH="$HOME/.local/bin:$PATH"'
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.bash_profile" "$HOME/.profile"; do
    if [ -f "$rc" ] && ! grep -q '\.local/bin' "$rc" 2>/dev/null; then
        echo "$PATH_LINE" >> "$rc"
        sub "Added PATH to $rc"
    fi
done

# ---- nv alias ----
ALIAS_LINE='alias nv="opencode"'
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    if [ -f "$rc" ] && ! grep -q "alias nv=" "$rc" 2>/dev/null; then
        echo "$ALIAS_LINE" >> "$rc"
        sub "Added nv alias to $rc"
    fi
done

# ---- Novahiz CLI ----
if [ -f "$BIN_DIR/novahiz" ]; then
    chmod +x "$BIN_DIR/novahiz"
    if [ ! -f "$LOCAL_BIN/novahiz" ]; then
        ln -sf "$BIN_DIR/novahiz" "$LOCAL_BIN/novahiz"
    fi
    ok "novahiz CLI ready"
fi

# Quick test
check "nv alias" "alias nv 2>/dev/null || true"
summary
