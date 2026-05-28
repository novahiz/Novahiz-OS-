---
name: novahiz-selection
description: Weighted Multi-Agent Selector. Use when the user asks "select agents", "which agent for this task", "route to expert", "delegate to agent", "agent routing", or any task requiring intelligent routing of a problem to the right specialized agent based on domain, efficiency score, and task fit.
hidden: true
---

# Weighted Multi-Agent Selector

## Purpose
Route any task to the optimal agent based on: domain match, efficiency score, availability, and task complexity.

## Selection Algorithm

### Input: Task Description
Parse the task into domain tags.

### Step 1 — Domain Match (Weight: 40%)
Score each agent on domain overlap.
```
domain_score = (matching_domains / total_task_domains) * 40
```

### Step 2 — Efficiency Score (Weight: 30%)
From registry, pull each agent's efficiency_score.
```
efficiency_score = (agent_score / 100) * 30
```

### Step 3 — Availability (Weight: 20%)
Check if agent's status is "active" and not overloaded.
```
availability_score = 20 if active else 0
```

### Step 4 — Specialization Bonus (Weight: 10%)
Exact role match gets +10.
```
specialization_bonus = 10 if exact_match else 0
```

### Total Score
```
total = domain_score + efficiency_score + availability_score + specialization_bonus
```

## Routing Table

| Task Keywords | Primary Agent | Adjacent Agent |
|--------------|-------------|----------------|
| build, implement, ship, code | Ralph | Sarah |
| design, ui, ux, beautiful | Luna | Arthur |
| architecture, system, pattern | Arthur | Victor |
| performance, optimize, latency | Kenzo | Ralph |
| growth, marketing, launch, seo | Elias | Sarah |
| database, supabase, backend, api | Malik | Dante |
| bug, fix, error, crash | Sarah | Cyrus |
| plan, strategy, roadmap | Victor | Arthur |
| audit, review, quality | Sarah | Cyrus |
| security, pentest, zero-trust | Neo | Iris |
| memory, recall, store, remember | Atlas | Nexus |
| token, compress, efficiency, brief | Caveman | Kenzo |
| docker, container, k8s | Blaise | Storm |
| mobile, react-native, flutter | Hugo | Luna |
| ml, ai, model, pipeline | Alan | Maya |

## Output Format
```
## Agent Selection for: [TASK]

| Rank | Agent | Role | Score | Rationale |
|------|-------|------|-------|-----------|
| 1 | [Name] | [Role] | [X/100] | [Why] |
| 2 | [Name] | [Role] | [X/100] | [Why] |

Recommended: **[Primary Agent]** — [1-line rationale]
```

## Hard Rules
- **Minimum 2 agents** must be selected for any Critical task
- **Sarah must be included** in all code-related selections
- **No single agent** handles a task exceeding their domain by >50%
