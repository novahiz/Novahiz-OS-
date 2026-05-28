#!/bin/bash
# =============================================================================
# Novahiz OS — Configuration Wizard
# Interactive setup for API keys, model routing, Obsidian vault
# =============================================================================
set -e
NOVAHIZ_DIR="${NOVAHIZ_DIR:-$HOME/.opencode}"
LIB_DIR="$NOVAHIZ_DIR/installers/lib"

[ -f "$LIB_DIR/common.sh" ] && source "$LIB_DIR/common.sh"

# Source detection
[ -f "$LIB_DIR/detect-os.sh" ] && source "$LIB_DIR/detect-os.sh"
detect_os 2>/dev/null || true

cd "$NOVAHIZ_DIR"

# ---- Banner ----
echo ""
echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║        NOVAHIZ OS v6.0 — Configuration Wizard        ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# ---- Step 1: Collect API Keys ----
header "Step 1: API Keys"
echo -e "  ${DIM}API keys are stored encrypted in ~/.novahiz/.env${NC}"
echo ""

ENV_FILE="$NOVAHIZ_ENV_DIR/.env"
mkdir -p "$NOVAHIZ_ENV_DIR"
touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

collect_key() {
    local name="$1" var="$2" required="$3" url="$4"
    local current=""

    # Check if already stored
    if grep -q "^${var}=" "$ENV_FILE" 2>/dev/null; then
        current=$(grep "^${var}=" "$ENV_FILE" | cut -d'=' -f2-)
        log "$name already configured ($(echo "${current:0:8}..."))"
        if [ "$required" = true ] && [ "${YES:-false}" != true ]; then
            echo -en "  ${YELLOW}?${NC} Re-enter $name? ${DIM}(y/N)${NC} "
            read -r response
            [[ "$response" =~ ^[Yy]$ ]] || return 0
        else
            return 0
        fi
    fi

    while true; do
        echo -en "  ${CYAN}?${NC} Enter your $name API key"
        [ "$required" = true ] && echo -e " ${RED}${BOLD}(required)${NC}" || echo -e " ${DIM}(optional)${NC}"
        echo -en "  ${DIM}  >${NC} "
        read -r key

        if [ -z "$key" ]; then
            if [ "$required" = true ]; then
                warn "$name is required. Enter a valid key or press Ctrl+C to exit."
                continue
            else
                warn "Skipping $name"
                return 0
            fi
        fi

        # Test key if URL provided
        if [ -n "$url" ]; then
            log "Testing key..."
            if curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $key" "$url" | grep -q "20[0-9]"; then
                ok "Key validated ✓"
            else
                warn "Could not validate key (API may need different endpoint)"
                echo -en "  ${YELLOW}?${NC} Save anyway? ${DIM}(y/N)${NC} "
                read -r save
                [[ "$save" =~ ^[Yy]$ ]] || continue
            fi
        fi

        # Save to .env
        if grep -q "^${var}=" "$ENV_FILE" 2>/dev/null; then
            sed -i "s|^${var}=.*|${var}=${key}|" "$ENV_FILE"
        else
            echo "${var}=${key}" >> "$ENV_FILE"
        fi
        export "$var"="$key"
        ok "$name saved"
        break
    done
}

# OpenRouter is REQUIRED
collect_key "OpenRouter" "OPENROUTER_API_KEY" true "https://openrouter.ai/api/v1/auth/key"

# Opencode Zen is OPTIONAL
collect_key "OpenCode Zen" "OPENCODE_ZEN_API_KEY" false ""

# Supabase is OPTIONAL
collect_key "Supabase" "SUPABASE_ACCESS_TOKEN" false ""

# GitHub is OPTIONAL
collect_key "GitHub" "GITHUB_TOKEN" false "https://api.github.com/user"

echo ""
ok "API keys configured in $ENV_FILE"

# ---- Step 2: Configure Model Router ----
header "Step 2: Model Router Configuration"

MODEL_ROUTER="$NOVAHIZ_DIR/config/model-router.json"
if [ -f "$MODEL_ROUTER" ]; then
    log "Using model-router.json from repo"
    ok "Model router ready"
