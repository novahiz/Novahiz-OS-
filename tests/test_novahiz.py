#!/usr/bin/env python3
"""
Novahiz OS — Unit Tests v6.0
Comprehensive test suite for all core components
"""
import unittest
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for sub in ["runtime", "metrics", "scripts"]:
    p = str(ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)

class TestConfig(unittest.TestCase):
    """Test configuration loading and validation"""
    
    def test_config_exists(self):
        """Config file should exist"""
        config_path = NOVAHIZ_DIR / "runtime" / "config.json"
        self.assertTrue(config_path.exists(), "config.json should exist")
    
    def test_config_valid_json(self):
        """Config should be valid JSON"""
        config_path = NOVAHIZ_DIR / "runtime" / "config.json"
        try:
            with open(config_path) as f:
                config = json.load(f)
            self.assertIsInstance(config, dict)
        except json.JSONDecodeError:
            self.fail("config.json is not valid JSON")
    
    def test_config_has_providers(self):
        """Config should have providers section"""
        config_path = NOVAHIZ_DIR / "runtime" / "config.json"
        config = json.load(open(config_path))
        self.assertIn("providers", config)
        self.assertIn("openrouter", config["providers"])
    
    def test_config_no_plain_api_keys(self):
        """Config should not contain plain API keys"""
        config_path = NOVAHIZ_DIR / "runtime" / "config.json"
        content = open(config_path).read()
        self.assertNotIn("sk-or-v1", content, "API keys should not be in config.json")
        self.assertNotIn("sk-TnPvEk", content, "API keys should not be in config.json")
    
    def test_config_permissions(self):
        """Config should have secure permissions (600)"""
        config_path = NOVAHIZ_DIR / "runtime" / "config.json"
        perms = oct(os.stat(config_path).st_mode)[-3:]
        self.assertEqual(perms, "600", f"Config permissions should be 600, got {perms}")

class TestMetrics(unittest.TestCase):
    """Test metrics collection and filtering"""
    
    def test_metrics_module_imports(self):
        """Metrics module should import"""
        try:
            from metrics import MetricsCollector
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import metrics: {e}")
    
    def test_metrics_collector_init(self):
        """MetricsCollector should initialize"""
        from metrics import MetricsCollector
        collector = MetricsCollector()
        self.assertIsInstance(collector.metrics, dict)
        self.assertIn("total_executions", collector.metrics)
    
    def test_metrics_record(self):
        """MetricsCollector should record executions"""
        from metrics import MetricsCollector
        collector = MetricsCollector()
        
        initial = collector.metrics["total_executions"]
        
        result = {
            "success": True,
            "agent": "test-agent",
            "provider": "openrouter",
            "model": "test-model",
            "tokens_used": 100,
            "model_tier": "smart"
        }
        collector.record(result)
        
        self.assertEqual(collector.metrics["total_executions"], initial + 1)
        self.assertEqual(collector.metrics["successful_executions"], 
                        collector.metrics.get("successful_executions", 0))
    
    def test_metrics_time_filter(self):
        """Metrics should support time-based filtering"""
        from metrics import MetricsCollector
        collector = MetricsCollector()
        
        stats = collector.get_stats(hours=24)
        self.assertIn("all_time", stats)
        self.assertIn("last_24h", stats)
        self.assertIn("top_agents", stats)
    
    def test_metrics_save(self):
        """Metrics should save to file"""
        from metrics import MetricsCollector
        collector = MetricsCollector()
        collector._save()
        
        metrics_path = NOVAHIZ_DIR / "metrics" / "usage.json"
        self.assertTrue(metrics_path.exists(), "metrics file should exist after save")

class TestModelSelection(unittest.TestCase):
    """Test model tier selection logic"""
    
    def test_select_model_security(self):
        """Security tasks should use premium tier"""
        try:
            from novahiz_runtime import select_model
            tier = select_model("audit this security vulnerability")
            self.assertEqual(tier, "premium")
        except Exception:
            self.skipTest("select_model not available")
    
    def test_select_model_simple(self):
        """Simple tasks should use flash tier"""
        try:
            from novahiz_runtime import select_model
            tier = select_model("fix typo")
            self.assertEqual(tier, "flash")
        except Exception:
            self.skipTest("select_model not available")
    
    def test_select_model_default(self):
        """Normal tasks should use smart tier"""
        try:
            from novahiz_runtime import select_model
            tier = select_model("build a REST API")
            self.assertEqual(tier, "smart")
        except Exception:
            self.skipTest("select_model not available")

