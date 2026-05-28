# Novahiz OS — Architecture Documentation

**Version:** 2.0  
**Last Updated:** 2026-05-27  
**Status:** Refactored for SOLID compliance

---

## 1. Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                    NOVAHIZ OS v6.0                          │
│              Unified Multi-Agent Orchestration              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Input    │────▶│  Unified Daemon │────▶│  LLM Providers  │
│  (CLI/MCP/API)  │     │ (novahiz-unified│     │ (OpenRouter,etc)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │   Rate Limiter  │
                    │   Budget Guard  │
                    └─────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │  Agent Registry │
                    │  (10+ Agents)   │
                    └─────────────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │  Memory System  │
                    │  (Nexus/Atlas)  │
                    └─────────────────┘
```

---

## 2. Principes Architecturaux (SOLID)

### 2.1 Single Responsibility Principle (SRP)

| Module | Responsabilité Unique |
|--------|----------------------|
| `novahiz-unified.py` | Orchestration des exécutions |
| `rate_limiter.py` | Gestion des rate limits |
| `rgpd_tools.py` | Conformité RGPD |
| `performance-audit.py` | Audit performance |
| `chaos-engineering.py` | Tests de résilience |

### 2.2 Open/Closed Principle (OCP)

**Extension sans modification:**

```python
# Nouvel agent → Ajouter dans AGENT_PROFILES
AGENT_PROFILES = {
    "neo-security": {...},
    "sarah-quality": {...},
    # Ajouter ici sans modifier le code existant
}

# Nouveau provider → Ajouter dans config.json
"providers": {
    "openrouter": {...},
    "new-provider": {...}  # Extension sans modification
}
```

### 2.3 Liskov Substitution Principle (LSP)

**Tous les agents respectent le même contrat:**

```python
class AgentInterface:
    def execute(self, task: str) -> dict:
        """Returns: {"success": bool, "content": str, ...}"""
        pass

# Tous les agents sont substituables
neo = NeoSecurityAgent()
sarah = SarahQualityAgent()
# Interchangeables dans l'orchestrateur
```

### 2.4 Interface Segregation Principle (ISP)

**Interfaces fines et spécialisées:**

| Interface | Méthodes | Usage |
|-----------|----------|-------|
| `LLMExecutor` | `execute()` | Exécution LLM |
| `RateLimiter` | `check()` | Rate limiting |
| `BudgetGuard` | `check_budget()` | Contrôle budget |
| `MetricsCollector` | `record()` | Tracking metrics |

### 2.5 Dependency Inversion Principle (DIP)

**Dépendances vers les abstractions:**

```python
# ❌ AVANT: Dépendance concrète
class Orchestrator:
    def __init__(self):
        self.executor = LLMExecutor()  # Concret

# ✅ APRÈS: Injection de dépendance
class Orchestrator:
    def __init__(self, executor: LLMExecutorInterface):
        self.executor = executor  # Abstraction
```

---

## 3. Composants Principaux

### 3.1 Unified Daemon

**Fichier:** `runtime/novahiz-unified.py`

**Responsabilités:**
- Polling des fichiers d'exécution
- Routing vers le bon modèle (flash/smart/premium)
- Application des rate limits
- Gestion du budget premium
- Logging centralisé

**Flux:**
```
Execution File → Validate → Rate Limit Check → Budget Check
                                            ↓
                                    Select Model Tier
                                            ↓
                                    LLM Execution
                                            ↓
                                    Update File + Log
```

### 3.2 Rate Limiter

**Fichier:** `runtime/rate_limiter.py`

**Algorithme:** Token Bucket

| Tier | Per Minute | Per Hour | Per Day |
|------|------------|----------|---------|
| Flash | 100 | 1000 | 5000 |
| Smart | 50 | 500 | 2000 |
| Premium | 10 | 50 | 200 |

### 3.3 Budget Guard

**Intégré dans:** `novahiz-unified.py`

**Fonction:**
- Limite quotidienne configurable (défaut: 3 appels premium/jour)
- Reset automatique chaque jour
- Auto-fallback vers smart tier si limite atteinte

### 3.4 Memory System

**Structure:**
```
memory/
├── 00_Core/          # Constitution, metrics, nexus
├── 01_Agents/        # Agent definitions
├── 02_Projects/      # Project tracking
├── 03_Patterns/      # Design patterns
├── 04_Archives/      # Historical data (immutable)
└── 05_Context/       # Current session context
```

---

## 4. Points de Décision Architecturaux (ADR)

### ADR-001: Unified Daemon

**Date:** 2026-05-27  
**Statut:** Accepté

**Contexte:** Deux daemons séparés (runtime + bridge) créaient de la complexité.

**Décision:** Fusionner en un seul daemon unifié.

**Conséquences:**
- ✅ -50% complexité
- ✅ Code partagé
- ⚠️  Single point of failure (mitigé par supervisor)

### ADR-002: Rate Limiting

**Date:** 2026-05-27  
**Statut:** Accepté

**Contexte:** Risque de coûts explosifs sans contrôle.

**Décision:** Token bucket algorithm avec limites par tier.

**Conséquences:**
- ✅ Coûts maîtrisés
- ✅ Protection API quotas
- ⚠️  Latence ajoutée (négligeable: <1ms)

### ADR-003: RGPD First

**Date:** 2026-05-27  
**Statut:** Accepté

**Contexte:** Conformité légale requise.

**Décision:** Privacy by design, opt-in par défaut.

**Conséquences:**
- ✅ Conformité RGPD
- ✅ Confiance utilisateurs
- ⚠️  Features analytics limitées

---

## 5. Diagrammes de Flux

### 5.1 Execution Flow

```
User Task
    │
    ▼
┌─────────────┐
│ Create File │ (executions/exec_*.json)
└─────────────┘
    │
    ▼
┌─────────────┐
│ Daemon Poll │ (2s interval)
└─────────────┘
    │
    ▼
┌─────────────┐
│ Rate Limit  │ ← Check tier limits
└─────────────┘
    │
    ▼
┌─────────────┐
│ Budget Check│ ← Premium budget guard
└─────────────┘
    │
    ▼
┌─────────────┐
│ LLM Execute │ → OpenRouter API
└─────────────┘
    │
    ▼
┌─────────────┐
│ Update File │ (status: completed/failed)
└─────────────┘
    │
    ▼
Log + Metrics
```

### 5.2 Memory Flow

```
┌──────────────┐
│ Write Nexus  │ → memory/00_Core/nexus.json
└──────────────┘
       │
       ▼
┌──────────────┐
│ Atomic Write │ → .tmp + rename()
└──────────────┘
       │
       ▼
┌──────────────┐
│ Versioning   │ → 04_Archives/ (immutable)
└──────────────┘
```

---

## 6. Sécurité

### 6.1 Controls

| Control | Implementation |
|---------|---------------|
| Secrets | Environment variables, never in code |
| Rate Limits | Token bucket per tier |
| Budget | Daily limit with auto-fallback |
| Audit Logs | All executions logged |
| RGPD | Opt-in, export, deletion tools |

### 6.2 Threat Model

| Threat | Mitigation |
|--------|------------|
| API Key Leak | .gitignore, env vars, secret scanner |
| Cost Explosion | Rate limits, budget guard |
| Data Loss | Backups, versioning |
| Privacy Violation | RGPD tools, opt-in default |

---

## 7. Performance

### 7.1 Benchmarks (2026-05-27)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Memory | 13.2 MB | <100 MB | ✅ |
| CPU Load | 1.26 | <4.0 | ✅ |
| File I/O | 0.079ms | <10ms | ✅ |
| Execution Avg | 25.31s | <30s | ✅ |
| Success Rate | 100% | >95% | ✅ |

### 7.2 Bottlenecks

| Bottleneck | Impact | Resolution |
|------------|--------|------------|
| HTTP Latency | 1829ms | Unavoidable (API distante) |
| Daemon Poll | 2s | Configurable, trade-off latency/CPU |

---

## 8. Évolutivité

### 8.1 Scaling Up

- **Vertical:** More CPU/RAM for daemon
- **Horizontal:** Multiple daemons with load balancer (future)

### 8.2 New Features

```
1. Create module in scripts/
2. Add unit tests in tests/
3. Update this doc
4. PR review → Merge
```

---

## 9. Références

- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Token Bucket Algorithm](https://en.wikipedia.org/wiki/Token_bucket)
- [RGPD/GDPR](https://gdpr.eu/)
- [Chaos Engineering](https://principlesofchaos.com/)

---

*Document vivant — Mis à jour à chaque changement architectural majeur*
