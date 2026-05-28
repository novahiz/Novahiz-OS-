# 🔍 NOVAHIZ OS v5.2 — AUDIT COMPLET & AMÉLIORATIONS

**Date:** 2026-05-27  
**Auditeur:** Novahiz Router  
**Score Actuel:** 72/100  
**Potentiel:** 95/100

---

## 📊 SCORE PAR CATÉGORIE

| Catégorie | Score | Status | Priorité |
|-----------|-------|--------|----------|
| **Code Quality** | 85/100 | ✅ Bon | 🟡 Moyenne |
| **Error Handling** | 60/100 | ⚠️ Moyen | 🔴 Haute |
| **Logging** | 65/100 | ⚠️ Moyen | 🟡 Moyenne |
| **Performance** | 75/100 | ✅ Bon | 🟡 Moyenne |
| **Security** | 40/100 | ❌ Critique | 🔴 **CRITIQUE** |
| **Monitoring** | 45/100 | ❌ Insuffisant | 🔴 Haute |
| **Testing** | 0/100 | ❌ Aucun | 🟠 Moyenne |
| **Documentation** | 80/100 | ✅ Bon | 🟢 Basse |

---

## 🔴 AMÉLIORATIONS CRITIQUES (Security)

### #1: API Keys en Clair dans config.json

**Problème:**
```json
{
  "api_key": "sk-or-v1-your-openrouter-api-key-here"
}
```

**Risque:** 🔴 **CRITIQUE**
- Clés exposées si repo git public
- Permissions fichier: `-rw-rw-r--` (tout le monde peut lire)
- Pas de chiffrement

**Solution:**
```bash
# 1. Move to environment variables
export OPENROUTER_API_KEY="sk-or-v1-..."
export OPENCODE_ZEN_API_KEY="sk-TnPvEk..."

# 2. Update config.json to reference env vars
{
  "api_key_env": "OPENROUTER_API_KEY",
  "api_key": ""  # Empty, will load from env
}

# 3. Restrict file permissions
chmod 600 ~/.opencode/runtime/config.json

# 4. Add .gitignore
echo "*.json" >> ~/.opencode/.gitignore
echo "!opencode.json" >> ~/.opencode/.gitignore
```

**Fichiers à modifier:**
- `~/.opencode/runtime/config.json`
- `~/.opencode/scripts/setup-env.sh`
- `~/.opencode/.gitignore`

---

### #2: Pas de Rate Limiting

**Problème:** Aucune protection contre les appels API excessifs

**Risque:** 🟠 **HAUT**
- Peut consumer quota API rapidement
- Risque de bannissement par providers
- Coûts imprévisibles

**Solution:**
```python
# Add to novahiz-runtime.py
class RateLimiter:
    def __init__(self, calls_per_minute=60):
        self.calls = []
        self.limit = calls_per_minute
    
    def wait_if_needed(self):
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [t for t in self.calls if now - t < 60]
        
        if len(self.calls) >= self.limit:
            sleep_time = 60 - (now - self.calls[0])
            if sleep_time > 0:
                log("INFO", f"Rate limit reached, waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        self.calls.append(time.time())

# Usage in LLMExecutor
self.rate_limiter = RateLimiter(calls_per_minute=60)

def execute(self, agent, task, model_tier):
    self.rate_limiter.wait_if_needed()
    # ... rest of execution
```

---

## 🔴 AMÉLIORATIONS HAUTE PRIORITÉ

### #3: Pas de Timeout Handling

**Problème:**
```bash
grep -n "timeout" /home/novahiz/.opencode/mcp/opencode-bridge.py
# (no results)
```

**Risque:** 🟠 **HAUT**
- Appels API peuvent hang indefinitely
- Daemon peut se bloquer
- Expérience utilisateur dégradée

