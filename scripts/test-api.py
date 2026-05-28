#!/usr/bin/env python3
"""Test API connectivity for all configured providers"""

import json
import urllib.request
import sys

CONFIG_FILE = "/home/novahiz/.opencode/runtime/config.json"

def test_provider(provider_id, config):
    api_key = config.get('api_key', '')
    base_url = config.get('base_url', '')
    
    try:
        if provider_id == "openrouter":
            req = urllib.request.Request(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return True, f"{len(data.get('data', []))} modèles"
        
        elif provider_id == "opencode-zen":
            req = urllib.request.Request(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                return True, f"{len(data.get('data', []))} modèles"
    
    except Exception as e:
        return False, str(e)

# Main
try:
    config = json.load(open(CONFIG_FILE))
    providers = config.get('providers', {})
    
    print("═══════════════════════════════════════════════════")
    print("  API CONNECTIVITY TEST")
    print("═══════════════════════════════════════════════════")
    
    for pid, pconfig in providers.items():
        if pconfig.get('enabled'):
            success, msg = test_provider(pid, pconfig)
            status = "✅" if success else "❌"
            print(f"{status} {pid}: {msg}")
    
    print("")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
