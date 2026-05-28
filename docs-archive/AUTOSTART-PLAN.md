# 🚀 NOVAHIZ OS — AUTO-START WITH OPENCODE

**Objectif:** Démarrage automatique de tous les services Novahiz quand OpenCode démarre

---

## 📁 ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│  OPENCODE DÉMARRAGE (terminal ou desktop)                   │
│         ↓                                                    │
│  1. ~/.opencode/scripts/novahiz-autostart.sh               │
│         ↓                                                    │
│  2. Vérifie si services déjà running                        │
│         ↓                                                    │
│  3. Démarre tous les services:                              │
│     - novahiz-runtime daemon (LLM executor)                 │
│     - opencode-bridge daemon (MCP execution)                │
│     - novahiz-mcp HTTP server (port 8765)                   │
│         ↓                                                    │
│  4. Écrit PID files dans ~/.opencode/pids/                  │
│         ↓                                                    │
│  5. Log dans ~/.opencode/logs/autostart.log                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 COMPOSANTS À CRÉER

### 1. Script Auto-Start (`novahiz-autostart.sh`)
- Vérifie si services déjà running
- Démarre tous les daemons
- Gère les PID files
- Logs détaillés

### 2. Script Stop (`novahiz-stop.sh`)
- Arrête proprement tous les services
- Nettoie les PID files

### 3. Script Status (`novahiz-status-all.sh`)
- Affiche status de tous les services
- Vérifie santé des daemons

### 4. OpenCode Config (`opencode.json`)
- MCP Novahiz configuré
- Plugins Novahiz activés
- Auto-start hook

### 5. Desktop Integration
- MCP server pour OpenCode Desktop
- Plugin manifest pour UI

---

## 📋 CHECKLIST IMPLÉMENTATION

- [ ] Créer `novahiz-autostart.sh`
- [ ] Créer `novahiz-stop.sh`
- [ ] Créer `novahiz-status-all.sh`
- [ ] Créer PID directory
- [ ] Update `~/.bashrc` avec auto-start hook
- [ ] Configurer `opencode.json` pour MCP
- [ ] Créer plugin manifest pour Desktop
- [ ] Tester démarrage automatique
- [ ] Tester arrêt propre
- [ ] Documentation

---

## 🎯 RÉSULTAT ATTENDU

```bash
# Quand utilisateur lance:
opencode

# Automatiquement:
✅ novahiz-runtime daemon
✅ opencode-bridge daemon
✅ novahiz-mcp HTTP
✅ MCP registered in OpenCode
✅ Plugins disponibles dans Desktop
```

---

[Executed by: Novahiz Router]
[Agent: novahiz-router]
[Timestamp: 02:15:00]