**Solution:**
```python
# Add to opencode-bridge.py
def execute_subagent(agent, task, model_tier="smart", timeout=120):
    """Execute with timeout"""
    log(f"Executing: {agent} (timeout: {timeout}s)")
    
    try:
        config = load_config()
        executor = LLMExecutor(config)
        
        # Set timeout on executor
        result = executor.execute(agent, task, model_tier, timeout=timeout)
        
        return result
        
    except TimeoutError as e:
        log("ERROR", f"Execution timeout after {timeout}s")
        return {
            "success": False,
            "error": f"Timeout after {timeout}s",
            "agent": agent,
            "method": "llm_timeout"
        }
```

---

### #4: Pas de Metrics/Stats Tracking

**Problème:** Aucune métrique de performance

**Impact:** 🟠 **MOYEN**
- Impossible d'optimiser sans données
- Pas de visibilité sur l'usage
- Debugging difficile

**Solution:**
```python
# Create ~/.opencode/metrics/metrics.py
import json
from datetime import datetime
from pathlib import Path

METRICS_FILE = Path.home() / ".opencode" / "metrics" / "usage.json"

class MetricsCollector:
    def __init__(self):
        self.metrics = self._load()
    
    def _load(self):
        if METRICS_FILE.exists():
            return json.load(open(METRICS_FILE))
        return {
            "total_executions": 0,
            "total_tokens": 0,
            "by_agent": {},
            "by_provider": {},
            "by_tier": {},
            "daily": {}
        }
    
    def record(self, result):
        self.metrics["total_executions"] += 1
        self.metrics["total_tokens"] += result.get("tokens_used", 0)
        
        agent = result.get("agent", "unknown")
        provider = result.get("provider", "unknown")
        
        self.metrics["by_agent"][agent] = self.metrics["by_agent"].get(agent, 0) + 1
        self.metrics["by_provider"][provider] = self.metrics["by_provider"].get(provider, 0) + 1
        
        today = datetime.now().strftime("%Y-%m-%d")
        self.metrics["daily"][today] = self.metrics["daily"].get(today, 0) + 1
        
        self._save()
    
    def _save(self):
        METRICS_FILE.parent.mkdir(exist_ok=True)
        json.dump(self.metrics, open(METRICS_FILE, "w"), indent=2)
    
    def get_stats(self):
        return {
            "total_executions": self.metrics["total_executions"],
            "total_tokens": self.metrics["total_tokens"],
            "avg_tokens": self.metrics["total_tokens"] / max(1, self.metrics["total_executions"]),
            "top_agents": sorted(self.metrics["by_agent"].items(), key=lambda x: x[1], reverse=True)[:5]
        }

# Usage in opencode-bridge.py
from metrics import MetricsCollector
metrics = MetricsCollector()

def process_execution_file(exec_file):
    # ... execution ...
    result = execute_subagent(agent, task)
    metrics.record(result)
```

---

### #5: Error Handling Incomplet

**Problème:**
```python
try:
    # execution
except Exception as e:
    log(f"ERROR: {e}")  # Too generic!
    return {"success": False, "error": str(e)}
```

**Risque:** 🟡 **MOYEN**
- Erreurs non catégorisées
- Retry logic inexistante
- Pas de fallback sur erreurs spécifiques

**Solution:**
```python
def execute_subagent(agent, task, model_tier="smart"):
    """Execute with proper error handling and retry"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            config = load_config()
            executor = LLMExecutor(config)
            result = executor.execute(agent, task, model_tier)
            
            if result.get("success"):
                return result
            
            # Check error type
            error = result.get("error", "")
            
            if "rate limit" in error.lower():
                log("WARN", f"Rate limited, waiting {retry_delay * (attempt + 1)}s")
                time.sleep(retry_delay * (attempt + 1))
                continue
            
            if "timeout" in error.lower():
                log("WARN", f"Timeout on attempt {attempt + 1}")
                continue
            
            # Non-retryable error
            return result
            
        except Exception as e:
            log("ERROR", f"Attempt {attempt + 1} failed: {type(e).__name__}: {e}")
            if attempt == max_retries - 1:
                return {
                    "success": False,
                    "error": f"All {max_retries} attempts failed: {e}",
                    "agent": agent
                }
            time.sleep(retry_delay)
```

