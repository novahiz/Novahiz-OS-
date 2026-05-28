# 🚀 NOVAHIZ OS v5.2 — Documentation Complète

**Version:** 5.2.0  
**Date:** 2026-05-26  
**Status:** Production Ready

---

## 📖 TABLE DES MATIÈRES

1. [Architecture](#architecture)
2. [Installation](#installation)
3. [Configuration Multi-Provider](#configuration-multi-provider)
4. [Routage LLM](#routage-llm)
5. [Commandes CLI](#commandes-cli)
6. [API & Intégrations](#api--intégrations)
7. [Dépannage](#dépannage)

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    NOVAHIZ OS v5.2                              │
│              Multi-Provider LLM Orchestration                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  USER → CLI → Router → Provider Manager → LLM API → Result     │
│         ↓      ↓         ↓              ↓          ↓            │
│       nv    config   flash/smart   openrouter   Response       │
│              models   premium       opencode-zen                │
│                         ↓                                      │
│                   Fallbacks                                    │
│                   (1, 2, 3)                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Composants

| Composant | Fichier | Rôle |
|-----------|---------|------|
| **CLI** | `~/.opencode/bin/nv` | Commande unifiée |
| **Config** | `~/.opencode/runtime/config.json` | Providers + modèles |
| **Router** | `~/.opencode/scripts/novahiz-cli.py` | Routage agents |
| **Config CLI** | `~/.opencode/scripts/novahiz-config.py` | Config providers |
| **Runtime** | `~/.opencode/runtime/novahiz-runtime.py` | Exécution LLM |
| **MCP HTTP** | `~/.opencode/mcp/novahiz-mcp-http.py` | API HTTP |

---

## 📦 INSTALLATION

### Prérequis

- Python 3.10+
- API keys (OpenRouter + OpenCode Zen)
- Connexion Internet

### Installation Automatique

```bash
# 1. Exécuter le script d'installation
bash ~/.opencode/install-v5.sh

# 2. Initialiser configuration
nv config init

# 3. Vérifier providers
nv config providers

# 4. Vérifier modèles
nv config models
```

### Installation Manuelle

```bash
# 1. Initialiser configuration
python3 ~/.opencode/scripts/novahiz-config.py init

# 2. Démarrer Runtime daemon
python3 ~/.opencode/runtime/novahiz-runtime.py daemon &

# 3. Vérifier status
nv config status
```

---

## ⚙️ CONFIGURATION MULTI-PROVIDER

### Providers Configurés

| Provider | API Key | Priority | Status |
|----------|---------|----------|--------|
| **openrouter** | `sk-or-v1-...` | 1 | ✅ Actif |
| **opencode-zen** | `sk-TnPvEk...` | 2 | ✅ Actif |

### Tiers de Modèles

#### Tier FLASH (Tâches simples, rapide)

| Fallback | Provider | Modèle |
|----------|----------|--------|
| **Default** | openrouter | `qwen/qwen3.5-9b` |
| Fallback 1 | openrouter | `qwen/qwen3.5-flash-02-23` |
| Fallback 2 | openrouter | `stepfun/step-3.5-flash` |
| Fallback 3 | openrouter | `z-ai/glm-4.7-flash` |

#### Tier SMART (Tâches normales)

| Fallback | Provider | Modèle |
|----------|----------|--------|
| **Default** | opencode-zen | `Qwen3.5 plus` |
| Fallback 1 | openrouter | `qwen/qwen3.6-flash` |
| Fallback 2 | openrouter | `qwen/qwen3.5-plus-20260420` |
| Fallback 3 | openrouter | `moonshotai/kimi-k2.5` |

#### Tier PREMIUM (Tâches critiques)

| Fallback | Provider | Modèle |
|----------|----------|--------|
| **Default** | openrouter | `qwen/qwen3.6-plus` |
| Fallback 1 | openrouter | `moonshotai/kimi-k2.5` |
| Fallback 2 | openrouter | `z-ai/glm-5` |

### Commandes de Configuration

```bash
# Initialiser configuration
nv config init

# Lister providers
nv config providers

# Activer/désactiver provider
nv config providers enable openrouter
nv config providers disable opencode-zen

# Lister modèles par tier
nv config models

# Définir modèle pour un tier
nv config set-model flash openrouter qwen/qwen3.5-9b
nv config set-model smart opencode-zen "Qwen3.5 plus"
nv config set-model premium openrouter qwen/qwen3.6-plus

# Définir fallback
nv config set-model flash openrouter qwen/qwen3.5-flash-02-23 1
nv config set-model smart openrouter qwen/qwen3.6-flash 1

# Voir modèles disponibles
nv config list-available
```

---

## 🎯 ROUTAGE LLM

### Comment Ça Marche

1. **Task arrive** → Analyse keywords
2. **Sélection tier** → flash/smart/premium
3. **Provider par défaut** → Selon config
4. **Fallback auto** → Si provider échoue

### Algorithme de Sélection

```python
def select_model(task, agent):
    # 1. Analyser complexité
    if "simple" in task: tier = "flash"
    elif "critical" in task: tier = "premium"
    else: tier = "smart"
    
    # 2. Récupérer config tier
    config = get_tier_config(tier)
    
    # 3. Essayer default
    if try_provider(config["default"]):
        return config["default"]
    
    # 4. Essayer fallbacks
    for fallback in config["fallbacks"]:
        if try_provider(fallback):
            return fallback
    
    # 5. Échec
    return None
```

### Exemples de Routage

| Task | Tier | Modèle | Provider |
|------|------|--------|----------|
| "Fix typo" | flash | qwen3.5-9b | openrouter |
| "Build API" | smart | Qwen3.5 plus | opencode-zen |
| "Security audit" | premium | qwen3.6-plus | openrouter |

---

## 💻 COMMANDES CLI

### Commandes Principales

```bash
# Routage
nv route "Build API"           # Router vers agent optimal
nv run "Build API"             # Router + exécuter
nv exec <agent> "task"         # Exécuter avec agent

# Configuration
nv config init                 # Initialiser config
nv config providers            # Lister providers
nv config models               # Lister modèles
nv config set-model ...        # Configurer modèle
nv config list-available       # Voir modèles dispos

# Runtime
runtime status                 # Status runtime
runtime daemon                 # Lancer daemon
runtime test                   # Créer test

# MCP
curl http://localhost:8765/health  # Health check
```

### Exemples Complets

```bash
# 1. Configuration initiale
nv config init
nv config providers
nv config models

# 2. Personnalisation
nv config set-model flash openrouter qwen/qwen3.5-9b
nv config set-model smart opencode-zen "Qwen3.5 plus"
nv config set-model premium openrouter qwen/qwen3.6-plus

# 3. Utilisation
nv route "Build REST API"
nv run "Create login form"

# 4. Monitoring
runtime status
tail -f ~/.opencode/logs/runtime.log
```

---

## 🔌 API & INTÉGRATIONS

### MCP HTTP API

**Endpoint:** `http://localhost:8765`

```bash
# Health check
curl http://localhost:8765/health

# Router task
curl "http://localhost:8765/route?task=Build+API"

# Auto route + execute
curl -X POST -d '{"task":"Build API"}' http://localhost:8765/auto

# Lister agents
curl http://localhost:8765/agents
```

### Response Format

```json
{
  "success": true,
  "agent": "nexus-api",
  "model": {
    "tier": "smart",
    "provider": "opencode-zen",
    "model": "Qwen3.5 plus"
  },
  "execution": {
    "execution_id": "exec_123",
    "status": "completed",
    "content": "..."
  }
}
```

---

## 🐛 DÉPANNAGE

### Problèmes Communs

#### 1. API Key Non Trouvée

**Symptôme:** `ERROR: API key not found`

**Solution:**
```bash
# Vérifier .bashrc
grep OPENROUTER_API_KEY ~/.bashrc

# Exporter manuellement
export OPENROUTER_API_KEY=sk-or-v1-...
export OPENCODE_ZEN_API_KEY=sk-TnPvEk...

# Redémarrer daemon
pkill -f novahiz-runtime
python3 ~/.opencode/runtime/novahiz-runtime.py daemon &
```

#### 2. Provider Échoue

**Symptôme:** `ERROR: HTTP error (401)`

**Solution:**
```bash
# Vérifier API key
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models

# Changer provider
nv config providers disable openrouter
nv config providers enable opencode-zen

# Ou utiliser fallback
nv config set-model smart openrouter qwen/qwen3.6-flash 1
```

#### 3. Daemon Ne Démarre Pas

**Symptôme:** Aucun processus après `daemon &`

**Solution:**
```bash
# Vérifier logs
tail -20 ~/.opencode/logs/runtime.log

# Mode debug
python3 -u ~/.opencode/runtime/novahiz-runtime.py daemon 2>&1 | head -50

# Kill anciens processus
pkill -9 -f novahiz-runtime
sleep 2

# Redémarrer
python3 ~/.opencode/runtime/novahiz-runtime.py daemon &
```

#### 4. Modèles Non Trouvés

**Symptôme:** `ERROR: Model not found`

**Solution:**
```bash
# Lister modèles disponibles
nv config list-available

# Mettre à jour config
nv config set-model flash openrouter qwen/qwen3.5-9b

# Vérifier config
cat ~/.opencode/runtime/config.json | jq '.models'
```

---

## 📊 MONITORING

### Logs

```bash
# Runtime logs
tail -f ~/.opencode/logs/runtime.log

# Daemon logs
tail -f ~/.opencode/logs/runtime-daemon.log

# MCP logs
tail -f ~/.opencode/logs/mcp-http.log
```

### Status

```bash
# Runtime status
runtime status

# Providers
nv config providers

# Modèles
nv config models

# Executions
ls ~/.opencode/executions/*.json | wc -l
```

### Metrics

```bash
# Count executions
cat ~/.opencode/executions/*.json | \
  jq -r '.status' | sort | uniq -c

# Success rate
cat ~/.opencode/executions/*.json | \
  jq -r '.result.success' | grep true | wc -l
```

---

## 📁 STRUCTURE DES FICHIERS

```
~/.opencode/
├── bin/
│   └── nv                      # CLI unifiée
├── runtime/
│   ├── config.json             # Config providers + modèles
│   ├── novahiz-runtime.py      # Moteur d'exécution
│   └── novahiz-runtime-fast.py # Daemon optimisé
├── scripts/
│   ├── novahiz-cli.py          # Smart router
│   └── novahiz-config.py       # Config CLI
├── mcp/
│   └── novahiz-mcp-http.py     # HTTP API
├── documentation/
│   ├── README.md               # Ce fichier
│   ├── CONFIGURATION.md        # Guide config
│   ├── MODELS.md               # Modèles LLM
│   ├── CLI.md                  # Commandes CLI
│   └── TROUBLESHOOTING.md      # Dépannage
├── executions/                 # Historique exécutions
├── logs/                       # Logs système
└── pids/                       # PID files
```

---

## 🎯 BEST PRACTICES

### Configuration

- ✅ Toujours avoir 2+ providers activés
- ✅ Configurer 3 fallbacks par tier
- ✅ Utiliser opencode-zen pour smart (meilleur rapport qualité/prix)
- ✅ Utiliser openrouter pour flash/premium (plus de choix)

### Exécution

- ✅ Daemon tourne en background
- ✅ Logs rotation automatique
- ✅ Monitoring régulier (status, logs)
- ✅ Backup config.json régulièrement

### Sécurité

- ✅ API keys dans .bashrc (pas dans git)
- ✅ Permissions restrictives sur config.json
- ✅ Logs ne contiennent pas de données sensibles

---

## 📞 SUPPORT

### Documentation

- `~/.opencode/documentation/README.md` — Ce fichier
- `~/.opencode/documentation/CONFIGURATION.md` — Config détaillée
- `~/.opencode/documentation/MODELS.md` — Modèles LLM
- `~/.opencode/documentation/CLI.md` — Commandes CLI
- `~/.opencode/documentation/TROUBLESHOOTING.md` — Dépannage

### Commandes Utiles

```bash
# Help complet
nv --help
nv config --help

# Status complet
nv status
runtime status
nv config providers
nv config models
```

---

**Version:** 5.2.0  
**Dernière MAJ:** 2026-05-26  
**Status:** ✅ Production Ready
