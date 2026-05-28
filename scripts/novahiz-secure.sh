#!/bin/bash
# =============================================================================
# novahiz-secure.sh — Security Audit v6.0
# Verifies API keys are in ~/.novahiz/.env (NOT in .bashrc or config files)
# =============================================================================

NOVAHIZ_DIR="$HOME/.opencode"
CONFIG_FILE="$NOVAHIZ_DIR/runtime/config.json"
ENV_FILE="$HOME/.novahiz/.env"

echo "═══════════════════════════════════════════════════════════"
echo "  NOVAHIZ OS — SECURITY AUDIT v6.0"
echo "═══════════════════════════════════════════════════════════"
echo ""

ISSUES=0

# 1. Check .env exists
if [ -f "$ENV_FILE" ]; then
    echo "✅ $ENV_FILE exists"
    perms=$(stat -c "%a" "$ENV_FILE" 2>/dev/null)
    if [ "$perms" = "600" ]; then
        echo "✅ Permissions: 600 (secure)"
    else
        echo "⚠️  Permissions: $perms (should be 600)"
        chmod 600 "$ENV_FILE"
        echo "✅ Fixed permissions to 600"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo "❌ $ENV_FILE not found"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# 2. Check no API keys in .bashrc
if grep -q "OPENROUTER_API_KEY\|OPENCODE_ZEN_API_KEY" ~/.bashrc 2>/dev/null; then
    echo "❌ API keys found in .bashrc (SECURITY RISK)"
    ISSUES=$((ISSUES + 1))
else
    echo "✅ No API keys in .bashrc"
fi
echo ""

# 3. Check no API keys in config.json
if grep -q "sk-or-v1\|sk-TnPvEk" "$CONFIG_FILE" 2>/dev/null; then
    echo "❌ API keys found in config.json (SECURITY RISK)"
    ISSUES=$((ISSUES + 1))
else
    echo "✅ No API keys in config.json"
fi
echo ""

# 4. Check .gitignore
if [ -f "$NOVAHIZ_DIR/.gitignore" ]; then
    echo "✅ .gitignore exists"
    if grep -q ".env" "$NOVAHIZ_DIR/.gitignore"; then
        echo "✅ .env excluded from git"
    else
        echo "⚠️  .env not in .gitignore"
        ISSUES=$((ISSUES + 1))
    fi
else
    echo "❌ .gitignore not found"
    ISSUES=$((ISSUES + 1))
fi
echo ""

echo "═══════════════════════════════════════════════════════════"
if [ $ISSUES -eq 0 ]; then
    echo "  ✅ SECURITY AUDIT PASSED (0 issues)"
else
    echo "  ⚠️  SECURITY AUDIT: $ISSUES issue(s) found"
fi
echo "═══════════════════════════════════════════════════════════"

exit $ISSUES
