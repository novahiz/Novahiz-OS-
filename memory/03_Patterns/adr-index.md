# ADR — Architecture Decision Records

## About ADRs
Architecture Decision Records document significant technical decisions made by the Novahiz Council. Each ADR captures the context, decision, and consequences to maintain institutional knowledge.

## ADR Format
```markdown
# ADR-[NUMBER]: [TITLE]

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded
**Authors**: [Sage(s) involved]
**Deciders**: [Final decision makers]

## Context
[What is the issue? What forces are at play?]

## Decision
[What is the change being made?]

## Consequences
- **Positive**: [Good outcomes]
- **Negative**: [Bad outcomes]
- **Neutral**: [Neither good nor bad]
```

## Index

| # | Title | Date | Status |
|---|-------|------|--------|
| 001 | Two-Layer Architecture (Skills + Novahiz) | 2026-05-12 | Accepted |
| 002 | 8-Sage Council Deliberation Protocol | 2026-05-12 | Accepted |
| 003 | NTM Memory Structure (5 branches) | 2026-05-12 | Accepted |
| 004 | 21-Agent Registry (11 Council + 10 Elite) | 2026-05-12 | Accepted |
| 005 | Source of Truth Files (skills-lock.json, registry.json, nexus.json) | 2026-05-12 | Accepted |

## ADR-001: Two-Layer Architecture
**Status**: Accepted | **Date**: 2026-05-12

### Context
Novahiz OS runs on top of OpenCode's skill system. We need a clear separation between task-execution skills and orchestration skills.

### Decision
- Layer 1: OpenCode skills (59) — task execution
- Layer 2: Novahiz skills (10) — orchestration & governance
- COMPLEMENTARY mode — no duplication, no conflicts

### Consequences
- Clear responsibility boundaries
- Skills evolve independently from orchestration
- Human review required for skill conflicts

## ADR-002: 8-Sage Council Deliberation Protocol
**Status**: Accepted | **Date**: 2026-05-12

### Context
Complex decisions require multi-perspective analysis. We need a structured protocol with clear roles.

### Decision
- 8 sages with defined domains + triggers
- 5-step deliberation flow
- Minimum 3 sages per deliberation
- Cache + timeout guards
- Caveman compression on synthesis

### Consequences
- Consistent decision quality
- Token efficiency via cache + compression
- Audit trail via deliberation history

## ADR-003: NTM Memory Structure
**Status**: Accepted | **Date**: 2026-05-12

### Context
Agents need persistent memory. We need a hierarchical structure that supports fast retrieval.

### Decision
- 5 branches: 00_Core, 01_Agents, 02_Projects, 03_Patterns, 04_Archives
- nexus.json per branch for fast indexing
- Global nexus.json for cross-branch search
- Sessions stored in 00_Core/sessions/

### Consequences
- Sub-millisecond retrieval via nexus indexes
- Clear memory boundaries by domain
- Session recovery possible

## ADR-004: 21-Agent Registry
**Status**: Accepted | **Date**: 2026-05-12

### Context
We need named agents with clear domains for task routing.

### Decision
- 11 Council Sages (95.0 efficiency target)
- 10 Elite Force (90.0 efficiency target)
- Registry stored in registry.json
- Scoreboard for efficiency tracking

### Consequences
- Clear routing via novahiz-selection
- Efficiency metrics via scoreboard
- Scalable agent synthesis

## ADR-005: Source of Truth Files
**Status**: Accepted | **Date**: 2026-05-12

### Context
Multiple skills reference shared data. We need canonical sources.

### Decision
- skills-lock.json: 59 skill inventory
- registry.json: 21 agent registry
- scoreboard.json: agent efficiency scores
- nexus.json (5x): NTM indexes

### Consequences
- Drift detection possible
- Single source for data integrity
- Auto-remediation possible