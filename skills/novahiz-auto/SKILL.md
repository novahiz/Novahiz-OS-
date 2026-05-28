# Novahiz Auto-Routing Skill

Utilise le moteur de routage Novahiz pour router et exécuter des tâches.

## Usage

```bash
nv route "build a REST API"          # → route vers le meilleur agent
nv council "design system"           # → délibération multi-agent
nv auto "fix security bug"           # → route + execute automatique
nv agents                            # → liste tous les agents
nv health                            # → état du système
```

## Integration MCP

Les outils MCP suivants sont disponibles via le serveur novahiz:

| Tool | Description |
|------|-------------|
| `novahiz_route` | Router une tâche vers l'agent optimal |
| `novahiz_execute` | Exécuter avec un agent spécifique |
| `novahiz_auto` | Router + exécuter automatiquement |
| `novahiz_council` | Délibération multi-agent (top 3-5) |
| `novahiz_list_agents` | Lister tous les agents |
| `novahiz_search` | Chercher des agents par mot-clé |
| `novahiz_health` | Health check complet |
| `novahiz_execution_status` | Statut des exécutions |
| `novahiz_scoreboard` | Scores et stats des agents |
| `novahiz_history` | Historique des exécutions |

## Flow recommandé

1. **Tâche simple** → exécute directement avec le skill approprié
2. **Tâche medium** → `novahiz_route` → exécute avec l'agent recommandé
3. **Tâche complexe** → `novahiz_council` → délibération → exécution multi-agent
