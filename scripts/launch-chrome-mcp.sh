#!/usr/bin/env bash
set -euo pipefail

NOVAHIZ_DIR="${NOVAHIZ_HOME:-${HOME}/.opencode}"
CHROME=""
for c in google-chrome google-chrome-stable chromium chromium-browser; do
    if command -v "$c" &>/dev/null; then
        CHROME="$c"
        break
    fi
done
if [ -z "$CHROME" ]; then
    echo "ERROR: Chrome/Chromium not found" >&2
    exit 1
fi

PORT="${1:-9222}"
HEADLESS="${2:-}"
PROFILE_DIR="${NOVAHIZ_DIR}/chrome-profile-mcp"
PID_FILE="${NOVAHIZ_DIR}/data/chrome-mcp.pid"
LOG_FILE="${NOVAHIZ_DIR}/logs/chrome-mcp.log"
DATA_DIR="${NOVAHIZ_DIR}/data"

mkdir -p "$DATA_DIR" "$PROFILE_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

if curl -sf "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
    log "OK: Chrome already running on port ${PORT}"
    PID=$(pgrep -f "chrome.*${PROFILE_DIR}" 2>/dev/null | head -1)
    [ -n "$PID" ] && echo "$PID" > "$PID_FILE"
    exit 0
fi

log "Launching Chrome on port ${PORT}..."

ARGS=(
    "--remote-debugging-port=${PORT}"
    "--remote-allow-origins=*"
    "--user-data-dir=${PROFILE_DIR}"
    "--no-first-run"
    "--no-default-browser-check"
    "--disable-sync"
    "--new-window"
    "--no-sandbox"
    "about:blank"
)
[ "$HEADLESS" = "headless" ] && ARGS+=("--headless=new")

nohup "$CHROME" "${ARGS[@]}" >/dev/null 2>&1 &
PID=$!
echo "$PID" > "$PID_FILE"
log "Chrome launched (PID: $PID)"

for i in $(seq 1 15); do
    sleep 1
    if curl -sf "http://127.0.0.1:${PORT}/json/version" >/dev/null 2>&1; then
        log "CDP ready after ${i}s"
        exit 0
    fi
done

log "ERROR: Chrome started but CDP port ${PORT} didn't open within 15s"
exit 1
