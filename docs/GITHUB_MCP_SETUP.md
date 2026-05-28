# 🐙 GitHub MCP Server — Configuration Guide

**Status:** ⚠️ Token compromis — DOIT ÊTRE RÉVOQUÉ

---

## ⚠️ URGENT: SÉCURITÉ

### Token Exposé: `github_personal_access_token_here`

**Ce token est COMPROMIS** car il a été partagé en clair.

**ACTION REQUISE:**
1. https://github.com/settings/tokens
2. Révoquer ce token IMMÉDIATEMENT
3. Créer un NOUVEAU token
4. Utiliser le nouveau token

---

## 📦 INSTALLATION

### Option 1: Script Automatique (RECOMMANDÉ)

```bash
cd /home/novahiz/.opencode
./scripts/setup-github-mcp.sh
```

### Option 2: Manuel

#### 1. Installer le serveur GitHub MCP

```bash
# Via npx (pas d'installation permanente)
npx -y @modelcontextprotocol/server-github
```

#### 2. Configurer opencode.json

```json
{
  "mcp": {
    "github": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      },
      "enabled": true
    }
  }
}
```

#### 3. Set Environment Variable

```bash
# Add to ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="votre_nouveau_token"

# Or temporary for current session
export GITHUB_TOKEN="votre_nouveau_token"
```

#### 4. Restart Opencode

```bash
# Quit opencode and restart
```

---

## 🔐 TOKEN SCOPES REQUIS

| Scope | Pourquoi |
|-------|----------|
| `repo` | Full control des repositories |
| `workflow` | Update GitHub Actions |
| `read:user` | Lire infos utilisateur |
| `user:email` | Lire emails (optionnel) |

---

## 🛠️ COMMANDES GITHUB MCP

Une fois configuré, ces commandes seront disponibles:

| Commande | Description |
|----------|-------------|
| `github.list_repos` | Lister repositories |
| `github.create_repo` | Créer repository |
| `github.get_file` | Lire fichier |
| `github.create_file` | Créer fichier |
| `github.update_file` | Modifier fichier |
| `github.delete_file` | Supprimer fichier |
| `github.list_issues` | Lister issues |
| `github.create_issue` | Créer issue |
| `github.list_pulls` | Lister PRs |
| `github.create_pull` | Créer PR |
| `github.search_repos` | Rechercher repos |
| `github.get_branch` | Infos branche |

---

## ✅ VÉRIFICATION

```bash
# Check MCP servers running
# (depends on opencode implementation)

# Test GitHub API
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/user
```

---

## 🔄 SYNCHRONISATION REPO

### Push vers GitHub

```bash
cd /home/novahiz/.opencode

# Initialize
git init
git config user.email "votre@email.com"
git config user.name "Votre Nom"

# Add remote
git remote add origin https://github.com/VOTRE_USER/novahiz-os.git

# Commit
git add .
git commit -m "v6.0 Production Ready"

# Push
git branch -M main
git push -u origin main
```

### Script de Sync

```bash
export GITHUB_USER="votre_username"
export GITHUB_TOKEN="votre_token"

./scripts/sync-github.sh
```

---

## 🆘 TROUBLESHOOTING

### MCP ne se lance pas

```bash
# Check npx
which npx

# Check token
echo $GITHUB_TOKEN

# Test GitHub API
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/user
```

### Permission denied

```bash
# Verify token scopes
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/user/repos
```

### Token expiré

```bash
# Revoke old: https://github.com/settings/tokens
# Create new token
# Update env var
export GITHUB_TOKEN="nouveau_token"
```

---

## 📚 RESSOURCES

- **GitHub MCP Server:** https://github.com/github/github-mcp-server
- **MCP Protocol:** https://modelcontextprotocol.io
- **GitHub API Docs:** https://docs.github.com/en/rest
- **Token Security:** https://docs.github.com/en/authentication

---

## ✅ CHECKLIST

- [ ] Ancien token révoqué
- [ ] Nouveau token créé
- [ ] Scopes corrects (repo, workflow)
- [ ] GITHUB_TOKEN dans ~/.bashrc
- [ ] opencode.json configuré
- [ ] GitHub MCP activé
- [ ] Test API réussi
- [ ] Premier push réussi

---

**Support:** novahiz-os@local  
**Dernière MAJ:** 2026-05-27
