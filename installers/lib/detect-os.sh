# =============================================================================
# Novahiz OS — OS Detection Library
# Detects OS, distribution, package manager, architecture
# =============================================================================

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

    # Architecture normalization
    case "$ARCH" in
        x86_64|amd64) ARCH="x64" ;;
        aarch64|arm64) ARCH="arm64" ;;
        i386|i686) ARCH="x86" ;;
    esac

    if [ "$OS" = "linux" ]; then
        if command -v apt &>/dev/null; then
            DISTRO="debian"; PKG="apt"
            PKG_INSTALL="apt install -y"
            PKG_UPDATE="apt update"
        elif command -v dnf &>/dev/null; then
            DISTRO="fedora"; PKG="dnf"
            PKG_INSTALL="dnf install -y"
            PKG_UPDATE="dnf check-update || true"
        elif command -v pacman &>/dev/null; then
            DISTRO="arch"; PKG="pacman"
            PKG_INSTALL="pacman -S --noconfirm"
            PKG_UPDATE="pacman -Sy"
        elif command -v zypper &>/dev/null; then
            DISTRO="suse"; PKG="zypper"
            PKG_INSTALL="zypper install -y"
            PKG_UPDATE="zypper refresh"
        elif command -v apk &>/dev/null; then
            DISTRO="alpine"; PKG="apk"
            PKG_INSTALL="apk add --no-cache"
            PKG_UPDATE="apk update"
        fi

        if grep -qi microsoft /proc/version 2>/dev/null; then
            DISTRO="${DISTRO}-wsl"
        fi

        # Desktop environment
        if [ -n "$XDG_CURRENT_DESKTOP" ]; then
            DESKTOP="$XDG_CURRENT_DESKTOP"
        elif [ -n "$GDMSESSION" ]; then
            DESKTOP="$GDMSESSION"
        else
            DESKTOP="unknown"
        fi
    fi

    if [ "$OS" = "macos" ]; then
        PKG="brew"
        if ! command -v brew &>/dev/null; then
            PKG_INSTALL='arch -arm64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            BREW_NOT_INSTALLED=true
        else
            PKG_INSTALL="brew install"
            BREW_NOT_INSTALLED=false
        fi
    fi

    if [ "$OS" = "windows" ]; then
        PKG="winget"
        PKG_INSTALL="winget install -e --id"
        # Detect PowerShell version
        POWERSHELL_VERSION=$(powershell -Command '$PSVersionTable.PSVersion.ToString()' 2>/dev/null || echo "unknown")
    fi

    export OS ARCH DISTRO PKG PKG_INSTALL PKG_UPDATE
}

# Run if executed directly
if [ "$(basename "$0")" = "detect-os.sh" ]; then
    detect_os
    echo "OS: $OS"
    echo "Arch: $ARCH"
    echo "Distro: $DISTRO"
    echo "Package Manager: $PKG"
fi
