#!/usr/bin/env python3
"""
NovaHiz OS — Real-time Health Monitor v2.0
Continuous monitoring + auto-healing + alerts
"""
import sys, os, json, time, threading, subprocess
from datetime import datetime
from pathlib import Path

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
CONFIG_DIR = os.path.join(NOVAHIZ_DIR, "config")
LOGS_DIR = os.path.join(NOVAHIZ_DIR, "logs")

# === MONITORING CONFIGURATION ===
MONITOR_CONFIG = {
    "check_interval": 30,  # seconds
    "api_port": 8080,
    "auto_heal": True,
    "alerts_enabled": True,
    "max_retries": 3,
    "components": {
        "api_server": {"critical": True, "auto_restart": True},
        "chrome_mcp": {"critical": False, "auto_restart": True},
        "memory_nexus": {"critical": True, "auto_restart": False},
        "registry": {"critical": True, "auto_restart": False},
        "skills": {"critical": True, "auto_restart": False},
        "model_router": {"critical": False, "auto_restart": True},
    }
}

# === HEALTH STATE ===
class HealthState:
    def __init__(self):
        self.status = {}
        self.alerts = []
        self.heal_attempts = {}
        self.last_check = None
        self.uptime = datetime.now()
    
    def to_dict(self):
        return {
            "status": self.status,
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "uptime": str(datetime.now() - self.uptime),
            "heal_attempts": self.heal_attempts
        }

STATE = HealthState()

# === LOGGING ===
def log_health(level, msg):
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_path = os.path.join(LOGS_DIR, "health.log")
    entry = f"[{datetime.now().isoformat()}] [{level}] {msg}"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
    if level in ("ERROR", "WARN", "HEAL"):
        print(entry)

def add_alert(component, message, severity="warn"):
    alert = {
        "timestamp": datetime.now().isoformat(),
        "component": component,
        "message": message,
        "severity": severity
    }
    STATE.alerts.append(alert)
    log_health(severity.upper(), f"[{component}] {message}")

# === COMPONENT CHECKS ===
def check_api_server():
    """Check if API server is responding"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(('127.0.0.1', MONITOR_CONFIG["api_port"]))
        s.close()
        return result == 0
    except:
        return False

def check_chrome_mcp():
    """Check if Chrome MCP is running"""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "chrome.*remote-debugging"],
            capture_output=True, text=True, timeout=5
        )
        return len(result.stdout.strip()) > 0
    except:
        return False

def check_memory_nexus():
    """Check if Nexus memory is valid"""
    nexus_path = os.path.join(NOVAHIZ_DIR, "memory", "nexus.json")
    if not os.path.isfile(nexus_path):
        return False
    try:
        with open(nexus_path, encoding='utf-8') as f:
            data = json.load(f)
        return "nodes" in data and len(data["nodes"]) > 0
    except:
        return False

def check_registry():
    """Check if registry is valid"""
    reg_path = os.path.join(NOVAHIZ_DIR, "registry", "novahiz-registry.json")
    if not os.path.isfile(reg_path):
        return False
    try:
        with open(reg_path, encoding='utf-8') as f:
            data = json.load(f)
        return "agents" in data and len(data["agents"]) > 0
    except:
        return False

def check_skills():
    """Check if skills directory exists and has content"""
    skills_dir = os.path.join(NOVAHIZ_DIR, "skills")
    if not os.path.isdir(skills_dir):
        return False
    try:
        count = len([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))])
        return count > 0
    except:
        return False

def check_model_router():
    """Check if model router script exists and is valid"""
    router_path = os.path.join(NOVAHIZ_DIR, "scripts", "python", "model-router.py")
    if not os.path.isfile(router_path):
        return False
    try:
        result = subprocess.run(
            [sys.executable, router_path, "status"],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except:
        return False

CHECKS = {
    "api_server": check_api_server,
    "chrome_mcp": check_chrome_mcp,
    "memory_nexus": check_memory_nexus,
    "registry": check_registry,
    "skills": check_skills,
    "model_router": check_model_router,
}

# === AUTO-HEALING ===
def heal_api_server():
    """Attempt to restart API server"""
    log_health("HEAL", "Attempting to restart API server...")
    api_script = os.path.join(NOVAHIZ_DIR, "api", "server.py")
    if os.path.isfile(api_script):
        subprocess.Popen([sys.executable, api_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        return check_api_server()
    return False

def heal_chrome_mcp():
    """Attempt to restart Chrome MCP"""
    log_health("HEAL", "Attempting to restart Chrome MCP...")
    launch_script = os.path.join(NOVAHIZ_DIR, "scripts", "launch-chrome-mcp.sh")
    if os.path.isfile(launch_script):
        subprocess.Popen([launch_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        return check_chrome_mcp()
    return False

def heal_model_router():
    """Model router is stateless, just verify it's available"""
    log_health("HEAL", "Model router check - verifying availability...")
    return check_model_router()

HEAL_ACTIONS = {
    "api_server": heal_api_server,
    "chrome_mcp": heal_chrome_mcp,
    "model_router": heal_model_router,
}

def attempt_heal(component):
    """Attempt auto-healing for a component"""
    if component not in HEAL_ACTIONS:
        return False
    
    # Track retry count
    if component not in STATE.heal_attempts:
        STATE.heal_attempts[component] = 0
    
    STATE.heal_attempts[component] += 1
    attempts = STATE.heal_attempts[component]
    
    if attempts > MONITOR_CONFIG["max_retries"]:
        add_alert(component, f"Max heal attempts ({attempts}) exceeded", "error")
        return False
    
    log_health("HEAL", f"Attempt {attempts}/{MONITOR_CONFIG['max_retries']} for {component}")
    success = HEAL_ACTIONS[component]()
    
    if success:
        log_health("HEAL", f"✓ {component} healed successfully")
        add_alert(component, "Auto-healed successfully", "success")
        STATE.heal_attempts[component] = 0  # Reset on success
    
    return success

