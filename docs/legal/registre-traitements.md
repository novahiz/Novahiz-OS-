# Novahiz OS — Registre des Traitements (RGPD Art. 30)

**Version:** 1.0  
**Date:** 2026-05-27  
**Responsable:** Novahiz OS Team

---

## 1. Vue d'Ensemble

| Traitement | Finalité | Données | Base Légale |
|------------|----------|---------|-------------|
| Exécution de tâches | Fonctionnalité principale | Prompts, résultats | Contrat (Art. 6.1b) |
| Logs d'exécution | Debug, audit | Timestamps, errors | Intérêt légitime (Art. 6.1f) |
| Métriques d'usage | Analytics | Tier, tokens | Consentement (Art. 6.1a) |
| Backups | Recovery | Config, mémoire | Intérêt légitime (Art. 6.1f) |

---

## 2. Détails des Traitements

### 2.1 Exécution de Tâches

| Élément | Description |
|---------|-------------|
| **Finalité** | Exécuter des tâches via agents IA |
| **Catégories de données** | Prompts, réponses, métadonnées |
| **Personnes concernées** | Utilisateurs finaux |
| **Destinataires** | OpenRouter (API LLM) |
| **Transfert hors UE** | Oui (OpenRouter, SCC) |
| **Durée de conservation** | Durée de la session + 30 jours |
| **Base légale** | Exécution du contrat (Art. 6.1b) |

### 2.2 Logs d'Exécution

| Élément | Description |
|---------|-------------|
| **Finalité** | Débogage, audit de sécurité |
| **Catégories de données** | Timestamps, niveaux de log, messages |
| **Personnes concernées** | Utilisateurs, administrateurs |
| **Destinataires** | Aucun (local) |
| **Transfert hors UE** | Non |
| **Durée de conservation** | 30 jours (rotation automatique) |
| **Base légale** | Intérêt légitime (Art. 6.1f) |

### 2.3 Métriques d'Usage

| Élément | Description |
|---------|-------------|
| **Finalité** | Analytics, amélioration produit |
| **Catégories de données** | Tier modèle, tokens utilisés, timestamps |
| **Personnes concernées** | Utilisateurs |
| **Destinataires** | Aucun (local, opt-in) |
| **Transfert hors UE** | Non |
| **Durée de conservation** | 90 jours |
| **Base légale** | Consentement (Art. 6.1a) |

### 2.4 Backups

| Élément | Description |
|---------|-------------|
| **Finalité** | Reprise après incident |
| **Catégories de données** | Config, mémoire, constitution |
| **Personnes concernées** | Utilisateurs |
| **Destinataires** | Aucun (local) |
| **Transfert hors UE** | Non (sauf backup cloud configuré par utilisateur) |
| **Durée de conservation** | 7 jours (rotation) |
| **Base légale** | Intérêt légitime (Art. 6.1f) |

---

## 3. Mesures de Sécurité

| Traitement | Mesures Techniques | Mesures Organisationnelles |
|------------|-------------------|---------------------------|
| Exécution | TLS 1.3, chiffrement transit | Validation des prompts |
| Logs | Permissions 600, rotation | Accès restreint |
| Métriques | Anonymisation, agrégation | Opt-in par défaut |
| Backups | Chiffrement (optionnel), checksum | Rotation automatique |

---

## 4. Sous-Traitants

| Sous-Traitant | Rôle | Localisation | Garanties |
|---------------|------|--------------|-----------|
| OpenRouter | API LLM | États-Unis | SCC, Privacy Shield |
| GitHub | Hébergement code | États-Unis | SCC |
| Vercel (optionnel) | Déploiement | États-Unis | SCC |

---

## 5. Droits des Personnes

| Droit | Comment l'exercer | Délai de réponse |
|-------|-------------------|------------------|
| Accès (Art. 15) | `python3 rgpd_tools.py export` | 30 jours |
| Rectification (Art. 16) | Modification manuelle | 30 jours |
| Effacement (Art. 17) | `python3 rgpd_tools.py delete` | 30 jours |
| Portabilité (Art. 20) | Export JSON/ZIP | 30 jours |
| Opposition (Art. 21) | `config/privacy.json` | Immédiat |

---

## 6. Analyse d'Impact (DPIA)

**DPIA requise ?** ❌ Non

**Justification:**
- Traitement à faible risque
- Données non sensibles
- Local-first, minimal data collection
- Pas de surveillance systématique

---

## 7. Violations de Données

### Procédure de Notification

| Étape | Délai | Responsable |
|-------|-------|-------------|
| Détection | Immédiat | Équipe technique |
| Évaluation | 24h | DPO |
| Notification CNIL | 72h | DPO |
| Notification utilisateurs | Si risque élevé | DPO |

### Contact DPO

**Email:** dpo@novahiz-os.local  
**Adresse:** [À compléter]

---

## 8. Révisions

| Version | Date | Modification | Approuvé Par |
|---------|------|--------------|--------------|
| 1.0 | 2026-05-27 | Création initiale | Novahiz Team |

---

## 9. Annexes

- [Privacy Policy](./PRIVACY_POLICY.md)
- [Terms of Service](./TERMS_OF_SERVICE.md)
- [RGPD Tools](../scripts/rgpd_tools.py)
- [Config Consentement](../config/privacy.json)

---

*Document conforme au RGPD (UE) 2016/679*
