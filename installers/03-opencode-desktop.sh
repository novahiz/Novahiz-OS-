#!/bin/bash
# =============================================================================
# Novahiz OS — OpenCode Desktop Installer
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "OpenCode Desktop"

if [ "${SKIP_DESKTOP:-false}" = true ]; then
    warn "Skipping OpenCode Desktop (--no-desktop)"
    exit 0
fi

if [ "${YES:-false}" != true ]; then
    confirm "Install OpenCode Desktop?" || { warn "Skipped"; exit 0; }
fi

case "$OS" in
    linux)
        if command -v opencode-desktop &>/dev/null; then
            ok "OpenCode Desktop already installed"
            exit 0
        fi
        log "Downloading OpenCode Desktop for Linux..."
        LATEST=$(curl -s https://api.github.com/repos/opencode-ai/opencode-desktop/releases/latest 2>/dev/null | grep "browser_download_url" | grep -E "$ARCH|amd64" | head -1 | cut -d'"' -f4)
        if [ -n "$LATEST" ]; then
            DEB_FILE="/tmp/opencode-desktop.deb"
            curl -fsSL -o "$DEB_FILE" "$LATEST"
            sudo dpkg -i "$DEB_FILE" 2>/dev/null || sudo apt install -y -f
            ok "OpenCode Desktop installed"
        else
            warn "Could not find download URL. Visit: https://docs.opencode.ai/install"
        fi
        ;;
    macos)
        if command -v opencode-desktop &>/dev/null; then
            ok "OpenCode Desktop already installed"
        else
            brew install --cask opencode-desktop 2>/dev/null || warn "Install via: brew install --cask opencode-desktop"
        fi
        ;;
    windows)
        winget install -e --id Opencode.Desktop 2>/dev/null || warn "Install via: winget install Opencode.Desktop"
        ;;
esac

check "OpenCode Desktop" "command -v opencode-desktop 2>/dev/null || test -d '/Applications/OpenCode Desktop.app' 2>/dev/null"
summary
