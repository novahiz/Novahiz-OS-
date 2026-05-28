# NOVAHIZ CLI — QUICK REFERENCE

**Version:** 1.7  
**Updated:** 2026-05-15

---

## STATUS COMMANDS

```bash
nv status          # System status + routing stats
nv status --json   # JSON output for scripting
nv health          # Health check (directories + DBs)
nv stats           # Global statistics
nv agents          # List all 22 agents
nv agents --json   # JSON output
nv skills          # List all 59 skills
nv skills --category marketing  # Filter by category
```

---

## ROUTING COMMANDS

```bash
nv route "Design a landing page"           # Auto-route to best agent
nv invoke luna-design --task "Design..."   # Invoke specific agent
nv council "PostgreSQL or SQLite?"         # Council deliberation (3-5 agents)
nv search "database"                       # Search agents + skills
```

---

## SYSTEM COMMANDS

```bash
nv sync            # Sync DB with YAML files
nv link            # Show skills linkage (71 links)
nv backup          # Create system backup
nv logs            # View system logs
nv logs --tail 50  # Last 50 lines
nv logs --level ERROR  # Filter by level
```

---

## MANAGEMENT COMMANDS

```bash
nv monitor         # Monitoring status
nv api status      # API server status
nv api start       # Start API (port 8080)
nv api stop        # Stop API
nv api restart     # Restart API
```

---

## OPTIONS

```bash
--json             # JSON output (scripting)
--quiet            # Minimal output
--verbose          # Detailed output
--help             # Full help
```

---

## ALIASES (after `source ~/.bashrc`)

```bash
nv                 # Main CLI
nvh                # nv --help
nvs                # nv status
nva                # nv agents
```

---

## EXAMPLES

### Quick Status
```bash
nv status
# Output: System Health 90% | Agents: 22 | Skills: 59 | Routes: 2
```

### Route Task
```bash
nv route "Create a design system"
# Output: Classifying... MEDIUM → Optimal: luna-design (95)
```

### Invoke Agent
```bash
nv invoke kenzo-performance --task "Optimize Core Web Vitals"
# Output: Invoking: kenzo-performance
```

### Council Deliberation
```bash
nv council "Should we use REST or GraphQL?"
# Output: Spawning council: arthur, malik, nexus → Deliberation...
```

### JSON Output (Scripting)
```bash
nv status --json | jq '.stats.agents'
# Output: 22
```

### Backup
```bash
nv backup
# Output: ✓ Backup: ~/.opencode/backups/20260515_011200/
```

---

## KEYBOARD SHORTCUTS

| Shortcut | Action |
|----------|--------|
| `nv <tab>` | Auto-complete commands |
| `Ctrl+C` | Cancel current command |
| `nv --help` | Show all commands |

---

## TROUBLESHOOTING

### Unknown Command
```bash
nv stat
# Output: Did you mean: nv status?
```

### API Not Running
```bash
curl http://localhost:8080/api/health
# If fails: nv api start
```

### Database Locked
```bash
pkill -f novahiz-cli.py
# Then retry command
```

---

## FILE LOCATIONS

| Component | Path |
|-----------|------|
| CLI Script | `~/.opencode/scripts/novahiz-cli.py` |
| Agents | `~/.opencode/agents/` (22 YAML) |
| Skills | `~/.opencode/skills/` (59 dirs) |
| Databases | `~/.opencode/data/` (4 DBs) |
| Memory | `~/.opencode/memory/` (5 branches) |
| Logs | `~/.opencode/logs/novahiz.log` |
| Backups | `~/.opencode/backups/` (7 days) |
| Config | `~/.opencode/config/` |

---

## API ENDPOINTS

| Endpoint | Method | Auth |
|----------|--------|------|
| `/api/health` | GET | Public |
| `/api/stats` | GET | Bearer |
| `/api/agents` | GET | Bearer |
| `/api/skills` | GET | Bearer |
| `/api/routing/route?task=<>` | GET | Bearer |

**Auth:** `-H "Authorization: Bearer TOKEN"`  
**Rate:** 100 req/min/IP  
**Port:** 8080

---

## DESKTOP EDITION

```bash
nvd status         # Desktop status
nvd health         # Desktop health
nvd-sync           # Manual sync from CLI
```

**Auto-Sync:** Hourly (cron: `0 * * * *`)  
**Location:** `~/.opencode-desktop/`

---

## CAZEMAN MODE

**Activation:** Automatic on every response

**Rules:**
- 1-3 phrases max
- Brutal truth, no fluff
- French unless EN asked

**Switch Levels:**
```
/caveman lite
/caveman full
/caveman ultra
stop caveman  # Disable
```

---

## AGENTS (22)

### Council (10)
- **luna-design** — UI/UX, Figma
- **kenzo-performance** — Optimization
- **malik-database** — SQL, Architecture
- **arthur-architecture** — Software Design
- **neo-security** — Security Audits
- **sarah-quality** — Testing, Reviews
- **elias-marketing** — Growth, Content
- **victor-strategy** — Planning
- **ralph-execution** — Deployment
- **atlas-memory** — Context

### Elite Force (12)
- **ryu-design**, **sage-07**, **orion-devops**, **vega-legal**, **phoenix-crisis**, **nexus-api**, **cipher-crypto**, **forge-cicd**, **pulse-realtime**, **ghost-stealth**, **sage-11**

---

## SKILLS (59)

### Universal (8)
brainstorming, caveman, simple, novahiz-status, novahiz-nexus, novahiz-metrics, novahiz-check, novahiz-constitution

### Specialized (51)
frontend-design, copywriting, seo-audit, deploy-to-vercel, tdd, xlsx, pdf, pptx, ...

---

**Quick Reference — NovaHiz OS v1.7**
