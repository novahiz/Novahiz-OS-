#!/bin/bash
# =============================================================================
# Novahiz OS — Dashboard & Metrics Setup
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "Dashboard"

DASHBOARD_DIR="$NOVAHIZ_DIR/dashboard/src"
mkdir -p "$DASHBOARD_DIR"

# Dashboard exists from repo, just verify
if [ -f "$DASHBOARD_DIR/status.html" ]; then
    ok "Dashboard HTML found"
fi

# ---- Cron job for daily metrics ----
CRON_JOB="0 6 * * * cd $NOVAHIZ_DIR && python3 scripts/dashboard.py 2>/dev/null || true"

if command -v crontab &>/dev/null; then
    if ! crontab -l 2>/dev/null | grep -q 'dashboard.py'; then
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
        ok "Daily metrics cron added (6 AM)"
    else
        ok "Cron already configured"
    fi
fi

check "Dashboard" "[ -f '$DASHBOARD_DIR/status.html' ]"
summary