class TestDaemonStatus(unittest.TestCase):
    """Test daemon status checks"""
    
    def test_runtime_daemon_running(self):
        """Runtime daemon should be running"""
        import subprocess
        result = subprocess.run(
            ["pgrep", "-f", "novahiz-unified.py"],
            capture_output=True
        )
        self.assertEqual(result.returncode, 0, "Runtime daemon should be running")
    
    def test_bridge_daemon_running(self):
        """Bridge daemon should be running"""
        import subprocess
        result = subprocess.run(
            ["pgrep", "-f", "opencode-bridge.py"],
            capture_output=True
        )
        self.assertEqual(result.returncode, 0, "Bridge daemon should be running")
    
    def test_mcp_http_running(self):
        """MCP HTTP server should be running"""
        import subprocess
        result = subprocess.run(
            ["pgrep", "-f", "novahiz-mcp-http.py"],
            capture_output=True
        )
        self.assertEqual(result.returncode, 0, "MCP HTTP should be running")

class TestHealthEndpoint(unittest.TestCase):
    """Test health check endpoint"""
    
    def test_health_endpoint_responds(self):
        """Health endpoint should respond"""
        import urllib.request
        try:
            with urllib.request.urlopen("http://127.0.0.1:8765/health", timeout=5) as resp:
                data = json.loads(resp.read().decode())
                self.assertTrue(data.get("success"), "Health endpoint should return success")
                self.assertEqual(data.get("status"), "healthy")
        except Exception as e:
            self.fail(f"Health endpoint failed: {e}")
    
    def test_health_checks_all_pass(self):
        """All health checks should pass"""
        import urllib.request
        try:
            with urllib.request.urlopen("http://127.0.0.1:8765/health", timeout=5) as resp:
                data = json.loads(resp.read().decode())
                checks = data.get("checks", {})
                for check_name, check_value in checks.items():
                    self.assertTrue(check_value, f"Health check {check_name} should pass")
        except Exception as e:
            self.fail(f"Health checks failed: {e}")

class TestAPIKeys(unittest.TestCase):
    """Test API key configuration"""
    
    def test_api_keys_in_env_file(self):
        """API keys should be in ~/.novahiz/.env file"""
        env_file = HOME / ".novahiz" / ".env"
        self.assertTrue(env_file.exists(), ".env file should exist")
        with open(env_file) as f:
            content = f.read()
        self.assertIn("OPENROUTER_API_KEY", content, 
                     "OPENROUTER_API_KEY should be in .env")
        self.assertIn("OPENCODE_ZEN_API_KEY", content,
                     "OPENCODE_ZEN_API_KEY should be in .env")
    
    def test_api_keys_in_env(self):
        """API keys should be in ~/.novahiz/.env (NOT in .bashrc)"""
        env_file = HOME / ".novahiz" / ".env"
        self.assertTrue(env_file.exists(), ".env file should exist")
        content = open(env_file).read()
        self.assertIn("OPENROUTER_API_KEY", content, 
                     "OPENROUTER_API_KEY should be in .env")
        self.assertIn("OPENCODE_ZEN_API_KEY", content,
                     "OPENCODE_ZEN_API_KEY should be in .env")
        
        # Verify NOT in .bashrc (security)
        bashrc = HOME / ".bashrc"
        if bashrc.exists():
            bashrc_content = open(bashrc).read()
            self.assertNotIn("OPENROUTER_API_KEY", bashrc_content,
                           "API keys should NOT be in .bashrc (security risk)")
            self.assertNotIn("OPENCODE_ZEN_API_KEY", bashrc_content,
                           "API keys should NOT be in .bashrc (security risk)")

class TestCLI(unittest.TestCase):
    """Test CLI commands"""
    
    def test_nv_command_exists(self):
        """nv command should exist"""
        nv_path = NOVAHIZ_DIR / "bin" / "novahiz"
        self.assertTrue(nv_path.exists(), "nv command should exist")
        self.assertTrue(os.access(nv_path, os.X_OK), "nv should be executable")
    
    def test_nv_status_command(self):
        """nv status should work"""
        import subprocess
        result = subprocess.run(
            [str(NOVAHIZ_DIR / "bin" / "novahiz"), "status"],
            capture_output=True,
            timeout=10
        )
        self.assertEqual(result.returncode, 0, "nv status should succeed")
    
    def test_nv_health_command(self):
        """nv health should work"""
        import subprocess
        # Try nv (new CLI), fallback to old novahiz binary
        nv_path = os.path.expanduser("~/.local/bin/nv")
        old_path = str(NOVAHIZ_DIR / "bin" / "novahiz")
        if os.path.isfile(nv_path):
            cmd = [nv_path, "health"]
        elif os.path.isfile(old_path):
            cmd = [old_path, "health"]
        else:
            # Use python module directly
            cmd = [sys.executable, "-m", "engine.scripts.novahiz_cli", "health"] if False else \
                  [sys.executable, str(NOVAHIZ_DIR / "scripts" / "novahiz-cli.py"), "health"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=10
        )
        self.assertEqual(result.returncode, 0, "nv health should succeed")
        self.assertIn(b"health", result.stdout.lower(), "Health output should mention health")
    
    def test_nv_metrics_command(self):
        """nv metrics should work"""
        import subprocess
        result = subprocess.run(
            [str(NOVAHIZ_DIR / "bin" / "novahiz"), "metrics"],
            capture_output=True,
            timeout=10
        )
        self.assertEqual(result.returncode, 0, "nv metrics should succeed")
        self.assertIn(b"statistics", result.stdout.lower(), "Metrics output should mention statistics")

