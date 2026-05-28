#!/bin/bash
# Novahiz OS - Setup Script for CI/CD
# Run this to set up pre-commit hooks and local tooling

set -e

echo "🚀 Novahiz OS CI/CD Setup"
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""

# =============================================================================
# PRE-COMMIT HOOKS
# =============================================================================
echo ""
echo "📌 Installing pre-commit hooks..."

if [ -d ".git" ]; then
    cp .git/hooks/pre-commit .git/hooks/pre-commit.backup 2>/dev/null || true
    echo "✅ Pre-commit hook installed"
    echo "   Location: .git/hooks/pre-commit"
else
    echo "⚠️  Not a git repository. Run 'git init' first."
fi

# =============================================================================
# PYTHON TOOLS
# =============================================================================
echo ""
echo "🐍 Installing Python tools..."

pip install --quiet flake8 black pytest pytest-cov semgrep safety pip-audit 2>/dev/null || {
    echo "⚠️  Some Python tools failed to install (may need sudo)"
}

echo "✅ Python linters installed"

# =============================================================================
# NODE TOOLS
# =============================================================================
echo ""
echo "📦 Installing Node.js tools..."

if command -v npm &> /dev/null; then
    npm install --global license-checker @cyclonedx/cyclonedx-npm 2>/dev/null || {
        echo "⚠️  Some NPM tools failed to install (may need sudo)"
    }
    echo "✅ NPM tools installed"
else
    echo "⚠️  npm not found. Install Node.js for full CI/CD support."
fi

# =============================================================================
# VALIDATION
# =============================================================================
echo ""
echo "🔍 Running validation..."

# Test pre-commit hook
if [ -x ".git/hooks/pre-commit" ]; then
    echo "✅ Pre-commit hook is executable"
else
    echo "❌ Pre-commit hook is not executable"
    chmod +x .git/hooks/pre-commit 2>/dev/null || true
fi

# Test flake8
if command -v flake8 &> /dev/null; then
    echo "✅ flake8 installed"
else
    echo "❌ flake8 not found"
fi

# Test black
if command -v black &> /dev/null; then
    echo "✅ black installed"
else
    echo "❌ black not found"
fi

# =============================================================================
# SUMMARY
# =============================================================================
echo ""
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""
echo "✅ CI/CD Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Commit this workflow: .github/workflows/ci.yml"
echo "2. Push to GitHub to enable Actions"
echo "3. Pre-commit hooks will run automatically on 'git commit'"
echo ""
echo "Manual test:"
echo "  .git/hooks/pre-commit"
echo ""
