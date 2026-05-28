#!/bin/bash
# Novahiz OS — GitHub Sync Script
# Secure deployment to existing GitHub repository

set -e

echo "🔄 Novahiz OS — GitHub Sync"
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""

# Configuration
GITHUB_USER="${GITHUB_USER:-}"
REPO_NAME="${REPO_NAME:-novahiz-os}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# Validation
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN not set"
    echo ""
    echo "Setup:"
    echo "  export GITHUB_TOKEN='your_token'"
    echo "  export GITHUB_USER='your_username'"
    echo ""
    exit 1
fi

if [ -z "$GITHUB_USER" ]; then
    echo "❌ GITHUB_USER not set"
    echo "  export GITHUB_USER='your_username'"
    exit 1
fi

REPO_URL="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"

cd "$(dirname "$0")/.."

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init --quiet
    git config user.email "novahiz-os@local"
    git config user.name "Novahiz OS"
    echo "  ✓ Git initialized"
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo "🔗 Adding GitHub remote..."
    git remote add origin "$REPO_URL"
    echo "  ✓ Remote added: github.com/${GITHUB_USER}/${REPO_NAME}"
else
    echo "  ✓ Remote already configured"
fi

# Check current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
echo ""
echo "📊 Current branch: $CURRENT_BRANCH"

# Status
echo ""
echo "📝 Git status:"
git status --short | head -20

# Count changes
CHANGED_FILES=$(git status --short | wc -l)
echo ""
echo "📈 Changes to commit: $CHANGED_FILES files"

if [ "$CHANGED_FILES" -gt 0 ]; then
    echo ""
    echo "📦 Staging changes..."
    git add -A
    
    echo "💬 Commit message:"
    read -p "Enter commit message (or press enter for auto): " COMMIT_MSG
    
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="v6.0 Production Ready - $(date +%Y-%m-%d)"
    fi
    
    git commit -m "$COMMIT_MSG"
    echo "  ✓ Committed: $COMMIT_MSG"
fi

# Push
echo ""
echo "🚀 Pushing to GitHub..."
echo "   Repository: github.com/${GITHUB_USER}/${REPO_NAME}"

git branch -M main 2>/dev/null || true

if git push -u origin main --force 2>&1; then
    echo "  ✓ Pushed successfully!"
    echo ""
    echo "✅ Sync complete!"
    echo ""
    echo "📬 View your repository:"
    echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}"
else
    echo "  ❌ Push failed"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check token permissions (repo, workflow)"
    echo "  2. Verify repository exists: https://github.com/new"
    echo "  3. Try: git push -u origin main"
    exit 1
fi

echo ""
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""
echo "🎉 Deployment complete!"
