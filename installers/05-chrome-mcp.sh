#!/bin/bash
# =============================================================================
# Novahiz OS — Chrome MCP Setup
# Configures Chrome for remote debugging (browser automation)
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "Chrome MCP (Browser Automation)"

CHROME=""
case "$OS" in
    linux)
        for c in google-chrome google-chrome-stable chromium chromium-browser; do
            command -v "$c" &>/dev/null && { CHROME="$c"; break; }
        done
        ;;
    macos)
        [ -d "/Applications/Google Chrome.app" ] && CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        ;;
    windows)
        [ -f "$PROGRAMFILES/Google/Chrome/Application/chrome.exe" ] && CHROME="$PROGRAMFILES/Google/Chrome/Application/chrome.exe"
        [ -f "$LOCALAPPDATA/Google/Chrome/Application/chrome.exe" ] && CHROME="$LOCALAPPDATA/Google/Chrome/Application/chrome.exe"
        ;;
esac

if [ -z "$CHROME" ]; then
    warn "Chrome not found. Install Chrome first."
    exit 0
fi
ok "Chrome found: $CHROME"

# ---- Create launch script ----
LAUNCH_SCRIPT="$NOVAHIZ_DIR/scripts/launch-chrome-mcp.sh"
cat > "$LAUNCH_SCRIPT" << 'LAUNCH'
#!/bin/bash
# Launch Chrome with remote debugging for MCP
CHROME_BIN="CHROME_PATH"
CHROME_PROFILE="$HOME/.opencode/chrome-profile-mcp"
CHROME_PORT=9222

mkdir -p "$CHROME_PROFILE"

if lsof -i :$CHROME_PORT &>/dev/null 2>&1; then
    echo "Chrome MCP already running on port $CHROME_PORT"
    echo "PID: $(lsof -ti :$CHROME_PORT)"
    exit 0
fi

echo "Starting Chrome MCP on port $CHROME_PORT..."
"$CHROME_BIN" \
    --remote-debugging-port=$CHROME_PORT \
    --user-data-dir="$CHROME_PROFILE" \
    --no-first-run \
    --no-default-browser-check \
    --disable-fre \
    --disable-features=TranslateUI \
    --disable-features=PrivacySandboxSettings4 \
    &
echo "Chrome MCP started (PID: $!)"
LAUNCH

sed -i "s|CHROME_PATH|$CHROME|g" "$LAUNCH_SCRIPT"
chmod +x "$LAUNCH_SCRIPT"

# Also create stop script
cat > "$NOVAHIZ_DIR/scripts/stop-chrome-mcp.sh" << 'STOP'
#!/bin/bash
PORT=9222
PID=$(lsof -ti :$PORT 2>/dev/null)
if [ -n "$PID" ]; then
    kill "$PID" 2>/dev/null && echo "Chrome MCP stopped (PID: $PID)" || echo "Could not stop Chrome MCP"
else
    echo "Chrome MCP not running"
fi
STOP
chmod +x "$NOVAHIZ_DIR/scripts/stop-chrome-mcp.sh"

ok "Chrome MCP scripts created"
check "Launch script" "[ -x '$LAUNCH_SCRIPT' ]"
summary
