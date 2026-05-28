---
name: novahiz-check
description: System Integrity & Health Check. Use when the user asks "status", "health check", "system check", "diagnostics", "novahiz status", or "is everything working". Validates all 47 installed skills, 21 agents, memory structure, and constitution integrity.
hidden: true
---

# System Health Check

## When to Run
- User says "status", "health check", "system check", "diagnostics"
- On startup (before major tasks)
- After agent synthesis or skill installation

## Check Sequence

### 1 — Skills Integrity (47 expected)
```
For each installed skill in skills/:
  - Verify SKILL.md exists
  - Verify hash matches skills-lock.json
  - Check for required subfiles (references/, agents/, etc.)
Result: X/47 skills healthy
```

### 2 — Memory Structure (NTM)
```
For each branch in memory/:
  - Verify directory exists
  - Verify nexus.json is valid JSON
  - Check node count vs last recorded
Result: X/5 branches healthy
```

### 3 — Agent Registry
```
For each agent in registry.json:
  - Verify manifest exists
  - Verify status is "active"
  - Check efficiency_score
Result: X/21 agents active
```

### 4 — Constitution Integrity
```
  - Verify constitution.md is unmodified
  - Verify no forbidden actions have been taken
  - Verify no absolute paths in use
Result: CONSTITUTION STATUS: ACTIVE / VIOLATED
```

### 5 — Novahiz System Files
```
  - Verify ~\.cache\opencode\.novahiz\ structure
  - Verify council/ deliberation files
  - Verify dashboard/ structure
Result: SYSTEM FILES: OK / MISSING
```

## Output Format
```
## Novahiz OS — Health Check

### Skills Integrity
  [████████████████████░░░░░] 47/47 healthy
  [SKILL] [STATUS]

### Memory Structure (NTM)
  [████████████████████] 5/5 branches healthy
  00_Core: X nodes | 01_Agents: X nodes | ...

### Agent Registry
  [████████████████████] 21/21 active
  Council: 11 | Elite Force: 10

### Constitution Integrity
  STATUS: ACTIVE ✓

### Novahiz System
  memory/: OK | council/: OK | dashboard/: OK

### OPENCODE SKILLS OVERLAY
  47 skills installed via npx skills
  Source: opencode.ai/skills hub + github
  Overlap detection: DISABLED (skills are complementary)

### OVERALL STATUS: HEALTHY ✅
  Score: 98/100
  Recommendations: [list if any]
```

## Auto-Remediation
If a skill or file is missing, the system should attempt to reinstall via `npx skills add`.
