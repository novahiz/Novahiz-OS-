#!/usr/bin/env python3
"""
NovaHiz OS v1.7 - Monitoring Notifier
Supports Telegram and Discord notifications
"""

import json
import os
import socket
import sqlite3
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
CONFIG_DIR = os.path.join(NOVAHIZ_DIR, "config")
MONITORING_CONFIG = os.path.join(CONFIG_DIR, "monitoring.json")

def load_config():
    if os.path.exists(MONITORING_CONFIG):
        with open(MONITORING_CONFIG) as f:
            return json.load(f)
    return {"enabled": False, "channels": {"telegram": {}, "discord": {}}}

def save_config(config):
    with open(MONITORING_CONFIG, 'w') as f:
        json.dump(config, f, indent=2)

def check_api():
    """Check if API server is responding"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 8080))
        sock.close()
        return result == 0
    except:
        return False

def check_database():
    """Check if databases are accessible"""
    try:
        db_path = os.path.join(NOVAHIZ_DIR, "data", "novahiz.db")
        conn = sqlite3.connect(db_path, timeout=2)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM agents")
        result = cursor.fetchone()[0]
        conn.close()
        return result >= 22
    except:
        return False

def send_telegram_message(bot_token, chat_id, message):
    """Send message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        req = Request(url, json.dumps(data).encode(), {
            'Content-Type': 'application/json'
        })
        with urlopen(req, timeout=10) as response:
            return json.loads(response.read()).get('ok', False)
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def send_discord_message(webhook_url, message, title="NovaHiz Alert"):
    """Send message via Discord Webhook"""
    if not webhook_url:
        return False
    
    payload = {
        "embeds": [{
            "title": title,
            "description": message,
            "color": 16744448,
            "timestamp": datetime.now().isoformat(),
            "footer": {"text": "NovaHiz OS v1.7"}
        }]
    }
    
    try:
        req = Request(webhook_url, json.dumps(payload).encode(), {
            'Content-Type': 'application/json'
        })
        with urlopen(req, timeout=10) as response:
            return response.getcode() == 200
    except Exception as e:
        print(f"Discord error: {e}")
        return False

def send_notification(message, title="NovaHiz Alert"):
    """Send notification to all configured channels"""
    config = load_config()
    
    if not config.get("enabled"):
        return True
    
    results = {"telegram": False, "discord": False}
    
    telegram = config.get("channels", {}).get("telegram", {})
    if telegram.get("enabled") and telegram.get("bot_token") and telegram.get("chat_id"):
        results["telegram"] = send_telegram_message(
            telegram["bot_token"],
            telegram["chat_id"],
            message
        )
    
    discord = config.get("channels", {}).get("discord", {})
    if discord.get("enabled") and discord.get("webhook_url"):
        results["discord"] = send_discord_message(
            discord["webhook_url"],
            message,
            title
        )
    
    return results

def test_notification(channel="all"):
    """Test notification for a specific channel or all"""
    config = load_config()
    test_message = "✅ *NovaHiz Test Notification*\n\nThis is a test message from NovaHiz OS v1.7 monitoring system."
    
    if channel in ["all", "telegram"]:
        telegram = config.get("channels", {}).get("telegram", {})
        if telegram.get("enabled"):
            result = send_telegram_message(
                telegram["bot_token"],
                telegram["chat_id"],
                test_message
            )
            print(f"Telegram: {'✓ Sent' if result else '✗ Failed'}")
        elif channel == "telegram":
            print("Telegram: ✗ Not configured")
    
    if channel in ["all", "discord"]:
        discord = config.get("channels", {}).get("discord", {})
        if discord.get("enabled"):
            result = send_discord_message(discord["webhook_url"], test_message, "NovaHiz Test")
            print(f"Discord: {'✓ Sent' if result else '✗ Failed'}")
        elif channel == "discord":
            print("Discord: ✗ Not configured")

