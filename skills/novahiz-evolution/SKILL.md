---
name: novahiz-evolution
description: Self-Healing & Auto-Patching. Full health check, drift detection, overlap detection. Auto-invoked on session boot.
humanName: eveline-evolution
hidden: true
triggers: [evolution, heal, patch, self-heal, drift, auto-fix, boot]
autoInvokeOnBoot: true
---

# Self-Healing & Evolution Engine

## Boot Health Check (auto-run once per session)

Checklist:
```
✓ skills-lock.json → all skills present? (verify path + hash)
✓ novahiz-synthesis/SKILL.md → continuity engine present
✓ registry.json → all agents active?
✓ nexus.json (8x) → all valid JSON? (global + 7 branches)
✓ scoreboard.json → valid JSON + all agents?
✓ memory/00_Core/ → constitution, scoreboard, metrics
✓ memory/01_Agents/ → all agent memory files
✓ memory/02_Projects/ → index
✓ memory/03_Patterns/ → index, adr-index
✓ memory/04_Archives/ → evolution-log
✓ memory/05_Context/ → current.md, recent-sessions.md
✓ memory/06_Workflows/ → crisis, bug-triage, feature-delivery, pr-review, data-analysis
→ Log to evolution-log.md with timestamp
```

## Drift Detection

For each skill in skills-lock.json:
- Path mismatch → flag as DRIFTED
- Hash mismatch → flag as CORRUPTED
- Missing file → flag as MISSING

Never auto-delete. Always flag + log.

## Overlap Detection

Compare all 58 skill `description:` fields:
- >80% semantic similarity → flag CONFLICT (human review required)
- Exact name match → flag DUPLICATE risk

## Auto-Patch Actions

| Issue | Action | Human? |
|-------|--------|--------|
| Skill drifted | Log + flag | No |
| Skill corrupted | Log + flag | No |
| Memory fragmented | Invoke Atlas | No |
| nexus.json invalid | Rebuild from files | No |
| Directory missing | Create + log | No |
| Skill conflict | Flag for review | **YES** |
| Constitution violated | Alert + halt | **YES** |
| Agent manifest missing | Flag for review | **YES** |

## Evolution Log
`04_Archives/evolution-log.md` — all patches logged.

Format:
```markdown
## TIMESTAMP — TYPE
- Detected: [what]
- Action: [what done]
- Result: [OK/FAIL]
- Human review: [YES/NO]
```
