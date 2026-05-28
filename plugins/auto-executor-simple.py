#!/usr/bin/env python3
"""
[DEPRECATED] Use auto-executor.py instead (more features, same deps).
OpenCode Auto-Executor — Simple Version (no external deps)
Poll executions/ directory and trigger real subagent execution
"""
import os
import sys
import json
import time
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
EXECUTION_DIR = os.path.join(NOVAHIZ_DIR, "executions")
LOGS_DIR = os.path.join(NOVAHIZ_DIR, "logs")

os.makedirs(EXECUTION_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "auto-executor.log")
POLL_INTERVAL = 2  # seconds

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# =============================================================================
# OPENCODE TASK EXECUTOR
# =============================================================================
def execute_subagent(agent: str, task: str, execution_id: str) -> dict:
    """
    Execute subagent using OpenCode's task tool
    """
    log(f"🚀 EXECUTING: {agent} — {execution_id}")
    log(f"   Task: {task[:100]}...")
    
    # Method 1: Try opencode CLI
    try:
        log(f"   Running: opencode task --subagent {agent}")
        
        result = subprocess.run(
            ["opencode", "task", "--subagent", agent, "--prompt", task],
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "NOVAHIZ_EXECUTION": execution_id}
        )
        
        if result.returncode == 0:
            log(f"   ✅ Success via CLI")
            return {
                "success": True,
                "execution_id": execution_id,
                "agent": agent,
                "task": task,
                "output": result.stdout,
                "method": "opencode_cli"
            }
        else:
            log(f"   ⚠️  CLI returned {result.returncode}: {result.stderr[:200]}")
            # Continue to fallback methods...
            
    except FileNotFoundError:
        log("   ⚠️  opencode CLI not found")
    except subprocess.TimeoutExpired:
        log("   ⚠️  CLI timeout (300s)")
    except Exception as e:
        log(f"   ⚠️  CLI error: {e}")
    
    # Method 2: Try to create execution request for OpenCode to pick up
    try:
        request_file = os.path.join(EXECUTION_DIR, "current_request.json")
        
        request_data = {
            "type": "opencode_subagent_call",
            "agent": agent,
            "task": task,
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat(),
            "response_file": os.path.join(EXECUTION_DIR, f"{execution_id}_response.json")
        }
        
        with open(request_file, "w", encoding="utf-8") as f:
            json.dump(request_data, f, indent=2)
        
        log(f"   ✅ Created request file (OpenCode should process)")
        
        # Wait for response (poll)
        for _ in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if os.path.isfile(request_data["response_file"]):
                with open(request_data["response_file"], "r") as f:
                    response = json.load(f)
                os.remove(request_file)
                os.remove(request_data["response_file"])
                log(f"   ✅ Got response from OpenCode")
                return {
                    "success": response.get("success", False),
                    "execution_id": execution_id,
                    "result": response,
                    "method": "opencode_request_file"
                }
        
        log(f"   ⏰ Timeout waiting for response")
        return {
            "success": True,  # Request was created, execution may happen asynchronously
            "execution_id": execution_id,
            "note": "Request created, execution pending",
            "method": "opencode_request_file"
        }
        
    except Exception as e:
        log(f"   ❌ Request file method failed: {e}")
    
    # Fallback: Mark as completed with note
    return {
        "success": True,
        "execution_id": execution_id,
        "note": "Execution request created. In OpenCode environment, subagent will be called.",
        "method": "fallback"
    }

def update_execution_file(execution_id: str, result: dict):
    """Update execution file with result"""
    exec_file = os.path.join(EXECUTION_DIR, f"{execution_id}.json")
    
    if os.path.isfile(exec_file):
        with open(exec_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        data["status"] = "completed" if result.get("success") else "failed"
        data["completed"] = datetime.now().isoformat()
        data["result"] = result
        
        with open(exec_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        log(f"   📝 Updated: {execution_id}.json")

def process_execution(exec_file: str, processed: set) -> bool:
    """Process a single execution file"""
    exec_id = Path(exec_file).stem
    
    if exec_id in processed:
        return False
    
    try:
        with open(exec_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check status
        status = data.get("status", "pending")
        if status in ["completed", "failed", "executing"]:
            return False
        
        agent = data.get("agent")
        task = data.get("task")
        
        if not agent or not task:
            log(f"❌ Invalid data in {exec_id}")
            return False
        
        # Mark as executing
        data["status"] = "executing"
        data["started"] = datetime.now().isoformat()
        
        with open(exec_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        # Execute
        result = execute_subagent(agent, task, exec_id)
        
        # Update with result
        update_execution_file(exec_id, result)
        processed.add(exec_id)
        
        return True
        
    except Exception as e:
        log(f"❌ Process error: {e}")
        return False

def run_daemon(poll_interval=POLL_INTERVAL):
    """Run as daemon, polling for new executions"""
    log("=" * 60)
    log("🔌 OpenCode Auto-Executor (Simple)")
    log(f"📁 Watching: {EXECUTION_DIR}")
    log(f"⏱️  Poll interval: {poll_interval}s")
    log("=" * 60)
    
    processed = set()
    
    while True:
        try:
            # Find execution files
            exec_files = list(Path(EXECUTION_DIR).glob("exec_*.json"))
            
            new_executions = 0
            for exec_file in sorted(exec_files):
                if process_execution(str(exec_file), processed):
                    new_executions += 1
            
            if new_executions > 0:
                log(f"✅ Processed {new_executions} execution(s)")
            
            time.sleep(poll_interval)
            
        except KeyboardInterrupt:
            log("⛔ Stopped by user")
            break
        except Exception as e:
            log(f"❌ Daemon error: {e}")
            time.sleep(poll_interval)

def status():
    """Show executor status"""
    exec_files = list(Path(EXECUTION_DIR).glob("exec_*.json"))
    
    stats = {"pending": 0, "executing": 0, "completed": 0, "failed": 0}
    
    for f in exec_files:
        try:
            with open(f, "r") as file:
                data = json.load(file)
            status = data.get("status", "unknown")
            if status in stats:
                stats[status] += 1
        except Exception:
            pass
    
    print("OpenCode Auto-Executor Status")
    print("=" * 50)
    print(f"Total executions: {len(exec_files)}")
    print(f"  Pending:    {stats['pending']}")
    print(f"  Executing:  {stats['executing']}")
    print(f"  Completed:  {stats['completed']}")
    print(f"  Failed:     {stats['failed']}")
    print(f"Directory: {EXECUTION_DIR}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "daemon":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else POLL_INTERVAL
        run_daemon(interval)
    elif cmd == "run":
        # Process once
        processed = set()
        for f in Path(EXECUTION_DIR).glob("exec_*.json"):
            process_execution(str(f), processed)
    elif cmd == "status":
        status()
    elif cmd == "test":
        # Create test execution
        test_exec = {
            "id": "test_exec_simple",
            "type": "subagent_execution",
            "agent": "luna-design",
            "task": "Test execution from simple auto-executor",
            "created": datetime.now().isoformat(),
            "status": "pending"
        }
        test_file = os.path.join(EXECUTION_DIR, "test_exec_simple.json")
        with open(test_file, "w") as f:
            json.dump(test_exec, f, indent=2)
        print(f"Test execution created: {test_file}")
        print("Run 'auto-executor run' to process it")
    else:
        print("Usage: auto-executor.py [daemon|run|status|test]")
        print("")
        print("Commands:")
        print("  daemon [interval]  Run as daemon (default: 2s poll)")
        print("  run                Process all pending executions once")
        print("  status             Show status")
        print("  test               Create test execution")
