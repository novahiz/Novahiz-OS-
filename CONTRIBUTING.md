# Novahiz OS — Guide de Contribution

**Version:** 1.0  
**Date:** 2026-05-27

---

## 1. Comment Contribuer

### 1.1 Types de Contributions

| Type | Description | Processus |
|------|-------------|-----------|
| 🐛 Bug Report | Signaler un bug | GitHub Issues |
| 💡 Feature Request | Proposer une fonctionnalité | GitHub Issues + Discussion |
| 🔧 Code Fix | Corriger un bug | Pull Request |
| 📚 Documentation | Améliorer docs | Pull Request |
| 🧪 Tests | Ajouter tests | Pull Request |

### 1.2 Prérequis

- ✅ Avoir lu ce guide
- ✅ Fork du projet
- ✅ Branch dédiée (`feature/ma-fonctionnalite`)
- ✅ Tests passants

---

## 2. Licence et Droits d'Auteur

### 2.1 Licence du Projet

Novahiz OS est sous licence **MIT**.

**En contribuant, vous acceptez que :**
- Votre code soit distribué sous licence MIT
- Vos contributions soient utilisées commercialement
- Vos contributions soient modifiées par d'autres

### 2.2 Contributor License Agreement (CLA)

**Par défaut, en soumettant une PR, vous acceptez le CLA implicite suivant :**

```
CLA IMPLICITE NOVAHIZ OS
========================

Je certifie :
1. Être titulaire des droits sur ma contribution
2. Autoriser la distribution sous licence MIT
3. Que ma contribution ne viole pas de droits tiers
4. Avoir le droit de soumettre cette contribution

Signature : [Votre nom d'utilisateur GitHub]
Date : [Date de la PR]
```

### 2.3 Attribution

Les contributeurs seront crédités dans :
- `CONTRIBUTORS.md` (liste des contributeurs)
- Git history (commits)
- Release notes (contributions majeures)

---

## 3. Standards de Code

### 3.1 Python

```python
# Style: PEP 8
# Format: black
# Lint: flake8

def ma_fonction(param: str) -> bool:
    """
    Description courte.

    Args:
        param: Description du paramètre

    Returns:
        Description de la valeur de retour
    """
    return True
```

### 3.2 JavaScript/TypeScript

```typescript
// Style: StandardJS
// Format: Prettier

/**
 * Description courte.
 * @param param - Description
 * @returns Description
 */
export function maFonction(param: string): boolean {
  return true;
}
```

### 3.3 Commits Git

```
format: <type>(scope): <description>

types: feat, fix, docs, style, refactor, test, chore

examples:
  feat(runtime): add rate limiting
  fix(mcp): resolve connection timeout
  docs(legal): add privacy policy
```

---

## 4. Processus de Review

### 4.1 Checklist PR

Avant de soumettre :

- [ ] Code formaté (black/pret tier)
- [ ] Tests ajoutés/mis à jour
- [ ] Documentation mise à jour
- [ ] Pas de secrets/credentials
- [ ] Commit messages clairs
- [ ] Branch à jour avec main

### 4.2 Critères d'Acceptation

| Critère | Requis |
|---------|--------|
| Tests passants | ✅ Obligatoire |
| Code review | ✅ 1 approbation min. |
| Documentation | ✅ Si feature/fix |
| Performance | ⚠️ Si impact significatif |
| Sécurité | ✅ Scan secrets OK |

### 4.3 Timeline

| Étape | Délai typique |
|-------|---------------|
| Review initiale | 2-5 jours |
| Feedback → Fix | 1-3 jours |
| Merge | 1 jour après approbation |

---

## 5. Code de Conduite

### 5.1 Engagement

Nous nous engageons à maintenir un environnement **ouvert, inclusif et respectueux**.

### 5.2 Comportements Attendus

- ✅ Empathie et respect
- ✅ Critique constructive
- ✅ Reconnaissance des erreurs
- ✅ Focus sur le meilleur pour la communauté

### 5.3 Comportements Inacceptables

- ❌ Harcèlement, discrimination
- ❌ Attaques personnelles
- ❌ Trolling, commentaires déplacés
- ❌ Promotion de contenu illégal

### 5.4 Signalement

**Contact:** conduct@novahiz-os.local  
**Réponse:** Sous 7 jours

---

## 6. Questions Fréquentes

### Q: Puis-je contribuer sans signer de CLA explicite ?

**R:** Oui. Le CLA implicite (section 2.2) s'applique automatiquement.

### Q: Comment suis-je crédité ?

**R:** Votre nom GitHub apparaît dans `CONTRIBUTORS.md` et l'historique Git.

### Q: Puis-je retirer ma contribution ?

**R:** Non. Une fois merge, votre contribution est distribuée sous MIT (irrévocable).

### Q: Code commercial autorisé ?

**R:** Oui. Novahiz OS peut être utilisé commercialement (licence MIT).

---

## 7. Outils de Développement

### Setup

```bash
# Fork et clone
git clone https://github.com/VOTRE_USER/novahiz-os.git
cd novahiz-os

# Installer dépendances
pip install -r requirements.txt 2>/dev/null || true
npm install 2>/dev/null || true

# Setup pre-commit hooks
./setup-cicd.sh
```

### Tests

```bash
# Run tests
cd tests && python3 -m pytest test_novahiz.py -v

# Lint
flake8 runtime/ mcp/
black --check runtime/ mcp/
```

---

## 8. Reconnaissance

**Contributeurs Notables :**

| Contributeur | Contributions |
|--------------|---------------|
| [À compléter] | [À compléter] |

**Rejoignez la liste !** 🚀

---

## 9. Contact

- **Issues:** [GitHub Issues](https://github.com/novahiz-os/novahiz-os/issues)
- **Discussions:** [GitHub Discussions](https://github.com/novahiz-os/novahiz-os/discussions)
- **Email:** contribute@novahiz-os.local

---

*En contribuant à Novahiz OS, vous acceptez ces termes.*
