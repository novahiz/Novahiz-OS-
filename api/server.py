#!/usr/bin/env python3
"""
NovaHiz OS - API Server
REST API using standard library only (no external dependencies)
"""

import json
import sqlite3
import os
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import datetime
from collections import defaultdict

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
DATA_DIR = os.path.join(NOVAHIZ_DIR, "data")
CONFIG_DIR = os.path.join(NOVAHIZ_DIR, "config")
PORT = 8080

# Rate limiting: 100 requests per minute per IP
RATE_LIMIT = 100
RATE_WINDOW = 60  # seconds
request_counts = defaultdict(list)  # {ip: [(timestamp, count)]}

NOVAHIZ_DB = os.path.join(DATA_DIR, "novahiz.db")
SKILLS_DB = os.path.join(DATA_DIR, "skills-index.db")
TASKS_DB = os.path.join(DATA_DIR, "tasks-history.db")
TRACKING_DB = os.path.join(DATA_DIR, "agents-tracking.db")
AUTH_CONFIG = os.path.join(CONFIG_DIR, "api-auth.json")

def check_auth_config():
    """Load auth configuration"""
    if os.path.exists(AUTH_CONFIG):
        with open(AUTH_CONFIG) as f:
            return json.load(f)
    return {"enabled": False, "token": "", "createdAt": None, "expiresAt": None}

def verify_auth(handler):
    """Verify authentication for a request"""
    config = check_auth_config()
    
    if not config.get("enabled"):
        return True
    
    auth_header = handler.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header[7:]
    
    if config.get("token") != token:
        return False
    
    if config.get("expiresAt"):
        expires = datetime.datetime.fromisoformat(config["expiresAt"])
        if datetime.datetime.now() > expires:
            return False
    
    return True

