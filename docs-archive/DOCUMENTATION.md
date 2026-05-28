# NOVAHIZ OS v1.7 — DOCUMENTATION COMPLÈTE

**Multi-Agent Orchestration System for OpenCode Desktop/CLI**

---

## TABLE DES MATIÈRES

```
1.  INTRODUCTION & OVERVIEW
2.  INSTALLATION & SETUP
3.  ARCHITECTURE DÉTAILLÉE
4.  CLI — COMMANDES COMPLÈTES
5.  API SERVER
6.  DESKTOP EDITION
7.  AGENTS — FICHES COMPLÈTES
8.  SKILLS — CATALOGUE
9.  MEMORY NEXUS
10. DATABASES
11. MONITORING & ALERTING
12. BACKUP & RESTORE
13. TESTS & VALIDATION
14. CUSTOM INSTRUCTIONS
15. WORKFLOWS SPÉCIALISÉS
16. DÉPANNAGE & FAQ
17. ANNEXES
```

---

# 1. INTRODUCTION & OVERVIEW

## 1.1 Qu'est-ce que NovaHiz OS

**NovaHiz OS** est un système d'orchestration multi-agent qui transforme OpenCode en un hub d'intelligence artificielle avec:

- **22 agents spécialisés** (10 Council + 12 Elite Force)
- **59 skills** (compétences transversales)
- **Memory Nexus** (5 branches, 23 nodes)
- **4 bases SQLite** (tracking + history)
- **API REST** (9 endpoints, port 8080)
- **CLI complète** (15+ commandes)
- **Desktop Edition** (configuration isolée)

## 1.2 Architecture 3-Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER 0 — CAVEMAN MODE                       │
│  Filtre de compression: 1-3 phrases, brutal truth, no fluff     │
│  Actif sur CHAQUE réponse (obligatoire)                         │
────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              LAYER 1 — NOVAHIZ ROUTER (Primary)                 │
│         Sovereign Orchestration Layer • Classification          │
│         Routing • Governance • Council Deliberation             │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
─────────────────────────┐     ┌─────────────────────────┐
│   LAYER 2 — COUNCIL     │     │  LAYER 2 — ELITE FORCE  │
│   10 Agents Actifs      │     │   12 Agents Simulés     │
│   • Luna (Design)       │     │   • Ryù (Design JP)     │
│   • Kenzo (Performance) │     │   • Sage-07 (Data)      │
│   • Malik (Database)    │     │   • Orion (DevOps)      │
│   • Arthur (Architect)  │     │   • Vega (Legal)        │
│   • Neo (Security)      │     │   • Phoenix (Crisis)    │
│   • Sarah (Quality)     │     │   • Nexus (API)         │
│   • Elias (Marketing)   │     │   • Cipher (Crypto)     │
│   • Victor (Strategy)   │     │   • Forge (CI/CD)       │
│   • Ralph (Execution)   │     │   • Pulse (Realtime)    │
│   • Atlas (Memory)      │     │   • Ghost (Stealth)     │
│                         │     │   • Sage-11 (Legal)     │
└─────────────────────────┘     └─────────────────────────┘
```

## 1.3 CLI vs Desktop: Comparaison

| Aspect | CLI | Desktop | Puissance |
|--------|-----|---------|-----------|
| **Agents** | 22 | 22 | 100% ✓ |
| **Skills** | 59 | 59 | 100% ✓ |
| **CAVEMAN MODE** | ✓ (router + skill) | ✓ (skill seul) | 90% |
| **Commandes directes** | `nv route`, `nv invoke` | ❌ | 0% |
| **Routing auto** | ✓ |  | 0% |
| **API Server** | ✓ (port 8080) | ✓ (via CLI) | 100% |
| **Backup auto** | ✓ (systemd timer) | ✓ (shared) | 100% |
| **Sync** | Source | Hourly (cron) | 100% |
| **Sessions** | CLI sessions | Desktop sessions (isolées) | 100% |
| **UI Comfort** | Terminal | OpenCode Desktop | Desktop ✓ |

**Conclusion:** Desktop = **85% puissance CLI**

## 1.4 CAVEMAN MODE Philosophy

**Règles:**
- 1-3 phrases max
- Brutal truth, no fluff
- French unless EN asked
- Point essential only
- No intro, no conclusion, no apology

**Exemples:**
```
User: "comment ça marche?"
→ "`nv status` ou API:8080"

User: "fait ça"
→ "Done."

User: "explique"
→ "Brief: [concept] → [what it do]"

User: "fais une review"
→ "Code/Security/Design? Précise."
```

---

# 2. INSTALLATION & SETUP

## 2.1 Prérequis Système

```bash
# Vérifier Python 3.8+
python3 --version

# Vérifier OpenCode Desktop
which code  # ou opencode

# Espace disque requis: ~15MB
df -h ~
```

## 2.2 Installation CLI (Step-by-Step)

```bash
# 1. Créer la structure
mkdir -p ~/.opencode/{agents,skills,data,memory,config,scripts,tests,api,logs,backups}

