# 🤙 COMMANDES CLI — RÉFÉRENCE COMPLÈTE

**Version:** 5.2.0  
**Dernière MAJ:** 2026-05-26

---

## 📖 TABLE DES MATIÈRES

1. [Commandes Principales](#commandes-principales)
2. [Configuration](#configuration)
3. [Routage](#routage)
4. [Exécution](#exécution)
5. [Monitoring](#monitoring)
6. [Exemples](#exemples)

---

## 🚀 COMMANDES PRINCIPALES

### nv — Commande Unifiée

```bash
# Help
nv --help

# Status
nv status

# Version
nv --version
```

### Raccourcis

```bash
# nvr = nv route
nvr "Build API"

# nve = nv exec
nve nexus-api "Build API"

# nvrn = nv run
nvrn "Build API"
```

---

## ⚙️ CONFIGURATION

### novahiz-config.py

**Emplacement:** `~/.opencode/scripts/novahiz-config.py`

#### Initialisation

```bash
# Initialiser configuration
python3 ~/.opencode/scripts/novahiz-config.py init
```

#### Providers

```bash
# Lister providers
python3 ~/.opencode/scripts/novahiz-config.py providers

# Activer provider
python3 ~/.opencode/scripts/novahiz-config.py providers enable openrouter
python3 ~/.opencode/scripts/novahiz-config.py providers enable opencode-zen

# Désactiver provider
python3 ~/.opencode/scripts/novahiz-config.py providers disable opencode-zen
```

#### Modèles

```bash
# Lister modèles par tier
python3 ~/.opencode/scripts/novahiz-config.py models

# Définir modèle default
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter qwen/qwen3.5-9b
python3 ~/.opencode/scripts/novahiz-config.py set-model smart opencode-zen "Qwen3.5 plus"
python3 ~/.opencode/scripts/novahiz-config.py set-model premium openrouter qwen/qwen3.6-plus

# Définir fallback (index: 1, 2, 3)
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter qwen/qwen3.5-flash-02-23 1
python3 ~/.opencode/scripts/novahiz-config.py set-model smart openrouter qwen/qwen3.6-flash 1
python3 ~/.opencode/scripts/novahiz-config.py set-model premium openrouter moonshotai/kimi-k2.5 1
```

#### Liste des Modèles Disponibles

```bash
# Voir modèles de tous les providers
python3 ~/.opencode/scripts/novahiz-config.py list-available
```

---

## 🎯 ROUTAGE

### novahiz-cli.py

**Emplacement:** `~/.opencode/scripts/novahiz-cli.py`

#### Router une Tâche

```bash
# Route vers agent optimal
python3 ~/.opencode/scripts/novahiz-cli.py route "Build a REST API"

# Output:
# → Agent: nexus-api
# → Skill: novahiz-selection
# → Confidence: 100%
```

#### Lister Agents

```bash
# Tous les agents
python3 ~/.opencode/scripts/novahiz-cli.py agents

# Recherche par keyword
python3 ~/.opencode/scripts/novahiz-cli.py search database
python3 ~/.opencode/scripts/novahiz-cli.py search security
```

#### Scoreboard

```bash
# Performance des agents
python3 ~/.opencode/scripts/novahiz-cli.py scoreboard
```

---

## ▶️ EXÉCUTION

### novahiz-runtime.py

**Emplacement:** `~/.opencode/runtime/novahiz-runtime.py`

#### Status

```bash
# Status runtime
python3 ~/.opencode/runtime/novahiz-runtime.py status

# Output:
# Provider: openrouter
# Models: flash=qwen/qwen3.5-9b...
# Executions: 5
```

#### Daemon

```bash
# Démarrer daemon
python3 ~/.opencode/runtime/novahiz-runtime.py daemon

# Avec intervalle custom
python3 ~/.opencode/runtime/novahiz-runtime.py daemon 5

# En background
python3 ~/.opencode/runtime/novahiz-runtime.py daemon > /dev/null 2>&1 &
```

#### Exécution Directe

```bash
# Exécuter avec agent spécifique
python3 ~/.opencode/runtime/novahiz-runtime.py exec luna-design "Design button"

# Avec modèle spécifique
python3 ~/.opencode/runtime/novahiz-runtime.py exec nexus-api "Build API" premium
```

#### Test

```bash
# Créer test execution
python3 ~/.opencode/runtime/novahiz-runtime.py test
```

---

## 📊 MONITORING

### Runtime Status

```bash
# Status simple
python3 ~/.opencode/runtime/novahiz-runtime.py status

# Status détaillé
cat ~/.opencode/runtime/config.json | jq '.'
```

### Logs

```bash
# Runtime logs
tail -f ~/.opencode/logs/runtime.log

# Daemon logs
tail -f ~/.opencode/logs/runtime-daemon.log

# MCP logs
tail -f ~/.opencode/logs/mcp-http.log

# Config logs
tail -f ~/.opencode/logs/config.log
```

### Executions

```bash
# Count executions
ls ~/.opencode/executions/*.json | wc -l

# Voir dernières executions
ls -lt ~/.opencode/executions/*.json | head -5

# Status des executions
cat ~/.opencode/executions/*.json | jq -r '.status' | sort | uniq -c
```

### Health Check

```bash
# MCP HTTP health
curl http://localhost:8765/health

# Output:
# {"success": true, "status": "healthy"}
```

---

## 📋 EXEMPLES COMPLETS

### Workflow Complet

```bash
# 1. Initialiser configuration
python3 ~/.opencode/scripts/novahiz-config.py init

# 2. Vérifier providers
python3 ~/.opencode/scripts/novahiz-config.py providers

# 3. Vérifier modèles
python3 ~/.opencode/scripts/novahiz-config.py models

# 4. Démarrer daemon
python3 ~/.opencode/runtime/novahiz-runtime.py daemon &

# 5. Router tâche
python3 ~/.opencode/scripts/novahiz-cli.py route "Build API"

# 6. Exécuter
python3 ~/.opencode/runtime/novahiz-runtime.py exec nexus-api "Build API"

# 7. Vérifier status
python3 ~/.opencode/runtime/novahiz-runtime.py status
```

### Personnalisation Modèles

```bash
# 1. Voir modèles disponibles
python3 ~/.opencode/scripts/novahiz-config.py list-available

# 2. Configurer flash
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter qwen/qwen3.5-9b
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter qwen/qwen3.5-flash-02-23 1

# 3. Configurer smart
python3 ~/.opencode/scripts/novahiz-config.py set-model smart opencode-zen "Qwen3.5 plus"
python3 ~/.opencode/scripts/novahiz-config.py set-model smart openrouter qwen/qwen3.6-flash 1

# 4. Configurer premium
python3 ~/.opencode/scripts/novahiz-config.py set-model premium openrouter qwen/qwen3.6-plus
python3 ~/.opencode/scripts/novahiz-config.py set-model premium openrouter moonshotai/kimi-k2.5 1

# 5. Vérifier
python3 ~/.opencode/scripts/novahiz-config.py models
```

### Monitoring en Temps Réel

```bash
# Terminal 1: Daemon logs
tail -f ~/.opencode/logs/runtime-daemon.log

# Terminal 2: Nouvelles executions
watch -n 2 'ls ~/.opencode/executions/*.json 2>/dev/null | wc -l'

# Terminal 3: Status
watch -n 5 'python3 ~/.opencode/runtime/novahiz-runtime.py status'
```

---

## 🔧 ALIASES RECOMMANDÉS

### ~/.bashrc

```bash
# Novahiz CLI
alias nv='python3 ~/.opencode/scripts/novahiz-cli.py'
alias nvc='python3 ~/.opencode/scripts/novahiz-config.py'
alias nvr='python3 ~/.opencode/runtime/novahiz-runtime.py'

# Raccourcis
alias nvroute='nv route'
alias nvrun='nv run'
alias nvexec='nv exec'
alias nvstatus='nvr status'
alias nvd='nvr daemon'

# Config
alias nvproviders='nvc providers'
alias nvmodels='nvc models'
alias nvsetmodel='nvc set-model'

# Monitoring
alias nvlogs='tail -f ~/.opencode/logs/runtime.log'
alias nvdlogs='tail -f ~/.opencode/logs/runtime-daemon.log'
```

### Après Ajout

```bash
# Reload .bashrc
source ~/.bashrc

# Tester
nvroute "Build API"
nvstatus
```

---

## 📊 TABLEAU RÉCAPITULATIF

| Commande | Fichier | Usage |
|----------|---------|-------|
| `nv config init` | novahiz-config.py | Initialiser config |
| `nv config providers` | novahiz-config.py | Lister providers |
| `nv config models` | novahiz-config.py | Lister modèles |
| `nv config set-model` | novahiz-config.py | Configurer modèle |
| `nv route` | novahiz-cli.py | Router tâche |
| `nv run` | novahiz-cli.py | Router + exécuter |
| `runtime status` | novahiz-runtime.py | Status runtime |
| `runtime daemon` | novahiz-runtime.py | Lancer daemon |
| `runtime exec` | novahiz-runtime.py | Exécution directe |
| `curl /health` | novahiz-mcp-http.py | Health check |

---

**Documentation liée:**
- [README.md](README.md) — Documentation principale
- [CONFIGURATION.md](CONFIGURATION.md) — Configuration détaillée
- [MODELS.md](MODELS.md) — Modèles LLM
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Dépannage
