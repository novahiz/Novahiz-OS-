# NOVAHIZ API — QUICK REFERENCE

**Version:** 1.7  
**Port:** 8080  
**Updated:** 2026-05-15

---

## START API SERVER

```bash
# Manual
python3 ~/.opencode/api/server.py

# Background
python3 ~/.opencode/api/server.py &

# Via CLI
nv api start

# Check
curl http://localhost:8080/api/health
```

---

## ENDPOINTS

### System

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health` | GET | Public | Health check |
| `/api/stats` | GET | Bearer | Global statistics |
| `/api/openapi.json` | GET | Public | OpenAPI 3.0.3 spec |

### Agents

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/agents` | GET | Bearer | List all agents |
| `/api/agents/:id` | GET | Bearer | Get agent details |
| `/api/agents/stats` | GET | Bearer | Agent statistics |

### Skills

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/skills` | GET | Bearer | List all skills |
| `/api/skills/stats` | GET | Bearer | Skill statistics |

### Tasks

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/tasks` | GET | Bearer | List tasks |
| `/api/tasks/stats` | GET | Bearer | Task statistics |
| `/api/task/:id` | GET | Bearer | Get task details |

### Routing

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/routing/route?task=<>` | GET | Bearer | Route a task |
| `/api/routing/history` | GET | Bearer | Routing history |

---

## AUTHENTICATION

### Enable Auth (Opt-in)

```bash
cat > ~/.opencode/config/api-auth.json << 'EOF'
{
  "enabled": true,
  "token": "your-secret-token-here",
  "createdAt": "2026-05-15T00:00:00",
  "expiresAt": "2027-05-15T00:00:00"
}
EOF
```

### Use in Requests

```bash
curl -H "Authorization: Bearer your-secret-token-here" \
     http://localhost:8080/api/stats
```

### Response on Auth Fail

```json
{
  "error": "Unauthorized",
  "message": "Valid API token required"
}
```

---

## RATE LIMITING

**Limit:** 100 requests per minute per IP  
**Window:** 60 seconds  
**Response on Exceed:** 429 Too Many Requests

```json
{
  "error": "Too Many Requests",
  "message": "Rate limit of 100 requests per 60s exceeded"
}
```

**Header:** `Retry-After: 60`

---

## CURL EXAMPLES

### Health Check (Public)
```bash
curl http://localhost:8080/api/health

# Response:
{
  "status": "healthy",
  "timestamp": "2026-05-15T01:12:14",
  "version": "1.7"
}
```

### Get Stats
```bash
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8080/api/stats

# Response:
{
  "version": "1.7",
  "agents": 22,
  "skills": 59,
  "tasks": 0,
  "routes": 2
}
```

### List Agents
```bash
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8080/api/agents

# Response:
[
  {
    "id": "novahiz-router",
    "name": "Novahiz Router",
    "type": "primary",
    "domain": "orchestration",
    "score": 100
  },
  {
    "id": "luna-design",
    "name": "Luna",
    "type": "subagent",
    "domain": "design",
    "score": 95
  }
  # ... 22 total
]
```

### Route a Task
```bash
curl -G -H "Authorization: Bearer TOKEN" \
     --data-urlencode "task=Design a landing page" \
     http://localhost:8080/api/routing/route

# Response:
{
  "classification": "MEDIUM",
  "optimal_agent": "luna-design",
  "score": 95,
  "routing_id": "route_20260515_011214"
}
```

### Get Routing History
```bash
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8080/api/routing/history

# Response:
[
  {
    "id": "route_20260515_011214",
    "task": "Design a landing page",
    "classification": "MEDIUM",
    "agent": "luna-design",
    "timestamp": "2026-05-15T01:12:14"
  }
]
```

### Get OpenAPI Spec
```bash
curl http://localhost:8080/api/openapi.json
```

---

## POST ENDPOINTS

### Create Task (Example)

```bash
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task": "Design login page", "agent": "luna-design"}' \
  http://localhost:8080/api/tasks
```

---

## RESPONSE CODES

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized (auth enabled) |
| 404 | Not Found |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

---

## OPENAPI SPEC

**Location:** `~/.opencode/api/docs/openapi.json`

**Version:** 3.0.3

**Access:**
```bash
curl http://localhost:8080/api/openapi.json
```

**Components:**
- Info (title, version, contact)
- Servers (localhost:8080)
- Paths (9 endpoints)
- Components (schemas, security schemes)
- Tags (System, Agents, Skills, Tasks, Routing)

---

## MANAGEMENT

### Check if Running
```bash
pgrep -f "api-server.py" && echo "Running" || echo "Not running"
```

### Start
```bash
python3 ~/.opencode/api/server.py &
```

### Stop
```bash
pkill -f "api-server.py"
```

### Restart
```bash
pkill -f "api-server.py"
python3 ~/.opencode/api/server.py &
```

### Check Port
```bash
netstat -tlnp | grep 8080
```

---

## LOGS

**Location:** `~/.opencode/logs/novahiz.log`

**View:**
```bash
tail -f ~/.opencode/logs/novahiz.log | grep API
```

---

## MONITORING

### Health Check Script
```bash
#!/bin/bash
response=$(curl -s http://localhost:8080/api/health)
if echo "$response" | grep -q "healthy"; then
  echo "✓ API is healthy"
else
  echo " API is down"
  # Send alert (Telegram/Discord)
fi
```

### Cron Monitoring
```bash
# Check every 5 minutes
*/5 * * * * curl -s http://localhost:8080/api/health | grep -q "healthy" || echo "API DOWN" | mail -s "NovaHiz Alert" admin@example.com
```

---

## TROUBLESHOOTING

### Port Already in Use
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9

# Restart API
python3 ~/.opencode/api/server.py &
```

### Auth Errors
```bash
# Check config
cat ~/.opencode/config/api-auth.json

# Disable auth temporarily
echo '{"enabled": false}' > ~/.opencode/config/api-auth.json
```

### Rate Limit Exceeded
```bash
# Wait 60 seconds
sleep 60

# Or increase limit in server.py
# RATE_LIMIT = 200  # Change from 100 to 200
```

---

## INTEGRATION EXAMPLES

### Python
```python
import requests

TOKEN = "your-token"
BASE_URL = "http://localhost:8080"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Get stats
response = requests.get(f"{BASE_URL}/api/stats", headers=headers)
print(response.json())

# Route task
response = requests.get(
    f"{BASE_URL}/api/routing/route",
    headers=headers,
    params={"task": "Design a landing page"}
)
print(response.json())
```

### Node.js
```javascript
const axios = require('axios');

const TOKEN = 'your-token';
const BASE_URL = 'http://localhost:8080';

const config = {
  headers: { 'Authorization': `Bearer ${TOKEN}` }
};

// Get stats
axios.get(`${BASE_URL}/api/stats`, config)
  .then(res => console.log(res.data));

// Route task
axios.get(`${BASE_URL}/api/routing/route`, {
  ...config,
  params: { task: 'Design a landing page' }
})
  .then(res => console.log(res.data));
```

### Bash Script
```bash
#!/bin/bash

TOKEN="your-token"
BASE_URL="http://localhost:8080"

# Get stats
curl -s -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/api/stats" | jq .

# Route task
curl -s -G -H "Authorization: Bearer $TOKEN" \
     --data-urlencode "task=Design login page" \
     "$BASE_URL/api/routing/route" | jq .
```

---

**Quick Reference — NovaHiz API v1.7**
