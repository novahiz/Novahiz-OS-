# Novahiz OS — API Documentation

**Version:** 6.0  
**Last Updated:** 2026-05-27

---

## 1. Vue d'Ensemble

Novahiz OS expose plusieurs interfaces:

| Interface | Type | Usage |
|-----------|------|-------|
| CLI | Command-line | Exécution directe |
| MCP | JSON-RPC | Intégration IDE |
| Execution Files | File-based | Queue d'exécution |
| Memory API | Python | Gestion mémoire |

---

## 2. CLI API

### 2.1 Unified Daemon

```bash
# Status
python3 ~/.opencode/runtime/novahiz-unified.py status

# Start daemon
python3 ~/.opencode/runtime/novahiz-unified.py daemon [poll_interval_sec]

# Stop daemon
python3 ~/.opencode/runtime/novahiz-unified.py stop

# Direct execution
python3 ~/.opencode/runtime/novahiz-unified.py exec <agent> <task> [tier]
```

### 2.2 Exemples

```bash
# Voir status
$ python3 ~/.opencode/runtime/novahiz-unified.py status
Novahiz OS Unified Daemon v6.0 Status
==================================================
Active Providers: openrouter
Premium Budget: 0/3
Executions: 39
  Pending: 0, Completed: 38
  Executing: 0, Failed: 1

# Exécuter tâche
$ python3 ~/.opencode/runtime/novahiz-unified.py exec neo-security "Audit this code"
{
  "success": true,
  "agent": "neo-security",
  "provider": "openrouter",
  "model": "qwen/qwen3.6-plus",
  "content": "...",
  "tokens_used": 2500
}
```

---

## 3. Execution Files API

### 3.1 Format

**Location:** `~/.opencode/executions/exec_<timestamp>_<id>.json`

**Schema:**
```json
{
  "id": "exec_20260527_121843_871965",
  "agent": "neo-security",
  "task": "Audit this code for vulnerabilities",
  "status": "pending|executing|completed|failed",
  "model_tier": "flash|smart|premium",
  "created": "2026-05-27T12:18:43.871982",
  "started": "2026-05-27T12:18:44.558707",
  "completed": "2026-05-27T12:19:13.671978",
  "result": {
    "success": true,
    "provider": "openrouter",
    "model": "qwen/qwen3.6-flash",
    "content": "...",
    "tokens_used": 4807,
    "fallback_used": false
  }
}
```

### 3.2 Workflow

```
1. Create file with status="pending"
2. Daemon polls and detects file
3. Daemon sets status="executing"
4. Daemon executes LLM call
5. Daemon sets status="completed" or "failed"
6. Daemon writes result
```

### 3.3 Exemple (Python)

```python
import json
import time
from pathlib import Path
from datetime import datetime

EXECUTION_DIR = Path.home() / ".opencode" / "executions"

def create_execution(agent: str, task: str, tier: str = "smart"):
    exec_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    exec_file = EXECUTION_DIR / f"{exec_id}.json"
    
    data = {
        "id": exec_id,
        "agent": agent,
        "task": task,
        "status": "pending",
        "model_tier": tier,
        "created": datetime.now().isoformat()
    }
    
    with open(exec_file, "w") as f:
        json.dump(data, f, indent=2)
    
    return exec_file

def wait_for_completion(exec_file, timeout=120):
    start = time.time()
    
    while time.time() - start < timeout:
        with open(exec_file) as f:
            data = json.load(f)
        
        if data["status"] in ["completed", "failed"]:
            return data["result"]
        
        time.sleep(1)
    
    raise TimeoutError("Execution did not complete")

# Usage
exec_file = create_execution("sarah-quality", "Review this code")
result = wait_for_completion(exec_file)
print(result["content"])
```

---

## 4. MCP API (JSON-RPC)

### 4.1 Endpoints

| Method | Params | Returns |
|--------|--------|---------|
| `novahiz/execute` | agent, task, tier | Execution result |
| `novahiz/status` | - | Daemon status |
| `novahiz/budget` | - | Budget status |
| `novahiz/rate_limit` | - | Rate limit status |

### 4.2 Exemple de Requête

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "novahiz/execute",
  "params": {
    "agent": "neo-security",
    "task": "Find security vulnerabilities",
    "tier": "smart"
  }
}
```

### 4.3 Exemple de Réponse

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true,
    "agent": "neo-security",
    "provider": "openrouter",
    "model": "qwen/qwen3.6-flash",
    "content": "...",
    "tokens_used": 2500,
    "fallback_used": false
  }
}
```

---

## 5. Memory API (Python)

### 5.1 Immutable State

```python
from runtime.immutable_state import get_metrics_state, atomic_update_metrics

# Get state
metrics = get_metrics_state()

# Read (thread-safe, no lock)
current = metrics.get()
used_today = metrics.get("premiumBudget.used_today", 0)

# Update (atomic)
new_state = metrics.update({"used_today": used_today + 1})
metrics.commit(new_state, "Increment premium usage")

# Or use convenience function
atomic_update_metrics(
    {"used_today": 5},
    "Reset daily counter"
)
```

### 5.2 RGPD Tools

