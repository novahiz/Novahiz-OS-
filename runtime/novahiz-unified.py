#!/usr/bin/env python3
"""
Novahiz OS — Unified Daemon
Combines Runtime execution + MCP Bridge functionality
Single daemon for all Novahiz OS operations
"""

import os
import sys
import json
import time
import signal
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# =============================================================================
# PATHS
# =============================================================================
HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
CONFIG_DIR = os.path.join(NOVAHIZ_DIR, "config")
EXECUTION_DIR = os.path.join(NOVAHIZ_DIR, "executions")
LOGS_DIR = os.path.join(NOVAHIZ_DIR, "logs")
RUNTIME_DIR = os.path.join(NOVAHIZ_DIR, "runtime")
MEMORY_DIR = os.path.join(NOVAHIZ_DIR, "memory", "00_Core")
MCP_DIR = os.path.join(NOVAHIZ_DIR, "mcp")

for d in [CONFIG_DIR, EXECUTION_DIR, LOGS_DIR, RUNTIME_DIR, MEMORY_DIR]:
    os.makedirs(d, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, "novahiz-unified.log")
PID_FILE = os.path.join(LOGS_DIR, "novahiz-unified.pid")
CONFIG_FILE = os.path.join(RUNTIME_DIR, "config.json")
METRICS_FILE = os.path.join(MEMORY_DIR, "metrics.json")


