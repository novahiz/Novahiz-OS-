#!/bin/bash
# =============================================================================
# Novahiz OS v6.0 — Universal Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash
#        curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash -s -- --yes
# =============================================================================
set -e

# ---- Detect if sourced or piped ----
if [ -n "$BASH_SOURCE" ] && [ "$BASH_SOURCE" != "$0" ]; then
    echo "Please run this script directly, not with 'source'"
    echo "  curl -fsSL https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.sh | bash"
    exit 1
fi

# ---- Parse flags ----
QUIET=false
YES=false
VERBOSE=false
SKIP_OBSIDIAN=false
SKIP_DESKTOP=false
DEV=false

for arg in "$@"; do
    case "$arg" in
        --quiet|--silent|-q) QUIET=true ;;
        --yes|-y) YES=true ;;
        --verbose|-v) VERBOSE=true ;;
        --no-obsidian) SKIP_OBSIDIAN=true ;;
        --no-desktop) SKIP_DESKTOP=true ;;
        --dev) DEV=true ;;
    esac
done

VERBOSE=true  # Always verbose during install

# ---- Constants ----
REPO_URL="https://github.com/novahiz/Novahiz-OS-.git"
REPO_BRANCH="main"
NOVAHIZ_DIR="$HOME/.opencode"
NOVAHIZ_ENV_DIR="$HOME/.novahiz"
OBSIDIAN_VAULT="$HOME/Documents/llm-wiki"
PYTHON_MIN="3.10"
NODE_MIN="18"

# ---- Colors ----
if [ -t 1 ]; then
    GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'
    BOLD='\033[1m'; NC='\033[0m'
else
    GREEN=''; YELLOW=''; RED=''; CYAN=''; BOLD=''; NC=''
fi

# ---- Logging helpers ----
log()   { echo -e "${CYAN}${BOLD}[•]${NC} $*"; }
ok()    { echo -e "${GREEN}${BOLD}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}${BOLD}[!]${NC} $*"; }
fail()  { echo -e "${RED}${BOLD}[✗]${NC} $*"; }
header(){ echo -e "\n${CYAN}${BOLD}━━━ $* ━━━${NC}"; }
sub()   { echo -e "  ${CYAN}→${NC} $*"; }

# ---- Error trap ----
trap 'fail "Installation failed at line $LINENO"; echo "Check logs: $NOVAHIZ_DIR/logs/install.log"; exit 1' ERR

# ---- OS Detection ----
detect_os() {
    OS="unknown"
    ARCH="$(uname -m)"
    DISTRO=""
    PKG=""
    PKG_INSTALL=""

    case "$(uname -s)" in
        Linux*)  OS="linux" ;;
        Darwin*) OS="macos" ;;
        MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
    esac

    if [ "$OS" = "linux" ]; then
        if command -v apt &>/dev/null; then
            DISTRO="debian"; PKG="apt"; PKG_INSTALL="apt install -y"
        elif command -v dnf &>/dev/null; then
            DISTRO="fedora"; PKG="dnf"; PKG_INSTALL="dnf install -y"
        elif command -v pacman &>/dev/null; then
            DISTRO="arch"; PKG="pacman"; PKG_INSTALL="pacman -S --noconfirm"
        elif command -v zypper &>/dev/null; then
            DISTRO="suse"; PKG="zypper"; PKG_INSTALL="zypper install -y"
        elif command -v apk &>/dev/null; then
            DISTRO="alpine"; PKG="apk"; PKG_INSTALL="apk add --no-cache"
        fi
        # Check for WSL
        if grep -qi microsoft /proc/version 2>/dev/null; then
            DISTRO="${DISTRO}-wsl"
        fi
    fi

    if [ "$OS" = "macos" ]; then
        PKG="brew"
        if ! command -v brew &>/dev/null; then
            PKG_INSTALL='arch -arm64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        else
            PKG_INSTALL="brew install"
        fi
    fi

    if [ "$OS" = "windows" ]; then
        PKG="winget"
        PKG_INSTALL="winget install -e --id"
    fi
}

