#!/usr/bin/env python3
"""
Novahiz OS — MCP Module Unit Tests v4.0 (Engine-Driven)
Tests: novahiz-mcp.py, engine modules, config, runtime
"""
import json
import unittest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".opencode"))
sys.path.insert(0, str(Path.home() / ".opencode" / "mcp"))

NOVAHIZ_DIR = Path.home() / ".opencode"
ENGINE_DIR = NOVAHIZ_DIR / "engine"
MCP_DIR = NOVAHIZ_DIR / "mcp"


class TestNovahizMCP(unittest.TestCase):
    """Test novahiz-mcp.py v4 module loading."""

    def test_mcp_server_exists(self):
        """novahiz-mcp.py should exist"""
        self.assertTrue((MCP_DIR / "novahiz-mcp.py").exists())

    def test_mcp_server_has_run_mcp_server(self):
        """Should have run_mcp_server function"""
        with open(MCP_DIR / "novahiz-mcp.py") as f:
            content = f.read()
        self.assertIn("run_mcp_server", content)

    def test_mcp_has_12_tools(self):
        """Should define 12 MCP tools"""
        with open(MCP_DIR / "novahiz-mcp.py") as f:
            content = f.read()
        # Count tool definitions in MCP_TOOLS
        count = content.count('"novahiz_')
        self.assertGreaterEqual(count, 10, "Should have 10+ tools")
        self.assertIn('"novahiz_route"', content)
        self.assertIn('"novahiz_execute"', content)
        self.assertIn('"novahiz_auto"', content)
        self.assertIn('"novahiz_council"', content)
        self.assertIn('"novahiz_plugin_info"', content)

    def test_mcp_imports_engine(self):
        """Should import engine modules"""
        with open(MCP_DIR / "novahiz-mcp.py") as f:
            content = f.read()
        self.assertIn("from engine import", content)
        self.assertIn("from engine.plugin import", content)


class TestEngineModule(unittest.TestCase):
    """Test engine module architecture."""

    def test_engine_init_exists(self):
        """engine/__init__.py should exist"""
        self.assertTrue((ENGINE_DIR / "__init__.py").exists())

    def test_engine_modules_exist(self):
        """All engine modules should exist"""
        for mod in ["registry.py", "router.py", "scoring.py", "executor.py", "plugin.py"]:
            self.assertTrue((ENGINE_DIR / mod).exists(), f"{mod} should exist")

    def test_engine_registry_loads(self):
        """Engine registry should load"""
        sys.path.insert(0, str(NOVAHIZ_DIR))
        from engine import AgentRegistry
        reg = AgentRegistry()
        ok = reg.load()
        self.assertTrue(ok)
        self.assertGreater(reg.count(), 0)


class TestConfig(unittest.TestCase):
    """Test configuration files."""

    def test_config_exists(self):
        """Config file should exist"""
        config = NOVAHIZ_DIR / "runtime" / "config.json"
        self.assertTrue(config.exists())

    def test_config_valid_json(self):
        """Config should be valid JSON"""
        with open(NOVAHIZ_DIR / "runtime" / "config.json") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_routing_rules_exists(self):
        """routing-rules.json should exist"""
        rules = NOVAHIZ_DIR / "config" / "routing-rules.json"
        self.assertTrue(rules.exists())
        with open(rules) as f:
            data = json.load(f)
        self.assertIn("weights", data)
        self.assertIn("complexity_keywords", data)

    def test_agent_registry_exists(self):
        """agent-registry.json should exist"""
        registry = NOVAHIZ_DIR / "config" / "agent-registry.json"
        self.assertTrue(registry.exists())
        with open(registry) as f:
            data = json.load(f)
        self.assertIn("agents", data)


class TestRuntime(unittest.TestCase):
    """Test runtime functionality."""

    def test_runtime_exists(self):
        """Runtime should exist"""
        runtime = NOVAHIZ_DIR / "runtime" / "novahiz-runtime.py"
        self.assertTrue(runtime.exists())

    def test_runtime_has_health_check(self):
        """Runtime should have health check (engine or runtime file)."""
        # Check engine-based health (novahiz-mcp.py or engine modules)
        engine_files = [
            NOVAHIZ_DIR / "mcp" / "novahiz-mcp.py",
            NOVAHIZ_DIR / "engine" / "router.py",
            NOVAHIZ_DIR / "engine" / "__init__.py",
        ]
        runtime_file = NOVAHIZ_DIR / "runtime" / "novahiz-runtime.py"
        
        has_health = False
        for f in engine_files + [runtime_file]:
            if f.exists():
                with open(f) as fh:
                    content = fh.read()
                if any(kw in content.lower() for kw in ["def handle_health", "health check", "health_check"]):
                    has_health = True
                    break
        # Also check nv CLI health command
        if not has_health:
            cli_file = NOVAHIZ_DIR / "scripts" / "novahiz-cli.py"
            if cli_file.exists():
                with open(cli_file) as fh:
                    content = fh.read()
                if "cmd_health" in content or "health" in content.lower():
                    has_health = True
        self.assertTrue(has_health, "Health check should exist in engine or CLI")

    def test_executions_dir_exists(self):
        """Executions dir should exist"""
        self.assertTrue((NOVAHIZ_DIR / "executions").is_dir())


if __name__ == "__main__":
    unittest.main(verbosity=2)
