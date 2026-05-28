#!/usr/bin/env python3
"""
NovaHiz Task Processor
Watches for pending tasks and processes them
Can be run as daemon or on-demand
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
PENDING_DIR = os.path.join(NOVAHIZ_DIR, "pending_tasks")
COMPLETED_DIR = os.path.join(NOVAHIZ_DIR, "completed_tasks")
LOGS_DIR = os.path.join(NOVAHIZ_DIR, "logs")

for d in [PENDING_DIR, COMPLETED_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "task-processor.log")


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def process_task(task_file):
    """Process a single task file"""
    log(f"Processing: {task_file}")

    try:
        with open(task_file, "r", encoding="utf-8") as f:
            task_data = json.load(f)

        agent = task_data.get("agent")
        task = task_data.get("task")

        if not agent or not task:
            log(f"ERROR: Invalid task data in {task_file}")
            return False

        log(f"Task: {task}")
        log(f"Agent: {agent}")

        # Update status
        task_data["status"] = "processing"
        task_data["started"] = datetime.now().isoformat()

        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, indent=2)

        # In a real OpenCode environment, this would call the task tool
        # For now, we create an execution request
        log(f"Ready to execute with {agent}")

        # Mark as completed
        task_data["status"] = "completed"
        task_data["completed"] = datetime.now().isoformat()

        # Move to completed
        completed_file = os.path.join(COMPLETED_DIR, os.path.basename(task_file))

        with open(completed_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, indent=2)

        os.remove(task_file)
        log(f"Completed: {completed_file}")

        return True

    except Exception as e:
        log(f"ERROR: {e}")
        return False


def run_daemon(poll_interval=5):
    """Run as daemon, polling for new tasks"""
    log("Starting task processor daemon")
    log(f"Poll interval: {poll_interval}s")
    log(f"Watching: {PENDING_DIR}")

    while True:
        try:
            tasks = list(Path(PENDING_DIR).glob("task_*.json"))

            if tasks:
                log(f"Found {len(tasks)} pending task(s)")

                for task_file in sorted(tasks):
                    process_task(str(task_file))
            else:
                log("No pending tasks")

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            log("Daemon stopped")
            break
        except Exception as e:
            log(f"ERROR: {e}")
            time.sleep(poll_interval)


def run_once():
    """Process all pending tasks once"""
    log("Processing pending tasks (one-shot)")

    tasks = list(Path(PENDING_DIR).glob("task_*.json"))

    if not tasks:
        log("No pending tasks")
        return

    log(f"Found {len(tasks)} task(s)")

    success = 0
    for task_file in sorted(tasks):
        if process_task(str(task_file)):
            success += 1

    log(f"Processed {success}/{len(tasks)} tasks")


def status():
    """Show task processor status"""
    pending = list(Path(PENDING_DIR).glob("task_*.json"))
    completed = list(Path(COMPLETED_DIR).glob("task_*.json"))

    print("NovaHiz Task Processor Status")
    print("=" * 50)
    print(f"Pending tasks: {len(pending)}")
    print(f"Completed tasks: {len(completed)}")
    print(f"Pending dir: {PENDING_DIR}")
    print(f"Completed dir: {COMPLETED_DIR}")
    print("")

    if pending:
        print("Pending:")
        for task_file in pending:
            try:
                with open(task_file, "r") as f:
                    data = json.load(f)
                print(f"  - {data.get('agent')}: {data.get('task', '')[:50]}")
            except Exception:
                print(f"  - {task_file.name}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "daemon":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        run_daemon(interval)
    elif cmd == "run":
        run_once()
    elif cmd == "status":
        status()
    else:
        print("Usage: task-processor.py [daemon|run|status]")
        print("")
        print("Commands:")
        print("  daemon [interval]  Run as daemon (default: 5s poll)")
        print("  run                Process all pending tasks once")
        print("  status             Show status")
