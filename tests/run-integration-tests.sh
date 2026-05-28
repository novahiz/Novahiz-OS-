#!/bin/bash
# =============================================================================
# Novahiz OS — Integration Test Suite
# Tests end-to-end functionality
# =============================================================================

NOVAHIZ_DIR="$HOME/.opencode"
SCRIPTS_DIR="$NOVAHIZ_DIR/scripts"
TESTS_DIR="$NOVAHIZ_DIR/tests"

echo "═══════════════════════════════════════════════════════"
echo "  NOVAHIZ OS v6.0 — INTEGRATION TESTS"
echo "═══════════════════════════════════════════════════════"
echo ""

PASSED=0
FAILED=0

test_case() {
    local name="$1"
    local cmd="$2"
    local expected="$3"
    
    echo -n "Testing: $name... "
    
    result=$(eval "$cmd" 2>&1)
    
    if echo "$result" | grep -qi "$expected"; then
        echo -e "✅ PASS"
        PASSED=$((PASSED + 1))
    else
        echo -e "❌ FAIL"
        echo "  Expected: $expected"
        echo "  Got: $result"
        FAILED=$((FAILED + 1))
    fi
}

# Test 1: CLI commands exist
test_case "nv command exists" "which nv" "novahiz"

# Test 2: nv status works
test_case "nv status" "timeout 5 nv status" "NOVAHIZ OS"

# Test 3: nv health works
test_case "nv health" "timeout 5 nv health" "SYSTEM HEALTH"

# Test 4: metrics script works
test_case "metrics script" "timeout 5 python3 $NOVAHIZ_DIR/metrics/metrics.py" "USAGE STATISTICS"

# Test 5: Daemons running
test_case "Runtime daemon" "pgrep -f novahiz-unified.py" "[0-9]"

# Test 6: Bridge daemon
test_case "Bridge daemon" "pgrep -f opencode-bridge.py" "[0-9]"

# Test 7: MCP HTTP
test_case "MCP HTTP" "pgrep -f novahiz-mcp-http.py" "[0-9]"

# Test 8: Health endpoint
test_case "Health endpoint" "curl -s http://127.0.0.1:8765/health" "healthy"

# Test 9: API keys in env
test_case "OPENROUTER_API_KEY" "env | grep OPENROUTER" "OPENROUTER"

# Test 10: API keys in env
test_case "OPENCODE_ZEN_API_KEY" "env | grep OPENCODE" "OPENCODE"

# Test 11: Config exists
test_case "config.json exists" "test -f $NOVAHIZ_DIR/runtime/config.json" ""

# Test 12: Config secure permissions
perms=$(stat -c "%a" "$NOVAHIZ_DIR/runtime/config.json" 2>/dev/null)
if [ "$perms" = "600" ]; then
    echo -e "Testing: Config permissions (600)... ✅ PASS"
    PASSED=$((PASSED + 1))
else
    echo -e "Testing: Config permissions (600)... ❌ FAIL (got $perms)"
    FAILED=$((FAILED + 1))
fi

# Test 13: No API keys in config
if ! grep -q "sk-or-v1" "$NOVAHIZ_DIR/runtime/config.json" 2>/dev/null; then
    echo -e "Testing: No API keys in config... ✅ PASS"
    PASSED=$((PASSED + 1))
else
    echo -e "Testing: No API keys in config... ❌ FAIL"
    FAILED=$((FAILED + 1))
fi

# Test 14: Metrics file exists
test_case "metrics/usage.json" "test -f $NOVAHIZ_DIR/metrics/usage.json" ""

# Test 15: Documentation exists
test_case "README.md" "test -f $NOVAHIZ_DIR/README.md" ""

# Test 15b: MAINTENANCE.md exists
test_case "MAINTENANCE.md" "test -f $NOVAHIZ_DIR/MAINTENANCE.md" ""

# Test 16: Executions directory
test_case "executions directory" "test -d $NOVAHIZ_DIR/executions" ""

# Test 17: Recent executions have results
recent=$(ls -t "$NOVAHIZ_DIR/executions"/exec_*.json 2>/dev/null | head -1)
if [ -n "$recent" ] && grep -q '"result"' "$recent" 2>/dev/null; then
    echo -e "Testing: Recent executions have results... ✅ PASS"
    PASSED=$((PASSED + 1))
else
    echo -e "Testing: Recent executions have results... ❌ FAIL"
    FAILED=$((FAILED + 1))
fi

# Test 18: OpenCode CLI works
test_case "opencode CLI" "timeout 10 opencode --version" "[0-9]"

echo ""
echo "═══════════════════════════════════════════════════════"
echo "  INTEGRATION TEST SUMMARY"
echo "═══════════════════════════════════════════════════════"
echo "  Passed: $PASSED"
echo "  Failed: $FAILED"
echo "  Total:  $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "  Status: ${GREEN}✅ ALL TESTS PASSED${NC}"
    exit 0
else
    echo -e "  Status: ${RED}⚠️  SOME TESTS FAILED${NC}"
    exit 1
fi
