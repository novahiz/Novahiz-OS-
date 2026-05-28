#!/usr/bin/env python3
"""
OpenCode Plugin — Novahiz Auto-Executor
Watch executions/ directory and trigger real subagent execution via OpenCode task tool
"""
import os
import sys
import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
EXECUTION_DIR = os.path.join(NOVAHIZ_DIR, "executions")
LOGS_DIR = os.path.join(NOVAHIZ_DIR, "logs")

os.makedirs(EXECUTION_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "auto-executor.log")

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

# =============================================================================
# OPENCODE TASK EXECUTOR
# =============================================================================
async def execute_subagent_via_opencode(agent: str, task: str, execution_id: str) -> dict:
    """
    Execute subagent using OpenCode's task tool
    This is the CRITICAL function that makes execution REAL
    """
    log(f"🚀 EXECUTING: {agent} — {execution_id}")
    log(f"   Task: {task}")
    
    try:
        # Import OpenCode's task tool if available
        # This works when running INSIDE OpenCode context
        try:
            from opencode.tools import task as opencode_task
            log("   Using OpenCode task tool (import)")
            
            # Call the task tool
            result = await opencode_task(
                subagent=agent,
                prompt=task,
                timeout=300  # 5 minutes timeout
            )
            
            log(f"   ✅ Execution complete: {execution_id}")
            return {
                "success": True,
                "execution_id": execution_id,
                "agent": agent,
                "task": task,
                "result": result,
                "method": "opencode_task_tool"
            }
            
        except ImportError:
            # OpenCode task tool not available via import
            # Try CLI method
            log("   OpenCode task tool not imported, trying CLI...")
            
            import subprocess
            cmd = f"opencode task --subagent {agent} --prompt \"{task.replace('"', '\\"')}\""
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                log(f"   ✅ Execution complete via CLI: {execution_id}")
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "agent": agent,
                    "task": task,
                    "output": result.stdout,
                    "method": "opencode_cli"
                }
            else:
                log(f"   ❌ CLI failed: {result.stderr}")
                return {
                    "success": False,
                    "execution_id": execution_id,
                    "error": result.stderr,
                    "method": "opencode_cli"
                }
                
    except Exception as e:
        log(f"   ❌ Execution failed: {e}")
        return {
            "success": False,
            "execution_id": execution_id,
            "error": str(e)
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

# =============================================================================
# FILE WATCHER
# =============================================================================
class ExecutionHandler(FileSystemEventHandler):
    def __init__(self):
        self.processed = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        if event.src_path.endswith(".json") and "exec_" in event.src_path:
            exec_id = Path(event.src_path).stem
            if exec_id not in self.processed:
                log(f"📁 New execution detected: {exec_id}")
                self.process_execution(event.src_path)
    
    def process_execution(self, exec_file: str):
        """Process a single execution file"""
        try:
            with open(exec_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Check if already processed
            if data.get("status") in ["completed", "failed", "executing"]:
                log(f"   ⏭️  Skipping (status={data.get('status')})")
                return
            
            exec_id = data.get("id", Path(exec_file).stem)
            agent = data.get("agent")
            task = data.get("task")
            
            if not agent or not task:
                log(f"   ❌ Invalid execution data")
                return
            
            # Mark as executing
            data["status"] = "executing"
            data["started"] = datetime.now().isoformat()
            
            with open(exec_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            # Execute via OpenCode
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                execute_subagent_via_opencode(agent, task, exec_id)
            )
            loop.close()
            
            # Update file with result
            update_execution_file(exec_id, result)
            self.processed.add(exec_id)
            
        except Exception as e:
            log(f"   ❌ Process error: {e}")

# =============================================================================
# MAIN
# =============================================================================
def run_watcher():
    """Run file watcher daemon"""
    log("=" * 60)
    log("🔌 OpenCode Auto-Executor Plugin Started")
    log(f"📁 Watching: {EXECUTION_DIR}")
    log("=" * 60)
    
    event_handler = ExecutionHandler()
    observer = Observer()
    observer.schedule(event_handler, EXECUTION_DIR, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("⛔ Stopped by user")
        observer.stop()
    observer.join()

# Process existing pending executions
def process_pending():
    """Process any pending executions on startup"""
    log("📋 Processing pending executions...")
    
    pending = 0
    for exec_file in Path(EXECUTION_DIR).glob("exec_*.json"):
        try:
            with open(exec_file, "r") as f:
                data = json.load(f)
            
            if data.get("status") == "pending":
                pending += 1
                log(f"   Found pending: {exec_file.stem}")
        except:
            pass
    
    log(f"   {pending} pending executions found")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Process once and exit
        process_pending()
    else:
        # Run as daemon
        process_pending()
        run_watcher()
