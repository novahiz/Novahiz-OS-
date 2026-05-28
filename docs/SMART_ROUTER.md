# NovaHiz OS v2.0 — Smart Router Upgrade

## Improvements Applied

### 1. Routage Intelligent (Smart Routing) ✓
**Avant:** Keyword matching simple (premier match gagne)
**Après:** Multi-criteria scoring avec:
- Keyword match counting (weighted by position)
- Memory context boost (RAG)
- Historical performance (scoreboard)
- Domain priority base

**Fichier:** `scripts/python/smart-router.py`

**Algorithme:**
```python
score = keyword_score + memory_boost + perf_score + base_priority
confidence = min(100, score * 10)
```

**Exemple:**
```bash
nv route "build a rest api with authentication"
# → nexus-api (100% confidence)
# Top candidates: nexus-api: 22.0, neo-security: 21.0, ralph-execution: 21.0
```

### 2. Memory RAG Integration ✓
**Avant:** Memory isolée, pas utilisée pour routing
**Après:** Les 20 derniers noeuds memory analysés pour extraire keywords contextuels

**Fonctionnement:**
- Load recent memory nodes (last 20)
- Extract keywords (words >3 chars + tags)
- Boost agent scores if their domains match memory keywords

**Commande:**
```bash
nv smart memory
# Nodes loaded: 20
# Keywords: 150
```

### 3. Agent Evaluation System (Scoreboard) ✓
**Avant:** Scores statiques dans registry
**Après:** Scoreboard dynamique mis à jour après chaque task

**Metrics:**
- `tasks`: Nombre de tasks assignées
- `success`: Nombre de succès
- `avg_time`: Temps moyen (exponential moving average)
- `score`: Base priority + success rate bonus (0-10)

**Fichier:** `config/scoreboard.json`

**Commandes:**
```bash
nv scoreboard          # Voir rankings
nv smart update <agent> [success] [duration]  # Update score
```

### 4. Nouvelles Commandes CLI

| Commande | Description |
|----------|-------------|
| `nv scoreboard` | Agent performance rankings |
| `nv smart test` | Test routing with samples |
| `nv smart memory` | Show memory context keywords |
| `nv smart update` | Update agent performance |

### 5. Agent Profiles (24 agents)

Chaque agent a un profil avec:
- `domains`: Liste de keywords associés
- `priority`: Score de base (80-100)
- `type`: subagent/simulated/primary

**Top agents:**
- novahiz-router: 100
- luna-design, kenzo-performance, malik-database, etc.: 95
- nexus-api, orion-devops, etc.: 90
- samuel-legal, ghost-stealth: 85

## Usage Examples

```bash
# Route with confidence
nv route "optimize database performance"
# → malik-database (100% confidence)
# Top: malik-database: 22.0, kenzo-performance: 21.0

# View scoreboard
nv scoreboard

# Test smart router
nv smart test

# Check memory context
nv smart memory

# Update agent score after task completion
nv smart update neo-security true 1200
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  User Task Input                    │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│              Smart Router (score_task)              │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │   Keyword   │  │    Memory    │  │  History  │  │
│  │   Matching  │  │      RAG     │  │ Scoreboard│  │
│  └──────┬──────┘  └──────┬───────┘  └─────┬─────┘  │
│         │                │                 │        │
│         └────────────────┼─────────────────┘        │
│                          │                          │
│                   [Score Calculation]               │
│                          │                          │
│                   [Rank Agents]                     │
└──────────────────────────┼──────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Best Agent + Skill    │
              │  + Confidence Score    │
              └────────────────────────┘
```

## Performance

- Routing latency: <50ms (local scoring)
- Memory context: ~20 nodes analyzed
- Scoreboard updates: O(1) per agent

## Files Modified/Created

| File | Status | Description |
|------|--------|-------------|
| `scripts/python/smart-router.py` | NEW | Smart routing engine |
| `scripts/novahiz-cli.py` | UPDATED | Integrated smart routing |
| `config/scoreboard.json` | NEW | Dynamic agent scores |
| `docs/SMART_ROUTER.md` | NEW | This documentation |

## Backwards Compatibility

- Legacy `route_task()` function preserved
- Old `nv route` commands still work
- JSON output format compatible

## Next Steps (Pending)

- [ ] Health check temps réel + auto-healing
- [ ] API REST complète + webhooks
- [ ] CLI interactive mode + autocomplete

---
**Version:** 2.0
**Date:** 2026-05-26
**Author:** Novahiz OS Team
