# Workflow: Crisis Management

> Protocol for P0 incidents and production emergencies.

## Trigger
- Production down
- Data breach
- Critical security vulnerability
- `crisis`, `emergency`, `P0`, `incident`, `down`

## Steps

### 1. Declare Crisis (Victor)
- [ ] Assess severity: **CRISIS** / Major / Normal
- [ ] Assign incident commander (usually Ralph)
- [ ] Page relevant agents (Malik for backend, Neo for security, etc.)

### 2. Contain (Malik + Ralph)
- [ ] Stop the bleeding first
- [ ] Rollback if deploy caused it
- [ ] Enable maintenance mode if needed
- [ ] Notify stakeholders

### 3. Diagnose (Sarah + systematic-debugging)
- [ ] Find root cause
- [ ] Time-box: 30 minutes max
- [ ] Isolate if not already

### 4. Fix (Ralph)
- [ ] Implement fix
- [ ] Test in staging
- [ ] Deploy with rollback plan ready
- [ ] Monitor for 15 minutes post-deploy

### 5. Post-Mortem (Sarah + all)
- [ ] Document timeline (minute by minute)
- [ ] Identify root cause
- [ ] What worked / what didn't
- [ ] Action items (who/when)
- [ ] Store in `04_Archives/` as `incident-YYYY-MM-DD.md`

### 6. Restore
- [ ] Close incident in tracking
- [ ] Update hot-topics.md
- [ ] Notify stakeholders
- [ ] Update scoreboard: all participants get +1 deliberation