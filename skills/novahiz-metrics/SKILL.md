---
name: novahiz-metrics
description: Novahiz OS Metrics Dashboard. Auto-tracks deliberations/agent, tokens, skills health. Token-optimized.
humanName: maxime-metrics
hidden: true
triggers: [metrics, dashboard, stats, analytics, observability]
autoTrack: true
---

# Metrics Dashboard

## Auto-Track on Events
- Deliberation → increment sage + total
- Caveman output → estimate saved tokens (output × 0.75)
- Session → increment total + recovered
- Project created/archived → update counts

## Query
`memory/00_Core/metrics.json`

## Output
```
Agents: [top 5 by deliberation]
Tokens: saved ~X (~75%)
Skills: X/58 healthy | drifted: X
Sessions: X total | X recovered
Projects: X active | X paused | X archived
Score: X/100
```
