#!/bin/bash
# =============================================================================
# run-linters.sh — Code Quality Tools v6.0.1
# =============================================================================

NOVAHIZ_DIR="$HOME/.opencode"
BLACK=~/.local/bin/black
FLAKE8=~/.local/bin/flake8
PYLINT=~/.local/bin/pylint

echo "═══════════════════════════════════════════════════════════"
echo "  NOVAHIZ OS — CODE QUALITY CHECK v6.0.1"
echo "═══════════════════════════════════════════════════════════"
echo ""

cd "$NOVAHIZ_DIR"

echo "1. BLACK (Code Format)"
echo "─────────────────────────────────────────────────────────────"
$BLACK mcp/*.py runtime/*.py --check 2>&1 | tail -5
echo ""

echo "2. FLAKE8 (Linting)"
echo "─────────────────────────────────────────────────────────────"
ERRORS=$($FLAKE8 mcp/*.py runtime/*.py --max-line-length=120 --ignore=E501,W503,E402 2>&1 | wc -l)
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ No flake8 errors"
else
    echo "⚠️  $ERRORS flake8 warnings (mostly style)"
fi
echo ""

echo "3. PYLINT (Deep Analysis)"
echo "─────────────────────────────────────────────────────────────"
echo "Running pylint on main modules..."
$PYLINT runtime/novahiz-runtime.py --disable=all --enable=E 2>&1 | tail -5
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "  TIP: Run '$BLACK mcp/*.py runtime/*.py' to auto-fix format"
echo "═══════════════════════════════════════════════════════════"
