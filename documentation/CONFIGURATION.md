# ⚙️ CONFIGURATION MULTI-PROVIDER

**Version:** 5.2.0  
**Dernière MAJ:** 2026-05-26

---

## 🎯 VUE D'ENSEMBLE

Novahiz OS v5.2 supporte **multi-providers LLM** avec fallback automatique.

**Providers supportés:**
- ✅ **OpenRouter** (100+ modèles)
- ✅ **OpenCode Zen** (modèles Qwen optimisés)

---

## 📋 CONFIGURATION PAR DÉFAUT

### Providers

| Provider | API Key | Priority | Status |
|----------|---------|----------|--------|
| **openrouter** | `sk-or-v1-72053bf...` | 1 | ✅ Actif |
| **opencode-zen** | `sk-TnPvEkSpGh...` | 2 | ✅ Actif |

### Modèles par Tier

#### FLASH (Tâches simples)

```json
{
  "default": {"provider": "openrouter", "model": "qwen/qwen3.5-9b"},
  "fallbacks": [
    {"provider": "openrouter", "model": "qwen/qwen3.5-flash-02-23"},
    {"provider": "openrouter", "model": "stepfun/step-3.5-flash"},
    {"provider": "openrouter", "model": "z-ai/glm-4.7-flash"}
  ]
}
```

#### SMART (Tâches normales)

```json
{
  "default": {"provider": "opencode-zen", "model": "Qwen3.5 plus"},
  "fallbacks": [
    {"provider": "openrouter", "model": "qwen/qwen3.6-flash"},
    {"provider": "openrouter", "model": "qwen/qwen3.5-plus-20260420"},
    {"provider": "openrouter", "model": "moonshotai/kimi-k2.5"}
  ]
}
```

#### PREMIUM (Tâches critiques)

```json
{
  "default": {"provider": "openrouter", "model": "qwen/qwen3.6-plus"},
  "fallbacks": [
    {"provider": "openrouter", "model": "moonshotai/kimi-k2.5"},
    {"provider": "openrouter", "model": "z-ai/glm-5"}
  ]
}
```

---

## 🔧 COMMANDES DE CONFIGURATION

### Initialisation

```bash
# Initialiser configuration par défaut
python3 ~/.opencode/scripts/novahiz-config.py init
```

### Providers

```bash
# Lister providers
python3 ~/.opencode/scripts/novahiz-config.py providers

# Activer provider
python3 ~/.opencode/scripts/novahiz-config.py providers enable openrouter

# Désactiver provider
python3 ~/.opencode/scripts/novahiz-config.py providers disable opencode-zen
```

### Modèles

```bash
# Lister modèles par tier
python3 ~/.opencode/scripts/novahiz-config.py models

# Définir modèle default
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter qwen/qwen3.5-9b
python3 ~/.opencode/scripts/novahiz-config.py set-model smart opencode-zen "Qwen3.5 plus"
python3 ~/.opencode/scripts/novahiz-config.py set-model premium openrouter qwen/qwen3.6-plus

# Définir fallback (index 1, 2, ou 3)
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter qwen/qwen3.5-flash-02-23 1
python3 ~/.opencode/scripts/novahiz-config.py set-model smart openrouter qwen/qwen3.6-flash 1
```

### Liste des Modèles Disponibles

```bash
# Voir tous les modèles des providers
python3 ~/.opencode/scripts/novahiz-config.py list-available
```

---

## 📝 FICHIER DE CONFIGURATION

**Emplacement:** `~/.opencode/runtime/config.json`

### Structure Complète

```json
{
  "version": "5.2.0",
  "providers": {
    "openrouter": {
      "enabled": true,
      "name": "OpenRouter",
      "api_key_env": "OPENROUTER_API_KEY",
      "api_key": "sk-or-v1-...",
      "base_url": "https://openrouter.ai/api/v1",
      "timeout": 60,
      "max_tokens": 8192,
      "priority": 1
    },
    "opencode-zen": {
      "enabled": true,
      "name": "OpenCode Zen",
      "api_key_env": "OPENCODE_ZEN_API_KEY",
      "api_key": "sk-TnPvEk...",
      "base_url": "https://api.opencode.ai/v1",
      "timeout": 60,
      "max_tokens": 8192,
      "priority": 2
    }
  },
  "models": {
    "flash": {...},
    "smart": {...},
    "premium": {...}
  },
  "runtime": {
    "retry_count": 3,
    "retry_delay": 2,
    "auto_fallback": true,
    "max_fallbacks": 3
  }
}
```

