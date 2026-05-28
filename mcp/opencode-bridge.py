#!/usr/bin/env python3
"""
OpenCode Execution Bridge
Watches for execution requests and triggers subagent execution via Novahiz Runtime
This is the BRIDGE between MCP server and Novahiz Runtime LLM executor
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

NOVAHIZ_DIR = os.path.join(Path.home(), ".opencode")
EXECUTION_DIR = os.path.join(NOVAHIZ_DIR, "executions")
LOGS_DIR = os.path.join(NOVAHIZ_DIR, "logs")

os.makedirs(EXECUTION_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "opencode-bridge.log")

# Import runtime LLM executor and metrics
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from runtime.novahiz_unified import LLMExecutor, load_config
_METRICS = str(Path(__file__).resolve().parent.parent / "metrics")
if _METRICS not in sys.path:
    sys.path.insert(0, _METRICS)
from metrics import MetricsCollector

metrics = MetricsCollector()

# Configuration
DEFAULT_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def execute_subagent(
    agent: str, task: str, model_tier: str = "smart", timeout: int = DEFAULT_TIMEOUT
) -> dict:
    """
    Execute a subagent using Novahiz Runtime LLM executor
    Features: timeout handling, retry logic, metrics tracking
    """
    log(f"Executing subagent: {agent} (tier: {model_tier}, timeout: {timeout}s)")
    log(f"Task: {task[:100]}...")

    # Retry logic with exponential backoff
    for attempt in range(MAX_RETRIES):
        try:
            # Load config and create executor
            config = load_config()
            executor = LLMExecutor(config)

            # Execute with multi-provider fallback chain
            result = executor.execute(agent, task, model_tier)

            # Record metrics
            metrics.record(result)

            if result.get("success"):
                log(
                    f"SUCCESS: {agent} via {result.get('provider')} / {result.get('model')}"
                )
                log(f"Tokens used: {result.get('tokens_used', 0)}")
            else:
                log(f"FAILED: {result.get('error')}")

                # Check if retryable error
                error = result.get("error", "").lower()
                if "timeout" in error or "rate limit" in error:
                    if attempt < MAX_RETRIES - 1:
                        wait_time = RETRY_DELAY * (attempt + 1)
                        log(
                            f"Retryable error, waiting {wait_time}s before attempt {attempt + 2}"
                        )
                        time.sleep(wait_time)
                        continue

            return result

        except TimeoutError as e:
            log(f"ERROR: Timeout on attempt {attempt + 1}")
            if attempt == MAX_RETRIES - 1:
                return {
                    "success": False,
                    "agent": agent,
                    "error": f"Timeout after {timeout}s",
                    "method": "llm_timeout",
                }
            time.sleep(RETRY_DELAY * (attempt + 1))

        except Exception as e:
            log(f"ERROR: Attempt {attempt + 1} failed: {type(e).__name__}: {e}")
            if attempt == MAX_RETRIES - 1:
                error_result = {
                    "success": False,
                    "agent": agent,
                    "error": f"All {MAX_RETRIES} attempts failed: {e}",
                    "method": "llm_bridge_error",
                }
                metrics.record(error_result)
                return error_result
            time.sleep(RETRY_DELAY * (attempt + 1))

    # Should not reach here, but just in case
    return {
        "success": False,
        "agent": agent,
        "error": "Unknown error",
        "method": "llm_bridge_error",
    }


def process_execution_file(exec_file: str) -> bool:
    """Process a single execution file with proper file sync"""
    log(f"Processing: {exec_file}")

    try:
        with open(exec_file, "r", encoding="utf-8") as f:
            exec_data = json.load(f)

        agent = exec_data.get("agent")
        task = exec_data.get("task")
        exec_id = exec_data.get("id")

        if not agent or not task:
            log(f"ERROR: Invalid execution data")
            return False

        # Update status to processing
        exec_data["status"] = "processing"
        exec_data["started"] = datetime.now().isoformat()

        with open(exec_file, "w", encoding="utf-8") as f:
            json.dump(exec_data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        # Execute via OpenCode bridge
        result = execute_subagent(agent, task)

        # Update with result
        exec_data["status"] = "completed" if result.get("success") else "failed"
        exec_data["completed"] = datetime.now().isoformat()
        exec_data["result"] = result

        # Write with proper sync to prevent race condition
        with open(exec_file, "w", encoding="utf-8") as f:
            json.dump(exec_data, f, indent=2)
            f.flush()  # Force write to buffer
            os.fsync(f.fileno())  # Ensure on disk

        # Verify write succeeded
        time.sleep(0.1)  # Small delay for file system
        try:
            verify_data = json.load(open(exec_file))
            if verify_data.get("status") != exec_data["status"]:
                log(f"WARN: Status mismatch for {exec_id}, re-writing...")
                with open(exec_file, "w", encoding="utf-8") as f:
                    json.dump(exec_data, f, indent=2)
                    f.flush()
                    os.fsync(f.fileno())
        except Exception as e:
            log(f"ERROR: Verify failed for {exec_id}: {e}")

        log(f"Completed: {exec_id}")
        return True

    except Exception as e:
        log(f"ERROR: {e}")
        return False


def run_daemon(poll_interval=2):
    """Run as daemon, watching for execution requests"""
    log("=" * 60)
    log("OpenCode Bridge Daemon Started")
    log(f"Watching: {EXECUTION_DIR}")
    log(f"Poll interval: {poll_interval}s")
    log("=" * 60)

    processed = set()

    while True:
        try:
            # Look for new execution files
            exec_files = list(Path(EXECUTION_DIR).glob("exec_*.json"))

            for exec_file in exec_files:
                exec_id = exec_file.stem

                if exec_id not in processed:
                    log(f"New execution detected: {exec_id}")

                    if process_execution_file(str(exec_file)):
                        processed.add(exec_id)
                        log(f"Processed: {exec_id}")
                    else:
                        log(f"Failed: {exec_id}")

            # Also check for current_request.json (real-time mode)
            request_file = os.path.join(EXECUTION_DIR, "current_request.json")
            if os.path.isfile(request_file):
                try:
                    with open(request_file, "r") as f:
                        request = json.load(f)

                    if request.get("type") == "opencode_subagent_call":
                        agent = request.get("agent")
                        task = request.get("task")

                        log(f"Real-time execution: {agent}")
                        result = execute_subagent(agent, task)

                        # Write response
                        callback = request.get("callback")
                        if callback:
                            with open(callback, "w") as f:
                                json.dump(result, f, indent=2)

                        # Clean up request
                        os.remove(request_file)

                except Exception as e:
                    log(f"Request processing error: {e}")

            time.sleep(poll_interval)

        except KeyboardInterrupt:
            log("Daemon stopped by user")
            break
        except Exception as e:
            log(f"Daemon error: {e}")
            time.sleep(poll_interval)


def run_once():
    """Process all pending executions once"""
    log("Processing pending executions (one-shot)")

    exec_files = list(Path(EXECUTION_DIR).glob("exec_*.json"))

    if not exec_files:
        log("No pending executions")
        return

    success = 0
    for exec_file in exec_files:
        if process_execution_file(str(exec_file)):
            success += 1

    log(f"Processed {success}/{len(exec_files)} executions")


def status():
    """Show bridge status"""
    exec_files = list(Path(EXECUTION_DIR).glob("exec_*.json"))

    pending = sum(1 for f in exec_files if "pending" in open(str(f)).read())
    completed = sum(1 for f in exec_files if "completed" in open(str(f)).read())
    failed = sum(1 for f in exec_files if "failed" in open(str(f)).read())

    print("OpenCode Bridge Status")
    print("=" * 50)
    print(f"Total executions: {len(exec_files)}")
    print(f"  Pending: {pending}")
    print(f"  Completed: {completed}")
    print(f"  Failed: {failed}")
    print(f"Directory: {EXECUTION_DIR}")
    print("")

    if exec_files:
        print("Recent executions:")
        for f in sorted(exec_files)[-5:]:
            try:
                with open(f, "r") as file:
                    data = json.load(file)
                print(
                    f"  - {data.get('id')}: {data.get('agent')} [{data.get('status')}]"
                )
            except Exception:
                print(f"  - {f.name}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "daemon":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        run_daemon(interval)
    elif cmd == "run":
        run_once()
    elif cmd == "status":
        status()
    elif cmd == "test":
        # Create a test execution
        test_exec = {
            "id": "test_exec",
            "type": "subagent_execution",
            "agent": "luna-design",
            "task": "Test execution from bridge",
            "created": datetime.now().isoformat(),
            "status": "pending",
        }
        test_file = os.path.join(EXECUTION_DIR, "test_exec.json")
        with open(test_file, "w") as f:
            json.dump(test_exec, f, indent=2)
        print(f"Test execution created: {test_file}")
    else:
        print("Usage: opencode-bridge.py [daemon|run|status|test]")
        print("")
        print("Commands:")
        print("  daemon [interval]  Run as daemon (default: 2s poll)")
        print("  run                Process all pending executions")
        print("  status             Show status")
        print("  test               Create test execution")
