---
name: novahiz-agents
description: Novahiz 21-Agent Registry. Maps each humanized agent (Elias, Kenzo, Luna, Sarah, etc.) to their OpenCode skill equivalents. Use when the user asks "agents", "agent roster", "who is X", "agent registry", "elite force", "council members", "list agents". Contains 11 Council Sages + 10 Elite Force specialists.
humanName: nora-agents
hidden: true
triggers: [agents, roster, registry, council, elite-force, list-agents, who-is]
---

# Novahiz Agent Registry — 21 Experts

## THE COUNCIL (11 Sages)

| Name | Role | OpenCode Skill | Domain |
|------|------|---------------|--------|
| **Elias** | Growth Architect | content-strategy, launch-strategy | growth, gtm, launch |
| **Kenzo** | Optimizer | vercel-react-best-practices | performance, latency |
| **Malik** | Supabase Expert | systematic-debugging, tdd | backend, db |
| **Luna** | UI/UX Pro Max | ui-ux-pro-max, frontend-design | design, ui, ux |
| **Sarah** | Auditor | requesting-code-review, seo-audit | quality, bugs |
| **Arthur** | Senior Architect | improve-codebase-architecture | architecture |
| **Ralph** | Lead Executor | brainstorming, executing-plans | execution |
| **Victor** | The Architect | writing-plans, to-prd | strategy, planning |
| **Atlas** | Fragmentation Specialist | *internal only* | memory, ntm |
| **Cyrus** | Loop Architect | tdd | loops, adversarial |
| **Caveman** | Token Compression | caveman | token-efficiency |

## THE ELITE FORCE (10 Specialists)

| Name | Role | OpenCode Skill | Domain |
|------|------|---------------|--------|
| **Neo** | Penetration Tester | agent-browser, webapp-testing | security, pentest |
| **Iris** | Security Auditor | webapp-testing, requesting-code-review | security, compliance |
| **Sophia** | Compliance Auditor | requesting-code-review, seo-audit | compliance, gov |
| **Hugo** | Mobile Developer Pro | frontend-design, ui-ux-pro-max | mobile, react-native |
| **Zane** | Microservices Architect | improve-codebase-architecture | microservices |
| **Dante** | Postgres Pro | systematic-debugging, tdd | postgres, sql |
| **Blaise** | Docker Expert | github-actions-docs, webapp-testing | docker, k8s |
| **Storm** | Chaos Engineer | webapp-testing, systematic-debugging | chaos, resilience |
| **Maya** | Data Engineer | xlsx, pdf, content-strategy | data, etl |
| **Alan** | MLOps Engineer | content-strategy, copywriting | mlops, ml |

## Activation Protocol
Use `novahiz-selection` to route tasks to the optimal agent. Select 1-3 based on domain match. **Never activate all 21 for a single task.**

## Efficiency Targets
- Council Sages: 95.0 minimum
- Elite Force: 90.0 minimum
- Caveman: 75% compression without accuracy loss

## Memory Boundaries
- Council: `memory/01_Agents/[name]/`
- Elite Force: `memory/01_Agents/[name]/`
- Novahiz internal: `memory/00_Core/`