else
    warn "model-router.json not found, creating default..."
    mkdir -p "$NOVAHIZ_DIR/config"
    cat > "$MODEL_ROUTER" << 'EOF'
{
  "v": "1.0",
  "enabled": true,
  "tiers": {
    "flash": {
      "primary": "openrouter/qwen/qwen3.5-9b",
      "fallbacks": ["openrouter/stepfun/step-3.5-flash", "openrouter/qwen/qwen3.5-flash-02-23"],
      "description": "Fast, cheap — Q&A, formatting, search",
      "targetRatio": 0.6
    },
    "smart": {
      "primary": "opencode/qwen3.5-plus",
      "fallbacks": ["openrouter/qwen/qwen3.6-plus"],
      "description": "Balanced — build, refactor, features",
      "targetRatio": 0.3
    },
    "premium": {
      "primary": "openrouter/qwen/qwen3.6-plus",
      "fallbacks": ["opencode/qwen3.6-plus"],
      "description": "Maximum capability — architecture, security",
      "targetRatio": 0.1
    }
  },
  "budget": {
    "premiumPerSession": 3,
    "autoDowngrade": true,
    "downgradeTo": "smart"
  },
  "agentOverrides": {
    "neo-security": "premium",
    "cipher-crypto": "premium",
    "arthur-architecture": "smart",
    "novahiz-router": "smart",
    "athena-initialization": "smart",
    "ralph-execution": "smart",
    "luna-design": "smart",
    "kenzo-performance": "smart",
    "malik-database": "smart",
    "sarah-quality": "smart",
    "victor-strategy": "smart",
    "nexus-api": "smart",
    "ryu-design": "smart",
    "forge-cicd": "flash",
    "orion-devops": "smart",
    "phoenix-crisis": "premium",
    "pulse-realtime": "flash",
    "simon-data": "flash",
    "ralph-browser": "flash",
    "elias-marketing": "smart",
    "vega-legal": "smart",
    "ghost-stealth": "smart",
    "samuel-legal": "smart",
    "atlas-memory": "flash"
  },
  "domainRouting": {
    "security": "premium",
    "cryptography": "premium",
    "architecture": "premium",
    "design": "smart",
    "performance": "smart",
    "database": "smart",
    "api": "smart",
    "execution": "smart",
    "marketing": "smart",
    "strategy": "smart",
    "quality": "smart",
    "memory": "flash",
    "legal": "smart",
    "data": "flash",
    "browser": "flash",
    "realtime": "flash",
    "crisis": "premium",
    "devops": "smart",
    "cicd": "flash"
  }
}
EOF
    ok "Default model-router.json created"
fi

# ---- Step 3: Configure opencode.json ----
header "Step 3: OpenCode Configuration"

OPENCODE_CONFIG="$NOVAHIZ_DIR/opencode.json"
if [ -f "$OPENCODE_CONFIG" ]; then
    # Ensure paths are correct
    sed -i "s|\$NOVAHIZ_DIR|$NOVAHIZ_DIR|g" "$OPENCODE_CONFIG" 2>/dev/null || true
    sed -i "s|\$HOME|$HOME|g" "$OPENCODE_CONFIG" 2>/dev/null || true
    sed -i "s|/home/novahiz|$HOME|g" "$OPENCODE_CONFIG" 2>/dev/null || true
    sed -i "s|/home/novahiz/Documents/llm-wiki|$OBSIDIAN_VAULT|g" "$OPENCODE_CONFIG" 2>/dev/null || true
    ok "opencode.json patched for this user"
fi

# ---- Step 4: Environment Variables ----
header "Step 4: Environment Variables"

ENV_EXPORT="# Novahiz OS — Auto-loaded environment"
for var in OPENROUTER_API_KEY OPENCODE_ZEN_API_KEY SUPABASE_ACCESS_TOKEN GITHUB_TOKEN; do
    if grep -q "^${var}=" "$ENV_FILE" 2>/dev/null; then
        ENV_EXPORT="${ENV_EXPORT}
export ${var}=\"$(grep "^${var}=" "$ENV_FILE" | cut -d'=' -f2-)\""
    fi
done

# Add to shell configs
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
    if [ -f "$rc" ]; then
        if ! grep -q "source.*novahiz.*env" "$rc" 2>/dev/null; then
            echo -e "\n# Novahiz OS — load environment" >> "$rc"
            echo "[ -f \"$NOVAHIZ_ENV_DIR/.env\" ] && set -a && source \"$NOVAHIZ_ENV_DIR/.env\" && set +a" >> "$rc"
            sub "Added env loader to $rc"
        fi
    fi
done

# Export for current session
set -a
source "$ENV_FILE" 2>/dev/null || true
set +a
ok "Environment loaded"

# ---- Step 5: Final Summary ----
header "Configuration Complete"
echo ""
echo -e "  ${BOLD}API Keys configured:${NC}"
grep -o '^[^=]*' "$ENV_FILE" 2>/dev/null | while read -r var; do
    echo -e "    ${GREEN}✓${NC} $var"
done

echo ""
ok "Wizard complete. You can re-run anytime via: bash $NOVAHIZ_DIR/config-wizard/wizard.sh"
