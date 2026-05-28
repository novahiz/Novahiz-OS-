#!/bin/bash
# =============================================================================
# run-linters.sh — Code Quality Tools v6.1.0
# =============================================================================

NOVAHIZ_DIR="$HOME/.opencode"
BLACK=~/.local/bin/black
FLAKE8=~/.local/bin/flake8
PYLINT=~/.local/bin/pylint

echo "═══════════════════════════════════════════════════════════"
echo "  NOVAHIZ OS — CODE QUALITY CHECK v6.1.0"
echo "═══════════════════════════════════════════════════════════"
echo ""

cd "$NOVAHIZ_DIR"

echo "1. BLACK (Code Format)"
echo "─────────────────────────────────────────────────────────────"
$BLACK mcp/ runtime/ engine/ scripts/ api/ plugins/ tests/ --check 2>&1 | tail -5
echo ""

echo "2. FLAKE8 (Linting)"
echo "─────────────────────────────────────────────────────────────"
ERRORS=$($FLAKE8 mcp/ runtime/ engine/ scripts/ api/ plugins/ tests/ --max-line-length=120 --ignore=E501,W503,E402 2>&1 | wc -l)
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ No flake8 errors"
else
    echo "⚠️  $ERRORS flake8 warnings (mostly style)"
fi
echo ""

echo "3. PYLINT (Deep Analysis)"
echo "─────────────────────────────────────────────────────────────"
echo "Running pylint on main modules..."
$PYLINT runtime/novahiz-unified.py --disable=all --enable=E 2>&1 | tail -5
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "  TIP: Run '$BLACK mcp/ runtime/ engine/ scripts/ api/ plugins/ tests/' to auto-fix format"
echo "═══════════════════════════════════════════════════════════"
