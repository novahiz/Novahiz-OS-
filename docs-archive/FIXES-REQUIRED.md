# 🔧 NOVAHIZ OS v5.2 — FIXES REQUIS

**Date:** 2026-05-27  
**Audit:** Honnête et complet  
**Status:** 4 problèmes critiques identifiés

---

## ❌ PROBLÈMES IDENTIFIÉS

| # | Problème | Impact | Priorité |
|---|----------|--------|----------|
| 1 | MCP ≠ Runtime (systèmes séparés) | Résultats incomplets | 🔴 Critique |
| 2 | Smart tier = provider désactivé | Fallback automatique (perte temps) | 🟠 Moyen |
| 3 | `nv status` commande manquante | UX dégradée | 🟡 Faible |
| 4 | Résultats exécution inconsistants | Tracking impossible | 🟠 Moyen |

---

## 🔧 SOLUTIONS

### FIX #1: MCP → Runtime Integration

**Problème:** MCP crée fichiers mais n'utilise pas runtime pour exécution LLM

**Solution:** Modifier `novahiz-mcp.py` pour appeler runtime directement

**Fichier:** `~/.opencode/mcp/novahiz-mcp.py`

**Action:** Ajouter fonction `execute_with_runtime()` qui:
1. Crée fichier d'exécution
2. Appelle runtime pour traitement immédiat
3. Récupère résultat complet (provider, model, tokens)

---

### FIX #2: Smart Tier → OpenRouter

**Problème:** Smart tier utilise opencode-zen (désactivé) → always fallback

**Solution:** Changer default smart tier vers openrouter

**Fichier:** `~/.opencode/runtime/config.json`

**Action:** 
```json
"smart": {
  "default": {"provider": "openrouter", "model": "qwen/qwen3.6-flash"},
  "fallbacks": [...]
}
```

---

### FIX #3: nv status Command

**Problème:** `nv status` returns "Unknown command"

**Solution:** Add status command to nv script

**Fichier:** `~/.opencode/bin/novahiz`

**Action:** Add case:
```bash
status|s)
    python3 "$RUNTIME_DIR/novahiz-runtime.py" status
    ;;
```

---

### FIX #4: Consistent Results Tracking

**Problème:** Some executions have provider/model, others don't

**Solution:** Ensure runtime always writes complete results

**Fichier:** `~/.opencode/runtime/novahiz-runtime.py`

**Action:** Verify `process_execution()` always writes full result dict

---

## 📋 CHECKLIST

- [ ] Fix #1: MCP → Runtime integration
- [ ] Fix #2: Smart tier provider change
- [ ] Fix #3: nv status command
- [ ] Fix #4: Result consistency check
- [ ] Test all fixes end-to-end
- [ ] Update documentation

---

[Executed by: Novahiz Router]
[Agent: novahiz-router]
[Timestamp: 01:25:00]
