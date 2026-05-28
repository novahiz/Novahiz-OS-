# 🐛 DÉPANNAGE — GUIDE COMPLET

**Version:** 5.2.0  
**Dernière MAJ:** 2026-05-26

---

## 🔍 DIAGNOSTIC RAPIDE

### Commandes de Base

```bash
# 1. Vérifier status
python3 ~/.opencode/runtime/novahiz-runtime.py status

# 2. Vérifier providers
python3 ~/.opencode/scripts/novahiz-config.py providers

# 3. Vérifier daemon
ps aux | grep novahiz-runtime | grep -v grep

# 4. Vérifier logs
tail -20 ~/.opencode/logs/runtime.log
```

---

## ⚠️ PROBLÈMES COMMUNS

### 1. API Key Non Trouvée

**Symptômes:**
```
[ERROR] API key not found in OPENROUTER_API_KEY
[ERROR] HTTP error (401): {"error": {"message": "No cookie auth credentials found"}}
```

**Solutions:**

```bash
# 1. Vérifier .bashrc
grep OPENROUTER_API_KEY ~/.bashrc
grep OPENCODE_ZEN_API_KEY ~/.bashrc

# 2. Exporter manuellement
export OPENROUTER_API_KEY=sk-or-v1-your-openrouter-api-key-here
export OPENCODE_ZEN_API_KEY=sk-TnPvEkSpGhfk8ubcWhdCWR1octoF9sq545bTfJ4BhodaeIEINBVtLnnRHwZBpNiy

# 3. Vérifier config
cat ~/.opencode/runtime/config.json | jq '.providers'

# 4. Redémarrer daemon
pkill -f novahiz-runtime
python3 ~/.opencode/runtime/novahiz-runtime.py daemon &
```

---

### 2. Provider Échoue

**Symptômes:**
```
[ERROR] OpenRouter failed: HTTP error (400)
[ERROR] OpenCode Zen failed: Timeout
```

**Solutions:**

```bash
# 1. Tester API key
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  https://openrouter.ai/api/v1/models | jq '.data | length'

# 2. Vérifier provider activé
python3 ~/.opencode/scripts/novahiz-config.py providers

# 3. Activer fallback
python3 ~/.opencode/scripts/novahiz-config.py providers enable openrouter
python3 ~/.opencode/scripts/novahiz-config.py providers enable opencode-zen

# 4. Changer modèle
python3 ~/.opencode/scripts/novahiz-config.py set-model smart openrouter qwen/qwen3.6-flash

# 5. Vérifier modèles disponibles
python3 ~/.opencode/scripts/novahiz-config.py list-available
```

---

### 3. Daemon Ne Démarre Pas

**Symptômes:**
```bash
$ python3 ~/.opencode/runtime/novahiz-runtime.py daemon &
# Aucun processus ne démarre
```

**Solutions:**

```bash
# 1. Vérifier Python
python3 --version
# Doit être: Python 3.10+

# 2. Mode debug
python3 -u ~/.opencode/runtime/novahiz-runtime.py daemon 2>&1 | head -50

# 3. Kill anciens processus
pkill -9 -f novahiz-runtime
sleep 2

# 4. Vérifier logs
tail -50 ~/.opencode/logs/runtime.log

# 5. Redémarrer
cd ~/.opencode/runtime
python3 novahiz-runtime.py daemon > ../logs/runtime-daemon.log 2>&1 &
echo $! > ../pids/runtime.pid

# 6. Vérifier
ps -p $(cat ../pids/runtime.pid)
```

---

### 4. Exécutions Restent Pending

**Symptômes:**
```json
{
  "status": "pending",
  "result": null
}
```

**Solutions:**

```bash
# 1. Vérifier daemon running
ps aux | grep novahiz-runtime | grep -v grep

# 2. Vérifier logs
tail -f ~/.opencode/logs/runtime-daemon.log

# 3. Force process
python3 ~/.opencode/runtime/novahiz-runtime.py exec ralph-execution "test"

# 4. Vérifier config
cat ~/.opencode/runtime/config.json | jq '.runtime'

# 5. Redémarrer daemon
pkill -f novahiz-runtime
sleep 2
python3 ~/.opencode/runtime/novahiz-runtime.py daemon &
```

---

### 5. Modèles Non Trouvés

**Symptômes:**
```
[ERROR] HTTP error (400): {"error": {"message": "qwen/qwen3.5-plus is not a valid model ID"}}
```

**Solutions:**

```bash
# 1. Lister modèles disponibles
python3 ~/.opencode/scripts/novahiz-config.py list-available

# 2. Mettre à jour config
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter qwen/qwen3.5-9b
python3 ~/.opencode/scripts/novahiz-config.py set-model smart openrouter qwen/qwen3.6-flash
python3 ~/.opencode/scripts/novahiz-config.py set-model premium openrouter qwen/qwen3.6-plus

# 3. Vérifier
python3 ~/.opencode/scripts/novahiz-config.py models

# 4. Redémarrer daemon
pkill -f novahiz-runtime
python3 ~/.opencode/runtime/novahiz-runtime.py daemon &
```

---

### 6. Fallback Ne Fonctionne Pas

