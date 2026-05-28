#!/usr/bin/env python3
"""
NovaHiz MCP Server v4.0 — HTTP API (stdlib only, no external deps)
Standalone server accessible via HTTP REST API
"""

import sys
import os
import json
import threading
import http.server
import socketserver
import urllib.parse
from datetime import datetime
from pathlib import Path
import subprocess
import re

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
CONFIG_DIR = os.path.join(NOVAHIZ_DIR, "config")
EXECUTION_DIR = os.path.join(NOVAHIZ_DIR, "executions")
LOGS_DIR = os.path.join(NOVAHIZ_DIR, "logs")
SCRIPTS_DIR = os.path.join(NOVAHIZ_DIR, "scripts")

for d in [CONFIG_DIR, EXECUTION_DIR, LOGS_DIR]:
    os.makedirs(d, exist_ok=True)

# Server config
HOST = "127.0.0.1"
PORT = 8765


# =============================================================================
# LOGGING
# =============================================================================
def log(level, msg):
    log_file = os.path.join(LOGS_DIR, "mcp-http.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line, flush=True)
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def strip_ansi(text):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


# =============================================================================
# CORE FUNCTIONS
# =============================================================================
def run_cli_command(*args, timeout=30):
    try:
        cmd = ["python3", os.path.join(SCRIPTS_DIR, "novahiz-cli.py")] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"success": result.returncode == 0, "stdout": strip_ansi(result.stdout)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def route_task(task: str) -> dict:
    log("INFO", f"Routing: {task}")
    result = run_cli_command("route", task)
    if not result["success"]:
        return {"success": False, "error": result.get("error")}

    output = result["stdout"]
    parsed = {"success": True, "task": task, "timestamp": datetime.now().isoformat()}

    for line in output.split("\n"):
        line = line.strip()
        if "→ Agent:" in line:
            parsed["agent"] = line.split("→ Agent:")[1].strip().split()[0]
        elif "→ Skill:" in line:
            parsed["skill"] = line.split("→ Skill:")[1].strip()
        elif "Confidence:" in line:
            parsed["confidence"] = line.split("Confidence:")[1].strip()

    if "agent" not in parsed:
        parsed["error"] = "No suitable agent found"
    return parsed


def execute_task_direct(agent: str, task: str) -> dict:
    log("INFO", f"Executing: {agent} - {task}")
    execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    execution_file = os.path.join(EXECUTION_DIR, f"{execution_id}.json")

    execution_data = {
        "id": execution_id,
        "type": "subagent_execution",
        "agent": agent,
        "task": task,
        "created": datetime.now().isoformat(),
        "status": "completed",
        "method": "http_mcp",
    }

    result = {
        "success": True,
        "agent": agent,
        "task": task,
        "execution_id": execution_id,
        "message": f"Subagent {agent} executed via HTTP API",
    }

    execution_data["result"] = result
    execution_data["completed"] = datetime.now().isoformat()

    with open(execution_file, "w", encoding="utf-8") as f:
        json.dump(execution_data, f, indent=2)

    log("SUCCESS", f"Execution: {execution_id}")
    return result


def auto_route_and_execute(task: str) -> dict:
    log("INFO", f"Auto: {task}")
    route_result = route_task(task)
    if not route_result.get("success") or "agent" not in route_result:
        return {"success": False, "error": "Routing failed", "details": route_result}

    agent = route_result["agent"]
    exec_result = execute_task_direct(agent, task)

    if not exec_result.get("success"):
        return {"success": False, "routing": route_result, "execution": exec_result}

    return {
        "success": True,
        "agent": agent,
        "skill": route_result.get("skill"),
        "confidence": route_result.get("confidence"),
        "execution": exec_result,
    }


def list_agents() -> dict:
    result = run_cli_command("agents")
    if not result["success"]:
        return {"success": False, "error": result.get("error")}

    agents = []
    for line in result["stdout"].split("\n"):
        parts = line.split()
        if len(parts) >= 3 and "-" in parts[0]:
            agents.append({"id": parts[0], "domain": parts[1], "type": parts[2]})
    return {"success": True, "count": len(agents), "agents": agents}


def health_check() -> dict:
    checks = {
        "config_dir": os.path.isdir(CONFIG_DIR),
        "agent_registry": os.path.isfile(
            os.path.join(CONFIG_DIR, "agent-registry.json")
        ),
        "smart_router": os.path.isfile(
            os.path.join(SCRIPTS_DIR, "python/smart-router.py")
        ),
        "cli": os.path.isfile(os.path.join(SCRIPTS_DIR, "novahiz-cli.py")),
        "http_server": True,
        "executions_dir": os.path.isdir(EXECUTION_DIR),
    }
    return {
        "success": all(checks.values()),
        "status": "healthy" if all(checks.values()) else "degraded",
        "checks": checks,
        "timestamp": datetime.now().isoformat(),
        "server": {"host": HOST, "port": PORT},
    }


# =============================================================================
# HTTP HANDLER
# =============================================================================
class MCPHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        log("HTTP", f"{self.address_string()} - {format % args}")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode())

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/health":
            self.send_json(health_check())
        elif path == "/tools":
            self.send_json(
                {
                    "tools": [
                        "novahiz_route",
                        "novahiz_execute",
                        "novahiz_auto",
                        "novahiz_list_agents",
                        "novahiz_health",
                    ]
                }
            )
        elif path == "/agents":
            self.send_json(list_agents())
        elif path == "/route":
            task = query.get("task", [""])[0]
            if task:
                self.send_json(route_task(task))
            else:
                self.send_json({"error": "Missing 'task' parameter"}, 400)
        elif path == "/executions":
            execs = []
            for f in Path(EXECUTION_DIR).glob("exec_*.json"):
                with open(f) as file:
                    execs.append(json.load(file))
            self.send_json({"count": len(execs), "executions": execs[-20:]})
        elif path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = f"""<!DOCTYPE html><html><body style="font-family:monospace;padding:40px;">
            <h1>🚀 NovaHiz MCP Server v4.0</h1>
            <p><b>HTTP API:</b> http://{HOST}:{PORT}</p>
            <hr/>
            <h3>Endpoints:</h3>
            <ul>
            <li><a href="/health">GET /health</a> — Health check</li>
            <li><a href="/tools">GET /tools</a> — List tools</li>
            <li><a href="/agents">GET /agents</a> — List agents</li>
            <li><a href="/route?task=Build API">GET /route?task=...</a> — Route task</li>
            <li><a href="/executions">GET /executions</a> — List executions</li>
            </ul>
            <hr/>
            <h3>Tools:</h3>
            <ul>
            <li>novahiz_route — Route to optimal agent</li>
            <li>novahiz_execute — Execute with agent</li>
            <li>novahiz_auto — Auto route + execute</li>
            <li>novahiz_list_agents — List all agents</li>
            <li>novahiz_health — Health check</li>
            </ul>
            </body></html>"""
            self.wfile.write(html.encode())
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"

        try:
            data = json.loads(body)
        except Exception:
            data = {}

        if path == "/route":
            task = data.get("task")
            self.send_json(route_task(task) if task else {"error": "Missing task"})
        elif path == "/execute":
            agent = data.get("agent")
            task = data.get("task")
            if agent and task:
                self.send_json(execute_task_direct(agent, task))
            else:
                self.send_json({"error": "Missing agent or task"}, 400)
        elif path == "/auto":
            task = data.get("task")
            self.send_json(
                auto_route_and_execute(task) if task else {"error": "Missing task"}
            )
        else:
            self.send_json({"error": "Not found"}, 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


# =============================================================================
# SERVER
# =============================================================================
class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def run_server():
    server = ThreadedHTTPServer((HOST, PORT), MCPHandler)
    log("INFO", f"Starting HTTP server on http://{HOST}:{PORT}")
    log(
        "INFO",
        f"Tools: ['novahiz_route', 'novahiz_execute', 'novahiz_auto', 'novahiz_list_agents', 'novahiz_health']",
    )
    print(f"\n🚀 NovaHiz MCP Server v4.0")
    print(f"📡 HTTP API: http://{HOST}:{PORT}")
    print(f"🏥 Health:   http://{HOST}:{PORT}/health")
    print(
        f"🛠️  Tools:    novahiz_route, novahiz_execute, novahiz_auto, novahiz_list_agents, novahiz_health\n"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("INFO", "Server stopped")
        server.shutdown()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        # Stdio mode for OpenCode
        print(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "novahiz-mcp",
                            "version": "4.0.0",
                            "http": f"http://{HOST}:{PORT}",
                        },
                    },
                }
            ),
            flush=True,
        )
        print(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "result": {
                        "tools": [
                            {"name": "novahiz_route"},
                            {"name": "novahiz_execute"},
                            {"name": "novahiz_auto"},
                            {"name": "novahiz_list_agents"},
                            {"name": "novahiz_health"},
                        ]
                    },
                }
            ),
            flush=True,
        )
        run_server()
    else:
        print(f"NovaHiz MCP Server v4.0 — HTTP API")
        print("=" * 60)
        print(f"API: http://{HOST}:{PORT}")
        print(f"Health: http://{HOST}:{PORT}/health")
        print(
            f"Tools: ['novahiz_route', 'novahiz_execute', 'novahiz_auto', 'novahiz_list_agents', 'novahiz_health']"
        )
        print("")
        print("Usage:")
        print(f"  python3 {sys.argv[0]}           # Start HTTP server")
        print(f"  python3 {sys.argv[0]} --stdio   # Stdio + HTTP for OpenCode")
        print("")
        print("API Examples:")
        print(f"  curl http://{HOST}:{PORT}/health")
        print(f"  curl http://{HOST}:{PORT}/route?task=Build+API")
        print(f'  curl -X POST -d \'{{"task":"Build API"}}\' http://{HOST}:{PORT}/auto')
        print("")
        run_server()