def run_health_check():
    """Run health checks and send alerts if needed"""
    config = load_config()
    
    if not config.get("enabled"):
        return {"status": "disabled"}
    
    results = {"api": None, "database": None, "timestamp": datetime.now().isoformat()}
    alerts = []
    
    checks = config.get("checks", {})
    
    if checks.get("api", True):
        results["api"] = check_api()
        if not results["api"]:
            alerts.append("🔴 *API Server Down*\nThe NovaHiz API server is not responding on port 8080.")
    
    if checks.get("database", True):
        results["database"] = check_database()
        if not results["database"]:
            alerts.append("🔴 *Database Error*\nCannot connect to NovaHiz database or data is corrupted.")
    
    if alerts:
        message = "\n\n".join(alerts) + f"\n\n⏰ Time: {results['timestamp']}"
        send_notification(message, "NovaHiz Alert")
    
    return results

def get_status():
    """Get monitoring status"""
    config = load_config()
    
    status = {
        "enabled": config.get("enabled", False),
        "interval_minutes": config.get("interval_minutes", 5),
        "checks": config.get("checks", {}),
        "channels": {
            "telegram": {
                "enabled": config.get("channels", {}).get("telegram", {}).get("enabled", False),
                "configured": bool(config.get("channels", {}).get("telegram", {}).get("bot_token"))
            },
            "discord": {
                "enabled": config.get("channels", {}).get("discord", {}).get("enabled", False),
                "configured": bool(config.get("channels", {}).get("discord", {}).get("webhook_url"))
            }
        }
    }
    
    return status

def configure_telegram(bot_token, chat_id, enable=True):
    """Configure Telegram channel"""
    config = load_config()
    
    if "channels" not in config:
        config["channels"] = {}
    if "telegram" not in config["channels"]:
        config["channels"]["telegram"] = {}
    
    config["channels"]["telegram"]["enabled"] = enable
    config["channels"]["telegram"]["bot_token"] = bot_token
    config["channels"]["telegram"]["chat_id"] = chat_id
    
    save_config(config)
    
    print("╔════════════════════════════════════════════════════╗")
    print("║        TELEGRAM CONFIGURED                      ║")
    print("╚════════════════════════════════════════════════════╝")
    print(f"\n  Bot Token: {bot_token[:10]}...{bot_token[-4:]}")
    print(f"  Chat ID: {chat_id}")
    print(f"  Enabled: {enable}")
    print("\n  Test with: novahiz-monitor.py test telegram")

def configure_discord(webhook_url, enable=True):
    """Configure Discord channel"""
    config = load_config()
    
    if "channels" not in config:
        config["channels"] = {}
    if "discord" not in config["channels"]:
        config["channels"]["discord"] = {}
    
    config["channels"]["discord"]["enabled"] = enable
    config["channels"]["discord"]["webhook_url"] = webhook_url
    
    save_config(config)
    
    print("╔════════════════════════════════════════════════════╗")
    print("║        DISCORD CONFIGURED                         ║")
    print("╚════════════════════════════════════════════════════╝")
    print(f"\n  Webhook URL: {webhook_url[:30]}...")
    print(f"  Enabled: {enable}")
    print("\n  Test with: novahiz-monitor.py test discord")

def enable_monitoring():
    """Enable monitoring"""
    config = load_config()
    config["enabled"] = True
    save_config(config)
    print("✓ Monitoring enabled")

def disable_monitoring():
    """Disable monitoring"""
    config = load_config()
    config["enabled"] = False
    save_config(config)
    print("✓ Monitoring disabled")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("NovaHiz Monitor Notifier")
        print("Usage: novahiz-monitor.py [status|check|test|enable|disable]")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        status = get_status()
        print("\n╔════════════════════════════════════════════════════╗")
        print("║        MONITORING STATUS                          ║")
        print("╚════════════════════════════════════════════════════╝")
        print(f"\n  Enabled: {status['enabled']}")
        print(f"  Interval: {status['interval_minutes']} minutes")
        print(f"  Telegram: {'✓ Configured' if status['channels']['telegram']['configured'] else '✗ Not set'}")
        print(f"  Discord:  {'✓ Configured' if status['channels']['discord']['configured'] else '✗ Not set'}")
    elif cmd == "check":
        result = run_health_check()
        print(f"Health check: {result}")
    elif cmd == "test":
        channel = sys.argv[2] if len(sys.argv) > 2 else "all"
        test_notification(channel)
    elif cmd == "enable":
        enable_monitoring()
    elif cmd == "disable":
        disable_monitoring()
    else:
        print(f"Unknown command: {cmd}")