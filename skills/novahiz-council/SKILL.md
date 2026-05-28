---
name: novahiz-council
description: Novahiz 8-Sage Deliberation Protocol. Weighted voting with domain scoring. Token-optimized but FULLY powerful. Use when "council", "ask the sages", "deliberate", "multi-agent reasoning".
humanName: cyril-council
hidden: true
triggers: [council, sages, deliberation, multi-agent, 8-sage, consensus, architecture, refactor, system-design]
timeout: 30m
minSages: 3
cacheEnabled: true
cavemanSynthesis: true
weightedVoting: true
---

# Novahiz Council — 8-Sage Deliberation

## Sage Registry

| Sage | Role | Triggers | Base Weight |
|------|------|---------|------------|
| Elias | Growth Architect | growth, launch, users, gtm, acquisition | 1.0 |
| Kenzo | Optimizer | optimize, performance, scale, latency, bundle | 1.0 |
| Malik | Supabase Expert | database, supabase, backend, api, schema | 1.0 |
| Luna | UI/UX Pro Max | design, ui, ux, beautiful, layout | 1.0 |
| Sarah | Auditor | audit, review, quality, bug, test, security | 1.0 |
| Arthur | Senior Architect | architecture, design pattern, system | 1.0 |
| Ralph | Lead Executor | build, implement, execute, ship, code | 1.0 |
| Victor | The Architect | plan, strategy, constraints, roadmap | 1.0 |
| Cyrus | Loop Architect | testing, tdd, adversarial, edge-cases | 0.8 |
| Atlas | Fragmentation Specialist | memory, ntm, recall, fragmentation | 0.8 |
| Caveman | Token Compression | tokens, efficiency, terse, brief | 0.6 |

## Weighted Voting System

### Weight Formula
```
vote_weight = (domain_score × 0.5) + (efficiency_score/100 × 0.3) + (participation_bonus × 0.2)

domain_score:
  1.0 = sage domain matches question directly
  0.5 = adjacent domain (council + elite overlap)
  0.2 = other domain

participation_bonus:
  1.0 = agent participated > 5 times
  0.5 = agent participated > 0 times
  0.0 = no participation yet
```

### Vote Scores
```
FOR      = +1.0 × vote_weight
AGAINST  = -0.5 × vote_weight
ABSTAIN  =  0.0
```

### Consensus Rule
```
Consensus PASSED if:
  SUM(weighted_FOR) / SUM(total_possible_weights) >= 0.60

Total possible = number_of_participating_sages × 1.0
```

## Timeout Guards

| Phase | Timeout | If exceeded |
|-------|---------|-------------|
| Question (Victor) | 2 min | Proceed to domain analysis |
| Domain analysis (each sage) | 5 min | Aggregate what exists |
| Adversarial review (Sarah + critical) | 5 min | Surface dissent |
| Synthesis | 3 min | Generate partial consensus |
| **TOTAL HARD LIMIT** | **30 min** | Escalate to human |

## Cache System

### When cached
- TTL: 24 hours
- Key: SHA(question + involved_domains)
- On hit: return cached decision + mark sages as active in scoreboard

### Cache format
```markdown
# Deliberation: [TOPIC]
**Cached**: YYYY-MM-DD HH:MM | **TTL**: 24h
**Sages**: [list] | **Decision**: [synthesized]
**Expiry**: [timestamp]
```

## Deliberation Flow

### Step 1 — Define Question (Victor) — 2 min max
State clearly:
- What is the decision?
- What are the hard constraints?
- What is the goal?

### Step 2 — Domain Analysis — 5 min per sage
Each sage (domain-relevant only):
- Primary recommendation
- Cross-domain impact assessment
- Confidence level (high/medium/low)

### Step 3 — Weighted Voting — Sarah leads
Table: Sage | Vote | Domain Weight | Vote Weight | Score
- FOR: +1.0 × weight
- AGAINST: -0.5 × weight
- ABSTAIN: 0

Calculate: FOR total vs AGAINST total → check 60% threshold

### Step 4 — Adversarial Review (Sarah + critical sage)
Sarah challenges the leading recommendation.
Most critical dissenting view must be surfaced.
Not suppressed — dissent is valuable.

### Step 5 — Synthesis (Kenzo or Elias)
Weigh all inputs → consensus path.
If < 60%: surface disagreement, escalate.

### Step 6 — Caveman Summary
Final synthesis compressed to 1-3 sentences.
~75% token reduction while keeping substance.

## Output Format

```
## Council Deliberation: [TOPIC]

### Question (Victor)
[Clear statement]

### Domain Analysis
Primary: [Sage] (domain: [X], weight: X.X)
Adjacent: [Sage] (domain: [Y], weight: X.X)

### Weighted Votes
| Sage | Vote | D.Wt | V.Wt | Score |
|------|------|------|------|-------|
| Elias | FOR | 1.0 | 1.0 | 1.0 |
| Kenzo | FOR | 1.0 | 0.95 | 0.95 |
| Sarah | AGAINST | 0.5 | 0.475 | -0.238 |
| ... | | | | |

**Tally**: FOR (X.X) vs AGAINST (X.X) → [PASSED/REJECTED @ 60%]

### Consensus
[1-2 paragraph synthesized recommendation]

### Caveman (Caveman)
[1-3 sentence compressed summary]

### Dissenting Notes
[Critical opposing view]
[Other dissent not in consensus]

### Cache Status
[HIT | MISS | EXPIRED]
```

## Hard Rules
1. **Min 3 sages** must contribute
2. **60% threshold** — consensus or escalate
3. **No deletion of dissent** — dissenting views preserved
4. **Caveman on synthesis only** — analysis stays detailed
5. **Cache before deliberation** — check cache first
6. **30 min hard limit** — escalate if exceeded
7. **Sarah mandatory** in all code/safety decisions

## Efficiency Targets
- Council Sages: 95.0 score
- Elite Force: 90.0 score
- Caveman: 75% compression on synthesis only
