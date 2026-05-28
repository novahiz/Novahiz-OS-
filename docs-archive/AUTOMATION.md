# 🚀 NOVAHIZ MCP — Automatisation Totale

## Architecture Finale

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOVAHIZ OS v3.0                              │
│              FULLY AUTOMATED AGENT ROUTING                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  USER DEMANDE → OpenCode → MCP Server → Smart Router           │
│       ↓              ↓            ↓              ↓              │
│  "Build API"    (detect)   (novahiz_auto)  (nexus-api)         │
│       ↓              ↓            ↓              ↓              │
│  OpenCode Bridge → Execution → Subagent → Résultat             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Composants

### 1. MCP Server (`novahiz-mcp.py`)
- **Démarrage:** Automatique par OpenCode (via config MCP)
- **Transport:** stdio (OpenCode ↔ MCP)
- **Tools:** 7 tools MCP
  - `novahiz_route` — Routage seul
  - `novahiz_auto` — Routage + Exécution (AUTO)
  - `novahiz_execute` — Exécution directe
  - `novahiz_list_agents` — Liste agents
  - `novahiz_search` — Recherche
  - `novahiz_health` — Health check
  - `novahiz_execution_status` — Status exécutions

### 2. OpenCode Bridge (`opencode-bridge.py`)
- **Démarrage:** Daemon automatique
- **Rôle:** Pont entre MCP et OpenCode task system
- **Fonction:** Watch executions/ → appelle subagents

### 3. Task Processor (`task-processor.py`)
- **Démarrage:** Daemon automatique
- **Rôle:** Process pending_tasks/
- **Fonction:** Queue de tâches alternative

### 4. Supervisor (`supervisor.sh`)
- **Commande:** `bash ~/.opencode/mcp/supervisor.sh start`
- **Rôle:** Start/stop/restart des daemons
- **Gère:** Bridge + Task Processor

## Configuration OpenCode

```json
{
  "default_agent": "novahiz-router",
  "mcp": {
    "novahiz": {
      "command": "python3",
      "args": ["~/.opencode/mcp/novahiz-mcp.py", "--mcp"],
      "disabled": false,
      "auto_start": true
    }
  },
  "tools": {
    "novahiz_route": {"auto_use": true},
    "novahiz_auto": {"auto_use": true}
  },
  "agents": {
    "novahiz-router": {
      "auto_route": true
    }
  }
}
```

## Flux d'Automatisation Complète

### Scénario: User demande "Build a REST API"

```
1. USER → OpenCode
   "Build a REST API with authentication"

2. OpenCode → MCP Server (novahiz_auto tool)
   {task: "Build a REST API with authentication"}

3. MCP Server → Smart Router Python
   - Analyse keywords: "REST", "API", "authentication"
   - Score agents: nexus-api (22), ralph-execution (21)...
   - Résultat: nexus-api (100% confidence)

4. MCP Server → OpenCode Bridge
   Crée: executions/exec_TIMESTAMP.json
   {
     "agent": "nexus-api",
     "task": "Build a REST API with authentication",
     "status": "pending"
   }

5. OpenCode Bridge (daemon) détecte le fichier
   - Lit execution file
   - Appelle: task --subagent nexus-api --prompt "..."

6. nexus-api exécute la tâche
   - Utilise skill: novahiz-selection
   - Produit résultat

7. Bridge met à jour execution file
   {
     "status": "completed",
     "result": {...}
   }

8. OpenCode retourne résultat au USER
```

## Commandes Utilisateur

### Terminal
```bash
# Démarrer les services (à faire une fois)
bash ~/.opencode/mcp/supervisor.sh start

# Status
bash ~/.opencode/mcp/supervisor.sh status

# CLI unifiée
nv route "Build API"      # Voir quel agent
nv run "Build API"        # Route + execute
nv exec agent "task"      # Exécution directe
nv health                 # Health check
nv agents                 # Liste agents
```

### Dans OpenCode (automatique)
```
User: "Build a REST API"
  ↓ (automatique, pas d'intervention)
OpenCode appelle novahiz_auto
  ↓
MCP route vers nexus-api
  ↓
Bridge exécute nexus-api
  ↓
Résultat retourné
```

