#!/usr/bin/env python3
"""
NovaHiz OS v1.7 - API Authentication Module
Token-based authentication for API server
"""

import os
import sys
import json
import secrets
import hashlib
import time
from datetime import datetime, timedelta

HOME = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME, ".opencode", "config")
AUTH_CONFIG = os.path.join(CONFIG_DIR, "api-auth.json")

os.makedirs(CONFIG_DIR, exist_ok=True)

def load_config():
    if os.path.exists(AUTH_CONFIG):
        with open(AUTH_CONFIG) as f:
            return json.load(f)
    return {"enabled": False, "token": "", "createdAt": None, "expiresAt": None}

def save_config(config):
    with open(AUTH_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)

def generate_token(length=32):
    """Generate a secure random token"""
    token = secrets.token_urlsafe(length)
    return token

def create_token(duration_days=365):
    """Create a new API token"""
    config = load_config()
    
    token = generate_token(64)
    now = datetime.now()
    expires = now + timedelta(days=duration_days)
    
    config["enabled"] = True
    config["token"] = token
    config["createdAt"] = now.isoformat()
    config["expiresAt"] = expires.isoformat()
    
    save_config(config)
    
    print("╔════════════════════════════════════════════════════╗")
    print("║        API TOKEN GENERATED                       ║")
    print("╚════════════════════════════════════════════════════╝")
    print(f"\n  Token: {token[:16]}...{token[-8:]}")
    print(f"  Created: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Expires: {expires.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n  Valid for: {duration_days} days")
    print(f"\n  Usage:")
    print(f"  curl -H 'Authorization: Bearer {token}' http://localhost:8080/api/stats")
    print("\n⚠️  Save this token securely - it cannot be recovered!")
    
    return token

def revoke_token():
    """Revoke the current API token"""
    config = load_config()
    
    if not config.get("token"):
        print("✗ No API token exists")
        return False
    
    config = {"enabled": False, "token": "", "createdAt": None, "expiresAt": None}
    save_config(config)
    
    print("✓ API token revoked successfully")
    return True

def verify_token(token):
    """Verify if a token is valid"""
    config = load_config()
    
    if not config.get("enabled"):
        return True
    
    if not token:
        return False
    
    if config.get("token") != token:
        return False
    
    if config.get("expiresAt"):
        expires = datetime.fromisoformat(config["expiresAt"])
        if datetime.now() > expires:
            return False
    
    return True

def status():
    """Show current auth status"""
    config = load_config()
    
    print("\n╔════════════════════════════════════════════════════╗")
    print("║        API AUTHENTICATION STATUS                  ║")
    print("╚════════════════════════════════════════════════════╝")
    
    if config.get("enabled") and config.get("token"):
        created = config.get("createdAt", "Unknown")
        expires = config.get("expiresAt", "Never")
        print(f"\n  Status:  ENABLED")
        print(f"  Created: {created}")
        print(f"  Expires: {expires}")
        print(f"\n  Token: {config['token'][:16]}...{config['token'][-8:]}")
        print("\n  Use: curl -H 'Authorization: Bearer <token>' ...")
    else:
        print("\n  Status:  DISABLED")
        print("\n  Generate with: novahiz-api-auth.py generate")
    
    print()

def enable_auth():
    """Enable authentication (generate token if needed)"""
    config = load_config()
    
    if config.get("enabled") and config.get("token"):
        print("✓ Auth already enabled with existing token")
        status()
        return
    
    create_token()
    print("\n✓ API authentication enabled")

def disable_auth():
    """Disable authentication"""
    config = {"enabled": False, "token": "", "createdAt": None, "expiresAt": None}
    save_config(config)
    print("✓ API authentication disabled")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        status()
        print("Usage: novahiz-api-auth.py [generate|revoke|enable|disable|status]")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "generate":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 365
        create_token(days)
    elif cmd == "revoke":
        revoke_token()
    elif cmd == "enable":
        enable_auth()
    elif cmd == "disable":
        disable_auth()
    elif cmd == "status":
        status()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: novahiz-api-auth.py [generate|revoke|enable|disable|status]")
        sys.exit(1)