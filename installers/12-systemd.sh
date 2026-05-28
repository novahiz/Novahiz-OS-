#!/bin/bash
# =============================================================================
# Novahiz OS — Systemd Service Installer
# Linux-only. Auto-start at boot.
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "Systemd Services"

if [ "$OS" != "linux" ]; then
    warn "Systemd is Linux-only. Skipping."
    exit 0
fi

if ! command -v systemctl &>/dev/null; then
    warn "systemctl not found. Skipping."
    exit 0
fi

if [ "${YES:-false}" != true ]; then
    confirm "Install systemd services (auto-start at boot)?" || { warn "Skipped"; exit 0; }
fi

DEPLOY_DIR="$NOVAHIZ_DIR/deploy"
INSTALLED=0

for service_file in "$DEPLOY_DIR"/*.service; do
    [ -f "$service_file" ] || continue
    name=$(basename "$service_file")

    # Patch paths for this user
    sed -i "s|/home/novahiz|$HOME|g" "$service_file"
    sed -i "s/User=novahiz/User=$(whoami)/g" "$service_file"
    sed -i "s/Group=novahiz/Group=$(id -gn)/g" "$service_file"

    log "Installing $name..."
    sudo cp "$service_file" "/etc/systemd/system/$name"
    sudo systemctl daemon-reload 2>/dev/null
    sudo systemctl enable "$name" 2>/dev/null && {
        sub "$name enabled"
        INSTALLED=$((INSTALLED + 1))
    } || warn "Could not enable $name"
done

ok "$INSTALLED systemd services installed"
check "systemd units" "systemctl list-unit-files | grep -q novahiz"
summary