**Symptômes:**
```
[ERROR] All retry attempts failed
[ERROR] No fallback configured
```

**Solutions:**

```bash
# 1. Vérifier auto_fallback
cat ~/.opencode/runtime/config.json | jq '.runtime.auto_fallback'
# Doit être: true

# 2. Vérifier fallbacks configurés
python3 ~/.opencode/scripts/novahiz-config.py models

# 3. Ajouter fallbacks manquants
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter qwen/qwen3.5-flash-02-23 1
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter stepfun/step-3.5-flash 2
python3 ~/.opencode/scripts/novahiz-config.py set-model flash openrouter z-ai/glm-4.7-flash 3

# 4. Vérifier max_fallbacks
cat ~/.opencode/runtime/config.json | jq '.runtime.max_fallbacks'
# Doit être: 3
```

---

### 7. MCP HTTP Ne Répond Pas

**Symptômes:**
```bash
$ curl http://localhost:8765/health
# Connection refused
```

**Solutions:**

```bash
# 1. Vérifier processus
ps aux | grep novahiz-mcp-http | grep -v grep

# 2. Vérifier port
netstat -tlnp | grep 8765

# 3. Démarrer MCP
nohup python3 ~/.opencode/mcp/novahiz-mcp-http.py > ~/.opencode/logs/mcp-http.log 2>&1 &

# 4. Vérifier
sleep 2
curl http://localhost:8765/health

# 5. Logs
tail -20 ~/.opencode/logs/mcp-http.log
```

---

### 8. CLI Ne Fonctionne Pas

**Symptômes:**
```bash
$ nv config providers
# Command not found
```

**Solutions:**

```bash
# 1. Utiliser chemin complet
python3 ~/.opencode/scripts/novahiz-config.py providers

# 2. Vérifier .bashrc
grep "novahiz" ~/.bashrc

# 3. Ajouter alias
cat >> ~/.bashrc << 'EOF'
alias nv='python3 ~/.opencode/scripts/novahiz-cli.py'
alias nvc='python3 ~/.opencode/scripts/novahiz-config.py'
alias nvr='python3 ~/.opencode/runtime/novahiz-runtime.py'
EOF

# 4. Reload
source ~/.bashrc

# 5. Tester
nv config providers
```

---

## 🔧 OUTILS DE DIAGNOSTIC

### Script de Diagnostic Complet

```bash
#!/bin/bash
echo "═══════════════════════════════════════════════════════"
echo "  NOVAHIZ OS — DIAGNOSTIC"
echo "═══════════════════════════════════════════════════════"

echo ""
echo "1. Python version:"
python3 --version

echo ""
echo "2. Config file:"
ls -la ~/.opencode/runtime/config.json 2>/dev/null || echo "❌ Non trouvé"

echo ""
echo "3. Providers:"
python3 ~/.opencode/scripts/novahiz-config.py providers 2>/dev/null | grep -E "(OPENROUTER|OPENCODE)"

echo ""
echo "4. Daemon status:"
ps aux | grep novahiz-runtime | grep -v grep | wc -l | xargs -I {} echo "{} processus"

echo ""
echo "5. Executions:"
ls ~/.opencode/executions/*.json 2>/dev/null | wc -l | xargs -I {} echo "{} executions"

echo ""
echo "6. Logs récents:"
tail -5 ~/.opencode/logs/runtime.log 2>/dev/null

echo ""
echo "═══════════════════════════════════════════════════════"
```

**Usage:**
```bash
# Sauvegarder
cat > ~/novahiz-diagnostic.sh << 'EOF'
# ... script ci-dessus ...
EOF
chmod +x ~/novahiz-diagnostic.sh

# Exécuter
~/novahiz-diagnostic.sh
```

---

## 📞 SUPPORT

### Fichiers de Log

| Log | Emplacement | Usage |
|-----|-------------|-------|
| Runtime | `~/.opencode/logs/runtime.log` | Exécutions LLM |
| Daemon | `~/.opencode/logs/runtime-daemon.log` | Daemon activity |
| MCP | `~/.opencode/logs/mcp-http.log` | HTTP API |
| Config | `~/.opencode/logs/config.log` | Configuration changes |

### Commandes Utiles

```bash
# Voir tous les logs
find ~/.opencode/logs -name "*.log" -exec tail -10 {} \;

# Logs en temps réel
tail -f ~/.opencode/logs/*.log

# Chercher erreurs
grep -r "ERROR" ~/.opencode/logs/ | tail -20

# Count errors
grep -r "ERROR" ~/.opencode/logs/ | wc -l
```

---

## 📊 CHECKLIST DE DÉPANNAGE

- [ ] Python 3.10+ installé
- [ ] API keys configurées dans .bashrc
- [ ] Config file existe et valide
- [ ] Providers activés
- [ ] Daemon running
- [ ] Logs ne montrent pas d'erreurs critiques
- [ ] Executions sont processed
- [ ] MCP HTTP répond sur port 8765

---

**Documentation liée:**
- [README.md](README.md) — Documentation principale
- [CONFIGURATION.md](CONFIGURATION.md) — Configuration
- [CLI.md](CLI.md) — Commandes CLI
