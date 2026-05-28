#!/bin/bash
# =============================================================================
# run-coverage.sh — Test Coverage Report v6.0.1
# Note: Current tests are integration tests (CLI/config), not unit tests
# Coverage will be low because tests don't import MCP/runtime modules directly
# =============================================================================

NOVAHIZ_DIR="$HOME/.opencode"
TESTS_DIR="$NOVAHIZ_DIR/tests"
COVERAGE=~/.local/bin/coverage

echo "═══════════════════════════════════════════════════════════"
echo "  NOVAHIZ OS — TEST COVERAGE v6.0.1"
echo "═══════════════════════════════════════════════════════════"
echo ""

cd "$TESTS_DIR"

echo "Running tests with coverage..."
python3 -m $COVERAGE run --source="$NOVAHIZ_DIR/mcp,$NOVAHIZ_DIR/runtime" \
    --omit="*/tests/*,*/__pycache__/*" \
    test_novahiz.py 2>&1 | tail -5

echo ""
echo "Coverage Report:"
python3 -m $COVERAGE report --omit="*/tests/*,*/__pycache__/*"

echo ""
echo "NOTE: Low coverage is expected - tests focus on integration (CLI/config)"
echo "      not unit testing of MCP/runtime modules."
echo ""
echo "HTML Report: $NOVAHIZ_DIR/tests/coverage_html/index.html"
python3 -m $COVERAGE html --omit="*/tests/*,*/__pycache__/*"

echo ""
echo "═══════════════════════════════════════════════════════════"
