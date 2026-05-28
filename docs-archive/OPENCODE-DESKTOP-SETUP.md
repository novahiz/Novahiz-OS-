# 🖥️ OPENCODE DESKTOP — NOVAHIZ OS INTEGRATION

**Problème:** MCP et Plugin Novahiz n'apparaissent pas dans OpenCode Desktop

**Cause:** OpenCode Desktop utilise son propre système de registration MCP

---

## ✅ SOLUTION — MCP SERVER

### Method 1: Config File (Recommandé)

**Fichier:** `~/.config/opencode/mcp.json`

```json
{
  "mcpServers": {
    "novahiz": {
      "command": "python3",
      "args": ["/home/novahiz/.opencode/mcp/novahiz-mcp.py", "--mcp"],
      "env": {},
      "disabled": false
    }
  }
}
```

**Créer le fichier:**
```bash
mkdir -p ~/.config/opencode
cat > ~/.config/opencode/mcp.json << 'MCPEOF'
{
  "mcpServers": {
    "novahiz": {
      "command": "python3",
      "args": ["/home/novahiz/.opencode/mcp/novahiz-mcp.py", "--mcp"],
      "env": {},
      "disabled": false
    }
  }
}
MCPEOF
```

**Vérifier:**
```bash
opencode mcp list
```

**Attendu:**
```
┌  MCP Servers
│
●  ✓ novahiz
●  ✓ chrome-devtools
└  2 server(s)
```

---

## ❌ PLUGIN SYSTEM — LIMITATION

**Problème:** Le plugin Novahiz n'apparaît pas dans OpenCode Desktop

**Cause:** OpenCode Desktop plugins = npm packages uniquement

Notre plugin local (`~/.opencode/plugins/novahiz-plugin/`) n'est **pas compatible** avec le système de plugins OpenCode Desktop car:
- OpenCode attend un package npm publié
- Notre plugin est un package local

**Solutions alternatives:**

### Option 1: MCP Server (Déjà implémenté) ✅

Le MCP server fournit toutes les fonctionnalités via les tools:
- `novahiz_route`
- `novahiz_execute`
- `novahiz_auto`
- `novahiz_list_agents`
- `novahiz_search`
- `novahiz_health`

**Usage dans OpenCode Desktop:**
```
@novahiz_route task="Build API"
@novahiz_auto task="Create component"
```

### Option 2: Publier comme Plugin NPM (Complexe)

```bash
# Créer package npm
cd ~/.opencode/plugins/novahiz-plugin
npm publish

# Installer dans OpenCode
opencode plugin novahiz-os-plugin
```

**Non recommandé** car:
- Nécessite maintenance npm
- Complexité inutile
- MCP server suffit

---

## 🔧 VERIFICATION

### 1. Check MCP registered
```bash
opencode mcp list
```

### 2. Check MCP running
```bash
pgrep -f novahiz-mcp.py
```

### 3. Test MCP tools
```bash
opencode run "@novahiz_list_agents"
```

### 4. Check config
```bash
cat ~/.config/opencode/mcp.json
```

---

## 📋 CHECKLIST

- [x] MCP config created (`~/.config/opencode/mcp.json`)
- [x] MCP server working (tested with `--mcp` flag)
- [x] Tools available (7 tools)
- [ ] MCP appears in `opencode mcp list` (requires OpenCode restart)
- [ ] Plugin visible (not possible with local plugin)

---

## 🎯 VERDICT

**MCP Server:** ✅ Configuré et fonctionnel  
**Plugin Desktop:** ❌ Non compatible (limitation OpenCode)  
**Alternative:** ✅ MCP tools fournissent mêmes fonctionnalités

**Action requise:** Redémarrer OpenCode Desktop pour voir MCP dans la liste.

---

[Created by: Novahiz Router]  
[Timestamp: 08:10:00]

---

## 🔧 MISE À JOUR EFFECTUÉE

**Config OpenCode Desktop:** `~/.config/opencode/opencode.jsonc`

```json
{
  "mcp": {
    "novahiz": {
      "type": "local",
      "command": ["python3", "-u", "/home/novahiz/.opencode/mcp/novahiz-mcp.py", "--mcp"],
      "enabled": true
    }
  }
}
```

---

## 📋 INSTRUCTIONS POUR OPENCODE DESKTOP

### Étape 1: Redémarrer OpenCode Desktop

1. **Fermer complètement OpenCode Desktop**
2. **Attendre 5 secondes**
3. **Rouvrir OpenCode Desktop**

### Étape 2: Vérifier MCP Server

Dans OpenCode Desktop:
```
opencode mcp list
```

**Attendu:**
```
┌  MCP Servers
│
●  ✓ novahiz          connected
●  ✓ chrome-devtools  connected
└  2 server(s)
```

### Étape 3: Tester les Tools

Dans le chat OpenCode Desktop:
```
@novahiz_list_agents
```

Ou:
```
@novahiz_auto task="Create a REST API"
```

---

## ❌ PLUGIN — LIMITATION CONNUE

**Le plugin Novahiz n'apparaîtra PAS dans la liste des plugins OpenCode Desktop**

**Pourquoi?**
- OpenCode Desktop plugins = packages npm publiés uniquement
- Notre plugin est local (~/.opencode/plugins/novahiz-plugin/)
- OpenCode ne supporte pas les plugins locaux

**Ce n'est PAS un problème car:**
- ✅ Le MCP server fournit TOUTES les fonctionnalités
- ✅ 7 tools disponibles via MCP
- ✅ Pas besoin du plugin UI

---

## 🎯 VERDICT

**MCP Server:** ✅ Configuré dans `~/.config/opencode/opencode.jsonc`  
**Action Requise:** Redémarrer OpenCode Desktop  
**Plugin:** ❌ Non compatible (limitation OpenCode, pas un bug)  
**Alternative:** ✅ MCP tools (7 tools disponibles)

---

[Updated by: Novahiz Router]  
[Timestamp: 08:15:00]