# ---- Version comparison ----
version_ge() {
    printf '%s\n' "$1" "$2" | sort -V | head -1 | grep -q "^$2$"
}

# ---- Install prerequisite if missing ----
ensure_cmd() {
    local name="$1"
    local cmd="$2"
    local install_cmd="$3"
    local version_flag="${4:---version}"
    local min_version="$5"

    if command -v "$cmd" &>/dev/null; then
        local version
        version=$("$cmd" $version_flag 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+(\.[0-9]+)?' | head -1)
        if [ -n "$min_version" ] && [ -n "$version" ]; then
            if version_ge "$version" "$min_version"; then
                ok "$name $version"
            else
                warn "$name $version (need $min_version+), upgrading..."
                eval "$install_cmd"
            fi
        else
            ok "$name $version"
        fi
    else
        log "Installing $name..."
        if [ "$OS" = "linux" ]; then
            eval "sudo $install_cmd" || eval "$install_cmd"
        else
            eval "$install_cmd"
        fi
        command -v "$cmd" &>/dev/null && ok "$name installed" || warn "$name may not be installed"
    fi
}

# =============================================================================
# PHASE 1: PREREQUISITES
# =============================================================================
header "PHASE 1/5 — Detecting System"
detect_os
log "OS: $OS | Arch: $ARCH | Distro: $DISTRO"
ok "System detected: $OS ($DISTRO) on $ARCH"

header "Installing Prerequisites"
case "$OS" in
    linux)
        sudo true  # Cache sudo
        ensure_cmd "Python 3" "python3" "$PKG_INSTALL python3 python3-pip python3-venv" "--version" "$PYTHON_MIN"
        ensure_cmd "Node.js" "node" "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash - && $PKG_INSTALL nodejs" "--version" "$NODE_MIN"
        ensure_cmd "Git" "git" "$PKG_INSTALL git"
        ensure_cmd "curl" "curl" "$PKG_INSTALL curl"
        ensure_cmd "jq" "jq" "$PKG_INSTALL jq"
        ensure_cmd "make" "make" "$PKG_INSTALL build-essential"
        # Flatpak for Obsidian
        if ! command -v flatpak &>/dev/null; then
            log "Installing flatpak..."
            sudo $PKG_INSTALL flatpak
            sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
        fi
        ;;
    macos)
        ensure_cmd "Homebrew" "brew" "$PKG_INSTALL"
        ensure_cmd "Python 3" "python3" "brew install python@3.12" "--version" "$PYTHON_MIN"
        ensure_cmd "Node.js" "node" "brew install node@20" "--version" "$NODE_MIN"
        ensure_cmd "Git" "git" "brew install git"
        ensure_cmd "jq" "jq" "brew install jq"
        ;;
    windows)
        log "Windows detected — prerequisites will be handled by install.ps1"
        log "Run this in PowerShell as Administrator:"
        log "  Set-ExecutionPolicy Bypass -Scope Process -Force"
        log '  iex ((New-Object System.Net.WebClient).DownloadString("https://raw.githubusercontent.com/novahiz/Novahiz-OS-/main/install.ps1"))'
        exit 0
        ;;
esac

# ---- Python pip packages ----
log "Installing Python packages..."
pip3 install --user --upgrade pip setuptools wheel 2>/dev/null || true

# =============================================================================
# PHASE 2: CLONE NOVAHIZ OS
# =============================================================================
header "PHASE 2/5 — Installing Novahiz OS"

if [ -d "$NOVAHIZ_DIR/.git" ]; then
    log "Novahiz OS already installed. Updating..."
    cd "$NOVAHIZ_DIR"
    git stash 2>/dev/null || true
    git pull origin "$REPO_BRANCH" 2>/dev/null || true
    ok "Updated Novahiz OS"