# === MAIN MONITOR LOOP ===
def run_health_check():
    """Run all health checks"""
    for component, check_fn in CHECKS.items():
        config = MONITOR_CONFIG["components"].get(component, {})
        is_critical = config.get("critical", False)
        auto_heal = config.get("auto_restart", False) and MONITOR_CONFIG["auto_heal"]
        
        try:
            healthy = check_fn()
            STATE.status[component] = {
                "healthy": healthy,
                "last_check": datetime.now().isoformat(),
                "critical": is_critical
            }
            
            if not healthy:
                severity = "error" if is_critical else "warn"
                add_alert(component, f"Health check failed", severity)
                
                if auto_heal:
                    attempt_heal(component)
            else:
                # Clear heal attempts on success
                STATE.heal_attempts[component] = 0
                
        except Exception as e:
            STATE.status[component] = {
                "healthy": False,
                "last_check": datetime.now().isoformat(),
                "critical": is_critical,
                "error": str(e)
            }
            add_alert(component, f"Check exception: {e}", "error")
    
    STATE.last_check = datetime.now()

def monitor_loop():
    """Continuous monitoring loop"""
    log_health("INFO", "Health monitor starting...")
    interval = MONITOR_CONFIG["check_interval"]
    
    while True:
        run_health_check()
        time.sleep(interval)

# === CLI COMMANDS ===
def cmd_status():
    """Show current health status"""
    run_health_check()
    print(json.dumps(STATE.to_dict(), indent=2))

def cmd_watch():
    """Watch mode - continuous display"""
    print("Watching health status (Ctrl+C to stop)...")
    try:
        while True:
            run_health_check()
            os.system('clear' if os.name != 'nt' else 'cls')
            print(f"=== NovaHiz Health Monitor [{datetime.now().strftime('%H:%M:%S')}] ===\n")
            
            for comp, status in STATE.status.items():
                icon = "✓" if status["healthy"] else "✗"
                crit = " [CRITICAL]" if status.get("critical") else ""
                print(f"  {icon} {comp:<15} {'OK' if status['healthy'] else 'FAIL'}{crit}")
            
            if STATE.alerts:
                print(f"\n  Recent alerts: {len(STATE.alerts)}")
                for a in STATE.alerts[-3:]:
                    print(f"    [{a['severity']}] {a['component']}: {a['message']}")
            
            print(f"\n  Uptime: {STATE.to_dict()['uptime']}")
            print(f"  Next check: {MONITOR_CONFIG['check_interval']}s")
            
            time.sleep(MONITOR_CONFIG["check_interval"])
    except KeyboardInterrupt:
        print("\nMonitor stopped.")

def cmd_start():
    """Start background monitor"""
    pid_file = os.path.join(NOVAHIZ_DIR, "logs", "health-monitor.pid")
    
    # Check if already running
    if os.path.isfile(pid_file):
        with open(pid_file) as f:
            pid = f.read().strip()
        try:
            os.kill(int(pid), 0)
            print(f"Health monitor already running (PID: {pid})")
            return
        except:
            pass
    
    # Start in background
    log_health("INFO", "Starting health monitor daemon...")
    monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
    monitor_thread.start()
    
    with open(pid_file, 'w') as f:
        f.write(str(os.getpid()))
    
    print(f"Health monitor started (PID: {os.getpid()})")
    print(f"Interval: {MONITOR_CONFIG['check_interval']}s")
    print(f"Auto-heal: {'ON' if MONITOR_CONFIG['auto_heal'] else 'OFF'}")

def cmd_stop():
    """Stop background monitor"""
    pid_file = os.path.join(NOVAHIZ_DIR, "logs", "health-monitor.pid")
    if os.path.isfile(pid_file):
        with open(pid_file) as f:
            pid = f.read().strip()
        try:
            os.kill(int(pid), 9)
            os.remove(pid_file)
            print(f"Health monitor stopped (PID: {pid})")
        except:
            print("Failed to stop monitor")
    else:
        print("Health monitor not running")

def cmd_alerts():
    """Show recent alerts"""
    run_health_check()
    alerts = STATE.alerts[-20:]
    if not alerts:
        print("No alerts")
        return
    
    print(f"=== Recent Alerts ({len(alerts)}) ===\n")
    for a in alerts:
        severity_icon = {"error": "✗", "warn": "⚠", "success": "✓"}.get(a["severity"], "•")
        print(f"  [{a['timestamp'][:19]}] {severity_icon} [{a['severity']}] {a['component']}")
        print(f"      {a['message']}")

def cmd_config():
    """Show current configuration"""
    print(json.dumps(MONITOR_CONFIG, indent=2))

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "status":
        cmd_status()
    elif cmd == "watch":
        cmd_watch()
    elif cmd == "start":
        cmd_start()
    elif cmd == "stop":
        cmd_stop()
    elif cmd == "alerts":
        cmd_alerts()
    elif cmd == "config":
        cmd_config()
    elif cmd == "check":
        run_health_check()
        print("Health check completed")
    else:
        print(f"Usage: health-monitor.py [status|watch|start|stop|alerts|config|check]")
        sys.exit(1)
