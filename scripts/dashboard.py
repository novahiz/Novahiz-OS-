#!/usr/bin/env python3
"""
Novahiz OS — Real-time Monitoring Dashboard v6.1
Shows system metrics, executions, and performance
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

HOME = Path.home()
NOVAHIZ_DIR = HOME / ".opencode"
METRICS_FILE = NOVAHIZ_DIR / "metrics" / "usage.json"
EXECUTIONS_DIR = NOVAHIZ_DIR / "executions"
LOGS_DIR = NOVAHIZ_DIR / "logs"

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def get_metrics():
    """Load usage metrics"""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            return json.load(f)
    return {}

def get_execution_stats():
    """Get execution statistics"""
    exec_files = list(EXECUTIONS_DIR.glob("exec_*.json"))
    stats = {"pending": 0, "executing": 0, "completed": 0, "failed": 0}
    
    for f in exec_files:
        try:
            with open(f) as file:
                data = json.load(file)
            status = data.get("status", "unknown")
            if status in stats:
                stats[status] += 1
        except Exception:
            pass
    
    return stats

def get_daemon_status():
    """Check if daemons are running"""
    import subprocess
    try:
        result = subprocess.run(
            ["pgrep", "-f", "novahiz-runtime"],
            capture_output=True, text=True
        )
        runtime = "✅ Running" if result.returncode == 0 else "❌ Stopped"
        
        result = subprocess.run(
            ["pgrep", "-f", "opencode-bridge"],
            capture_output=True, text=True
        )
        bridge = "✅ Running" if result.returncode == 0 else "❌ Stopped"
        
        return runtime, bridge
    except Exception:
        return "❌ Unknown", "❌ Unknown"

def get_recent_errors():
    """Get recent error logs"""
    errors = []
    log_files = ["runtime.log", "opencode-bridge.log", "mcp-http-error.log"]
    
    for log_name in log_files:
        log_file = LOGS_DIR / log_name
        if log_file.exists():
            try:
                with open(log_file) as f:
                    lines = f.readlines()[-10:]  # Last 10 lines
                    for line in lines:
                        if "ERROR" in line or "error" in line:
                            errors.append(line.strip()[:80])
            except Exception:
                pass
    
    return errors[:5]  # Return max 5 errors

def render_dashboard():
    """Render the monitoring dashboard"""
    clear_screen()
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "NOVAHIZ OS — MONITORING DASHBOARD v6.1" + " " * 19 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Date/Time
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Daemon Status
    print("┌" + "─" * 78 + "┐")
    print("│ DAEMON STATUS" + " " * 63 + "│")
    print("├" + "─" * 78 + "┤")
    runtime, bridge = get_daemon_status()
    print(f"│  Runtime Daemon:  {runtime}" + " " * (78 - 20 - len(runtime)) + "│")
    print(f"│  Bridge Daemon:   {bridge}" + " " * (78 - 20 - len(bridge)) + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # Execution Stats
    stats = get_execution_stats()
    total = sum(stats.values())
    print("┌" + "─" * 78 + "┐")
    print("│ EXECUTION STATISTICS" + " " * 56 + "│")
    print("├" + "─" * 78 + "┤")
    print(f"│  Total Executions:    {total}" + " " * (78 - 24 - len(str(total))) + "│")
    print(f"│  Pending:             {stats['pending']}" + " " * (78 - 24 - len(str(stats['pending']))) + "│")
    print(f"│  Executing:           {stats['executing']}" + " " * (78 - 24 - len(str(stats['executing']))) + "│")
    print(f"│  Completed:           {stats['completed']}" + " " * (78 - 24 - len(str(stats['completed']))) + "│")
    print(f"│  Failed:              {stats['failed']}" + " " * (78 - 24 - len(str(stats['failed']))) + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # Metrics
    metrics = get_metrics()
    total_execs = metrics.get("total_executions", 0)
    total_tokens = metrics.get("total_tokens", 0)
    print("┌" + "─" * 78 + "┐")
    print("│ USAGE METRICS (All Time)" + " " * 50 + "│")
    print("├" + "─" * 78 + "┤")
    print(f"│  Total Executions:    {total_execs}" + " " * (78 - 24 - len(str(total_execs))) + "│")
    print(f"│  Total Tokens:        {total_tokens:,}" + " " * (78 - 24 - len(f"{total_tokens:,}")) + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # Recent Errors
    errors = get_recent_errors()
    print("┌" + "─" * 78 + "┐")
    print("│ RECENT ERRORS" + " " * 63 + "│")
    print("├" + "─" * 78 + "┤")
    if errors:
        for error in errors:
            print(f"│  ⚠️  {error}" + " " * (78 - 7 - len(error)) + "│")
    else:
        print("│  ✅ No recent errors" + " " * 55 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # Footer
    print("Press Ctrl+C to exit | Refresh: 5s")
    print()

def main():
    """Main loop"""
    print("🚀 Starting Novahiz OS Monitoring Dashboard...")
    time.sleep(1)
    
    try:
        while True:
            render_dashboard()
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
        sys.exit(0)

if __name__ == "__main__":
    main()
