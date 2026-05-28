---
name: novahiz-synthesis
description: Novahiz Agent Synthesis Protocol. Use when the user wants to create a new specialized agent, "synthesize an agent", "add a new expert", "create agent", or " onboard a new specialist". Follows the autonomous agent creation loop defined in the Novahiz OS specification.
hidden: true
---

# Agent Synthesis Protocol

## When to Activate
- User says "create agent", "synthesize agent", "add new expert", "onboard specialist"
- A gap in the existing agent roster is identified during a task
- A new domain expertise is needed that no current agent covers

## Synthesis Loop (5 Steps)

### Step 1 — Requirement Analysis
Submit the user's description to the **Council** for domain classification.
Output: primary domain, adjacent domains, priority level (Critical/High/Medium/Low)

### Step 2 — Architectural Design
**Victor** and **Arthur** define:
- The agent's constraints and boundaries
- What it MUST do and what it MUST NOT do
- Interfaces with existing agents
- Portability requirements (relative paths only)

### Step 3 — PRD Generation
**Ralph** creates the `manifest.md`:
```
agents/[agent_name]/manifest.md
```
Contains: identity, role, domain, constraints, instructions, efficiency_target

### Step 4 — Code Scaffolding
Automatic folder creation:
```
agents/[agent_name]/
├── manifest.md          # Identity & constraints
├── core/                 # Core logic
│   ├── deliberation.py   # Decision engine
│   └── execution.py     # Action engine
└── memory/              # Agent-specific memory
```

### Step 5 — Integration & Activation
- Register agent in `agents/registry.json`
- Add to relevant skills via the council deliberation
- The agent is immediately available for tasks

## Agent Manifest Template
```markdown
---
name: [Agent Name]
role: [Official Title]
domain: [Primary Domain]
status: active
efficiency_target: 95.0
priority_level: [Critical|High|Medium|Low]
author: Novahiz OS v1.0
date: YYYY-MM-DD
---

## Identity
[Brief identity statement]

## Core Responsibilities
- [Responsibility 1]
- [Responsibility 2]

## Hard Constraints
- [MUST DO]
- [MUST NOT DO]

## Interfaces
- [Other agents it collaborates with]
- [Seams it must respect]

## Token Efficiency
[How to compress outputs when needed]

## Audit Requirements
[Sarah's review criteria]
```

## Critical Domain Agents (require Council)
- Security, auth, payments, data storage, API design
- These require 8-sage deliberation before synthesis
