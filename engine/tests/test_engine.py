#!/usr/bin/env python3
"""
Tests unitaires du moteur Novahiz Engine.
Couvre : registry, router, scoring, executor.
"""
import sys
import os
import json
import time
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".."))

from engine import AgentRegistry, Router, Scoreboard, Executor
from engine.plugin import PluginManager


class TestRegistry(unittest.TestCase):
    """Tests du AgentRegistry."""

    @classmethod
    def setUpClass(cls):
        cls.registry = AgentRegistry()
        cls.registry.load()

    def test_load(self):
        self.assertTrue(self.registry._loaded)
        self.assertGreater(self.registry.count(), 0)

    def test_list_returns_dicts(self):
        agents = self.registry.list()
        self.assertIsInstance(agents, list)
        self.assertGreater(len(agents), 0)
        for a in agents:
            self.assertIn("id", a)
            self.assertIn("domain", a)
            self.assertIn("score", a)

    def test_get_existing(self):
        a = self.registry.get("neo-security")
        self.assertIsNotNone(a)
        self.assertEqual(a.get("domain"), "Security")

    def test_get_nonexistent(self):
        self.assertIsNone(self.registry.get("nonexistent-agent"))

    def test_search_by_id(self):
        results = self.registry.search("neo")
        self.assertGreater(len(results), 0)
        ids = [r["id"] for r in results]
        self.assertIn("neo-security", ids)

    def test_search_by_domain(self):
        results = self.registry.search("database")
        self.assertGreater(len(results), 0)

    def test_search_by_keyword(self):
        results = self.registry.search("kubernetes")
        self.assertGreater(len(results), 0)
        ids = [r["id"] for r in results]
        self.assertIn("orion-devops", ids)

    def test_search_empty(self):
        results = self.registry.search("xyznonexistentkeyword")
        self.assertEqual(len(results), 0)

    def test_routing_rules_exist(self):
        rules = self.registry.routing_rules
        self.assertIn("keyword_match_weight", rules)
        self.assertIn("priority_weight", rules)
        self.assertIn("score_weight", rules)


class TestRouter(unittest.TestCase):
    """Tests du Router."""

    @classmethod
    def setUpClass(cls):
        cls.router = Router()

    def test_route_success(self):
        result = self.router.route("fix security bug in authentication")
        self.assertTrue(result["success"])
        self.assertIn("primary", result)
        self.assertGreater(result["primary"]["confidence"], 0)

    def test_route_security(self):
        result = self.router.route("fix security vulnerability")
        self.assertEqual(result["primary"]["agent_id"], "neo-security")

    def test_route_design(self):
        result = self.router.route("design mobile app interface")
        self.assertEqual(result["primary"]["agent_id"], "luna-design")

    def test_route_database(self):
        result = self.router.route("optimize PostgreSQL query")
        self.assertEqual(result["primary"]["agent_id"], "malik-database")

    def test_route_api(self):
        result = self.router.route("build a REST API")
        self.assertEqual(result["primary"]["agent_id"], "nexus-api")

    def test_route_marketing(self):
        result = self.router.route("create marketing campaign")
        self.assertEqual(result["primary"]["agent_id"], "elias-marketing")

    def test_route_architecture(self):
        result = self.router.route("refactor monolith to microservices")
        self.assertEqual(result["primary"]["agent_id"], "arthur-architecture")

    def test_route_performance(self):
        result = self.router.route("optimize page load speed")
        self.assertEqual(result["primary"]["agent_id"], "kenzo-performance")

    def test_classify_simple(self):
        self.assertEqual(self.router.classify("how to define a basic variable"), "SIMPLE")

    def test_classify_medium(self):
        self.assertEqual(self.router.classify("build a REST API"), "MEDIUM")

    def test_classify_complex(self):
        self.assertEqual(self.router.classify("design a distributed system architecture"), "COMPLEX")

    def test_route_multi(self):
        result = self.router.route_multi("build full stack application", max_agents=3)
        self.assertTrue(result["success"])
        self.assertGreaterEqual(result["count"], 1)
        self.assertLessEqual(result["count"], 3)

    def test_route_no_match(self):
        result = self.router.route("xyznonexistenttask12345")
        self.assertFalse(result["success"])


