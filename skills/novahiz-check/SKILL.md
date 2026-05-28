---
name: novahiz-check
description: "System Integrity & Health Check. Full validation: skills, agents, memory, constitution. Token-optimized."
humanName: nina-check
hidden: true
triggers: [status, health, check, diagnostics, system-check, verify]
---

# System Health Check

## Sources of Truth
- `skills-lock.json` → 58 skills inventory
- `registry.json` → 21 agents registry
- `nexus.json` (6x) → NTM indexes
- `scoreboard.json` → agent efficiency
- `constitution.md` → rules

## Check Sequence

### 1 — Skills (58 expected)
```
For each skill in skills-lock.json:
  - file exists at path?
  - hash matches? (drift check)
  Count: X/58 present | Y drifted
```

### 2 — Memory Structure (5 branches)
```
For each branch:
  - directory exists?
  - nexus.json valid JSON?
  - node count > 0?
Count: X/5 healthy
```

### 3 — Agents (21 expected)
```
For each agent in registry.json:
  - manifest exists?
  - status = "active"?
  - efficiency score >= target?
Count: X/21 active
```

### 4 — Constitution
```
- constitution.md present
- no forbidden actions detected
- no absolute paths in skills
STATUS: ACTIVE | VIOLATED
```

### 5 — Scoreboard
```
- valid JSON
- 21 agents
- scores in range
STATUS: VALID | CORRUPT
```

### 6 — Novahiz System Skills (13 total)
```
- all 13 present + valid?
```

## Output Format
```
## Novahiz OS v1.4 — Health Check

Skills:      [████████████░░░░░] 58/58 | drifted: 0
Memory:       [████████████] 5/5 branches | 6/6 nexus.json
Agents:       [████████████] 21/21 | active: 21
Constitution: ACTIVE
Scoreboard:   VALID
System:       13/13 OK

STATUS: HEALTHY | DEGRADED (X issues)
Score: X/100
```

## Remediation
| Issue | Action |
|-------|--------|
| Missing skill | Flag as drifted |
| Invalid nexus.json | Rebuild from files |
| Missing directory | Create + log |
| Missing agent | Flag for human review |