# 2. Cloner/installer NovaHiz OS
git clone https://github.com/novahiz/novahiz-os.git /tmp/novahiz-os
cp -r /tmp/novahiz-os/* ~/.opencode/

# 3. Rendre les scripts exécutables
chmod +x ~/.opencode/scripts/*.py ~/.opencode/scripts/*.sh

# 4. Ajouter les aliases au bashrc
cat >> ~/.bashrc << 'EOF'

# NovaHiz OS CLI aliases
alias nv='python3 ~/.opencode/scripts/novahiz-cli.py'
alias nvh='nv --help'
alias nvs='nv status'
EOF

# 5. Reload bashrc
source ~/.bashrc

# 6. Vérifier l'installation
nv health
```

## 2.3 Installation Desktop (Configuration Isolated)

```bash
# 1. Créer le répertoire Desktop
mkdir -p ~/.opencode-desktop

# 2. Copier tous les composants (100% copie, pas symlink)
cp -r ~/.opencode/{agents,skills,memory,data,config,scripts,tests} ~/.opencode-desktop/

# 3. Créer la config Desktop-specific
cat > ~/.opencode-desktop/opencode.jsonc << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": ["/home/novahiz/.opencode-desktop/skills"]
  }
}
EOF

# 4. Mettre à jour la config OpenCode Desktop
cat > ~/.config/opencode/opencode.jsonc << 'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": ["/home/novahiz/.opencode-desktop/skills"]
  }
}
EOF

# 5. Créer les scripts dédiés Desktop
cat > ~/.opencode-desktop/scripts/nvd-cli.py << 'EOF'
#!/usr/bin/env python3
import os, sys
DESKTOP_DIR = os.path.expanduser("~/.opencode-desktop")
os.environ['NOVAHIZ_HOME'] = DESKTOP_DIR
sys.path.insert(0, os.path.join(DESKTOP_DIR, 'scripts'))
exec(open(os.path.join(DESKTOP_DIR, 'scripts', 'novahiz-cli.py')).read())
EOF
chmod +x ~/.opencode-desktop/scripts/nvd-cli.py

# 6. Ajouter les aliases Desktop
cat >> ~/.bashrc << 'EOF'

# NovaHiz Desktop aliases
alias nvd='python3 ~/.opencode-desktop/scripts/nvd-cli.py'
alias nvd-sync='bash ~/.opencode-desktop/scripts/sync-from-cli.sh'
EOF

# 7. Installer le cron job (hourly sync)
cat > /tmp/novahiz-cron << 'EOF'
0 * * * * bash $HOME/.opencode-desktop/scripts/sync-from-cli.sh
EOF
crontab /tmp/novahiz-cron
rm /tmp/novahiz-cron

# 8. Vérifier l'installation Desktop
nvd status
```

## 2.4 Synchronisation CLI ↔ Desktop

### Auto-Sync (Cron)
```bash
# Fréquence: Toutes les 1 heure (0 * * * *)
# Composants sync: agents, skills, memory, config, scripts, data, AGENTS.md
# Log: ~/.opencode-desktop/sync.log

# Vérifier le cron job
crontab -l | grep sync-from-cli

# Voir les logs de sync
tail -20 ~/.opencode-desktop/sync.log
```

### Manual Sync
```bash
# Lancer une sync manuelle
nvd-sync

# Output:
# ✓ Sync complete! Check ~/.opencode-desktop/sync.log for details
```

### Sync Script Structure
```bash
#!/bin/bash
# ~/.opencode-desktop/scripts/sync-from-cli.sh

CLI_DIR="$HOME/.opencode"
DESKTOP_DIR="$HOME/.opencode-desktop"

# rsync components
rsync -av --delete "$CLI_DIR/agents/" "$DESKTOP_DIR/agents/"
rsync -av --delete "$CLI_DIR/skills/" "$DESKTOP_DIR/skills/"
rsync -av "$CLI_DIR/memory/" "$DESKTOP_DIR/memory/"
rsync -av "$CLI_DIR/config/" "$DESKTOP_DIR/config/"
rsync -av "$CLI_DIR/data/" "$DESKTOP_DIR/data/"
# + AGENTS.md sync
```

## 2.5 Verification Scripts

```bash
# CLI verification
python3 ~/.opencode/tests/test_novahiz.py

# Desktop verification
bash ~/.opencode-desktop/scripts/verify-desktop.sh

# Expected output: ALL CHECKS PASSED ✓
```

---

# 3. ARCHITECTURE DÉTAILLÉE

## 3.1 NovaHiz Router (Primary Agent)

**Rôle:** Sovereign Orchestration Layer

**Fichier:** `~/.opencode/agents/novahiz-router.yaml`

**Responsabilités:**
- Classification des tâches (SIMPLE/MEDIUM/COMPLEX)
- Routing vers le subagent optimal
- Council deliberation (3-5 agents pour COMPLEX)
- Aggregation des réponses
- CAVEMAN MODE enforcement

**Routing Protocol:**
```
1. CLASSIFY → SIMPLE / MEDIUM / COMPLEX

2a. SIMPLE:
    → Exécute directement
    → Utilise les skills disponibles

2b. MEDIUM:
    → Route vers le subagent optimal (1 seul)
    → Syntaxe: [SUBAGENT:agent-name] task

2c. COMPLEX:
    → Spawn 3-5 subagents via [SUBAGENT:name]
    → Délibération avec votes
    → Seuil consensus: 60%
    → Aggregateur: moi

3. EXÉCUTE → Skills + Agents
4. PERSIST → Memory (Atlas)
```

## 3.2 10 Council Agents (Actifs)

| Agent | Domain | Score | Skills | Usage |
|-------|--------|-------|--------|-------|
| **Luna** | Design, UI/UX, Figma | 95 | 5 | High |
| **Kenzo** | Performance, optimization | 95 | 4 | Medium |
| **Malik** | Database, SQL, architecture | 95 | 1 | Medium |
| **Arthur** | Software architecture, patterns | 95 | 3 | High |
| **Neo** | Security, audits, vulnerabilities | 90 | 1 | Medium |
| **Sarah** | Code quality, testing, reviews | 95 | 3 | High |
| **Elias** | Marketing, growth, content | 95 | 9 | Medium |
| **Victor** | Strategy, planning, decision | 95 | 4 | Medium |
| **Ralph** | Execution, build, deployment | 95 | 4 | High |
| **Atlas** | Memory, context, retrieval | 95 | 4 | Low |

## 3.3 12 Elite Force Agents (Simulés)

| Agent | Domain | Score | Invocation |
|-------|--------|-------|------------|
| **Ryù** | Design (Japon), innovation UX | 90 | Registry |
| **Sage-07** | Data science, analytics | 88 | Registry |
| **Orion** | DevOps, infrastructure | 92 | Registry |
| **Vega** | Legal, compliance | 85 | Registry |
| **Phoenix** | Crisis management | 87 | Registry |
| **Nexus** | API integration | 91 | Registry |
| **Cipher** | Cryptography | 89 | Registry |
| **Forge** | CI/CD pipelines | 90 | Registry |
| **Pulse** | Real-time systems | 88 | Registry |
| **Ghost** | Stealth operations | 86 | Registry |
| **Sage-11** | Legal | 85 | Registry |

## 3.4 Memory Nexus (5 Branches)

```
~/.opencode/memory/
├── nexus.json              # Global nexus (23 nodes)
├── 00_Core/
│   ├── nexus.json          # Core memory
│   ├── scoreboard.json     # Agent metrics (22 agents)
│   ├── metrics.json        # System metrics
│   ├── selection-cache.json # Agent selection cache
│   ── sessions/           # Session tracking (isolated CLI/Desktop)
├── 01_Agents/
│   ├── [agent].md          # Agent memory (22 files)
│   └── [agent]_deliberations/ # Deliberation history
├── 02_Projects/            # Project-specific memory
├── 03_Patterns/            # Design patterns, code patterns
└── 04_Archives/            # Archived sessions
```

**Branches:**
1. **00_Core** — System memory, scoreboard, metrics
2. **01_Agents** — Agent-specific memory + deliberations
3. **02_Projects** — Project context
4. **03_Patterns** — Reusable patterns
5. **04_Archives** — Historical data

## 3.5 Skills System (59 Compétences)

**Structure:**
```
~/.opencode/skills/
├── agent-browser/          # Browser automation
├── brainstorming/          # Creative brainstorming
├── caveman/                # CAVEMAN MODE skill
├── content-strategy/       # Content planning
├── copywriting/            # Marketing copy
├── frontend-design/        # UI components
├── ... (59 total)
└── xlsx/                   # Spreadsheet handling
```

**Skill Structure (YAML frontmatter):**
```markdown
---
name: skill-name
description: >
  Skill description (multi-line)
triggers: [trigger1, trigger2]
hidden: false  # true for internal skills
---

Skill content (markdown)
```

**Mapping:** `~/.opencode/config/skills-linkage.json`
- 8 Universal skills (tous agents)
- 51 Specialized skills (par domaine)

---

# 4. CLI — COMMANDES COMPLÈTES

## 4.1 Status Commands

### `nv status`
```bash
# System status + routing stats
nv status

# JSON output
nv status --json

# Output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🚀 NOVAHIZ OS v1.7          [● online]   01:12:14
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
#   SYSTEM STATUS
#   ────────────────────────────────────────────────
#   System Health        ██████████████████████░░░ 90%
#
#   Agents: 22   Skills: 59   Routes: 2
#
#   Route Classification:
#     ◆ MEDIUM: 2
#
#   Top Agents by Usage:
#     ◆ Luna: 2 uses
```

### `nv health`
```bash
# System health check
nv health

# Output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   🏥 SYSTEM HEALTH CHECK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
#   Directories:
#     ✓ agents       exist
#     ✓ skills       exist
#     ✓ data         exist
#     ✓ api          exist
#     ✓ memory       exist
#     ✓ config       exist
#
#   Databases:
#     ✓ novahiz.db
#     ✓ skills-index.db
#     ✓ agents-tracking.db
#     ✓ tasks-history.db
#
#   SYSTEM OPERATIONAL
```

### `nv stats`
```bash
# Global statistics
nv stats

# JSON output
nv stats --json
```

### `nv agents`
```bash
# List all 22 agents
nv agents

# JSON output
nv agents --json

# Output:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   AGENT REGISTRY (22 agents)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
#   ID                       DOMAIN          SCORE
#   ─────────────────────────────────────────────────
#   novahiz-router           orchestration   100
#   luna-design              design          95
#   kenzo-performance        performance     95
#   ... (22 total)
```

### `nv skills`
```bash
# List all 59 skills
nv skills

# Filter by category
nv skills --category marketing

# JSON output
nv skills --json
```

## 4.2 Routing Commands

### `nv route <task>`
```bash
# Auto-route task to optimal agent
nv route "Design a landing page for SaaS"

# Output:
# Classifying task... MEDIUM
# Optimal agent: luna-design (score: 95)
# Routing to: Luna
#
# [Luna responds with design recommendations]
```

### `nv invoke <agent>`
```bash
# Invoke specific agent
nv invoke luna-design --task "Create a design system"

# Output:
# Invoking: luna-design
# Task: Create a design system
#
# [Luna responds]
```

### `nv council <task>`
```bash
# Council deliberation (3-5 agents)
nv council "Should we use PostgreSQL or SQLite?"

# Output:
# Spawning council: malik-database, arthur-architecture, kenzo-performance
# Deliberation in progress...
#
# [Each agent provides perspective]
# [Router aggregates and provides consensus]
```

### `nv search <query>`
```bash
# Search agents + skills
nv search "database"

# Output:
# Agents:
#   • malik-database (Database, SQL, architecture)
#
# Skills:
#   • xlsx (Spreadsheet handling)
```

## 4.3 System Commands

### `nv sync`
```bash
# Sync database with YAML files
nv sync

# Output:
# Syncing agents... ✓ 22 agents
# Syncing skills... ✓ 59 skills
# Database updated.
```

### `nv link`
```bash
# Show skills linkage
nv link

# Output:
# Skills Linkage (71 links)
#
# luna-design:
#   • frontend-design
#   • canvas-design
#   • extract-design-system
#   ...
```

### `nv backup`
```bash
# Create system backup
nv backup

# Output:
# Creating backup...
# ✓ Backup: ~/.opencode/backups/20260515_011200/
# Rotation: 7 days (old backups archived)
```

### `nv logs`
```bash
# View system logs
nv logs

# Last 50 lines
nv logs --tail 50

# Filter by level
nv logs --level ERROR
```

## 4.4 Management Commands

### `nv monitor`
```bash
# Monitoring status
nv monitor

# Output:
# Monitoring: DISABLED (opt-in)
#
# Channels:
#   Telegram: Not configured
#   Discord: Not configured
#
# Configure: ~/.opencode/config/monitoring.json
```

### `nv api`
```bash
# API server management
nv api status    # Check if running
nv api start     # Start API server
nv api stop      # Stop API server
nv api restart   # Restart API server
```

## 4.5 Options

```bash
# JSON output (for scripting)
nv status --json

# Quiet mode (minimal output)
nv status --quiet

# Verbose mode (detailed output)
nv status --verbose

# Help
nv --help
nv <command> --help
```

## 4.6 Command Suggestions (Typo Correction)

```bash
# User types wrong command
nv stat

# Output:
# Unknown command: stat
# Did you mean: nv status?
```

---

# 5. API SERVER

## 5.1 Overview

**Port:** 8080  
**Protocol:** HTTP/REST  
**Auth:** Bearer token (opt-in)  
**Rate Limit:** 100 req/min/IP

## 5.2 Start API Server

```bash
# Start
python3 ~/.opencode/api/server.py

# Background
python3 ~/.opencode/api/server.py &

# Via CLI
nv api start

# Check status
curl http://localhost:8080/api/health
```

## 5.3 Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/health` | Public | Health check |
| GET | `/api/stats` | ✓ | Global statistics |
| GET | `/api/agents` | ✓ | List all agents |
| GET | `/api/agents/:id` | ✓ | Get agent details |
| GET | `/api/skills` | ✓ | List all skills |
| GET | `/api/tasks` | ✓ | List tasks |
| GET | `/api/routing/route?task=...` | ✓ | Route a task |
| GET | `/api/routing/history` | ✓ | Routing history |
| GET | `/api/openapi.json` | Public | OpenAPI spec |

## 5.4 Authentication (Opt-in)

```bash
# Enable auth
cat > ~/.opencode/config/api-auth.json << 'EOF'
{
  "enabled": true,
  "token": "your-secret-token-here",
  "createdAt": "2026-05-15T00:00:00",
  "expiresAt": "2027-05-15T00:00:00"
}
EOF

# Use in requests
curl -H "Authorization: Bearer your-secret-token-here" \
     http://localhost:8080/api/stats
```

## 5.5 Rate Limiting

```
Limit: 100 requests per minute per IP
Response on exceed: 429 Too Many Requests
Header: Retry-After: 60
```

## 5.6 Exemples curl

```bash
# Health check (public)
curl http://localhost:8080/api/health

# Get stats
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8080/api/stats

# List agents
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8080/api/agents

# Route a task
curl -G -H "Authorization: Bearer TOKEN" \
     --data-urlencode "task=Design a landing page" \
     http://localhost:8080/api/routing/route

# Get OpenAPI spec
curl http://localhost:8080/api/openapi.json
```

## 5.7 OpenAPI Spec

**Location:** `~/.opencode/api/docs/openapi.json`

**Version:** 3.0.3

**Access:** `GET /api/openapi.json`

---

# 6. DESKTOP EDITION

## 6.1 Overview

**Configuration:** Isolée (100% copie)  
**Taille:** ~12MB  
**Sync:** Auto (hourly) + Manuel

## 6.2 Directory Structure

```
~/.opencode-desktop/
├── agents/           # 22 agents YAML (copie)
├── skills/           # 59 skills (copie)
├── memory/           # Nexus 5 branches (copie isolée)
├── data/             # 4 DBs SQLite (copie dédiée)
├── config/           # Config files (copie)
├── scripts/          # Scripts (copie + dédiés)
├── tests/            # 20 tests unitaires (copie)
├── AGENTS.md         # Custom instructions
├── opencode.jsonc    # Config Desktop-specific
├── README.desktop.md # Desktop documentation
└── sync.log          # Sync logs
```

## 6.3 Commandes Dédiées

```bash
# Desktop status
nvd status

# Desktop health
nvd health

# Manual sync
nvd-sync

# Desktop agents
nvd agents

# Desktop skills
nvd skills
```

## 6.4 Auto-Sync (Cron)

```bash
# Schedule: 0 * * * * (every hour at minute 0)
# Script: ~/.opencode-desktop/scripts/sync-from-cli.sh
# Log: ~/.opencode-desktop/sync.log

# Check cron job
crontab -l | grep sync-from-cli
# Output: 0 * * * * bash /home/novahiz/.opencode-desktop/scripts/sync-from-cli.sh

# Next sync
date -d '+1 hour' '+%H:00'
```

## 6.5 Limitations vs CLI

| Feature | CLI | Desktop |
|---------|-----|---------|
| `nv route` | ✓ | ❌ (via chat only) |
| `nv invoke` | ✓ | ❌ (via chat only) |
| `nv council` | ✓ | ❌ (via chat only) |
| `nv backup` | ✓ | ✓ (shared) |
| `nv api` | ✓ | ✓ (via CLI) |
| Commands | 15+ | 5 (status/health/agents/skills/search) |

## 6.6 Cas d'Usage Recommandés

**Desktop:**
- Travail quotidien via UI
- Chat avec agents
- Visualisation status
- Sessions isolées

**CLI:**
- Orchestration complexe
- Routing auto
- Backup management
- API management
- Scripting (JSON output)

---

# 7. AGENTS — FICHES COMPLÈTES

## 7.1 Novahiz Router

```yaml
name: novahiz-router
role: NovaHiz OS Sovereign Orchestration Layer
type: primary
model: anthropic/claude-3-5-sonnet
```

**Responsabilités:**
- Classification (SIMPLE/MEDIUM/COMPLEX)
- Routing vers subagents
- Council deliberation
- CAVEMAN MODE enforcement

**Invocation:**
```bash
# Auto (via router)
nv route "task"

# Direct
nv invoke novahiz-router --task "orchestrate this project"
```

## 7.2 Luna (Design)

```yaml
name: luna-design
role: Design Council Expert
type: subagent
domain: design
score: 95
```

**Expertise:**
- UI/UX Design
- Figma → Code
- Design Systems
- Animations CSS/JS
- Responsive Design
- Accessibilité

**Skills:**
- frontend-design
- canvas-design
- extract-design-system
- ui-ux-pro-max
- web-design-guidelines

**Invocation:**
```bash
nv invoke luna-design --task "Design a login page"
```

## 7.3 Kenzo (Performance)

```yaml
name: kenzo-performance
role: Performance Optimization Expert
type: subagent
domain: performance
score: 95
```

**Expertise:**
- Core Web Vitals
- Performance optimization
- Caching strategies
- Bundle optimization
- Lazy loading

**Skills:**
- vercel-react-best-practices
- improve-codebase-architecture
- next-best-practices
- vercel-composition-patterns

## 7.4 Malik (Database)

```yaml
name: malik-database
role: Database Architecture Expert
type: subagent
domain: database
score: 95
```

**Expertise:**
- SQL/NoSQL
- Database architecture
- Query optimization
- Indexing strategies
- Data modeling

**Skills:**
- xlsx

## 7.5 Arthur (Architecture)

```yaml
name: arthur-architecture
role: Software Architecture Expert
type: subagent
domain: architecture
score: 95
```

**Expertise:**
- Software architecture
- Design patterns
- System design
- Code organization
- Scalability

**Skills:**
- improve-codebase-architecture
- vercel-composition-patterns
- next-best-practices

## 7.6 Neo (Security)

```yaml
name: neo-security
role: Security Audit Expert
type: subagent
domain: security
score: 90
```

**Expertise:**
- Security audits
- Vulnerability assessment
- OWASP Top 10
- Authentication/Authorization
- Encryption

**Skills:**
- github-actions-docs

## 7.7 Sarah (Quality)

```yaml
name: sarah-quality
role: Code Quality Expert
type: subagent
domain: quality
score: 95
```

**Expertise:**
- Code reviews
- Testing strategies
- TDD/BDD
- Code quality metrics
- Best practices

**Skills:**
- requesting-code-review
- tdd
- systematic-debugging
- writing-plans

## 7.8 Elias (Marketing)

```yaml
name: elias-marketing
role: Marketing & Growth Expert
type: subagent
domain: marketing
score: 95
```

**Expertise:**
- Content marketing
- Growth strategies
- SEO
- Social media
- Email campaigns

**Skills:**
- copywriting
- content-strategy
- seo-audit
- social-content
- email-sequence
- marketing-ideas
- marketing-psychology
- page-cro
- pricing-strategy
- launch-strategy

## 7.9 Victor (Strategy)

```yaml
name: victor-strategy
role: Strategy & Planning Expert
type: subagent
domain: strategy
score: 95
```

**Expertise:**
- Strategic planning
- Decision making
- Roadmapping
- Prioritization
- Risk assessment

**Skills:**
- content-strategy
- launch-strategy
- brainstorming
- grill-me

## 7.10 Ralph (Execution)

```yaml
name: ralph-execution
role: Execution & Deployment Expert
type: subagent
domain: execution
score: 95
```

**Expertise:**
- Build automation
- Deployment
- CI/CD
- Release management
- DevOps

**Skills:**
- executing-plans
- deploy-to-vercel
- vercel-cli-with-tokens
- github-actions-docs

## 7.11 Atlas (Memory)

```yaml
name: atlas-memory
role: Memory & Context Expert
type: subagent
domain: memory
score: 95
```

**Expertise:**
- Context management
- Memory retrieval
- Session tracking
- Knowledge graphs

**Skills:**
- novahiz-nexus
- novahiz-memory
- novahiz-metrics
- novahiz-check

## 7.12-7.22 Elite Force Agents

| Agent | Domain | Score | Invocation |
|-------|--------|-------|------------|
| Ryù | Design (Japon) | 90 | Registry |
| Sage-07 | Data Science | 88 | Registry |
| Orion | DevOps | 92 | Registry |
| Vega | Legal | 85 | Registry |
| Phoenix | Crisis | 87 | Registry |
| Nexus | API | 91 | Registry |
| Cipher | Cryptography | 89 | Registry |
| Forge | CI/CD | 90 | Registry |
| Pulse | Realtime | 88 | Registry |
| Ghost | Stealth | 86 | Registry |
| Sage-11 | Legal | 85 | Registry |

---

# 8. SKILLS — CATALOGUE

## 8.1 Universal Skills (8)

Available to ALL agents:

| Skill | Description |
|-------|-------------|
| `brainstorming` | Creative ideation |
| `caveman` | CAVEMAN MODE compression |
| `simple` | Fast decision-making |
| `novahiz-status` | System dashboard |
| `novahiz-nexus` | Memory operations |
| `novahiz-metrics` | Metrics tracking |
| `novahiz-check` | Health checks |
| `novahiz-constitution` | System rules |

## 8.2 Specialized Skills (51)

### Architecture (1)
- `improve-codebase-architecture`

### Creative (2)
- `canvas-design`
- `extract-design-system`

### Development (15)
- `frontend-design`
- `ui-ux-pro-max`
- `web-design-guidelines`
- `vercel-react-best-practices`
- `next-best-practices`
- `vercel-composition-patterns`
- `vercel-react-view-transitions`
- `remotion-best-practices`
- `tdd`
- `systematic-debugging`
- `requesting-code-review`
- `writing-plans`
- `executing-plans`
- `to-prd`
- `to-issues`

### DevOps (4)
- `deploy-to-vercel`
- `vercel-cli-with-tokens`
- `github-actions-docs`
- `webapp-testing`

### Marketing (10)
- `copywriting`
- `content-strategy`
- `seo-audit`
- `social-content`
- `email-sequence`
- `marketing-ideas`
- `marketing-psychology`
- `page-cro`
- `pricing-strategy`
- `launch-strategy`

### Utilities (19)
- `agent-browser`
- `browser-use`
- `xlsx`
- `pdf`
- `pptx`
- `programmatic-seo`
- `schema-markup`
- `ai-seo`
- `cold-email`
- `popup-cro`
- `signup-flow-cro`
- `onboarding-cro`
- `paywall-upgrade-cro`
- `form-cro`
- `grill-me`
- `find-skills`
- `skills-cli`
- `skill-creator`
- `customize-opencode`

## 8.3 Mapping Agents ↔ Skills

**File:** `~/.opencode/config/skills-linkage.json`

**Example:**
```json
{
  "luna-design": [
    "frontend-design",
    "canvas-design",
    "extract-design-system",
    "ui-ux-pro-max",
    "web-design-guidelines"
  ],
  "elias-marketing": [
    "copywriting",
    "content-strategy",
    "seo-audit",
    "social-content",
    "email-sequence",
    "marketing-ideas",
    "marketing-psychology",
    "page-cro",
    "pricing-strategy",
    "launch-strategy"
  ]
}
```

**Total:** 71 agent-skill links

## 8.4 Créer un Skill Personnalisé

```bash
# 1. Créer le répertoire
mkdir -p ~/.opencode/skills/my-custom-skill

# 2. Créer SKILL.md
cat > ~/.opencode/skills/my-custom-skill/SKILL.md << 'EOF'
---
name: my-custom-skill
description: >
  Custom skill for specific task
triggers: [my-trigger, custom-task]
hidden: false
---

# My Custom Skill

## Workflow

1. Step one
2. Step two
3. Step three

## Examples

\`\`\`bash
example command
\`\`\`
EOF

# 3. Sync
nv sync

# 4. Verify
nv skills | grep my-custom-skill
```

---

# 9. MEMORY NEXUS

## 9.1 Structure

```
~/.opencode/memory/
├── nexus.json              # Global nexus (23 nodes)
├── 00_Core/
│   ├── nexus.json          # Core memory
│   ├── scoreboard.json     # Agent metrics
│   ├── metrics.json        # System metrics
│   ├── selection-cache.json # Agent selection
│   └── sessions/           # Session tracking
├── 01_Agents/
│   ├── [agent].md          # Agent memory
│   └── [agent]_deliberations/
├── 02_Projects/
├── 03_Patterns/
└── 04_Archives/
```

## 9.2 Scoreboard (Agent Metrics)

**File:** `~/.opencode/memory/00_Core/scoreboard.json`

**Structure:**
```json
{
  "v": "1.4",
  "updated": "2026-05-14T20:59:09.287199",
  "agents": [
    {
      "id": "novahiz-router",
      "name": "Novahiz Router",
      "domain": "orchestration",
      "score": 100,
      "status": "subagent",
      "deliberations": 0,
      "lastActive": null,
      "firstSeen": "2026-05-14T21:02:00.638796",
      "sessions": 1,
      "tasksCompleted": 0,
      "successRate": 0.0
    }
  ]
}
```

**Metrics tracked:**
- Score (0-100)
- Status (active/subagent)
- Deliberations count
- Sessions count
- Tasks completed
- Success rate

## 9.3 Session Tracking

**Location:** `~/.opencode/memory/00_Core/sessions/`

**Isolation:**
- CLI sessions: `~/.opencode/memory/00_Core/sessions/`
- Desktop sessions: `~/.opencode-desktop/memory/00_Core/sessions/`

## 9.4 Deliberations

**Location:** `~/.opencode/memory/01_Agents/[agent]_deliberations/`

**Structure:**
```
luna-design_deliberations/
├── 20260514_143022_design-system.json
├── 20260514_151204_landing-page.json
└── ...
```

---

# 10. DATABASES

## 10.1 Overview

**Location:** `~/.opencode/data/`

**4 SQLite Databases:**
1. `novahiz.db` — Agent registry + routing
2. `skills-index.db` — Skills catalog
3. `agents-tracking.db` — Activity tracking
4. `tasks-history.db` — Task history

## 10.2 novahiz.db

**Tables:**
- `agents` (16 columns)
- `domains`
- `routing_log`
- `council_deliberations`

**Agents Schema:**
```sql
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    domain TEXT NOT NULL,
    score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    file_path TEXT,
    description TEXT,
    specialty TEXT,
    origin TEXT,
    invoke_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0
);
```

**Sample Data:**
```
novahiz-router | Novahiz Router | primary | orchestration | 100
luna-design    | Luna           | subagent| design        | 95
kenzo-performance | Kenzo       | subagent| performance   | 95
```

## 10.3 skills-index.db

**Tables:**
- `skills` (11 columns)

**Skills Schema:**
```sql
CREATE TABLE skills (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    trigger TEXT,
    description TEXT,
    file_path TEXT,
    keywords TEXT,
    agent_id TEXT,
    usage_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP
);
```

## 10.4 agents-tracking.db

**Purpose:** Track agent activity and usage

## 10.5 tasks-history.db

**Purpose:** Store task execution history

---

# 11. MONITORING & ALERTING

## 11.1 Configuration

**File:** `~/.opencode/config/monitoring.json`

```json
{
  "enabled": false,
  "checks": {
    "api": true,
    "database": true,
    "agents": false
  },
  "interval_minutes": 5,
  "channels": {
    "telegram": {
      "enabled": false,
      "bot_token": "",
      "chat_id": ""
    },
    "discord": {
      "enabled": false,
      "webhook_url": ""
    }
  },
  "alerts": {
    "api_down": true,
    "db_error": true,
    "agent_offline": false
  }
}
```

## 11.2 Telegram Integration

```json
{
  "telegram": {
    "enabled": true,
    "bot_token": "BOT_TOKEN_HERE",
    "chat_id": "CHAT_ID_HERE"
  }
}
```

**Get Bot Token:**
1. Create bot via @BotFather on Telegram
2. Copy token
3. Add to config

**Get Chat ID:**
1. Send message to bot
2. Visit: `https://api.telegram.org/bot<token>/getUpdates`
3. Copy chat_id

## 11.3 Discord Integration

```json
{
  "discord": {
    "enabled": true,
    "webhook_url": "WEBHOOK_URL_HERE"
  }
}
```

**Get Webhook URL:**
1. Server Settings → Integrations → Webhooks
2. Create webhook
3. Copy URL

## 11.4 Alert Types

| Alert | Description | Default |
|-------|-------------|---------|
| `api_down` | API server unreachable | ✓ |
| `db_error` | Database connection error | ✓ |
| `agent_offline` | Agent not responding |  |

---

# 12. BACKUP & RESTORE

## 12.1 Auto-Backup (Systemd Timer)

**Schedule:** Daily at 03:00

**Service:** `novahiz-backup.service`

**Timer:** `novahiz-backup.timer`

**Installation:**
```bash
bash ~/.opencode/scripts/install-backup-timer.sh
```

**Verify:**
```bash
systemctl --user status novahiz-backup.timer
systemctl --user list-timers
```

## 12.2 Manual Backup

```bash
# Create backup
nv backup

# Output:
# Creating backup...
# ✓ Backup: ~/.opencode/backups/20260515_011200/
```

## 12.3 Backup Structure

```
~/.opencode/backups/
├── 20260514_212424/
├── 20260514_224240/
├── 20260514_224341/
├── 20260515_004204/
└── ... (7 days rotation)
```

## 12.4 Rotation

**Policy:** 7 days

**Auto-cleanup:** Old backups automatically archived

## 12.5 Restore Procedure

```bash
# 1. Stop API server
nv api stop

# 2. Copy backup
cp -r ~/.opencode/backups/TIMESTAMP/* ~/.opencode/

# 3. Restart API
nv api start

# 4. Verify
nv health
```

---

# 13. TESTS & VALIDATION

## 13.1 Unit Tests (20 tests)

**File:** `~/.opencode/tests/test_novahiz.py`

**Categories:**
- CLI (9 tests)
- API (2 tests)
- Databases (4 tests)
- Memory (5 tests)

## 13.2 Run Tests

```bash
# Run all tests
python3 ~/.opencode/tests/test_novahiz.py

# Output:
# ....................
# ----------------------------------------------------------------------
# Ran 20 tests in 3.099s
# OK
```

## 13.3 Test Categories

### CLI Tests
- `test_status_command`
- `test_status_json`
- `test_agents_command`
- `test_agents_json`
- `test_health_command`
- `test_command_suggestion`
- `test_unknown_command`
- `test_help_command`
- `test_backup_command`

### API Tests
- `test_health_endpoint`
- `test_stats_endpoint`

### Database Tests
- `test_novahiz_db_exists`
- `test_agents_count`
- `test_skills_index_exists`
- `test_skills_count`

### Memory Tests
- `test_memory_directory_exists`
- `test_memory_branches`
- `test_nexus_json_exists`
- `test_scoreboard_exists`
- `test_scoreboard_agents`

## 13.4 Verification Scripts

```bash
# Desktop verification
bash ~/.opencode-desktop/scripts/verify-desktop.sh

# Output:
# ╔════════════════════════════════════════════════════╗
#      NOVAHIZ DESKTOP - VERIFICATION                 ║
# ╚════════════════════════════════════════════════════╝
#
# 1. Directory Structure: ✓
# 2. Agent Count: ✓ 22 agents
# 3. Skills Count: ✓ 59 skills
# 4. Config File: ✓
# 5. Sync Script: ✓
# 6. Desktop CLI Script: ✓
# 7. OpenCode Desktop Config: ✓
# 8. Databases: ✓
#
# ✓ ALL CHECKS PASSED
```

---

# 14. CUSTOM INSTRUCTIONS

## 14.1 CAVEMAN MODE (Règles Complètes)

**Activation:** Automatique sur chaque réponse

**Règles:**
```
1. 1-3 phrases max
2. Brutal truth, no fluff
3. French unless EN asked
4. Point essential only
5. No intro, no conclusion, no apology
6. Drop articles (a/an/the)
7. Drop filler (just/really/basically)
8. Drop pleasantries (sure/certainly)
9. Fragments OK
10. Technical terms exact
```

**Intensity Levels:**

| Level | Description | Example |
|-------|-------------|---------|
| `lite` | No filler, keep articles | "Component re-renders due to new object ref." |
| `full` | Drop articles, fragments | "New object ref each render. Wrap in useMemo." |
| `ultra` | Abbreviate, arrows | "Inline obj → new ref → re-render. useMemo." |
| `wenyan-lite` | Semi-classical Chinese | "組件頻重繪，以 useMemo 包之。" |
| `wenyan-full` | Classical Chinese | "物出新參照，致重繪。useMemo." |
| `wenyan-ultra` | Ultra-classical | "新參照→重繪。useMemo." |

**Switch Levels:**
```
/caveman lite
/caveman full
/caveman ultra
/caveman wenyan-lite
/caveman wenyan-full
/caveman wenyan-ultra
```

**Disable:**
```
stop caveman
normal mode
```

## 14.2 AGENTS.md (Custom Instructions)

**File:** `~/.opencode/AGENTS.md` (CLI)  
**File:** `~/.opencode-desktop/AGENTS.md` (Desktop)  
**File:** `~/.local/share/opencode/AGENTS.md` (OpenCode default)

**Content:**
```markdown
# NovaHiz OS v1.7 — Custom Instructions

## CAVEMAN MODE — OBLIGATOIRE

**Règles:**
- 1-3 phrases max
- Brutal truth, no fluff
- French unless EN asked

## Agents Disponibles (22)

**Novahiz Router** — Orchestration principale

**Council (10):**
- luna-design, kenzo-performance, malik-database, arthur-architecture
- neo-security, sarah-quality, elias-marketing, victor-strategy
- ralph-execution, atlas-memory

**Elite Force (12):**
- ryu-design, sage-07, orion-devops, vega-legal, phoenix-crisis
- nexus-api, cipher-crypto, forge-cicd, pulse-realtime, ghost-stealth
- sage-11
```

## 14.3 novahiz-router.yaml System Prompt

**File:** `~/.opencode/agents/novahiz-router.yaml`

**System Prompt:** 133 lines

**Key Sections:**
- CAVEMAN MODE enforcement
- Architecture (3-layer)
- 10 Council Agents
- 12 Elite Force Agents
- Routing Protocol
- Invocation syntax
- Skills paths
- Workflows

---

# 15. WORKFLOWS SPÉCIALISÉS

## 15.1 Code Review Workflow

**File:** `~/.opencode/workflows/code-review/pragmatic-code-review-subagent.md`

**Steps:**
1. Analyze code changes
2. Check for bugs
3. Review style consistency
4. Security assessment
5. Performance check
6. Provide actionable feedback

## 15.2 Design Review Workflow

**File:** `~/.opencode/workflows/design-review/design-review-agent.md`

**Steps:**
1. UX assessment
2. Accessibility check
3. Responsive design review
4. Design system alignment
5. Animation review
6. Provide recommendations

## 15.3 Security Review Workflow

**File:** `~/.opencode/workflows/security-review/security-review-slash-command.md`

**Steps:**
1. OWASP Top 10 check
2. Authentication review
3. Authorization check
4. Input validation
5. Encryption assessment
6. Provide security recommendations

## 15.4 Créer un Workflow Personnalisé

```bash
# 1. Créer le répertoire
mkdir -p ~/.opencode/workflows/my-workflow

# 2. Créer WORKFLOW.md
cat > ~/.opencode/workflows/my-workflow/WORKFLOW.md << 'EOF'
# My Custom Workflow

## Steps

1. Step one
2. Step two
3. Step three

## Triggers

- trigger-1
- trigger-2

## Output

Expected output format
EOF

# 3. Reference in agent YAML
```

---

# 16. DÉPANNAGE & FAQ

## 16.1 Erreurs Courantes

### Error: "Unknown command"
```bash
# Cause: Typo in command
# Solution: Use nv --help to see available commands
nv --help

# Auto-suggestion will help:
# Did you mean: nv status?
```

### Error: "ConfigInvalidError: Unrecognized key: agents"
```bash
# Cause: Invalid opencode.jsonc
# Solution: Remove 'agents' key

# Correct config:
{
  "$schema": "https://opencode.ai/config.json",
  "skills": {
    "paths": ["/home/novahiz/.opencode-desktop/skills"]
  }
}
```

### Error: "API not running"
```bash
# Cause: API server not started
# Solution: Start API server
nv api start

# Or manually:
python3 ~/.opencode/api/server.py &
```

### Error: "Database locked"
```bash
# Cause: Concurrent access
# Solution: Wait or kill process
pkill -f novahiz-cli.py

# Then retry
```

## 16.2 Logs

**Location:** `~/.opencode/logs/novahiz.log`

**View logs:**
```bash
# Last 50 lines
tail -50 ~/.opencode/logs/novahiz.log

# Follow (real-time)
tail -f ~/.opencode/logs/novahiz.log

# Filter by level
grep ERROR ~/.opencode/logs/novahiz.log
```

**Log levels:**
- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

## 16.3 Debug Commands

```bash
# System health
nv health

# Database check
sqlite3 ~/.opencode/data/novahiz.db "SELECT COUNT(*) FROM agents;"

# Skills check
ls -d ~/.opencode/skills/*/ | wc -l