---

## 🟡 AMÉLIORATIONS MOYENNE PRIORITÉ

### #6: Log Rotation

**Problème:** Pas de rotation → logs peuvent grossir indefiniment

**Solution:**
```bash
# Create ~/.opencode/logs/logrotate.conf
/home/novahiz/.opencode/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 novahiz novahiz
    postrotate
        # Signal daemons to reopen logs if needed
    endscript
}

# Add to crontab or run manually
logrotate -f ~/.opencode/logs/logrotate.conf
```

---

### #7: Log Levels (DEBUG/INFO/WARN/ERROR)

**Problème:** Tous les logs au même niveau

**Solution:**
```python
# Add to opencode-bridge.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("novahiz-bridge")

# Usage
log.debug("Debug info")
log.info("Normal operation")
log.warning("Something might be wrong")
log.error("Something is wrong")
log.critical("Critical failure")
```

---

### #8: Concurrent Execution Limit

**Problème:** Config existe mais pas implémenté

**Solution:**
```python
# Add to novahiz-runtime.py
import threading

class ExecutionManager:
    def __init__(self):
        self.max_concurrent = 5
        self.active = 0
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(self.max_concurrent)
    
    def process_execution(self, exec_file):
        with self.semaphore:
            with self.lock:
                self.active += 1
                log("INFO", f"Active executions: {self.active}/{self.max_concurrent}")
            
            try:
                # ... process execution ...
            finally:
                with self.lock:
                    self.active -= 1
```

---

### #9: Health Check Endpoint Amélioré

**Actuel:**
```json
{
  "success": true,
  "status": "healthy"
}
```

**Amélioration:**
```python
# Enhance novahiz-mcp-http.py
@app.route("/health")
def health():
    checks = {
        "runtime_daemon": check_pid("runtime.pid"),
        "bridge_daemon": check_pid("bridge.pid"),
        "mcp_http": True,  # We're here
        "task_processor": check_pid("task-processor.pid"),
        "openrouter_api": check_api("https://openrouter.ai/api/v1"),
        "disk_space": check_disk_space(),
        "memory": check_memory()
    }
    
    all_healthy = all(checks.values())
    
    return {
        "success": all_healthy,
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
        "uptime": get_uptime(),
        "version": "5.2.0"
    }
```

---

## 🟢 AMÉLIORATIONS BASSE PRIORITÉ

### #10: Unit Tests

**Structure proposée:**
```
~/.opencode/tests/
├── test_runtime.py
├── test_bridge.py
├── test_router.py
└── __init__.py
```

**Exemple:**
```python
# test_runtime.py
import unittest
from novahiz_runtime import LLMExecutor, select_model

class TestSelectModel(unittest.TestCase):
    def test_security_task_returns_premium(self):
        self.assertEqual(select_model("audit this security issue"), "premium")
    
    def test_simple_task_returns_flash(self):
        self.assertEqual(select_model("fix typo"), "flash")

class TestLLMExecutor(unittest.TestCase):
    def test_execute_with_fallback(self):
        executor = LLMExecutor()
        result = executor.execute("luna-design", "test task", "smart")
        self.assertIn("success", result)

if __name__ == "__main__":
    unittest.main()
```

---

### #11: Integration Tests