## Démarrage Automatique

### Option 1: Manuel (recommandé pour test)
```bash
# Une fois au début de chaque session
bash ~/.opencode/mcp/supervisor.sh start
```

### Option 2: Auto au login (Linux)
Ajouter à `~/.bashrc`:
```bash
# Novahiz MCP auto-start
if [ -f ~/.opencode/mcp/supervisor.sh ]; then
    bash ~/.opencode/mcp/supervisor.sh start > /dev/null 2>&1
fi
```

### Option 3: Systemd service (production)
```ini
# /etc/systemd/system/novahiz-mcp.service
[Unit]
Description=Novahiz MCP Services
After=network.target

[Service]
Type=simple
User=novahiz
ExecStart=/home/novahiz/.opencode/mcp/supervisor.sh start
ExecStop=/home/novahiz/.opencode/mcp/supervisor.sh stop
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable novahiz-mcp
sudo systemctl start novahiz-mcp
```

## Health Check Complet

```bash
# Status des services
bash ~/.opencode/mcp/supervisor.sh status

# Health check MCP
python3 ~/.opencode/mcp/novahiz-mcp.py health

# Status exécutions
python3 ~/.opencode/mcp/opencode-bridge.py status

# Logs
tail -f ~/.opencode/logs/mcp-server-v3.log
tail -f ~/.opencode/logs/opencode-bridge.log
```

## Exemple de Session Complète

```bash
# 1. Démarrer services
$ bash ~/.opencode/mcp/supervisor.sh start

  OpenCode Bridge: ● Running (PID: 89733)
  Task Processor: ● Running (PID: 89742)

# 2. Tester routage
$ nv route "Build a REST API"

  → Agent: nexus-api
  → Skill: novahiz-selection
  → Confidence: 100%

# 3. Tester exécution auto
$ nv run "Create login form"

  {
    "success": true,
    "agent": "luna-design",
    "execution": {
      "execution_id": "exec_20260526_192000_123456",
      "status": "pending"
    }
  }

# 4. Vérifier exécution
$ python3 ~/.opencode/mcp/opencode-bridge.py status

  Total executions: 1
    Pending: 0
    Completed: 1
```

## Pourquoi C'est Idéal

| Critère | Solution |
|---------|----------|
| **Routage automatique** | ✅ MCP novahiz_auto tool |
| **Exécution automatique** | ✅ OpenCode Bridge daemon |
| **Pas d'intervention** | ✅ Tout est chaîné |
| **Multi-agents** | ✅ 23 agents profilés |
| **Tracking** | ✅ Executions/ avec historique |
| **Health monitoring** | ✅ Logs + status |
| **Scalable** | ✅ Architecture modulaire |

## Dépannage

### MCP Server ne démarre pas
```bash
# Vérifier config
cat ~/.opencode/opencode.json | jq .mcp

# Tester manuellement
python3 ~/.opencode/mcp/novahiz-mcp.py health
```

### Bridge ne process pas les exécutions
```bash
# Check daemon
ps aux | grep opencode-bridge

# Restart
bash ~/.opencode/mcp/supervisor.sh restart

# Check logs
tail ~/.opencode/logs/opencode-bridge.log
```

### Exécutions restent "pending"
```bash
# Lister pending
ls -la ~/.opencode/executions/*.json

# Process manually
python3 ~/.opencode/mcp/opencode-bridge.py run
```

## Prochaines Améliorations (Optionnel)

1. **WebSocket:** Communication real-time MCP ↔ OpenCode
2. **Feedback loop:** Ajuster scores basés sur résultats
3. **Multi-model:** Router aussi le modèle LLM (flash/smart/premium)
4. **Priority queue:** Prioriser les exécutions critiques
5. **Retry logic:** Re-execute on failure

---

**Status:** ✅ Production Ready — Full Automation  
**Version:** 3.0.0  
**Dernière MAJ:** 2026-05-26  
**Services:** MCP (auto) + Bridge (daemon) + Processor (daemon)