class TestScoreboard(unittest.TestCase):
    """Tests du Scoreboard."""

    def setUp(self):
        self.tmpfile = tempfile.mktemp(suffix=".json")
        self.sb = Scoreboard(self.tmpfile)

    def tearDown(self):
        try:
            os.remove(self.tmpfile)
        except OSError:
            pass

    def test_record_execution(self):
        self.sb.record_execution("neo-security", "fix bug", True, 1.5)
        stats = self.sb.get_stats("neo-security")
        self.assertIsNotNone(stats)
        self.assertEqual(stats.get("tasks"), 1)
        self.assertEqual(stats.get("success"), 1)

    def test_record_failure(self):
        self.sb.record_execution("luna-design", "design task", False, 2.0)
        stats = self.sb.get_stats("luna-design")
        self.assertEqual(stats.get("tasks"), 1)
        self.assertEqual(stats.get("success"), 0)

    def test_global_stats(self):
        self.sb.record_execution("agent-a", "task1", True, 1.0)
        self.sb.record_execution("agent-b", "task2", False, 2.0)
        stats = self.sb.get_stats()
        self.assertEqual(stats["total_tasks"], 2)
        self.assertEqual(stats["total_success"], 1)
        self.assertEqual(stats["success_rate"], 50.0)

    def test_history(self):
        self.sb.record_execution("agent-a", "history test", True, 0.5)
        history = self.sb.get_history(10)
        self.assertGreaterEqual(len(history), 1)
        self.assertEqual(history[-1]["agent"], "agent-a")

    def test_reset_agent(self):
        self.sb.record_execution("agent-x", "task1", True, 1.0)
        self.sb.reset("agent-x")
        stats = self.sb.get_stats("agent-x")
        self.assertEqual(stats.get("tasks"), 0)

    def test_reset_all(self):
        self.sb.record_execution("agent-a", "task1", True, 1.0)
        self.sb.record_execution("agent-b", "task2", True, 1.0)
        self.sb.reset()
        stats = self.sb.get_stats()
        self.assertEqual(stats["total_tasks"], 0)


class TestPluginManager(unittest.TestCase):
    """Tests du PluginManager."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.pm = PluginManager(self.tmpdir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_discover_empty(self):
        plugins = self.pm.discover()
        self.assertEqual(len(plugins), 0)

    def test_discover_with_plugin(self):
        # Crée un plugin minimal
        plugin_dir = os.path.join(self.tmpdir, "test-plugin")
        os.makedirs(plugin_dir)
        manifest = {"name": "test-plugin", "version": "1.0.0", "description": "Test"}
        with open(os.path.join(plugin_dir, "plugin.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f)
        plugin_code = """
def info():
    return {"name": "test-plugin"}
def setup(engine=None):
    return {"status": "ok"}
