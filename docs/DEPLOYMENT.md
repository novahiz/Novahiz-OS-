# 🚀 Novahiz OS — GitHub Deployment Guide

**Version:** 6.0  
**Status:** Production Ready

---

## ⚠️ SÉCURITÉ D'ABORD

### Token GitHub

**JAMAIS:**
- ❌ Committer un token
- ❌ Partager en clair
- ❌ Utiliser dans des scripts versionnés

**TOUJOURS:**
- ✅ Variables d'environnement
- ✅ GitHub Secrets pour CI/CD
- ✅ Révoquer tokens exposés

---

## 📋 PRÉREQUIS

### 1. Révoquer l'ancien token

1. Allez sur: https://github.com/settings/tokens
2. Trouvez `github_personal_access_token_here`
3. Cliquez "Revoke"

### 2. Créer un nouveau token

1. https://github.com/settings/tokens/new
2. Scopes requis:
   - `repo` (Full control of private repositories)
   - `workflow` (Update GitHub Action workflows)
3. Copiez le token
4. **Ne le partagez jamais**

### 3. Configurer l'environnement

```bash
# Add to ~/.bashrc or ~/.zshrc
export GITHUB_USER="votre_username"
export GITHUB_TOKEN="votre_nouveau_token"
export REPO_NAME="novahiz-os"
```

---

## 🔄 SYNCHRONISATION MANUELLE

### Option 1: Script Automatisé (RECOMMANDÉ)

```bash
# Set environment variables
export GITHUB_USER="votre_username"
export GITHUB_TOKEN="votre_token"

# Run sync script
cd /home/novahiz/.opencode
./scripts/sync-github.sh
```

### Option 2: Commandes Manuelles

```bash
cd /home/novahiz/.opencode

# Initialize git
git init

# Configure
git config user.email "votre@email.com"
git config user.name "Votre Nom"

# Add remote (replace with your repo)
git remote add origin https://github.com/VOTRE_USER/novahiz-os.git

# Add files
git add .

# Commit
git commit -m "v6.0 Production Ready"

# Push
git branch -M main
git push -u origin main
```

---

## 📁 STRUCTURE À COMMITTER

### ✅ Fichiers à Committer

```
novahiz-os/
├── runtime/              ✅ Code principal
├── mcp/                  ✅ MCP servers
├── scripts/              ✅ Scripts utilitaires
├── tests/                ✅ Tests unitaires
├── docs/                 ✅ Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── legal/
│   └── compliance/
├── .github/
│   └── workflows/        ✅ CI/CD
├── memory/               ✅ Structure (sans données sensibles)
├── .gitignore            ✅
├── README.md             ✅
└── CONTRIBUTING.md       ✅
```

### ❌ Fichiers à EXCLURE

```
├── runtime/config.json   ❌ Contient API keys
├── logs/                 ❌ Logs sensibles
├── executions/           ❌ Données temporaires
├── backups/              ❌ Backups
├── chrome-profile-mcp/   ❌ Profil Chrome
└── .env                  ❌ Secrets
```

---

## 🔧 CONFIGURATION DU REPO GITHUB

### 1. Créer le Repository

```
https://github.com/new
Nom: novahiz-os
Visibilité: Public ou Privé (selon choix)
Initialiser: NON (on push le code existant)
```

### 2. Activer GitHub Actions

1. Settings → Actions
2. "Allow all actions"
3. Save

### 3. Configurer les Secrets

Settings → Secrets and variables → Actions → New repository secret:

| Nom | Valeur |
|-----|--------|
| `OPENROUTER_API_KEY` | Votre clé OpenRouter |
| `GITHUB_TOKEN` | Auto-généré par GitHub |

---

## 📊 WORKFLOWS GITHUB ACTIONS

### CI/CD déjà configuré

Fichier: `.github/workflows/ci.yml`

**Triggers:**
- Push sur `main`, `master`, `dev`
- Pull requests

**Jobs:**
- ✅ Tests
- ✅ SAST (Semgrep)
- ✅ Secret scanning (GitLeaks)
- ✅ License audit
- ✅ Code quality (flake8, black)

---

## 🎯 POST-DÉPLOIEMENT

### Vérifier le déploiement

```bash
# View repo
https://github.com/VOTRE_USER/novahiz-os

# Check Actions tab
https://github.com/VOTRE_USER/novahiz-os/actions

# Check CI status
# Should show green checkmarks
```

### Branch Protection (RECOMMANDÉ)

Settings → Branches → Add branch protection rule:

- Branch name pattern: `main`
- ✅ Require pull request reviews
- ✅ Require status checks to pass
- ✅ Require branches to be up to date

---

## 🔄 WORKFLOW DE DÉVELOPPEMENT

### Quotidien

```bash
# Pull latest changes
git pull origin main

# Make changes
# ... edit files ...

# Test locally
python3 tests/test_novahiz_core.py

# Commit
git add .
git commit -m "feat: description"
git push
```

### Releases

```bash
# Create tag
git tag -a v6.0 -m "Production Ready"
git push origin v6.0

# Create GitHub Release
# https://github.com/VOTRE_USER/novahiz-os/releases/new
```

---

## 📈 MONITORING

### Dashboard GitHub

- **Traffic:** Insights → Traffic
- **Clones:** Voir nombre de clones
- **Views:** Voir visites

### Issues & Projects

- Utiliser GitHub Issues pour TODOs
- GitHub Projects pour tracking

---

## 🆘 TROUBLESHOOTING

### Push rejected

```bash
# Force push (if you're sure)
git push -u origin main --force

# Or pull first
git pull --rebase
git push
```

### Token expired

```bash
# Revoke old token
# Create new one
export GITHUB_TOKEN="nouveau_token"
```

### Large files

```bash
# Remove large files from git history
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch PATH_TO_FILE' \
  --prune-empty --tag-name-filter cat -- --all
```

---

## ✅ CHECKLIST FINALE

- [ ] Ancien token révoqué
- [ ] Nouveau token créé
- [ ] Variables d'environnement configurées
- [ ] Repository GitHub créé
- [ ] Script sync-github.sh exécuté
- [ ] CI/CD activé
- [ ] Secrets configurés
- [ ] Branch protection activée
- [ ] README à jour
- [ ] Premier déploiement réussi

---

**Support:** novahiz-os@local  
**Documentation:** docs/  
**License:** MIT
