#!/bin/bash
# Novahiz OS - Secret Scanner
# Scans codebase for potential secrets, API keys, and credentials

set -e

echo "🔍 Novahiz OS Secret Scanner"
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""

SCAN_DIR="${1:-.}"
REPORT_FILE="/tmp/secrets_report_$(date +%Y%m%d_%H%M%S).txt"
ERRORS=0

# Patterns to scan
PATTERNS=(
    "password\s*[:=]\s*[\"'][A-Za-z0-9+/=]{8,}[\"']"
    "secret\s*[:=]\s*[\"'][A-Za-z0-9+/=]{8,}[\"']"
    "api_key\s*[:=]\s*[\"'][A-Za-z0-9+/=]{8,}[\"']"
    "apikey\s*[:=]\s*[\"'][A-Za-z0-9+/=]{8,}[\"']"
    "token\s*[:=]\s*[\"'][A-Za-z0-9+/=]{8,}[\"']"
    "private_key\s*[:=]\s*[\"']-----BEGIN"
    "aws_access_key_id\s*[:=]\s*[\"']AKIA[A-Z0-9]{16}[\"']"
    "aws_secret_access_key\s*[:=]\s*[\"'][A-Za-z0-9+/=]{40}[\"']"
    "ghp_[A-Za-z0-9]{36}"
    "github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59}"
    "xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24}"
    "sk-[A-Za-z0-9]{48}"
    "Bearer\s+[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+\.[A-Za-z0-9\-_]+"
)

echo "Scanning: $SCAN_DIR"
echo "Report: $REPORT_FILE"
echo ""

# Scan for each pattern
for pattern in "${PATTERNS[@]}"; do
    MATCHES=$(grep -rInE "$pattern" \
        --include="*.py" --include="*.js" --include="*.ts" \
        --include="*.json" --include="*.yaml" --include="*.yml" \
        --include="*.sh" --include="*.env" --include="*.conf" \
        --exclude-dir=node_modules --exclude-dir=.git \
        --exclude-dir=__pycache__ --exclude-dir=*.egg-info \
        --exclude="scan-secrets.sh" \
        "$SCAN_DIR" 2>/dev/null || true)
    
    if [ -n "$MATCHES" ]; then
        echo "⚠️  Pattern: $pattern" >> "$REPORT_FILE"
        echo "$MATCHES" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check for files that shouldn't be committed
echo "Checking for sensitive files..."
SENSITIVE_FILES=$(find "$SCAN_DIR" -type f \( \
    -name "*.key" -o \
    -name "*.pem" -o \
    -name "*.p12" -o \
    -name "*.pfx" -o \
    -name "id_rsa*" -o \
    -name "id_ed25519*" -o \
    -name ".env*" -o \
    -name "*credentials*" -o \
    -name "*secrets*" \
    \) 2>/dev/null | grep -v node_modules | grep -v .git | grep -v "scan-secrets.sh" || true)

if [ -n "$SENSITIVE_FILES" ]; then
    echo "⚠️  Sensitive files found:" >> "$REPORT_FILE"
    echo "$SENSITIVE_FILES" >> "$REPORT_FILE"
    ERRORS=$((ERRORS + 1))
fi

# Check git history for leaked secrets (if git repo)
if [ -d ".git" ]; then
    echo "Checking git history (last 10 commits)..."
    GIT_SECRETS=$(git log -p --all -n 10 2>/dev/null | \
        grep -iE "(password|secret|api_key|token)\s*[:=]\s*[\"'][A-Za-z0-9+/=]{8,}" | \
        head -10 || true)
    
    if [ -n "$GIT_SECRETS" ]; then
        echo "⚠️  Potential secrets in git history:" >> "$REPORT_FILE"
        echo "$GIT_SECRETS" >> "$REPORT_FILE"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Report
echo ""
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ No secrets detected!"
    rm -f "$REPORT_FILE"
    exit 0
else
    echo "🚨 $ERRORS potential secret issue(s) found!"
    echo ""
    echo "Review report: $REPORT_FILE"
    echo ""
    echo "CAT /tmp/secrets_report*.txt to see details"
    echo ""
    echo "REMEDIATION:"
    echo "1. Remove secrets from code immediately"
    echo "2. Rotate exposed credentials"
    echo "3. Use environment variables or secret managers"
    echo "4. Add sensitive files to .gitignore"
    echo ""
    exit 1
fi
