---
name: novahiz-evolution
description: Self-Healing & Auto-Patching Engine. Use when the user asks "evolve", "self-heal", "patch", "auto-fix", or any task requiring the system to detect degradation and autonomously repair skill conflicts, broken references, or memory fragmentation.
hidden: true
---

# Self-Healing & Evolution Engine

## Core Mission
Detect system degradation and autonomously repair without human intervention.

## Degradation Detection

### Skill Drift
```
For each skill in skills/:
  - Compare hash to skills-lock.json
  - If mismatch: flag as drifted
  - If missing file: flag as corrupted
```

### Memory Fragmentation
```
For each branch nexus.json:
  - If nodeCount > 50: trigger Atlas fragmentation
  - If nexus.json invalid: rebuild from files
```

### Skill Duplication (Critical)
```
For each installed skill:
  - Extract domain tags from SKILL.md
  - Build conflict matrix
  - If 2 skills share >70% domain AND <5% unique content:
      → Mark the secondary as REDUNDANT
      → Do NOT auto-delete — flag for human review
```

### Memory Loop
```
If a node references a deleted node:
  - Reconstruct from 04_Archives if version exists
  - Else: mark as orphaned, flag for cleanup
```

## Auto-Patch Actions

| Degradation Type | Action | Requires Human? |
|-----------------|--------|----------------|
| Skill drifted | Reinstall from skills-lock.json | No |
| Skill corrupted | Reinstall from original source | No |
| Memory fragmented | Invoke Atlas fragmentation | No |
| Node orphaned | Reconstruct from archive | No |
| Skill conflict | Flag for review | YES |
| Constitution violated | Alert + halt operations | YES |
| Agent manifest missing | Re-synthesize agent | YES |

## Skill Duplication Detection (CRITICAL)
The 47 OpenCode skills and Novahiz system operate in **complementary mode** — no auto-deletion.

Detection rules:
- Compare `description:` fields for semantic overlap
- Compare `name:` fields for exact match
- **No auto-delete** — flag conflicts for human decision
- Log all conflicts in `memory/03_Patterns/skill-conflicts.md`

## Evolution Log
All auto-patches are logged to `memory/04_Archives/evolution-log.md`:
```
## [TIMESTAMP] Auto-Patch: [TYPE]
- Detected: [WHAT]
- Action: [WHAT WAS DONE]
- Result: [STATUS]
- Human review required: [YES/NO]
```
