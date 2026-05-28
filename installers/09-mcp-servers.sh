#!/bin/bash
# =============================================================================
# Novahiz OS — MCP Servers Configuration
# Patches opencode.json with correct paths for this user
# =============================================================================
set -e
source "$(dirname "$0")/lib/common.sh"

header "MCP Servers"

OPENCODE_CONFIG="$NOVAHIZ_DIR/opencode.json"

if [ ! -f "$OPENCODE_CONFIG" ]; then
    warn "opencode.json not found, creating..."
    cat > "$OPENCODE_CONFIG" << 'JSON'
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "novahiz-router",
  "model": "opencode/qwen3.5-plus",
  "small_model": "opencode/qwen3.5-plus",
  "instructions": ["AGENTS.md"],
  "skills": {
    "paths": ["$NOVAHIZ_DIR/skills", "$NOVAHIZ_DIR/.agents/skills"]
  },
  "mcp": {
    "novahiz": {
      "type": "local",
      "command": "python3",
      "args": ["$NOVAHIZ_DIR/mcp/novahiz-mcp.py", "--mcp"],
      "enabled": true
    },
    "obsidian": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@wickedevolutions/mcp-obsidian"],
      "env": { "OBSIDIAN_VAULT_PATH": "$HOME/Documents/llm-wiki" },
      "enabled": true
    },
    "tradingview": {
      "type": "local",
      "command": "node",
      "args": ["$NOVAHIZ_DIR/mcp/tradingview-mcp/server.js"],
      "enabled": true
    },
    "stitch": {
      "type": "local",
      "command": "python3",
      "args": ["$NOVAHIZ_DIR/mcp/stitch-mcp-wrapper.py"],
      "enabled": false
    },
    "supabase": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@supabase/mcp-server-supabase@latest", "--project-ref", "nfmsyivyhsjatazhcjgu"],
      "env": { "SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}" },
      "enabled": false
    },
    "github": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" },
      "enabled": false
    }
  },
  "tools": {
    "novahiz_route": true,
    "novahiz_auto": true,
    "novahiz_execute": true,
    "novahiz_list_agents": true,
    "novahiz_search": true,
    "novahiz_health": true
  }
}
JSON
fi

# Replace placeholders with actual paths
sed -i "s|\$NOVAHIZ_DIR|$NOVAHIZ_DIR|g" "$OPENCODE_CONFIG"
sed -i "s|\$HOME|$HOME|g" "$OPENCODE_CONFIG"

# Verify MCP entries
for mcp in novahiz obsidian tradingview stitch supabase github; do
    if grep -q "\"$mcp\"" "$OPENCODE_CONFIG" 2>/dev/null; then
        sub "$mcp: configured"
    fi
done

ok "MCP servers configured in opencode.json"
check "opencode.json" "[ -f '$OPENCODE_CONFIG' ]"
summary
