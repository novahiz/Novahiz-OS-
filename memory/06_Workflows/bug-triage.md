# Workflow: Bug Triage

> Standard protocol for triaging and resolving bugs.

## Trigger
- Bug report from user, test failure, or crash
- Any `bug`, `error`, `crash`, `failing` keyword

## Steps

### 1. Triage (Sarah + systematic-debugging)
- [ ] Reproduce the bug — get exact error message
- [ ] Identify affected component
- [ ] Estimate severity: **P0** (down) / **P1** (major) / **P2** (minor) / **P3** (cosmetic)
- [ ] Check if duplicate (search 04_Archives, 05_Context)

### 2. Root Cause (Malik + systematic-debugging)
- [ ] Apply 5-whys analysis
- [ ] Isolate the failing component
- [ ] Test isolation hypothesis

### 3. Fix (Cyrus + tdd)
- [ ] Write failing test first (TDD)
- [ ] Implement minimal fix
- [ ] All tests pass

### 4. Review (Sarah)
- [ ] Code review: style, security, edge cases
- [ ] Regression check
- [ ] Update scoreboard: +1 deliberation for Cyrus

### 5. Archive
- [ ] Move from 05_Context/hot-topics.md to Resolved
- [ ] Record in project decisions.md
- [ ] Update nexus.json
- [ ] Tag: `bug-fixed-[date]`