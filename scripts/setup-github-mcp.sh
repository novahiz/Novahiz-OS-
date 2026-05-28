#!/bin/bash
# Novahiz OS — GitHub MCP Server Setup
# Installs and configures GitHub MCP server

set -e

echo "🐙 GitHub MCP Server Setup"
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""

# =============================================================================
# SECURITY WARNING
# =============================================================================
echo "⚠️  SECURITY WARNING:"
echo ""
echo "The token you provided (ghp_WGOM...HjgP) has been exposed in chat."
echo "It SHOULD BE REVOKED immediately:"
echo "  https://github.com/settings/tokens"
echo ""
echo "This script will NOT use that token."
echo "You must create a NEW token after revoking the old one."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# =============================================================================
# INSTALL GITHUB MCP SERVER
# =============================================================================
echo ""
echo "📦 Installing GitHub MCP Server..."

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ npx not found. Install Node.js first."
    exit 1
fi

# Install via npx (GitHub official MCP server)
# https://github.com/github/github-mcp-server
echo "  Installing @github/github-mcp-server..."

# Create MCP config directory
MCP_DIR="$HOME/.opencode/mcp/github-mcp"
mkdir -p "$MCP_DIR"

# Create package.json for GitHub MCP
cat > "$MCP_DIR/package.json" << 'EOF'
{
  "name": "github-mcp-server",
  "version": "1.0.0",
  "description": "GitHub MCP Server for Novahiz OS",
  "dependencies": {
    "@modelcontextprotocol/server-github": "latest"
  }
}
EOF

# Install dependencies
cd "$MCP_DIR"
npm install --silent 2>/dev/null || {
    echo "⚠️  npm install failed. Manual setup required."
    echo ""
    echo "Alternative: Use npx directly in opencode.json"
}

# =============================================================================
# CONFIGURE OPENCODE
# =============================================================================
echo ""
echo "📝 Configuring opencode.json..."

CONFIG_FILE="$HOME/.opencode/opencode.json"

# Backup existing config
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "  ✓ Backup created"
fi

# Create new config with GitHub MCP
cat > "$CONFIG_FILE" << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "novahiz-router",
  "model": "opencode/qwen3.5-plus",
  "small_model": "opencode/qwen3.5-plus",
  "instructions": ["AGENTS.md"],
  "skills": {
    "paths": ["~/.opencode/skills", "~/.opencode/.agents/skills"]
  },
  "mcp": {
    "novahiz": {
      "type": "local",
      "command": "python3",
      "args": ["/home/novahiz/.opencode/mcp/novahiz-mcp.py", "--mcp"],
      "enabled": true
    },
    "github": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      },
      "enabled": true
    }
  },
  "tools": {
    "novahiz_route": true,
    "novahiz_auto": true,
    "novahiz_execute": true,
    "novahiz_list_agents": true,
    "novahiz_search": true,
    "novahiz_health": true,
    "github": true
  }
}
EOF

echo "  ✓ opencode.json updated"

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================
echo ""
echo "🔐 Environment Setup"
echo ""
echo "Add to your ~/.bashrc or ~/.zshrc:"
echo ""
echo '  # GitHub MCP Token (SECURE)'
echo '  export GITHUB_TOKEN="your_NEW_token_here"'
echo ""

# Create .env.example (not committed to git)
cat > "$HOME/.opencode/.env.example" << 'EOF'
# GitHub MCP Server Token
# Create at: https://github.com/settings/tokens
# Scopes: repo, workflow, read:user
GITHUB_TOKEN=your_token_here
EOF

echo "  ✓ .env.example created"

# =============================================================================
# VERIFICATION
# =============================================================================
echo ""
echo "✅ Setup Complete!"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. REVOKE old token:"
echo "   https://github.com/settings/tokens"
echo ""
echo "2. CREATE new token:"
echo "   - Scopes: repo, workflow, read:user"
echo "   - Copy the new token"
echo ""
echo "3. SET environment variable:"
echo "   export GITHUB_TOKEN='your_new_token'"
echo ""
echo "4. RESTART opencode to load GitHub MCP"
echo ""
echo "5. VERIFY GitHub MCP is running:"
echo "   Check opencode MCP status"
echo ""
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""
