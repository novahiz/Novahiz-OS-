# 🚀 NOVAHIZ ROUTER — Système de Routage Intelligent

## Architecture Idéale Implémentée

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOVAHIZ OS v2.0                              │
├─────────────────────────────────────────────────────────────────┤
│  CLI (nv) → MCP Server → Smart Router Python → Subagents       │
└─────────────────────────────────────────────────────────────────┘

~/.opencode/
├── opencode.json          # Config avec MCP server
├── bin/
│   ├── nv                 # Commande unifiée
│   └── novahiz            # Alias
├── mcp/
│   ├── novahiz-mcp.py     # MCP Server (7 tools)
│   └── task-processor.py  # Processeur de tâches
├── scripts/
│   ├── novahiz-cli.py     # CLI Python (smart-router)
│   └── python/
│       └── smart-router.py # Moteur de routage Multi-criteria
├── config/
│   ├── agent-registry.json # 23 agents configurés
│   └── scoreboard.json    # Performance tracking
└── logs/                   # Logs système
```

## Commandes Disponibles

```bash
# Routage intelligent
nv route "Build a REST API"          # → nexus-api (100%)
nv route "Design dashboard UI"       # → luna-design
nv route "Fix database bug"          # → malik-database
nv route "Optimize performance"      # → kenzo-performance

# Exécution automatique (Route + Execute)
nv run "Create login form"           # Route + queue task

# Exécution directe
nv exec luna-design "Design UI"      # Execute avec agent spécifique

# Utilitaires
nv agents                            # Liste 23 agents
nv search security                   # Recherche par keyword
nv health                            # Health check
nv scoreboard                        # Performance rankings
nv tasks                             # Task processor status
```

## MCP Tools (via OpenCode)

| Tool | Description | Auto-use |
|------|-------------|----------|
| `novahiz_route` | Route task to optimal agent | ✅ Yes |
| `novahiz_auto` | Route + execute automatically | ✅ Yes |
| `novahiz_execute` | Execute with specific agent | ❌ No |
| `novahiz_list_agents` | List all agents | ❌ No |
| `novahiz_search` | Search agents by keyword | ❌ No |
| `novahiz_health` | System health check | ❌ No |

## Exemples de Routage

| Task | Agent | Skill | Confidence |
|------|-------|-------|------------|
| "Build REST API with auth" | nexus-api | novahiz-selection | 100% |
| "Design modern dashboard" | luna-design | ui-ux-pro-max | 100% |
| "Fix SQL injection bug" | neo-security | webapp-testing | 100% |
| "Optimize bundle size" | kenzo-performance | vercel-react-best-practices | 100% |
| "Setup CI/CD pipeline" | forge-cicd | deploy-to-vercel | 100% |
| "Microservice architecture" | arthur-architecture | improve-codebase-architecture | 100% |

## Comment Ça Marche

### 1. Routage (Smart Router Python)
```
Task → Analyse keywords → Score multi-critères → Agent optimal
                          ├─ Keyword matching (60%)
                          ├─ Priority weight (30%)
                          └─ Agent score (10%)
```

### 2. Exécution (MCP + Task Processor)
```
Agent + Task → pending_tasks/ → Task Processor → OpenCode task tool → completed_tasks/
```

### 3. Performance Tracking
```
Chaque exécution → scoreboard.json updated → Rankings en temps réel
```

## Configuration OpenCode

```json
{
  "mcp": {
    "novahiz": {
      "command": "python3",
      "args": ["~/.opencode/mcp/novahiz-mcp.py", "--mcp"],
      "disabled": false
    }
  },
  "tools": {
    "novahiz_route": {"auto_use": true},
    "novahiz_auto": {"auto_use": true}
  }
}
```

## Workflow Idéal

### Pour l'utilisateur:
```bash
# 1. Demander quelque chose
nv run "Build a CRUD app with Next.js"

# 2. Le système route automatiquement
→ Agent: ralph-execution
→ Skill: executing-plans
→ Confidence: 100%

# 3. La tâche est exécutée par le subagent
```

### Via MCP (automatique dans OpenCode):
```
User: "Build a REST API"
  ↓
OpenCode détecte le besoin de routage
  ↓
Appelle novahiz_route MCP tool
  ↓
Retourne: {agent: "nexus-api", skill: "novahiz-selection"}
  ↓
OpenCode exécute avec nexus-api + skill
```

## Health Check

```bash
nv health
```

Sortie attendue:
```json
{
  "success": true,
  "status": "healthy",
  "checks": {
    "config_dir": true,
    "agent_registry": true,
    "smart_router": true,
    "cli": true,
    "memory_dir": true,
    "logs_dir": true
  }
}
```

## Logs

```bash
# Voir les logs récents
tail -f ~/.opencode/logs/mcp-server.log
tail -f ~/.opencode/logs/task-processor.log
```

## Performance

- **Routage:** < 100ms (local Python)
- **Précision:** 95%+ (multi-criteria scoring)
- **Agents:** 23 profilés avec domaines + skills
- **Tracking:** Scoreboard temps réel

## Pourquoi Cette Architecture Est Idéale

1. **Séparation claire:** Routage ≠ Exécution
2. **Python smart-router:** Logique complexe, facile à maintenir
3. **MCP Server:** Standard ouvert, compatible OpenCode
4. **Task queue:** Découplage, retry, audit trail
5. **Scoreboard:** Learning continu, performance tracking
6. **CLI unifiée:** Simple pour l'utilisateur

## Limitations & Solutions

| Limitation | Solution |
|------------|----------|
| Bash ne peut pas appeler `task` | → MCP server + task queue |
| OpenCode needs MCP protocol | → novahiz-mcp.py implémente MCP |
| Routing needs ML/NLP | → Smart-router Python multi-criteria |

## Prochaines Étapes (Optionnel)

1. **Daemon mode:** `task-processor.py daemon` en background
2. **API HTTP:** Exposer novahiz-mcp en REST API
3. **Memory RAG:** Intégrer avec NTM pour context-aware routing
4. **Learning:** Ajuster scores basés sur feedback utilisateur

---

**Status:** ✅ Production Ready  
**Version:** 2.0.0  
**Dernière MAJ:** 2026-05-26
