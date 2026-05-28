# =============================================================================
# Novahiz OS — Common Library
# Shared functions for all installer scripts
# Source: source "$NOVAHIZ_DIR/installers/lib/common.sh"
# =============================================================================

# ---- Colors (enable only in terminal) ----
if [ -t 1 ]; then
    GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
else
    GREEN=''; YELLOW=''; RED=''; CYAN=''; BOLD=''; DIM=''; NC=''
fi

# ---- Logging ----
log()    { echo -e "${CYAN}${BOLD}[•]${NC} $*"; }
ok()     { echo -e "${GREEN}${BOLD}[✓]${NC} $*"; }
warn()   { echo -e "${YELLOW}${BOLD}[!]${NC} $*"; }
fail()   { echo -e "${RED}${BOLD}[✗]${NC} $*"; }
header() { echo -e "\n${CYAN}${BOLD}━ $* ━${NC}"; }
sub()    { echo -e "  ${CYAN}→${NC} $*"; }
spacer() { echo ""; }

# ---- Track progress for validation ----
_PASSED=0; _FAILED=0
check() {
    local label="$1" cmd="$2"
    if eval "$cmd" &>/dev/null; then
        ok "$label"; _PASSED=$((_PASSED + 1))
    else
        fail "$label"; _FAILED=$((_FAILED + 1))
    fi
}
summary() {
    echo ""
    if [ "$_FAILED" -eq 0 ]; then
        ok "All $_PASSED checks passed"
    else
        warn "$_FAILED failed, $_PASSED passed"
    fi
}

# ---- OS info (must have been set by install.sh or detect-os.sh) ----
OS="${OS:-unknown}"; ARCH="${ARCH:-$(uname -m)}"
DISTRO="${DISTRO:-}"; PKG="${PKG:-}"

# ---- Ensure we're running from NOVAHIZ_DIR ----
NOVAHIZ_DIR="${NOVAHIZ_DIR:-$HOME/.opencode}"
ensure_novahiz_dir() {
    if [ ! -d "$NOVAHIZ_DIR" ]; then
        fail "Novahiz OS not found at $NOVAHIZ_DIR. Run install.sh first."
        exit 1
    fi
    cd "$NOVAHIZ_DIR"
}

# ---- Install a system package if missing ----
ensure_pkg() {
    local name="$1" pkg_name="$2"
    if ! command -v "$name" &>/dev/null; then
        log "Installing $name..."
        case "$OS" in
            linux) sudo $PKG_INSTALL "$pkg_name" ;;
            macos) brew install "$pkg_name" ;;
            windows) winget install -e --id "$pkg_name" ;;
        esac
        command -v "$name" &>/dev/null && ok "$name installed" || warn "$name install may have failed"
    else
        ok "$name already present"
    fi
}

# ---- Confirm step (skip if --yes) ----
confirm() {
    local msg="$1"
    if [ "${YES:-false}" = true ]; then
        return 0
    fi
    echo -en "  ${CYAN}?${NC} $msg ${DIM}(Y/n)${NC} "
    read -r response
    case "$response" in
        n|N|no|NO) return 1 ;;
        *) return 0 ;;
    esac
}

# ---- Spinner for long operations ----
spinner() {
    local pid=$1 msg="$2"
    local spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    local i=0
    echo -n "  $msg "
    while kill -0 "$pid" 2>/dev/null; do
        echo -ne "\b${spin:$i:1}"
        i=$(( (i + 1) % 10 ))
        sleep 0.1
    done
    echo -ne "\b"
    wait "$pid"
    echo "done"
}
