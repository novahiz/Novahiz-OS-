---
name: novahiz-boot
description: "Novahiz OS Boot Protocol. Run once at session start: health check, session recovery, metrics init. Token-optimized — only loaded at boot, not per message."
humanName: nicolas-boot
hidden: true
triggers: [boot, session-start]
loadOnce: boot-only
---

# Novahiz Boot Protocol

## Run once at session start (NOT per message)

## Boot Sequence
1. **novahiz-evolution** — verify skills (skills-lock.json), agents (registry.json), memory structure
2. **novahiz-synthesis** — load Supermemory + Obsidian wiki + Nexus context → continuity with all previous sessions
3. **novahiz-nexus** — recover last session from `00_Core/sessions/` if exists
4. **novahiz-metrics** — load metrics.json for observability
5. **Browser readiness** — verify `chrome-devtools-mcp` installed, Chrome debug port 9222 accessible, selection cache primed with browser patterns
6. **novahiz-auto** — ready for message classification

## Health Check (novahiz-evolution)
```
Checklist:
- skills-lock.json → all 58 skills present?
- registry.json → all 21 agents active?
- nexus.json (5x) → valid JSON?
- scoreboard.json → valid JSON?
- memory branches (5) → exist?
Log result to evolution-log.md
```

## Session Recovery (novahiz-nexus)
```
If 00_Core/sessions/ has recent session:
  → Load most recent summary
  → Inject context
  → Increment recovered count in metrics.json
```

## Session End Protocol
1. **novahiz-synthesis** → save session to Supermemory + update Nexus context + update Obsidian wiki if needed
2. **novahiz-nexus** → persist session to `00_Core/sessions/`
3. **novahiz-metrics** → update deliberation counts + timestamps
4. **scoreboard.json** → update agent participation

## Version
Novahiz OS v1.5 — Full Continuity (Supermemory + Wiki + Nexus)