```python
# Export data (Art. 15, 20 GDPR)
python3 ~/.opencode/scripts/rgpd_tools.py export

# Delete data (Art. 17 GDPR)
python3 ~/.opencode/scripts/rgpd_tools.py delete

# Manage consent (Art. 7 GDPR)
python3 ~/.opencode/scripts/rgpd_tools.py consent
```

---

## 6. Rate Limiting API

### 6.1 Configuration

**Fichier:** `~/.opencode/runtime/config.json`

```json
{
  "rate_limit": {
    "enabled": true,
    "flash": {
      "per_minute": 100,
      "per_hour": 1000,
      "per_day": 5000
    },
    "smart": {
      "per_minute": 50,
      "per_hour": 500,
      "per_day": 2000
    },
    "premium": {
      "per_minute": 10,
      "per_hour": 50,
      "per_day": 200
    }
  }
}
```

### 6.2 Python API

```python
from runtime.rate_limiter import get_rate_limiter

limiter = get_rate_limiter()

# Check if allowed
allowed, message = limiter.check("smart")
if allowed:
    # Execute
    pass
else:
    print(f"Rate limited: {message}")

# Get status
status = limiter.get_status("premium")
print(status)
# {"tier": "premium", "limits": {"minute": "9/10", ...}, "usage": {...}}

# Reset limits
limiter.reset("flash")  # Reset specific tier
limiter.reset()  # Reset all
```

---

## 7. Budget Guard API

### 7.1 Configuration

```json
{
  "budget": {
    "premium": {
      "daily_limit": 3,
      "enabled": true,
      "fallback_to_smart": true
    }
  }
}
```

### 7.2 Python API

```python
from runtime.novahiz_unified import check_premium_budget, increment_premium_usage

# Check budget
allowed, message = check_premium_budget()
if allowed:
    print(f"Budget OK: {message}")
else:
    print(f"Budget exceeded: {message}")
    # Auto-fallback to smart tier if configured

# Increment usage (called automatically after successful premium execution)
increment_premium_usage()
```

---

## 8. Performance Audit API

### 8.1 Run Audit

```bash
python3 ~/.opencode/scripts/performance-audit.py
```

### 8.2 Output

**JSON:** `~/.opencode/docs/performance/audit_report.json`

**Markdown:** `~/.opencode/docs/performance/AUDIT_REPORT.md`

### 8.3 Programmatic Usage

```python
import subprocess
import json

# Run audit
result = subprocess.run(
    ["python3", "~/.opencode/scripts/performance-audit.py"],
    capture_output=True, text=True
)

# Parse results
with open("~/.opencode/docs/performance/audit_report.json") as f:
    report = json.load(f)

print(f"Memory: {report['memory']['process_memory']['max_rss_mb']} MB")
print(f"Recommendations: {len(report['recommendations'])}")
```

---

## 9. Chaos Engineering API

### 9.1 Run Experiments

```bash
python3 ~/.opencode/scripts/chaos-engineering.py
```

### 9.2 Experiments

| Experiment | Risk | Description |
|------------|------|-------------|
| `kill-daemon` | Medium | Kill daemon, measure recovery |
| `network-latency` | Low | Test timeout handling |
| `fill-disk` | High | Simulate disk pressure |
| `memory-pressure` | Medium | Test OOM handling |

### 9.3 Output

**Report:** `~/.opencode/logs/chaos_report.json`

**Log:** `~/.opencode/logs/chaos_engineering.log`

---

## 10. Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| `RATE_LIMITED` | Tier limit exceeded | Wait or upgrade tier |
| `BUDGET_EXCEEDED` | Premium budget exceeded | Wait for reset or use smart tier |
| `API_KEY_MISSING` | No API key configured | Set `OPENROUTER_API_KEY` env var |
| `TIMEOUT` | LLM call timeout | Retry or check network |
| `INVALID_AGENT` | Unknown agent | Check agent name in AGENT_PROFILES |

---

## 11. Best Practices

### 11.1 Execution Files

```python
# ✅ DO: Use unique IDs
exec_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

# ❌ DON'T: Hardcode IDs
exec_id = "exec_123"

# ✅ DO: Handle timeouts
result = wait_for_completion(exec_file, timeout=120)

# ❌ DON'T: Infinite loops
while True:
    # No timeout!
    pass
```

### 11.2 Rate Limiting

```python
# ✅ DO: Check before executing
allowed, msg = limiter.check(tier)
if not allowed:
    log(f"Rate limited: {msg}")
    return

# ❌ DON'T: Ignore rate limits
result = execute()  # May exceed limits!
```

### 11.3 Immutable State

```python
# ✅ DO: Use atomic updates
state = get_metrics_state()
new_state = state.update({"key": "value"})
state.commit(new_state, "Description")

# ❌ DON'T: Direct file writes
with open(metrics_file, "w") as f:
    json.dump(data, f)  # No atomicity, no versioning!
```

---

## 12. Support

| Channel | Response Time |
|---------|---------------|
| GitHub Issues | 2-5 days |
| Email (dev@novahiz-os.local) | 1-3 days |
| Documentation | Always available |

---

*API Documentation v6.0 — Subject to change with major versions*