```bash
# test-integration.sh
#!/bin/bash
set -e

echo "Starting integration tests..."

# Test 1: Auto-start
~/.opencode/scripts/novahiz-stop.sh
sleep 2
~/.opencode/scripts/novahiz-autostart.sh
sleep 5

# Test 2: Services running
if ! pgrep -f "novahiz-runtime.py" > /dev/null; then
    echo "❌ Runtime not running"
    exit 1
fi
echo "✅ Runtime running"

# Test 3: Execute task
nv run "Test task for integration"
sleep 15

# Test 4: Check result
LATEST=$(ls -t ~/.opencode/executions/exec_*.json | head -1)
if ! grep -q '"success": true' "$LATEST"; then
    echo "❌ Execution failed"
    exit 1
fi
echo "✅ Execution successful"

# Test 5: Health check
if ! curl -s http://127.0.0.1:8765/health | grep -q '"success": true'; then
    echo "❌ Health check failed"
    exit 1
fi
echo "✅ Health check passed"

echo "✅ All integration tests passed!"
```

---

### #12: API Documentation

**Format:** OpenAPI/Swagger

```yaml
# ~/.opencode/docs/api.yaml
openapi: 3.0.0
info:
  title: Novahiz OS API
  version: 5.2.0
  description: Multi-agent orchestration API

paths:
  /health:
    get:
      summary: Health check
      responses:
        200:
          description: Service healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
  
  /execute:
    post:
      summary: Execute task with agent
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ExecuteRequest'
      responses:
        200:
          description: Execution result
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExecuteResponse'

components:
  schemas:
    HealthResponse:
      type: object
      properties:
        success:
          type: boolean
        status:
          type: string
        checks:
          type: object
    
    ExecuteRequest:
      type: object
      required:
        - agent
        - task
      properties:
        agent:
          type: string
        task:
          type: string
        tier:
          type: string
          enum: [flash, smart, premium]
```

---

## 📋 PLAN D'ACTION PRIORITISÉ

### Phase 1: Security (Immédiat - 2h)

```bash
# 1. Move API keys to environment
echo "export OPENROUTER_API_KEY='sk-or-...'" >> ~/.bashrc
echo "export OPENCODE_ZEN_API_KEY='sk-Tn...'" >> ~/.bashrc
source ~/.bashrc

# 2. Update config.json to use env vars
# (edit file, remove api_key values)

# 3. Restrict permissions
chmod 600 ~/.opencode/runtime/config.json

# 4. Add to .gitignore
echo "runtime/config.json" >> ~/.opencode/.gitignore
```

### Phase 2: Reliability (4h)

```bash
# 1. Add timeout handling to opencode-bridge.py
# 2. Add retry logic with exponential backoff
# 3. Add rate limiting
```

### Phase 3: Monitoring (3h)

```bash
# 1. Create metrics collector
# 2. Add metrics recording to bridge
# 3. Create metrics dashboard (simple HTML)
```

### Phase 4: Quality (4h)

```bash
# 1. Add log rotation
# 2. Implement proper log levels
# 3. Add concurrent execution limit
# 4. Enhance health check endpoint
```

### Phase 5: Testing (Optional - 8h)

```bash
# 1. Write unit tests
# 2. Write integration tests
# 3. Add CI/CD pipeline
```

---

## 📊 SCORE APRÈS AMÉLIORATIONS

| Catégorie | Avant | Après | Gain |
|-----------|-------|-------|------|
| Security | 40/100 | 95/100 | +55 |
| Error Handling | 60/100 | 90/100 | +30 |
| Monitoring | 45/100 | 85/100 | +40 |
| Performance | 75/100 | 90/100 | +15 |
| Testing | 0/100 | 80/100 | +80 |
| **TOTAL** | **72/100** | **95/100** | **+23** |

---

## 🎯 VERDICT

**État actuel:** 72/100 — Fonctionnel mais perfectible  
**Problèmes critiques:** 2 (Security API keys, Rate limiting)  
**Améliorations identifiées:** 12  
**Effort estimé:** 13 heures  
**Score potentiel:** 95/100 — Production-ready enterprise grade

**Recommandation:** Commencer par Phase 1 (Security) immédiatement.

---

[Executed by: Novahiz Router]
[Agent: novahiz-router]
[Timestamp: 02:31:30]