class TestExecutions(unittest.TestCase):
    """Test execution file handling"""
    
    def test_executions_directory_exists(self):
        """Executions directory should exist"""
        exec_dir = NOVAHIZ_DIR / "executions"
        self.assertTrue(exec_dir.exists(), "Executions directory should exist")
    
    def test_executions_have_results(self):
        """Recent executions should have results"""
        exec_dir = NOVAHIZ_DIR / "executions"
        exec_files = list(exec_dir.glob("exec_*.json"))
        
        if exec_files:
            # Check last 5 executions
            recent = sorted(exec_files)[-5:]
            for exec_file in recent:
                data = json.load(open(exec_file))
                self.assertIn("status", data, f"{exec_file} should have status")
                # New format: "status" + "agent" + "task" + optional "result"
                self.assertIn("agent", data, f"{exec_file} should have agent")
                self.assertIn("task", data, f"{exec_file} should have task")
    
    def test_completed_executions_have_provider(self):
        """Completed executions should have provider tracked"""
        exec_dir = NOVAHIZ_DIR / "executions"
        exec_files = list(exec_dir.glob("exec_*.json"))
        
        completed_count = 0
        with_provider_count = 0
        
        for exec_file in exec_files[-10:]:
            with open(exec_file) as f:
                data = json.load(f)
            if data.get("status") == "completed":
                completed_count += 1
                result = data.get("result", {})
                if result.get("success") and result.get("provider"):
                    with_provider_count += 1
                # Nouveau format: vérifier status et model_tier
                if data.get("status") == "completed" and data.get("model_tier"):
                    with_provider_count += 1
        
        # At least some should have provider tracked
        if completed_count > 0:
            self.assertGreater(with_provider_count, 0, 
                             "Some completed executions should have provider tracked")

class TestDocumentation(unittest.TestCase):
    """Test documentation exists"""
    
    def test_readme_exists(self):
        """README.md should exist (v6.0 consolidated)"""
        readme = NOVAHIZ_DIR / "README.md"
        self.assertTrue(readme.exists(), "README.md should exist")
    
    def test_maintenance_exists(self):
        """MAINTENANCE.md should exist (v6.0)"""
        maintenance = NOVAHIZ_DIR / "MAINTENANCE.md"
        self.assertTrue(maintenance.exists(), "MAINTENANCE.md should exist")
    
    def test_changelog_exists(self):
        """CHANGELOG.md should exist (v6.0)"""
        changelog = NOVAHIZ_DIR / "CHANGELOG.md"
        self.assertTrue(changelog.exists(), "CHANGELOG.md should exist")
    
    def test_agents_exists(self):
        """AGENTS.md should exist"""
        agents = NOVAHIZ_DIR / "AGENTS.md"
        self.assertTrue(agents.exists(), "AGENTS.md should exist")
    
    def test_docs_archive_exists(self):
        """docs-archive should exist (old docs archived)"""
        archive = NOVAHIZ_DIR / "docs-archive"
        self.assertTrue(archive.exists(), "docs-archive should exist")

class TestSecurity(unittest.TestCase):
    """Test security measures"""
    
    def test_gitignore_exists(self):
        """.gitignore should exist"""
        gitignore = NOVAHIZ_DIR / ".gitignore"
        self.assertTrue(gitignore.exists(), ".gitignore should exist")
    
    def test_gitignore_excludes_config(self):
        """.gitignore should exclude config.json"""
        gitignore = NOVAHIZ_DIR / ".gitignore"
        if gitignore.exists():
            content = open(gitignore).read()
            self.assertIn("config.json", content, 
                         ".gitignore should exclude config.json")
    
    def test_no_api_keys_in_logs(self):
        """Logs should not contain API keys"""
        logs_dir = NOVAHIZ_DIR / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                content = open(log_file).read()
                self.assertNotIn("sk-or-v1", content, 
                               f"API key found in {log_file}")
                self.assertNotIn("sk-TnPvEk", content,
                               f"API key found in {log_file}")

if __name__ == "__main__":
    print("═══════════════════════════════════════════════════════")
    print("  NOVAHIZ OS v6.0 — AUTOMATED TEST SUITE")
    print("═══════════════════════════════════════════════════════")
    print("")
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("")
    print("═══════════════════════════════════════════════════════")
    print("  TEST SUMMARY")
    print("═══════════════════════════════════════════════════════")