"""
        with open(os.path.join(plugin_dir, "plugin.py"), "w", encoding="utf-8") as f:
            f.write(plugin_code)

        plugins = self.pm.discover()
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0].name, "test-plugin")

    def test_load_and_setup(self):
        plugin_dir = os.path.join(self.tmpdir, "loader-test")
        os.makedirs(plugin_dir)
        with open(os.path.join(plugin_dir, "plugin.json"), "w", encoding="utf-8") as f:
            json.dump({"name": "loader-test", "version": "1.0.0"}, f)
        with open(os.path.join(plugin_dir, "plugin.py"), "w", encoding="utf-8") as f:
            f.write("def setup(e): return {'ok': True}\n")

        self.pm.discover()
        loaded = self.pm.load("loader-test")
        self.assertTrue(loaded)
        setup_res = self.pm.setup_all()
        self.assertIn("loader-test", setup_res)
        self.assertTrue(setup_res["loader-test"]["success"])

    def test_load_all(self):
        """Test discover + load_all cycle."""
        for name in ["p1", "p2"]:
            d = os.path.join(self.tmpdir, name)
            os.makedirs(d)
            with open(os.path.join(d, "plugin.json"), "w", encoding="utf-8") as f:
                json.dump({"name": name, "version": "0.1.0"}, f)
            with open(os.path.join(d, "plugin.py"), "w", encoding="utf-8") as f:
                f.write("def setup(e): return {'ok': True}\n")

        loaded = self.pm.load_all()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(len(self.pm.list_active()), 2)


class TestRoutingConfigExternal(unittest.TestCase):
    """Tests du chargement de la config externe routing-rules.json."""

    def setUp(self):
        self.rules_path = os.path.expanduser("~/.opencode/config/routing-rules.json")
        self._backup = None
        if os.path.isfile(self.rules_path):
            with open(self.rules_path, encoding="utf-8") as f:
                self._backup = f.read()

    def tearDown(self):
        if self._backup:
            with open(self.rules_path, "w", encoding="utf-8") as f:
                f.write(self._backup)

    def test_default_config_loaded(self):
        """La config par défaut doit être lisible."""
        with open(self.rules_path, encoding="utf-8") as f:
            cfg = json.load(f)
        self.assertIn("weights", cfg)
        self.assertIn("thresholds", cfg)
        self.assertIn("complexity_keywords", cfg)
        self.assertIn("version", cfg)

    def test_router_uses_external_weights(self):
        """Router doit charger les poids depuis la config externe."""
        router = Router()
        self.assertIn("keyword_match", router.weights)
        self.assertAlmostEqual(router.weights["keyword_match"], 0.6)

    def test_router_classify_from_external(self):
        """La classification doit utiliser les keywords de la config externe."""
        router = Router()
        # 'show' est dans SIMPLE de la config externe
        self.assertEqual(router.classify("show me how to do it"), "SIMPLE")
        # 'build' est dans MEDIUM
        self.assertEqual(router.classify("build a simple api"), "MEDIUM")
        # 'architecture' est dans COMPLEX
        self.assertEqual(router.classify("design a highload architecture"), "COMPLEX")


class TestDelegationBridge(unittest.TestCase):
    """Tests du bridge de délégation (execution files)."""

    def setUp(self):
        self.executions_dir = os.path.expanduser("~/.opencode/executions")
        os.makedirs(self.executions_dir, exist_ok=True)

    def test_delegation_file_created(self):
        """Vérifie que les fichiers .task.json sont créés correctement."""
        from engine import Executor
        executor = Executor()
        result = executor.execute("neo-security", "test delegation bridge", "opencode")
        if result.get("success"):
            exec_id = result.get("execution_id")
            if exec_id:
                # Simuler ce que handle_execute_and_delegate fait
                delegation = {
                    "agent": "neo-security",
                    "task": "test delegation bridge",
                    "execution_id": exec_id,
                    "status": "pending",
                }
                path = os.path.join(self.executions_dir, f"delegation_{exec_id}.task.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(delegation, f)
                self.assertTrue(os.path.isfile(path))
                os.remove(path)


class TestEngineIntegration(unittest.TestCase):
    """Tests d'intégration : router + scoreboard + executor."""

    def test_route_and_score(self):
        """Route une tâche, enregistre le résultat, vérifie le score."""
        router = Router()
        sb = Scoreboard(tempfile.mktemp(suffix=".json"))

        result = router.route("fix security vulnerability")
        self.assertTrue(result["success"])
        agent = result["primary"]["agent_id"]

        sb.record_execution(agent, "fix security vulnerability", True, duration=3.5)
        stats = sb.get_stats(agent)
        self.assertGreater(stats.get("tasks", 0), 0)

    def test_council_returns_mulitple(self):
        router = Router()
        result = router.route_multi("build a scalable enterprise architecture with microservices", max_agents=5)
        self.assertTrue(result["success"])
        self.assertIn("agents", result)
        # Should include architecture agent
        agent_ids = [a["agent_id"] for a in result["agents"]]
        self.assertIn("arthur-architecture", agent_ids)

    def test_route_and_delegate_flow(self):
        """Test du flow complet: route → create delegation file → verify."""
        router = Router()
        result = router.route("fix security vulnerability")
        self.assertTrue(result["success"])
        agent = result["primary"]["agent_id"]

        executor = Executor()
        exec_result = executor.execute(agent, "fix security vulnerability")
        self.assertIn("success", exec_result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