class NovahizAPI(BaseHTTPRequestHandler):
    
    def send_auth_error(self):
        """Send authentication error response"""
        self.send_response(401)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": "Unauthorized", "message": "Valid API token required"}).encode())
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # Rate limiting check
        client_ip = self.client_address[0]
        current_time = datetime.datetime.now().timestamp()
        
        if client_ip not in request_counts:
            request_counts[client_ip] = []
        
        # Remove old requests outside the window
        request_counts[client_ip] = [
            (ts, cnt) for ts, cnt in request_counts[client_ip]
            if current_time - ts < RATE_WINDOW
        ]
        
        # Count requests in current window
        total_requests = sum(cnt for _, cnt in request_counts[client_ip])
        
        if total_requests >= RATE_LIMIT:
            self.send_response(429)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Retry-After', str(RATE_WINDOW))
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Too Many Requests", "message": f"Rate limit of {RATE_LIMIT} requests per {RATE_WINDOW}s exceeded"}).encode())
            return
        
        # Record this request
        request_counts[client_ip].append((current_time, 1))
        
        # Health endpoint is always public
        if path != '/api/health' and not verify_auth(self):
            self.send_auth_error()
            return
        
        if path == '/api/health':
            self.handle_health()
        elif path == '/api/agents':
            self.handle_get_agents(query)
        elif path == '/api/agents/stats':
            self.handle_agent_stats()
        elif path == '/api/skills':
            self.handle_get_skills(query)
        elif path == '/api/skills/stats':
            self.handle_skills_stats()
        elif path == '/api/tasks':
            self.handle_get_tasks(query)
        elif path == '/api/tasks/stats':
            self.handle_tasks_stats()
        elif path == '/api/routing/route':
            self.handle_routing(query)
        elif path == '/api/routing/history':
            self.handle_routing_history()
        elif path == '/api/stats':
            self.handle_global_stats()
        elif path.startswith('/api/agent/'):
            agent_id = path.split('/')[-1]
            self.handle_get_agent(agent_id)
        elif path.startswith('/api/task/'):
            try:
                task_id = int(path.split('/')[-1])
                self.handle_get_task(task_id)
            except:
                self.send_error(400, "Invalid task ID")
        elif path == '/api/openapi.json' or path == '/api/docs':
            self.handle_openapi_spec()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if not verify_auth(self):
            self.send_auth_error()
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        if path == '/api/agents/search':
            self.handle_search_agents(data)
        elif path == '/api/tasks':
            self.handle_create_task(data)
        elif path == '/api/tasks/start':
            self.handle_start_task(data)
        elif path == '/api/tasks/complete':
            self.handle_complete_task(data)
        elif path == '/api/agents/track':
            self.handle_track_agent(data)
        elif path == '/api/routing/route':
            self.handle_route_task(data)
        else:
            self.send_error(404, "Endpoint not found")
    
    def send_cors_headers(self):
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def handle_health(self):
        self.send_json({
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'version': '1.7'
        })
    
    def handle_get_agents(self, query):
        limit = int(query.get('limit', [50])[0])
        domain = query.get('domain', [None])[0]
        status = query.get('status', [None])[0]
        
        conn = sqlite3.connect(NOVAHIZ_DB)
        cursor = conn.cursor()
        
        sql = "SELECT id, name, type, domain, score, status, usage_count, success_rate FROM agents"
        params = []
        
        if domain:
            sql += " WHERE domain = ?"
            params.append(domain)
        if status:
            sql += " AND status = ?" if domain else " WHERE status = ?"
            params.append(status)
        
        sql += " ORDER BY score DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        agents = [{
            'id': r[0], 'name': r[1], 'type': r[2], 'domain': r[3],
            'score': r[4], 'status': r[5], 'usage_count': r[6], 'success_rate': r[7]
        } for r in rows]
        
        self.send_json({'agents': agents, 'count': len(agents)})
    
    def handle_get_agent(self, agent_id):
        conn = sqlite3.connect(NOVAHIZ_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            self.send_error(404, "Agent not found")
            return
        
        columns = ['id', 'name', 'type', 'domain', 'score', 'status', 'file_path',
                  'description', 'specialty', 'origin', 'invoke_method', 'created_at',
                  'updated_at', 'last_used', 'usage_count', 'success_count', 'success_rate']
        
        agent = dict(zip(columns, row))
        conn.close()
        
        self.send_json(agent)
    
    def handle_agent_stats(self):
        conn = sqlite3.connect(NOVAHIZ_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'active'")
        active = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'simulated'")
        simulated = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(score) FROM agents")
        avg_score = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT domain, COUNT(*) FROM agents GROUP BY domain ORDER BY COUNT(*) DESC")
        by_domain = [{'domain': r[0], 'count': r[1]} for r in cursor.fetchall()]
        
        conn.close()
        
        self.send_json({
            'total_agents': active + simulated,
            'active': active,
            'simulated': simulated,
            'avg_score': round(avg_score, 1),
            'by_domain': by_domain
        })
    
    def handle_get_skills(self, query):
        limit = int(query.get('limit', [50])[0])
        category = query.get('category', [None])[0]
        
        conn = sqlite3.connect(SKILLS_DB)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("SELECT * FROM skills WHERE category = ? ORDER BY usage_count DESC LIMIT ?", (category, limit))
        else:
            cursor.execute("SELECT * FROM skills ORDER BY usage_count DESC LIMIT ?", (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'name', 'category', 'trigger', 'description', 'file_path', 'keywords', 'agent_id', 'usage_count', 'success_rate', 'created_at', 'last_used']
        skills = [dict(zip(columns, r)) for r in rows]
        
        self.send_json({'skills': skills, 'count': len(skills)})
    
    def handle_skills_stats(self):
        conn = sqlite3.connect(SKILLS_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM skills")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(usage_count) FROM skills")
        total_usage = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT AVG(success_rate) FROM skills WHERE success_rate > 0")
        avg_success = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT category, COUNT(*) FROM skills GROUP BY category ORDER BY COUNT(*) DESC")
        by_category = [{'category': r[0], 'count': r[1]} for r in cursor.fetchall()]
        
        conn.close()
        
        self.send_json({
            'total_skills': total,
            'total_usage': total_usage,
            'avg_success_rate': round(avg_success, 1),
            'by_category': by_category
        })
    
    def handle_get_tasks(self, query):
        limit = int(query.get('limit', [50])[0])
        status = query.get('status', [None])[0]
        
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?", (status, limit))
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'task_text', 'classification', 'domain', 'primary_agent', 'supporting_agents', 'duration', 'status', 'success', 'output', 'error', 'created_at', 'completed_at']
        tasks = [dict(zip(columns, r)) for r in rows]
        
        self.send_json({'tasks': tasks, 'count': len(tasks)})
    
    def handle_get_task(self, task_id):
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            self.send_error(404, "Task not found")
            return
        
        columns = ['id', 'task_text', 'classification', 'domain', 'primary_agent', 'supporting_agents', 'duration', 'status', 'success', 'output', 'error', 'created_at', 'completed_at']
        task = dict(zip(columns, row))
        conn.close()
        
        self.send_json(task)
    
    def handle_tasks_stats(self):
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'in_progress'")
        in_progress = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
        completed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'failed'")
        failed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE success = 1")
        successes = cursor.fetchone()[0]
        
        total = pending + in_progress + completed + failed
        success_rate = round(successes / completed * 100, 1) if completed > 0 else 0
        
        conn.close()
        
        self.send_json({
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'failed': failed,
            'success_rate': success_rate
        })
    
    def handle_create_task(self, data):
        task_text = data.get('task_text', '')
        classification = data.get('classification', 'MEDIUM')
        domain = data.get('domain', 'general')
        
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (task_text, classification, domain, status, created_at)
            VALUES (?, ?, ?, 'pending', ?)
        """, (task_text, classification, domain, datetime.datetime.now().isoformat()))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        self.send_json({'id': task_id, 'status': 'created'}, 201)
    
    def handle_start_task(self, data):
        task_id = data.get('task_id')
        agent = data.get('agent')
        
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks SET status = 'in_progress', primary_agent = ? WHERE id = ?
        """, (agent, task_id))
        conn.commit()
        conn.close()
        
        self.send_json({'status': 'started'})
    
    def handle_complete_task(self, data):
        task_id = data.get('task_id')
        success = data.get('success', True)
        
        conn = sqlite3.connect(TASKS_DB)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tasks SET status = 'completed', success = ?, completed_at = ? WHERE id = ?
        """, (success, datetime.datetime.now().isoformat(), task_id))
        conn.commit()
        conn.close()
        
        self.send_json({'status': 'completed'})
    
    def handle_track_agent(self, data):
        agent_id = data.get('agent_id')
        action = data.get('action', 'used')
        task = data.get('task', '')
        
        conn = sqlite3.connect(TRACKING_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_activity (agent_id, action, task, success, timestamp)
            VALUES (?, ?, ?, 1, ?)
        """, (agent_id, action, task, datetime.datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        self.send_json({'status': 'tracked'})
    
    def handle_routing(self, query):
        task = query.get('task', [''])[0]
        
        if not task:
            self.send_error(400, "Task is required")
            return
        
        conn = sqlite3.connect(NOVAHIZ_DB)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, domain, score FROM agents 
            WHERE status = 'active' 
            ORDER BY score DESC LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            self.send_json({'error': 'No agents available'})
            return
        
        self.send_json({
            'task': task,
            'agent': {'id': row[0], 'name': row[1], 'domain': row[2], 'score': row[3]},
            'classification': 'MEDIUM',
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    def handle_routing_history(self):
        conn = sqlite3.connect(NOVAHIZ_DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM routing_log ORDER BY timestamp DESC LIMIT 20")
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'task', 'classification', 'selected_agent', 'vote_count', 'consensus', 'decision', 'timestamp']
        history = [dict(zip(columns, r)) for r in rows]
        
        self.send_json({'history': history})
    
    def handle_openapi_spec(self):
        spec_path = os.path.join(NOVAHIZ_DIR, 'api', 'docs', 'openapi.json')
        if os.path.exists(spec_path):
            with open(spec_path) as f:
                data = json.load(f)
            self.send_json(data)
        else:
            self.send_json({'error': 'OpenAPI spec not found', 'message': 'Run novahiz-api-docs.py to generate'})
    
    def handle_global_stats(self):
        novahiz_conn = sqlite3.connect(NOVAHIZ_DB)
        skills_conn = sqlite3.connect(SKILLS_DB)
        tasks_conn = sqlite3.connect(TASKS_DB)
        
        nc = novahiz_conn.cursor()
        sc = skills_conn.cursor()
        tc = tasks_conn.cursor()
        
        nc.execute("SELECT COUNT(*) FROM agents")
        sc.execute("SELECT COUNT(*) FROM skills")
        tc.execute("SELECT COUNT(*) FROM tasks")
        
        agents_count = nc.fetchone()[0]
        skills_count = sc.fetchone()[0]
        tasks_count = tc.fetchone()[0]
        
        novahiz_conn.close()
        skills_conn.close()
        tasks_conn.close()
        
        self.send_json({
            'version': '1.7',
            'agents': agents_count,
            'skills': skills_count,
            'tasks': tasks_count,
            'timestamp': datetime.datetime.now().isoformat()
        })
    
    def handle_search_agents(self, data):
        query = data.get('query', '')
        
        conn = sqlite3.connect(NOVAHIZ_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM agents 
            WHERE name LIKE ? OR domain LIKE ? OR description LIKE ?
            LIMIT 20
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = ['id', 'name', 'type', 'domain', 'score', 'status']
        agents = [dict(zip(columns, r[:6])) for r in rows]
        
        self.send_json({'agents': agents, 'count': len(agents)})
    
    def log_message(self, format, *args):
        print(f"[API] {args[0]}")

def run_server(port=PORT):
    server = HTTPServer(('localhost', port), NovahizAPI)
    print(f"\n╔════════════════════════════════════════════╗")
    print(f"║       NOVAHIZ API SERVER v1.7           ║")
    print(f"╚════════════════════════════════════════════╝")
    print(f"\n🚀 Server running at http://localhost:{port}")
    print(f"\n📡 Available endpoints:")
    print(f"  GET  /api/health              - Health check")
    print(f"  GET  /api/agents             - List agents")
    print(f"  GET  /api/agents/stats       - Agent statistics")
    print(f"  GET  /api/skills             - List skills")
    print(f"  GET  /api/skills/stats       - Skills statistics")
    print(f"  GET  /api/tasks              - List tasks")
    print(f"  GET  /api/tasks/stats       - Tasks statistics")
    print(f"  GET  /api/routing/route     - Route a task")
    print(f"  GET  /api/routing/history   - Routing history")
    print(f"  GET  /api/stats              - Global stats")
    print(f"\nPress Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    run_server()