# =============================================================================
# LOGGING
# =============================================================================
def log(level, msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# =============================================================================
# CONFIGURATION LOADING
# =============================================================================
def load_config():
    """Load configuration from file"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def load_metrics():
    """Load metrics from file"""
    try:
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"premiumBudget": {"used_today": 0, "daily_limit": 3}}


def save_metrics(metrics):
    """Save metrics atomically"""
    try:
        temp_file = METRICS_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        os.replace(temp_file, METRICS_FILE)
    except Exception as e:
        log("ERROR", f"Failed to save metrics: {e}")


# =============================================================================
# PREMIUM BUDGET GUARD
# =============================================================================
def check_premium_budget():
    """Check if premium budget is exceeded"""
    metrics = load_metrics()
    today = datetime.now().strftime("%Y-%m-%d")
    budget = metrics.get("premiumBudget", {})

    last_reset = budget.get("last_reset_date", "")
    if last_reset != today:
        budget["used_today"] = 0
        budget["last_reset_date"] = today
        save_metrics(metrics)

    config = load_config()
    budget_config = config.get("budget", {}).get("premium", {})
    if not budget_config.get("enabled", True):
        return (True, "Budget guard disabled")

    daily_limit = budget_config.get("daily_limit", budget.get("daily_limit", 3))
    used_today = budget.get("used_today", 0)

    if used_today >= daily_limit:
        return (False, f"Premium budget exceeded: {used_today}/{daily_limit}")

    return (True, f"Budget OK: {used_today}/{daily_limit}")


def increment_premium_usage():
    """Increment premium usage counter"""
    metrics = load_metrics()
    budget = metrics.get("premiumBudget", {})
    budget["used_today"] = budget.get("used_today", 0) + 1
    budget["total_used"] = budget.get("total_used", 0) + 1
    budget["last_reset_date"] = datetime.now().strftime("%Y-%m-%d")
    save_metrics(metrics)


# =============================================================================
# AGENT PROFILES
# =============================================================================
AGENT_PROFILES = {
    "neo-security": {"domain": "Security", "system_prompt": "You are Neo, a security expert."},
    "sarah-quality": {"domain": "Quality", "system_prompt": "You are Sarah, a code quality expert."},
    "arthur-architecture": {"domain": "Architecture", "system_prompt": "You are Arthur, a software architect."},
    "kenzo-performance": {
        "domain": "Performance",
        "system_prompt": "You are Kenzo, a performance optimization expert.",
    },
    "luna-design": {"domain": "Design", "system_prompt": "You are Luna, a UI/UX designer."},
    "orion-devops": {"domain": "DevOps", "system_prompt": "You are Orion, a DevOps engineer."},
    "vega-legal": {"domain": "Legal", "system_prompt": "You are Vega, a legal advisor."},
    "elias-marketing": {"domain": "Marketing", "system_prompt": "You are Elias, a marketing strategist."},
    "victor-strategy": {"domain": "Strategy", "system_prompt": "You are Victor, a business strategist."},
    "ralph-execution": {"domain": "Execution", "system_prompt": "You are Ralph, an execution specialist."},
}


def select_model(task: str, agent: str = None) -> str:
    """Select model tier based on task complexity"""
    task_lower = task.lower()
    if any(kw in task_lower for kw in ["security", "audit", "critical", "architecture"]):
        return "premium"
    if any(kw in task_lower for kw in ["simple", "quick", "basic", "explain"]):
        return "flash"
    return "smart"


# =============================================================================
# RATE LIMITER (simplified inline version)
# =============================================================================
class SimpleRateLimiter:
    def __init__(self):
        self.config = load_config()
        self.usage = {"flash": 0, "smart": 0, "premium": 0}
        self.last_check = time.time()

    def check(self, tier: str) -> tuple:
        """Check if request is within rate limits"""
        rate_config = self.config.get("rate_limit", {})
        if not rate_config.get("enabled", True):
            return (True, "Rate limiting disabled")

        limits = rate_config.get(tier, {})
        per_minute = limits.get("per_minute", 60)

        # Simple per-minute check
        now = time.time()
        if now - self.last_check >= 60:
            self.usage = {"flash": 0, "smart": 0, "premium": 0}
            self.last_check = now

        if self.usage.get(tier, 0) >= per_minute:
            return (False, f"Rate limit exceeded: {per_minute}/min for {tier}")

        self.usage[tier] = self.usage.get(tier, 0) + 1
        return (True, "OK")


# =============================================================================
# LLM EXECUTOR (simplified)
# =============================================================================
class LLMExecutor:
    def __init__(self, config=None):
        self.config = config or load_config()

    def execute(self, agent: str, task: str, model_tier: str) -> dict:
        """Execute task via OpenRouter"""
        providers = self.config.get("providers", {})
        models = self.config.get("models", {})

        # Get model for tier
        tier_config = models.get(model_tier, {})
        default_model = tier_config.get("default", {})
        provider_id = default_model.get("provider", "openrouter")
        model = default_model.get("model", "")

        # Get API key
        provider = providers.get(provider_id, {})
        api_key = os.environ.get(provider.get("api_key_env", ""), "")

        if not api_key:
            return {"success": False, "error": "API key not set"}

        # Execute
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": task},
                ],
                "max_tokens": 4096,
            }

            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(payload).encode(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://novahiz.local",
                },
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read())
                content = result["choices"][0]["message"]["content"]

                return {
                    "success": True,
                    "agent": agent,
                    "provider": provider_id,
                    "model": model,
                    "content": content,
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                }
        except Exception as e:
            return {"success": False, "error": str(e)}


# =============================================================================
# SIGNAL HANDLING
# =============================================================================
running = True


def signal_handler(signum, frame):
    global running
    log("INFO", f"Received signal {signum}, shutting down...")
    running = False


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# =============================================================================
# EXECUTION MANAGER
# =============================================================================
class UnifiedExecutionManager:
    def __init__(self):
        self.executor = LLMExecutor()
        self.rate_limiter = SimpleRateLimiter()
        self.processed = set()

    def process_execution(self, exec_file: str) -> bool:
        """Process a single execution file"""
        exec_id = Path(exec_file).stem

        if exec_id in self.processed:
            return False

        try:
            with open(exec_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            status = data.get("status", "pending")
            if status in ["completed", "failed", "executing"]:
                return False

            agent = data.get("agent")
            task = data.get("task")

            if not agent or not task:
                log("ERROR", f"Invalid data in {exec_id}")
                return False

            data["status"] = "executing"
            data["started"] = datetime.now().isoformat()

            model_tier = select_model(task, agent)
            data["model_tier"] = model_tier

            # Check rate limit
            allowed, message = self.rate_limiter.check(model_tier)
            if not allowed:
                log("CRITICAL", f"RATE LIMITED: {message}")
                data["status"] = "failed"
                data["result"] = {"success": False, "error": message, "rate_limited": True}
                with open(exec_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                self.processed.add(exec_id)
                return True

            # Check premium budget
            if model_tier == "premium":
                allowed, message = check_premium_budget()
                if not allowed:
                    log("CRITICAL", f"PREMIUM BLOCKED: {message}")
                    budget_config = self.config.get("budget", {}).get("premium", {})
                    if budget_config.get("fallback_to_smart", True):
                        model_tier = "smart"
                    else:
                        data["status"] = "failed"
                        data["result"] = {"success": False, "error": message}
                        with open(exec_file, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2)
                        self.processed.add(exec_id)
                        return True

            with open(exec_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            result = self.executor.execute(agent, task, model_tier)

            data["status"] = "completed" if result.get("success") else "failed"
            data["completed"] = datetime.now().isoformat()
            data["result"] = result

            with open(exec_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.processed.add(exec_id)
            log("SUCCESS", f"Processed: {exec_id}")

            return True

        except Exception as e:
            log("ERROR", f"Process error: {e}")
            return False

    def run_daemon(self, poll_interval=2):
        """Run as daemon"""
        log("INFO", "=" * 60)
        log("INFO", "Novahiz OS Unified Daemon v6.0")
        log("INFO", f"Watching: {EXECUTION_DIR}")
        log("INFO", "=" * 60)

        iteration = 0
        while running:
            try:
                iteration += 1
                exec_files = [f for f in Path(EXECUTION_DIR).glob("*.json") if "_response" not in str(f)]

                if iteration % 10 == 0:
                    log("DEBUG", f"Iteration {iteration}, found {len(exec_files)} files")

                new_count = 0
                for exec_file in sorted(exec_files):
                    if self.process_execution(str(exec_file)):
                        new_count += 1

                if new_count > 0:
                    log("INFO", f"Processed {new_count} execution(s)")

                time.sleep(poll_interval)

            except Exception as e:
                log("ERROR", f"Daemon error: {e}")
                time.sleep(poll_interval)


# =============================================================================
# CLI
# =============================================================================
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "daemon":
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        manager = UnifiedExecutionManager()
        manager.run_daemon(int(sys.argv[2]) if len(sys.argv) > 2 else 2)
        try:
            os.remove(PID_FILE)
        except Exception:
            pass

    elif cmd == "status":
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

        config = load_config()
        metrics = load_metrics()
        budget = metrics.get("premiumBudget", {})
        budget_config = config.get("budget", {}).get("premium", {})
        daily_limit = budget_config.get("daily_limit", budget.get("daily_limit", 3))
        used_today = budget.get("used_today", 0)

        providers = config.get("providers", {})
        active = [k for k, v in providers.items() if v.get("enabled", False)]

        print("Novahiz OS Unified Daemon v6.0 Status")
        print("=" * 50)
        print(f"Active Providers: {', '.join(active)}")
        print(f"Premium Budget: {used_today}/{daily_limit}")
        print(f"Executions: {len(exec_files)}")
        print(f"  Pending: {stats['pending']}, Completed: {stats['completed']}")
        print(f"  Executing: {stats['executing']}, Failed: {stats['failed']}")

    elif cmd == "stop":
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read())
            os.kill(pid, signal.SIGTERM)
            os.remove(PID_FILE)
            print(f"Stopped PID {pid}")
        except Exception as e:
            print(f"Failed: {e}")

    else:
        print("Usage: novahiz-unified {daemon|status|stop}")
