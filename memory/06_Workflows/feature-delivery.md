# Workflow: Feature Delivery

> End-to-end workflow for shipping a feature.

## Trigger
- Feature request received
- `feature`, `build`, `implement`, `ship`

## Steps

### 1. Clarify (Victor + Elias)
- [ ] What exactly are we building?
- [ ] What does done look like?
- [ ] Any constraints?

### 2. Design (Luna + Arthur)
- [ ] UI/UX approach (Luna)
- [ ] Architecture (Arthur)
- [ ] ADR if significant decision needed

### 3. Plan (Victor)
- [ ] Break into issues (to-issues)
- [ ] Order: fastest validation first
- [ ] Set milestone

### 4. Build (Ralph + Cyrus)
- [ ] TDD loop: red → green → refactor
- [ ] Incremental commits
- [ ] Each piece reviewable

### 5. Test (Sarah + webapp-testing)
- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E smoke test

### 6. Polish (Luna + Kenzo)
- [ ] Design review
- [ ] Performance check
- [ ] Accessibility

### 7. Ship (Ralph + Blaise)
- [ ] Deploy to staging
- [ ] UAT sign-off
- [ ] Deploy to prod
- [ ] Monitor