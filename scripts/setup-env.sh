#!/bin/bash
# Export API keys from config.json to environment

CONFIG_FILE="$HOME/.opencode/runtime/config.json"

if [ -f "$CONFIG_FILE" ]; then
    # Extract OpenRouter key
    OR_KEY=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('providers',{}).get('openrouter',{}).get('api_key',''))" 2>/dev/null)
    if [ -n "$OR_KEY" ]; then
        export OPENROUTER_API_KEY="$OR_KEY"
        echo "✅ OPENROUTER_API_KEY exported"
    fi
    
    # Extract OpenCode Zen key
    OZ_KEY=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('providers',{}).get('opencode-zen',{}).get('api_key',''))" 2>/dev/null)
    if [ -n "$OZ_KEY" ]; then
        export OPENCODE_ZEN_API_KEY="$OZ_KEY"
        echo "✅ OPENCODE_ZEN_API_KEY exported"
    fi
    
    # Add to .bashrc if not present
    if [ -n "$OR_KEY" ] && ! grep -q "OPENROUTER_API_KEY" ~/.bashrc 2>/dev/null; then
        echo "export OPENROUTER_API_KEY=\"$OR_KEY\"" >> ~/.bashrc
        echo "✅ Added to .bashrc"
    fi
    
    if [ -n "$OZ_KEY" ] && ! grep -q "OPENCODE_ZEN_API_KEY" ~/.bashrc 2>/dev/null; then
        echo "export OPENCODE_ZEN_API_KEY=\"$OZ_KEY\"" >> ~/.bashrc
        echo "✅ Added to .bashrc"
    fi
else
    echo "❌ Config file not found: $CONFIG_FILE"
    exit 1
fi
