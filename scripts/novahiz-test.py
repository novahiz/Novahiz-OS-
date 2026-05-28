#!/usr/bin/env python3
"""
NovaHiz OS v1.7 - Integration Tests
Tests all major components of the system including new features
"""

import sys
import os
import json
import socket
import sqlite3
from urllib.request import urlopen, Request

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")

GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'

def log_pass(msg): print(f"{GREEN}[✓]{NC} {msg}")
def log_fail(msg): print(f"{RED}[✗]{NC} {msg}")
def log_warn(msg): print(f"{YELLOW}[!]{NC} {msg}")

class IntegrationTests:
    def __init__(self):
        self.passed = 0
        self.failed = 0
    
    def test(self, name, func):
        try:
            result = func()
            if result:
                log_pass(name)
                self.passed += 1
                return True
            else:
                log_fail(name)
                self.failed += 1
                return False
        except Exception as e:
            log_fail(f"{name} - Error: {e}")
            self.failed += 1
            return False
    
    def run_all(self):
        print("\n╔══════════════════════════════════════════════════╗")
        print("║     NOVAHIZ OS v1.7 - INTEGRATION TESTS        ║")
        print("╚══════════════════════════════════════════════════╝\n")
        
        print("━━━ DIRECTORIES ━━━")
        self.test("agents/ directory exists", lambda: os.path.isdir(f"{NOVAHIZ_DIR}/agents"))
        self.test("skills/ directory exists", lambda: os.path.isdir(f"{NOVAHIZ_DIR}/skills"))
        self.test("data/ directory exists", lambda: os.path.isdir(f"{NOVAHIZ_DIR}/data"))
        self.test("api/ directory exists", lambda: os.path.isdir(f"{NOVAHIZ_DIR}/api"))
        self.test("scripts/ directory exists", lambda: os.path.isdir(f"{NOVAHIZ_DIR}/scripts"))
        self.test("shell/ directory exists", lambda: os.path.isdir(f"{NOVAHIZ_DIR}/shell"))
        self.test("config/ directory exists", lambda: os.path.isdir(f"{NOVAHIZ_DIR}/config"))
        
        print("\n━━━ AGENTS ━━━")
        agents_count = len([f for f in os.listdir(f"{NOVAHIZ_DIR}/agents") if f.endswith('.yaml')])
        self.test(f"22 agents YAML files ({agents_count} found)", lambda: agents_count == 22)
        
        critical_agents = ["novahiz-router", "luna-design", "kenzo-performance", "sage-11", "orion-devops"]
        for agent in critical_agents:
            self.test(f"Agent: {agent}", lambda a=agent: os.path.isfile(f"{NOVAHIZ_DIR}/agents/{a}.yaml"))
        
        print("\n━━━ SKILLS ━━━")
        skills_count = len([f for f in os.listdir(f"{NOVAHIZ_DIR}/skills") if os.path.isdir(f"{NOVAHIZ_DIR}/skills/{f}")])
        self.test(f"59 skills ({skills_count} found)", lambda: skills_count == 59)
        
        critical_skills = ["brainstorming", "frontend-design", "copywriting", "social-content", "seo-audit"]
        for skill in critical_skills:
            self.test(f"Skill: {skill}", lambda s=skill: os.path.isdir(f"{NOVAHIZ_DIR}/skills/{s}"))
        
        print("\n━━━ DATABASES ━━━")
        dbs = ["novahiz.db", "skills-index.db", "agents-tracking.db", "tasks-history.db"]
        for db in dbs:
            db_path = f"{NOVAHIZ_DIR}/data/{db}"
            self.test(f"Database: {db}", lambda p=db_path: os.path.isfile(p))
        
        print("\n━━━ DB CONSISTENCY ━━━")
        if os.path.isfile(f"{NOVAHIZ_DIR}/data/novahiz.db"):
            conn = sqlite3.connect(f"{NOVAHIZ_DIR}/data/novahiz.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM agents")
            db_count = cursor.fetchone()[0]
            conn.close()
            self.test(f"22 agents in DB ({db_count} found)", lambda: db_count == 22)
        
        print("\n━━━ CONFIG FILES ━━━")
        config_files = [
            ("monitoring.json", "config/monitoring.json"),
            ("api-auth.json", "config/api-auth.json"),
            ("skills-linkage.json", "config/skills-linkage.json")
        ]
        for name, path in config_files:
            self.test(f"Config: {name}", lambda p=path: os.path.isfile(f"{NOVAHIZ_DIR}/{p}"))
        
        print("\n━━━ SKILLS LINKAGE ━━━")
        if os.path.isfile(f"{NOVAHIZ_DIR}/config/skills-linkage.json"):
            with open(f"{NOVAHIZ_DIR}/config/skills-linkage.json") as f:
                linkage = json.load(f)
            self.test("Skills linkage has mapping", lambda: "mapping" in linkage)
            self.test("Skills linkage has 21+ agents (actual: {})".format(len(linkage.get("mapping", {}))), lambda: len(linkage.get("mapping", {})) >= 21)
            self.test("Skills linkage has universal", lambda: "universal" in linkage)
        
        print("\n━━━ SCRIPTS ━━━")
        scripts = ["novahiz-cli.py", "novahiz-start.sh", "novahiz-update.sh", "novahiz-api.sh", "novahiz-sync.py", "novahiz-api-docs.py"]
        for script in scripts:
            self.test(f"Script: {script}", lambda s=script: os.path.isfile(f"{NOVAHIZ_DIR}/scripts/{s}"))
        
        print("\n━━━ PYTHON MODULES ━━━")
        modules = ["novahiz-monitor.py", "api-auth.py"]
        for mod in modules:
            self.test(f"Module: {mod}", lambda m=mod: os.path.isfile(f"{NOVAHIZ_DIR}/scripts/python/{m}"))
        
        print("\n━━━ API SERVER ━━━")
        def check_api():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', 8080))
                sock.close()
                return result == 0
            except Exception:
                return False
        
        api_running = check_api()
        if api_running:
            log_pass("API server responding on port 8080")
            self.passed += 1
            
            try:
                req = Request("http://127.0.0.1:8080/api/health")
                resp = urlopen(req, timeout=2)
                data = json.loads(resp.read())
                self.test("  /api/health returns valid JSON", lambda: "status" in data)
                self.test("  /api/health status is healthy", lambda: data.get("status") == "healthy")
                
                req2 = Request("http://127.0.0.1:8080/api/openapi.json")
                resp2 = urlopen(req2, timeout=2)
                spec = json.loads(resp2.read())
                self.test("  /api/openapi.json returns OpenAPI spec", lambda: "openapi" in spec)
                self.test("  OpenAPI version is 3.0.3", lambda: spec.get("openapi") == "3.0.3")
            except Exception as e:
                log_fail(f"  API tests failed: {e}")
                self.failed += 3
        
        else:
            log_warn("API server not running (start with: ~/.opencode/scripts/novahiz-api.sh start)")
        
        print("\n━━━ CONFIGURATION ━━━")
        self.test("opencode.jsonc exists", lambda: os.path.isfile(f"{HOME}/.config/opencode/opencode.jsonc"))
        self.test("registry JSON exists", lambda: os.path.isfile(f"{NOVAHIZ_DIR}/registry/novahiz-registry.json"))
        self.test("README.md exists", lambda: os.path.isfile(f"{NOVAHIZ_DIR}/README.md"))
        
        if os.path.isfile(f"{NOVAHIZ_DIR}/registry/novahiz-registry.json"):
            with open(f"{NOVAHIZ_DIR}/registry/novahiz-registry.json") as f:
                try:
                    registry = json.load(f)
                    self.test("Registry JSON valid", lambda: "agents" in registry)
                    self.test("Registry has 22 agents", lambda: len(registry.get("agents", [])) == 22)
                except Exception:
                    self.test("Registry JSON valid", lambda: False)
        
        print("\n━━━ SHELL COMPLETION ━━━")
        self.test("novahiz-sh.sh exists", lambda: os.path.isfile(f"{NOVAHIZ_DIR}/shell/novahiz-sh.sh"))
        
        print("\n━━━ SYSTEMD SERVICES ━━━")
        systemd_services = ["novahiz-api.service", "novahiz-log-rotate.timer"]
        for svc in systemd_services:
            self.test(f"Service: {svc}", lambda s=svc: os.path.isfile(f"{HOME}/.config/systemd/user/{s}"))
        
        print("\n╔══════════════════════════════════════════════════╗")
        print(f"║  RESULTS: {self.passed} passed, {self.failed} failed                  ║")
        print("╚══════════════════════════════════════════════════╝\n")
        
        return self.failed == 0

def main():
    tests = IntegrationTests()
    success = tests.run_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()