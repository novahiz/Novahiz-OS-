# Workflow: PR Review

> Standard protocol for reviewing code before merge.

## Trigger
- Pull request opened
- Code ready for merge
- `review`, `pr`, `merge` keyword

## Steps

### 1. Pre-Review (Sarah)
- [ ] Read PR description + motivation
- [ ] Understand scope (what's included / excluded)
- [ ] Check linked issues / tickets

### 2. Security Scan (Neo + Iris)
- [ ] No secrets / credentials in diff
- [ ] Input validation on all user-facing paths
- [ ] No untrusted external URLs

### 3. Quality Gate (Sarah + systematic-debugging)
- [ ] Tests exist and pass
- [ ] No obvious bugs or regressions
- [ ] Error handling present
- [ ] Logging appropriate (not verbose in prod)

### 4. Architecture Check (Arthur)
- [ ] Follows existing patterns
- [ ] No over-engineering
- [ ] Dependencies justified

### 5. Performance Check (Kenzo)
- [ ] No N+1 queries
- [ ] No blocking operations on hot paths
- [ ] Bundle size impact acceptable

### 6. Decision
- [ ] **APPROVE** — merge
- [ ] **REQUEST CHANGES** — comment with specifics
- [ ] **REJECT** — explain why + alternative path

### 7. Archive
- [ ] Record decision in project decisions.md
- [ ] Update scoreboard: +1 deliberation for reviewers
- [ ] Nexus sync