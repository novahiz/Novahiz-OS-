#!/usr/bin/env python3
"""
NovaHiz OS — REST API v2.0
Complete REST API with webhooks + SSE for deliberations
"""
import sys, os, json, time, threading, subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

from pathlib import Path
HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
CONFIG_DIR = os.path.join(NOVAHIZ_DIR, "config")
LOGS_DIR = os.path.join(NOVAHIZ_DIR, "logs")

# Accès direct à l'engine (évite subprocess vers smart-router.py)
_ROOT = str(Path(__file__).resolve().parent.parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from engine.router import Router
from engine.scoring import Scoreboard

# === API CONFIGURATION ===
API_CONFIG = {
    "host": "127.0.0.1",
    "port": 8080,
    "cors": True,
    "webhooks_enabled": True,
    "sse_enabled": True,
}

# === WEBHOOK SUBSCRIPTIONS ===
WEBHOOKS_FILE = os.path.join(CONFIG_DIR, "webhooks.json")

def load_webhooks():
    if os.path.isfile(WEBHOOKS_FILE):
        try:
            with open(WEBHOOKS_FILE, encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"subscriptions": []}

def save_webhooks(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(WEBHOOKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def trigger_webhook(event_type, payload):
    """Trigger webhooks for an event"""
    webhooks = load_webhooks()
    for sub in webhooks.get("subscriptions", []):
        if event_type in sub.get("events", []):
            url = sub.get("url")
            if url:
                # Fire and forget
                threading.Thread(target=send_webhook, args=(url, event_type, payload), daemon=True).start()

def send_webhook(url, event_type, payload):
    """Send webhook payload"""
    try:
        import urllib.request
        data = json.dumps({"event": event_type, "payload": payload, "timestamp": datetime.now().isoformat()}).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            log_api("INFO", f"Webhook sent to {url}: {resp.status}")
    except Exception as e:
        log_api("ERROR", f"Webhook failed to {url}: {e}")

# === SSE CLIENTS ===
SSE_CLIENTS = []
SSE_LOCK = threading.Lock()

def add_sse_client(handler):
    with SSE_LOCK:
        SSE_CLIENTS.append(handler)

def remove_sse_client(handler):
    with SSE_LOCK:
        if handler in SSE_CLIENTS:
            SSE_CLIENTS.remove(handler)

def broadcast_sse(event_type, data):
    """Broadcast SSE event to all connected clients"""
    with SSE_LOCK:
        for client in SSE_CLIENTS[:]:
            try:
                client.send_sse(event_type, data)
            except (BrokenPipeError, ConnectionResetError, OSError):
                SSE_CLIENTS.remove(client)

# === LOGGING ===
def log_api(level, msg):
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_path = os.path.join(LOGS_DIR, "api.log")
    entry = f"[{datetime.now().isoformat()}] [{level}] {msg}"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
    if level in ("ERROR", "WARN"):
        print(entry)

# === API HANDLER ===
class APIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        if API_CONFIG["cors"]:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", content_type)
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers(204)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        routes = {
            "/": self._get_root,
            "/health": self._get_health,
            "/status": self._get_status,
            "/agents": self._get_agents,
            "/skills": self._get_skills,
            "/scoreboard": self._get_scoreboard,
            "/memory": self._get_memory,
            "/webhooks": self._get_webhooks,
            "/events": self._get_events,  # SSE endpoint
        }
        
        if path in routes:
            routes[path](query)
        elif path.startswith("/route/"):
            task = path[7:]  # Remove "/route/"
            self._route_task(task, query)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}
        
        routes = {
            "/route": self._post_route,
            "/execute": self._post_execute,
            "/webhooks": self._post_webhook,
            "/scoreboard/update": self._post_scoreboard_update,
        }
        
        if path in routes:
            routes[path](data)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path.startswith("/webhooks/"):
            webhook_id = path[10:]
            self._delete_webhook(webhook_id)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def send_sse(self, event_type, data):
        """Send SSE event"""
        try:
            self.wfile.write(f"event: {event_type}\n".encode())
            self.wfile.write(f"data: {json.dumps(data)}\n\n".encode())
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
    
    def _get_root(self, query):
        self._set_headers()
        self.wfile.write(json.dumps({
            "name": "NovaHiz OS API",
            "version": "2.0",
            "endpoints": [
                "GET  /",
                "GET  /health",
                "GET  /status",
                "GET  /agents",
                "GET  /skills",
                "GET  /scoreboard",
                "GET  /memory",
                "GET  /route/<task>",
                "POST /route",
                "POST /execute",
                "GET  /webhooks",
                "POST /webhooks",
                "DELETE /webhooks/<id>",
                "GET  /events (SSE)",
            ]
        }, indent=2).encode())
    
    def _get_health(self, query):
        health_script = os.path.join(NOVAHIZ_DIR, "scripts", "python", "health-monitor.py")
        if os.path.isfile(health_script):
            result = subprocess.run(
                [sys.executable, health_script, "status"],
                capture_output=True, text=True, timeout=10
            )
            try:
                data = json.loads(result.stdout)
                healthy = all(s.get("healthy") for s in data.get("status", {}).values())
                self._set_headers(200 if healthy else 503)
                self.wfile.write(result.stdout.encode())
                return
            except (json.JSONDecodeError, ValueError, OSError):
                pass
        self._set_headers(503)
        self.wfile.write(json.dumps({"healthy": False, "error": "Health check failed"}).encode())
    
    def _get_status(self, query):
        """System status"""
        from pathlib import Path
        
        agents_dir = os.path.join(NOVAHIZ_DIR, "agents")
        skills_dir = os.path.join(NOVAHIZ_DIR, "skills")
        
        agent_count = len([f for f in os.listdir(agents_dir) if f.endswith('.yaml')]) if os.path.isdir(agents_dir) else 0
        skill_count = len([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]) if os.path.isdir(skills_dir) else 0
        
        nexus_path = os.path.join(NOVAHIZ_DIR, "memory", "nexus.json")
        memory_nodes = 0
        if os.path.isfile(nexus_path):
            with open(nexus_path, encoding='utf-8') as f:
                nexus = json.load(f)
                memory_nodes = len(nexus.get("nodes", []))
        
        self._set_headers()
        self.wfile.write(json.dumps({
            "agents": agent_count,
            "skills": skill_count,
            "memory_nodes": memory_nodes,
            "timestamp": datetime.now().isoformat()
        }, indent=2).encode())
    
    def _get_agents(self, query):
        """List all agents"""
        reg_path = os.path.join(NOVAHIZ_DIR, "registry", "novahiz-registry.json")
        if os.path.isfile(reg_path):
            with open(reg_path, encoding='utf-8') as f:
                registry = json.load(f)
            self._set_headers()
            self.wfile.write(json.dumps(registry.get("agents", []), indent=2).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Registry not found"}).encode())
    
    def _get_skills(self, query):
        """List all skills"""
        skills_dir = os.path.join(NOVAHIZ_DIR, "skills")
        if os.path.isdir(skills_dir):
            skills = sorted([d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))])
            self._set_headers()
            self.wfile.write(json.dumps({"skills": skills, "total": len(skills)}, indent=2).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Skills directory not found"}).encode())
    
    def _get_scoreboard(self, query):
        """Get agent scoreboard"""
        sb_path = os.path.join(CONFIG_DIR, "scoreboard.json")
        if os.path.isfile(sb_path):
            with open(sb_path, encoding='utf-8') as f:
                self._set_headers()
                self.wfile.write(f.read().encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Scoreboard not found"}).encode())
    
    def _get_memory(self, query):
        """Get memory nodes"""
        nexus_path = os.path.join(NOVAHIZ_DIR, "memory", "nexus.json")
        if os.path.isfile(nexus_path):
            with open(nexus_path, encoding='utf-8') as f:
                nexus = json.load(f)
            
            limit = int(query.get("limit", [20])[0])
            nodes = nexus.get("nodes", [])[-limit:]
            
            self._set_headers()
            self.wfile.write(json.dumps({"nodes": nodes, "total": len(nodes)}, indent=2).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Nexus not found"}).encode())
    
    def _get_webhooks(self, query):
        """List webhook subscriptions"""
        webhooks = load_webhooks()
        self._set_headers()
        self.wfile.write(json.dumps(webhooks, indent=2).encode())
    
    def _get_events(self, query):
        """SSE endpoint"""
        if not API_CONFIG["sse_enabled"]:
            self._set_headers(503)
            self.wfile.write(json.dumps({"error": "SSE disabled"}).encode())
            return
        
        self._set_headers(content_type="text/event-stream")
        add_sse_client(self)
        
        # Send initial connection event
        self.send_sse("connected", {"timestamp": datetime.now().isoformat()})
        
        # Keep connection alive
        try:
            while True:
                time.sleep(30)
                self.send_sse("ping", {"timestamp": datetime.now().isoformat()})
        except GeneratorExit:
            remove_sse_client(self)
        except Exception:
            remove_sse_client(self)
    
    def _route_task(self, task, query):
        """Route a task (GET) via engine.Router"""
        try:
            router = Router()
            result = router.route(task)
            data = {"success": True, "task": task, "primary": result}
            self._set_headers()
            self.wfile.write(json.dumps(data).encode())
            trigger_webhook("task.routed", data)
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Routing failed: {str(e)}"}).encode())
    
    def _post_route(self, data):
        """Route a task (POST) via engine.Router"""
        task = data.get("task", "")
        if not task:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Missing task"}).encode())
            return
        
        try:
            router = Router()
            response_data = router.route(task)
            self._set_headers()
            self.wfile.write(json.dumps(response_data).encode())
            trigger_webhook("task.routed", response_data)
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Routing failed: {str(e)}"}).encode())
    
    def _post_execute(self, data):
        """Execute a task with an agent"""
        agent = data.get("agent")
        task = data.get("task")
        
        if not agent or not task:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Missing agent or task"}).encode())
            return
        
        # Trigger execution (simplified - would normally invoke agent)
        response = {
            "status": "queued",
            "agent": agent,
            "task": task,
            "timestamp": datetime.now().isoformat()
        }
        
        self._set_headers(202)
        self.wfile.write(json.dumps(response, indent=2).encode())
        
        # Trigger webhook
        trigger_webhook("task.executed", response)
    
    def _post_webhook(self, data):
        """Register a webhook subscription"""
        url = data.get("url")
        events = data.get("events", ["*"])
        
        if not url:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Missing url"}).encode())
            return
        
        webhooks = load_webhooks()
        webhook_id = f"wh_{int(time.time())}"
        
        subscription = {
            "id": webhook_id,
            "url": url,
            "events": events,
            "created": datetime.now().isoformat(),
            "active": True
        }
        
        webhooks["subscriptions"].append(subscription)
        save_webhooks(webhooks)
        
        self._set_headers(201)
        self.wfile.write(json.dumps(subscription, indent=2).encode())
        
        log_api("INFO", f"Webhook registered: {url} for events: {events}")
    
    def _delete_webhook(self, webhook_id):
        """Delete a webhook subscription"""
        webhooks = load_webhooks()
        before = len(webhooks["subscriptions"])
        webhooks["subscriptions"] = [
            s for s in webhooks["subscriptions"] if s.get("id") != webhook_id
        ]
        
        if len(webhooks["subscriptions"]) < before:
            save_webhooks(webhooks)
            self._set_headers()
            self.wfile.write(json.dumps({"deleted": webhook_id}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Webhook not found"}).encode())
    
    def _post_scoreboard_update(self, data):
        """Update agent scoreboard via engine.Scoreboard"""
        agent_id = data.get("agent")
        success = data.get("success", True)
        duration = data.get("duration", 0)
        
        if not agent_id:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Missing agent"}).encode())
            return
        
        try:
            sb = Scoreboard()
            sb.record_execution(agent_id, "api", success, duration)
            stats = sb.get_stats(agent_id)
            response_data = {"agent": agent_id, **stats}
            self._set_headers()
            self.wfile.write(json.dumps(response_data).encode())
            trigger_webhook("scoreboard.updated", response_data)
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": f"Scoreboard update failed: {str(e)}"}).encode())
    
    def log_message(self, format, *args):
        log_api("INFO", f"{self.address_string()} - {format % args}")

# === API SERVER ===
class APIServer:
    def __init__(self):
        self.server = None
        self.thread = None
    
    def start(self, host=None, port=None):
        host = host or API_CONFIG["host"]
        port = port or API_CONFIG["port"]
        
        self.server = HTTPServer((host, port), APIHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        
        log_api("INFO", f"API server started on http://{host}:{port}")
        print(f"✓ API server running on http://{host}:{port}")
    
    def stop(self):
        if self.server:
            self.server.shutdown()
            log_api("INFO", "API server stopped")
            print("API server stopped")

# === CLI ===
def cmd_start():
    server = APIServer()
    pidfile = os.path.join(NOVAHIZ_DIR, "api.pid")
    with open(pidfile, "w") as f:
        f.write(str(os.getpid()))
    server.start()
    print("Press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
    finally:
        if os.path.isfile(pidfile):
            os.remove(pidfile)

def cmd_stop():
    """Stop API server via PID file (graceful shutdown)."""
    pidfile = os.path.join(NOVAHIZ_DIR, "api.pid")
    if os.path.isfile(pidfile):
        try:
            with open(pidfile) as f:
                pid = int(f.read().strip())
            os.kill(pid, 15)  # SIGTERM — graceful
            print(f"API server stopped (PID: {pid})")
            os.remove(pidfile)
            return
        except (ProcessLookupError, OSError):
            os.remove(pidfile)
        except Exception as e:
            print(f"Failed to stop API server: {e}")
            return

    # Fallback: pgrep (évite de se tuer soi-même)
    try:
        result = subprocess.run(
            ["pgrep", "-f", "novahiz-api.py"],
            capture_output=True, text=True, timeout=5
        )
        pids = [p for p in result.stdout.strip().split() if p and p != str(os.getpid())]
        if pids:
            for pid in pids:
                os.kill(int(pid), 15)
            print(f"API server stopped (PIDs: {', '.join(pids)})")
        else:
            print("API server not running")
    except FileNotFoundError:
        print("pgrep not found — cannot stop API server")
    except Exception as e:
        print(f"Failed to stop API server: {e}")

def cmd_status():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    result = s.connect_ex(('127.0.0.1', API_CONFIG["port"]))
    s.close()
    
    if result == 0:
        print(f"✓ API server running on port {API_CONFIG['port']}")
    else:
        print(f"○ API server not running on port {API_CONFIG['port']}")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"
    
    if cmd == "start":
        cmd_start()
    elif cmd == "stop":
        cmd_stop()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Usage: novahiz-api.py [start|stop|status]")
        sys.exit(1)