else
    log "Cloning Novahiz OS..."
    if [ -d "$NOVAHIZ_DIR" ]; then
        mv "$NOVAHIZ_DIR" "${NOVAHIZ_DIR}.backup.$(date +%s)"
        warn "Backed up existing $NOVAHIZ_DIR"
    fi
    git clone --branch "$REPO_BRANCH" "$REPO_URL" "$NOVAHIZ_DIR"
    ok "Novahiz OS cloned to $NOVAHIZ_DIR"
fi

cd "$NOVAHIZ_DIR"

# ---- Create required directories ----
mkdir -p "$NOVAHIZ_DIR"/{logs,config,executions,data,cache}
mkdir -p "$NOVAHIZ_ENV_DIR"

# =============================================================================
# PHASE 3: PATCH PATHS FOR THIS USER
# =============================================================================
header "PHASE 3/5 — Configuring for your system"

log "Patching hardcoded paths..."
OLD_HOME="/home/novahiz"
NEW_HOME="$HOME"

# Files that need path patching (exclude .git, binaries, node_modules)
find "$NOVAHIZ_DIR" -type f \( \
    -name "*.sh" -o -name "*.py" -o -name "*.json" -o -name "*.service" \
    -o -name "*.conf" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" \) \
    ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" \
    ! -path "*/executions/*" ! -path "*/logs/*" 2>/dev/null | while read -r file; do

    if grep -q "$OLD_HOME" "$file" 2>/dev/null; then
        sed -i "s|$OLD_HOME|$NEW_HOME|g" "$file"
    fi
done

# Patch User=novahiz in service files
find "$NOVAHIZ_DIR/deploy" "$NOVAHIZ_DIR/systemd" -name "*.service" 2>/dev/null | while read -r file; do
    sed -i "s/User=novahiz/User=$(whoami)/g" "$file" 2>/dev/null || true
    sed -i "s/Group=novahiz/Group=$(id -gn)/g" "$file" 2>/dev/null || true
done

ok "Paths patched for user $(whoami)"

# ---- Fix permissions ----
find "$NOVAHIZ_DIR"/bin -type f -exec chmod +x {} \; 2>/dev/null || true
find "$NOVAHIZ_DIR"/scripts -name "*.sh" -o -name "*.py" | xargs chmod +x 2>/dev/null || true
find "$NOVAHIZ_DIR"/mcp -name "*.py" -o -name "*.sh" | xargs chmod +x 2>/dev/null || true

# ---- Install Python deps ----
log "Installing Python dependencies..."
pip3 install --user -r "$NOVAHIZ_DIR/requirements.txt" 2>/dev/null || warn "Some Python packages failed"

# ---- Install Node dependencies (TradingView MCP) ----
if [ -f "$NOVAHIZ_DIR/mcp/tradingview-mcp/package.json" ]; then
    log "Installing TradingView MCP dependencies..."
    cd "$NOVAHIZ_DIR/mcp/tradingview-mcp" && npm install --production 2>/dev/null && ok "TradingView MCP ready" || warn "TradingView MCP npm install skipped"
    cd "$NOVAHIZ_DIR"
fi

# ---- Run component setup ----
if [ -f "$NOVAHIZ_DIR/installers/setup-novahiz.sh" ]; then
    log "Installing components..."
    bash "$NOVAHIZ_DIR/installers/setup-novahiz.sh" || warn "Some components had warnings"
fi

# ---- Symlink CLI tools ----
log "Setting up CLI..."
mkdir -p "$HOME/.local/bin"

for tool in "$NOVAHIZ_DIR/bin"/*; do
    name=$(basename "$tool")
    if [ ! -f "$HOME/.local/bin/$name" ]; then
        ln -sf "$tool" "$HOME/.local/bin/$name" 2>/dev/null || true
    fi
done

# Add to PATH
PATH_ENTRIES='export PATH="$HOME/.local/bin:$PATH"'
if [ -f "$HOME/.bashrc" ] && ! grep -q '\.local/bin' "$HOME/.bashrc"; then
    echo "$PATH_ENTRIES" >> "$HOME/.bashrc"
fi
if [ -f "$HOME/.zshrc" ] && ! grep -q '\.local/bin' "$HOME/.zshrc"; then
    echo "$PATH_ENTRIES" >> "$HOME/.zshrc"
fi
export PATH="$HOME/.local/bin:$PATH"

# ---- Alias ----
if ! command -v nv &>/dev/null; then
    alias nv='opencode' 2>/dev/null || true
fi

# =============================================================================
# PHASE 4: CONFIG WIZARD
# =============================================================================
header "PHASE 4/5 — Configuration"

if [ "$YES" = true ]; then
    log "Non-interactive mode: using defaults"
    warn "Installation will be minimal without API keys."
    warn "Run 'nv config' later to configure API keys."
else
    log "Running configuration wizard..."

    if [ -f "$NOVAHIZ_DIR/config-wizard/wizard.sh" ]; then
        bash "$NOVAHIZ_DIR/config-wizard/wizard.sh" || true
    else
        warn "Config wizard not found, skipping"
    fi
fi

# =============================================================================
# PHASE 5: VALIDATION
# =============================================================================
header "PHASE 5/5 — Validation"

errors=0
passed=0

check() {
    local label="$1"
    local cmd="$2"
    if eval "$cmd" &>/dev/null; then
        ok "$label"
        passed=$((passed + 1))
    else
        fail "$label"
        errors=$((errors + 1))
    fi
}

check "Python 3.10+"      "python3 -c 'import sys; assert sys.version_info >= (3,10)'"
check "Node.js 18+"       "node -e 'process.exit(Number(process.version.slice(1).split(\".\")[0] < 18))'"
check "Git installed"     "git --version"
check "Novahiz directory" "[ -d '$NOVAHIZ_DIR/engine' ]"
check "MCP server"        "[ -f '$NOVAHIZ_DIR/mcp/novahiz-mcp.py' ]"
check "Agent configs"     "[ -f '$NOVAHIZ_DIR/agents/novahiz-router.yaml' ]"
check "CLI tools"         "[ -f '$NOVAHIZ_DIR/bin/nv' ]"
check "Skills directory"  "[ -d '$NOVAHIZ_DIR/.agents/skills' ] || [ -d '$NOVAHIZ_DIR/skills' ]"
check "Config directory"  "[ -f '$NOVAHIZ_DIR/opencode.json' ]"
check "Runtime engine"    "[ -f '$NOVAHIZ_DIR/runtime/novahiz-unified.py' ]"

# Deep validation with Python script
if [ -f "$NOVAHIZ_DIR/config-wizard/final-validation.py" ]; then
    python3 "$NOVAHIZ_DIR/config-wizard/final-validation.py" || true
fi

echo ""
if [ "$errors" -eq 0 ]; then
    echo -e "\n${GREEN}${BOLD}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║  🚀 NOVAHIZ OS v6.0 — INSTALLED SUCCESSFULLY!  ║${NC}"
    echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}Quick start:${NC}"
    echo -e "    nv route \"explore this project\"      ${GREEN}← Route a task${NC}"
    echo -e "    nv agents                            ${GREEN}← List all agents${NC}"
    echo -e "    nv health                            ${GREEN}← System health check${NC}"
    echo -e "    opencode                             ${GREEN}← Launch OpenCode${NC}"
    echo ""
    echo -e "  ${BOLD}Docs:${NC} $NOVAHIZ_DIR/docs/"
    echo -e "  ${BOLD}Logs:${NC} $NOVAHIZ_DIR/logs/"
    echo ""

    # Suggest restarting shell
    if [ "$SHELL" != "$(ps -p $$ -o comm=)" ] 2>/dev/null; then
        echo -e "  ${YELLOW}Tip: Restart your shell or run: source ~/.bashrc${NC}"
    fi
else
    echo -e "\n${YELLOW}${BOLD}⚠️  $errors checks failed, $passed passed${NC}"
    echo -e "${YELLOW}See $NOVAHIZ_DIR/logs/install.log for details${NC}"
    exit 1
fi