---

## 🔄 FALLBACK AUTOMATIQUE

### Comment Ça Marche

1. **Tentative provider par défaut**
2. **Si échec → Fallback 1**
3. **Si échec → Fallback 2**
4. **Si échec → Fallback 3**
5. **Si tous échouent → Erreur**

### Exemple de Log

```
[20:30:15] [INFO] Executing: nexus-api (opencode-zen)
[20:30:16] [ERROR] OpenCode Zen failed: Timeout
[20:30:16] [INFO] Falling back to openrouter (fallback 1)
[20:30:18] [SUCCESS] Execution complete (qwen/qwen3.6-flash)
```

---

## 🎯 BEST PRACTICES

### Configuration Recommandée

```bash
# FLASH: Rapide, moins cher
nv config set-model flash openrouter qwen/qwen3.5-9b
nv config set-model flash openrouter qwen/qwen3.5-flash-02-23 1

# SMART: Meilleur rapport qualité/prix
nv config set-model smart opencode-zen "Qwen3.5 plus"
nv config set-model smart openrouter qwen/qwen3.6-flash 1

# PREMIUM: Maximum de performance
nv config set-model premium openrouter qwen/qwen3.6-plus
nv config set-model premium openrouter moonshotai/kimi-k2.5 1
```

### Quand Utiliser Chaque Tier

| Tier | Use Cases | Exemples |
|------|-----------|----------|
| **FLASH** | Tâches simples, rapides | "Fix typo", "Explain X", "Simple function" |
| **SMART** | Développement normal | "Build API", "Create component", "Refactor" |
| **PREMIUM** | Critique, complexe | "Security audit", "Architecture design", "Production code" |

---

## 🔒 SÉCURITÉ

### API Keys

**Ne JAMAIS:**
- ❌ Commiter `config.json` dans git
- ❌ Partager API keys publiquement
- ❌ Logger API keys

**Toujours:**
- ✅ Utiliser variables d'environnement
- ✅ Permissions 600 sur config.json
- ✅ Rotation régulière des keys

### Commandes

```bash
# Permissions restrictives
chmod 600 ~/.opencode/runtime/config.json

# Vérifier permissions
ls -la ~/.opencode/runtime/config.json

# Backup sécurisé
cp ~/.opencode/runtime/config.json ~/.opencode/runtime/config.json.backup
chmod 600 ~/.opencode/runtime/config.json.backup
```

---

## 📊 COMPARAISON PROVIDERS

| Critère | OpenRouter | OpenCode Zen |
|---------|------------|--------------|
| **Modèles** | 100+ | 10-20 |
| **Prix** | Variable | Fixe |
| **Latence** | 2-5s | 1-3s |
| **Qualité** | Excellente | Très bonne |
| **Fallback** | Multiple | Limited |
| **Recommandation** | Premium, Flash | Smart |

---

## 🐛 DÉPANNAGE

### Provider Non Trouvé

```bash
# Vérifier config
cat ~/.opencode/runtime/config.json | jq '.providers'

# Réinitialiser
python3 ~/.opencode/scripts/novahiz-config.py init
```

### API Key Invalide

```bash
# Tester API key OpenRouter
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models

# Tester API key OpenCode Zen
curl -H "Authorization: Bearer $OPENCODE_ZEN_API_KEY" \
  https://api.opencode.ai/v1/models
```

### Fallback Ne Fonctionne Pas

```bash
# Vérifier config fallbacks
python3 ~/.opencode/scripts/novahiz-config.py models

# Vérifier auto_fallback
cat ~/.opencode/runtime/config.json | jq '.runtime.auto_fallback'

# Doit être: true
```

---

**Documentation liée:**
- [README.md](README.md) — Documentation principale
- [MODELS.md](MODELS.md) — Modèles LLM détaillés
- [CLI.md](CLI.md) — Commandes CLI
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Dépannage
