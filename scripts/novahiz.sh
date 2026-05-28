#!/usr/bin/env bash
# Novahiz OS — Bash Entrypoint (Linux)
NOVAHIZ_DIR="${NOVAHIZ_HOME:-${HOME}/.opencode}"
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done
if [ -z "$PYTHON" ]; then
    echo "Python not found. Install Python 3.8+ from https://python.org" >&2
    exit 1
fi

# Chrome MCP commands handled natively
case "${1:-}" in
    chrome-start)
        shift
        exec "${NOVAHIZ_DIR}/scripts/launch-chrome-mcp.sh" "$@"
        ;;
    chrome-stop)
        exec "${NOVAHIZ_DIR}/scripts/stop-chrome-mcp.sh"
        ;;
    chrome-status)
        exec "${NOVAHIZ_DIR}/scripts/chrome-status.sh" "${2:-}"
        ;;
    *)
        exec "$PYTHON" "${NOVAHIZ_DIR}/scripts/novahiz-cli.py" "$@"
        ;;
esac