# Memory check
cat ~/.opencode/memory/nexus.json | python3 -m json.tool

# API check
curl http://localhost:8080/api/health
```

## 16.4 FAQ

### Q: Comment mettre à jour NovaHiz OS?
```bash
# Pull latest changes
cd /tmp/novahiz-os && git pull

# Sync to CLI
cp -r /tmp/novahiz-os/* ~/.opencode/

# Sync to Desktop
nvd-sync
```

### Q: Comment ajouter un agent?
```bash
# 1. Create YAML file
cat > ~/.opencode/agents/my-agent.yaml << 'EOF'
name: my-agent
role: My Custom Agent
type: subagent
model: anthropic/claude-3-5-sonnet

system: |
  Tu es **My Agent**, expert en...
EOF

# 2. Sync
nv sync

# 3. Verify
nv agents | grep my-agent
```

### Q: Comment désactiver CAVEMAN MODE?
```
stop caveman
normal mode
```

### Q: Desktop vs CLI — lequel utiliser?
- **Desktop:** Travail quotidien via UI
- **CLI:** Orchestration complexe, scripting

### Q: Comment backup manuellement?
```bash
nv backup
```

### Q: Où sont les sessions?
- CLI: `~/.opencode/memory/00_Core/sessions/`
- Desktop: `~/.opencode-desktop/memory/00_Core/sessions/`

### Q: Comment changer le modèle d'un agent?
```bash
# Edit agent YAML
nano ~/.opencode/agents/luna-design.yaml

# Change model:
model: anthropic/claude-3-5-sonnet
# to
model: anthropic/claude-3-opus
```

### Q: API rate limit — comment augmenter?
```bash
# Edit API server
nano ~/.opencode/api/server.py

# Change RATE_LIMIT (line 23):
RATE_LIMIT = 100  # requests per minute
# to
RATE_LIMIT = 200
```

### Q: Comment reset Desktop config?
```bash
# Remove Desktop config
rm -rf ~/.opencode-desktop/*

# Re-sync from CLI
nvd-sync
```

---

# 17. ANNEXES

## 17.1 Glossary

| Term | Definition |
|------|------------|
| **Agent** | AI specialist with specific domain expertise |
| **Skill** | Capability that agents can use |
| **CAVEMAN MODE** | Compression style: 1-3 phrases, no fluff |
| **Router** | Primary agent for orchestration |
| **Council** | 10 active subagents |
| **Elite Force** | 12 simulated subagents |
| **Nexus** | Memory system (5 branches) |
| **Scoreboard** | Agent metrics tracking |
| **Deliberation** | Multi-agent discussion |
| **Routing** | Task classification + agent selection |

## 17.2 CLI Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│              NOVAHIZ CLI — QUICK REFERENCE                 │
├────────────────────────────────────────────────────────────┤
│ STATUS:  nv status | nv health | nv stats | nv agents     │
│ SKILLS:  nv skills                                        │
│ ROUTING: nv route "<task>" | nv invoke <agent> --task <>  │
│ COUNCIL: nv council "<task>"                              │
│ SEARCH:  nv search "<query>"                              │
│ SYSTEM:  nv sync | nv link | nv backup | nv logs          │
│ MGMT:    nv monitor | nv api                             │
│ OPTIONS: --json | --quiet | --verbose | --help            │
└────────────────────────────────────────────────────────────┘
```

## 17.3 API Quick Reference Card

```
┌────────────────────────────────────────────────────────────┐
│              NOVAHIZ API — QUICK REFERENCE                 │
├────────────────────────────────────────────────────────────┤
│ Health:  GET /api/health (public)                          │
│ Stats:   GET /api/stats (auth)                             │
│ Agents:  GET /api/agents (auth)                            │
│ Skills:  GET /api/skills (auth)                            │
│ Tasks:   GET /api/tasks (auth)                             │
│ Route:   GET /api/routing/route?task=<> (auth)             │
│ Spec:    GET /api/openapi.json (public)                    │
│                                                            │
│ Auth:    -H "Authorization: Bearer TOKEN"                  │
│ Rate:    100 req/min/IP                                    │
│ Port:    8080                                              │
└────────────────────────────────────────────────────────────┘
```

## 17.4 Changelog v1.7

**Date:** 2026-05-15

**Changes:**
- Added 22 agents (10 Council + 12 Elite Force)
- Added 59 skills
- Implemented CAVEMAN MODE (Layer 0)
- Created Memory Nexus (5 branches, 23 nodes)
- Built CLI with 15+ commands
- Launched API server (9 endpoints)
- Added Desktop Edition (isolated config)
- Implemented auto-sync (hourly cron)
- Added systemd backup timer (daily 03:00)
- Created 20 unit tests (100% pass)
- Added monitoring (Telegram/Discord opt-in)
- Implemented rate limiting (100 req/min)

## 17.5 License

**MIT License**

Copyright (c) 2026 NovaHiz OS

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

---

**NOVAHIZ OS v1.7 — DOCUMENTATION COMPLÈTE**

**Generated:** 2026-05-15  
**Location:** `~/.opencode/DOCUMENTATION.md`  
**Desktop:** `~/.opencode-desktop/DOCUMENTATION.md`
