#!/usr/bin/env python3
"""
NovaHiz OS - Auto-Healing Daemon
Monitors and auto-restarts failed services
"""

import subprocess
import time
import os
from datetime import datetime, timedelta
from pathlib import Path

HOME = Path.home()
NOVAHIZ_DIR = HOME / ".opencode"
CONFIG_FILE = NOVAHIZ_DIR / "config" / "health-config.json"
LOG_FILE = NOVAHIZ_DIR / "logs" / "autoheal.log"
PID_FILE = NOVAHIZ_DIR / "logs" / "autoheal.pid"

API_URL = "http://localhost:8080"
CHROME_PORT = 9222

def log(message):
    """Log message to file and console"""
    timestamp = datetime.now().isoformat()
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def check_api():
    """Check if API server is responding"""
    try:
        import urllib.request
        req = urllib.request.urlopen(f"{API_URL}/api/health", timeout=5)
        return req.status == 200
    except Exception:
        return False

def check_chrome():
    """Check if Chrome MCP is running"""
    result = subprocess.run(
        ["pgrep", "-f", "chrome-devtools-mcp"],
        capture_output=True
    )
    return result.returncode == 0

def restart_api():
    """Restart API server"""
    log("🔄 Restarting API server...")
    subprocess.run(["pkill", "-f", "python3 server.py"])
    time.sleep(1)
    api_dir = NOVAHIZ_DIR / "api"
    subprocess.Popen(
        ["python3", "-u", "server.py"],
        cwd=api_dir,
        stdout=open(NOVAHIZ_DIR / "logs" / "api-server.log", "w"),
        stderr=subprocess.STDOUT
    )
    time.sleep(2)
    if check_api():
        log("✓ API server restarted successfully")
        return True
    else:
        log("✗ Failed to restart API server")
        return False

def restart_chrome():
    """Restart Chrome MCP"""
    log("🔄 Restarting Chrome MCP...")
    subprocess.run(["pkill", "-f", "chrome-devtools-mcp"])
    time.sleep(1)
    script = NOVAHIZ_DIR / "scripts" / "launch-chrome-mcp.sh"
    if script.exists():
        subprocess.Popen([str(script)])
        time.sleep(3)
        if check_chrome():
            log("✓ Chrome MCP restarted successfully")
            return True
    log("✗ Failed to restart Chrome MCP")
    return False

def main():
    """Main monitoring loop"""
    log("🚀 Auto-heal daemon started")
    
    # Save PID
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    
    # Track retries
    retries = {"api": 0, "chrome": 0}
    last_reset = datetime.now()
    
    while True:
        # Reset retry counters every hour
        if datetime.now() - last_reset > timedelta(hours=1):
            retries = {"api": 0, "chrome": 0}
            last_reset = datetime.now()
        
        # Check API
        if not check_api():
            if retries["api"] < 5:
                retries["api"] += 1
                restart_api()
            else:
                log("⚠ API server: Max retries reached, skipping")
        else:
            retries["api"] = 0
        
        # Check Chrome
        if not check_chrome():
            if retries["chrome"] < 5:
                retries["chrome"] += 1
                restart_chrome()
            else:
                log("⚠ Chrome MCP: Max retries reached, skipping")
        else:
            retries["chrome"] = 0
        
        time.sleep(30)

if __name__ == "__main__":
    main()
