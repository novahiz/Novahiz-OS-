---
name: novahiz-council
description: Novahiz 8-Sage Deliberation Protocol. Use when a complex decision requires multi-perspective analysis, or when the user invokes "council", "ask the sages", "deliberate", or "multi-agent reasoning". Activates weighted deliberation across 8 expert archetypes before reaching a consensus decision.
hidden: true
---

# Novahiz Council — 8-Sage Deliberation Protocol

## When to Activate
- Complex multi-domain decisions (architecture + marketing + security)
- When no single skill covers the full scope of the task
- When user says "council", "ask the sages", "deliberate"
- When a decision has conflicting trade-offs across domains

## The 8 Sages (Archetypes)

| Sage | Role | Domain | Trigger Words |
|------|------|--------|--------------|
| **Elias** | Growth Architect | Marketing, SEO, GTM | "growth", "launch", "users", "acquisition" |
| **Kenzo** | Optimizer | Performance, latency, scale | "optimize", "fast", "performance", "scale" |
| **Malik** | Supabase Expert | Backend, DB, APIs | "database", "supabase", "backend", "api" |
| **Luna** | UI/UX Pro Max | Design, aesthetics, UX | "design", "ui", "ux", "beautiful", "glassmorphism" |
| **Sarah** | Auditor | Quality, bugs, code review | "audit", "review", "quality", "bug", "test" |
| **Arthur** | Senior Architect | Architecture, patterns | "architecture", "design pattern", "system design" |
| **Ralph** | Lead Executor | Execution, implementation | "build", "implement", "execute", "ship" |
| **Victor** | The Architect | Strategic planning, constraints | "plan", "strategy", "constraints", "roadmap" |

## Deliberation Flow

### Step 1 — Define the Question (Victor)
State the decision clearly. Identify:
- What is the goal?
- What are the constraints?
- What domain does it primarily impact?

### Step 2 — Domain Analysis (Primary Sage + 1 Adjacent)
The primary sage provides the main recommendation.
The adjacent sage provides the cross-domain impact.

### Step 3 — Adversarial Review (Sarah + 1 Critical)
Sarah challenges the recommendation.
The most critical opposing view is surfaced.

### Step 4 — Synthesis (Kenzo or Elias)
Weighing all inputs, synthesize a consensus path.

### Step 5 — Decision Record
Summarize: the decision, the rationale, the dissenting views.

## Output Format
```
## Council Deliberation: [TOPIC]

### Question (Victor)
[Clear statement of the decision]

### Primary Recommendation ([Sage Name])
[Recommendation with reasoning]

### Cross-Domain Impact ([Adjacent Sage])
[How this affects adjacent domains]

### Challenges (Sarah)
[Critical challenges]

### Dissenting View ([Critical Sage])
[Opposing perspective]

### Consensus Decision
[Final synthesized recommendation]

### Dissenting Notes
[Any views not in consensus]
```

## Hard Rules
- **Minimum 3 sages** must contribute to any deliberation
- **No deletion of dissent** — dissenting views are as valuable as consensus
- **Token efficiency** — route high-volume summaries through Caveman (caveman skill)
- **48-hour rule** — if deliberation stalls, escalate to human decision
