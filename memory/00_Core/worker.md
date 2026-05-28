---
name: novahiz-worker
description: Autonomous Background Task Runner. Use when the user asks "worker", "background tasks", "daemon", "automation", or any task requiring scheduled or autonomous background processing like health checks, skill sync, or memory maintenance.
hidden: true
---

# Autonomous Background Worker

## Core Mission
Run non-blocking background tasks to keep the Novahiz OS healthy without interrupting the main agent loop.

## Background Task Queue

### Priority 1 — Always Running
| Task | Interval | Action |
|------|----------|--------|
| Health Check | Every 30 min | Run `novahiz-check` silently |
| Memory Sync | Every 15 min | Update nexus.json from changes |
| Evolution Scan | Every 60 min | Run `novahiz-evolution` drift detection |

### Priority 2 — On-Demand
| Task | Trigger | Action |
|------|---------|--------|
| Skill Sync | `novahiz sync` | Pull updates from registered repos |
| Agent Synthesis | `novahiz create` | Run synthesis protocol |
| Fragmentation | Memory > 50 nodes | Invoke Atlas |
| Council Deliberation | Complex decision | Activate 8-sage protocol |

## Safety Guards
- **Never auto-delete** skills or memory nodes
- **Never block** the main agent loop
- **Always log** actions to `memory/04_Archives/worker-log.md`
- **Human escalation** for any constitution violation

## Implementation
In OpenCode, the "worker" is the agent itself running these checks:
1. At session start: run a lightweight health check
2. When requested: run full health check or evolution scan
3. Memory sync: automatic after every store operation
