---
name: novahiz-synthesis
description: "Novahiz Continuity Engine. Auto-loads context from Obsidian wiki + Nexus at boot. Auto-saves session summaries. Bridges all chat sessions seamlessly."
humanName: nicolas-synthesis
hidden: true
triggers: [synthesis, continuity, session, context, memory, recall, resume]
autoInvokeOnBoot: true
loadOnce: boot-only
---

# Novahiz Synthesis — Continuity Engine

## Mission
Every new chat session MUST feel like a continuation, not a restart. The synthesis engine loads all persistent context at boot and saves session summaries at end — bridging knowledge across ALL projects automatically.

## Boot Protocol (auto-executed)

### Step 1 — Load Nexus session archive (cross-session context)
Read these files:
- `memory/05_Context/recent-sessions.md` — last 10 sessions log
- `memory/05_Context/current.md` — last session's active context
- `memory/04_Archives/sessions/` — read last 3 session summaries (most recent first)
- `memory/02_Projects/index.md` — project registry

→ Synthesize a brief "Previous sessions context" paragraph.

### Step 2 — Load Obsidian Wiki index
- Read `~/Documents/llm-wiki/index.md` (direct filesystem or obsidian-mcp)
- Note: what knowledge already exists (concepts, entities, summaries)

### Step 3 — Detect current project
- Read `pwd` to detect working directory
- Cross-reference with `memory/02_Projects/index.md`
- If new directory (not in index), treat as new project

### Step 4 — Inject context
Present a unified context summary:
```
[Synthesis] Continuity restored.
Previous sessions: X found
Wiki: Y concepts, Z entities, W summaries
Current project: <name or "new session">
Last session: <date> — <tasks> — <last decision>
```

## Session End Protocol

When session ends:

### Step 1 — Save session summary to archive
Create `memory/04_Archives/sessions/YYYY-MM-DD_HHMM_session-summary.md`:
```markdown
# Session Summary — YYYY-MM-DD HH:MM

## Project
- Name: <name>
- Directory: <pwd>

## Work Done
- <task 1>
- <task 2>

## Key Decisions
- <decision 1> | Rationale: <why>
- <decision 2> | Rationale: <why>

## Files Modified
- <path 1>
- <path 2>

## Next Recommended
- <next action>
```

### Step 2 — Update Nexus `05_Context/current.md`
Replace the session summary block with current session data.

### Step 3 — Update Nexus `05_Context/recent-sessions.md`
Prepend new row to the sessions table, keep max 10 entries.

### Step 4 — Update Obsidian wiki (if applicable)
If new knowledge was created, update the relevant wiki pages and `index.md`.

## Mid-Session Auto-Save

Every major milestone or decision:
- Update `memory/05_Context/current.md` hot topics and decisions tables
- Append to the session summary block
- If working on a wiki project, occasionally write raw files to `~/Documents/llm-wiki/raw/`

## Usage Note
This skill is `autoInvokeOnBoot` and `loadOnce: boot-only`. It runs once at session start and defines the continuity contract. The agent follows these instructions automatically for the entire session.

## Dependencies
- No external services — works entirely offline via filesystem
- Obsidian wiki at `~/Documents/llm-wiki/` (optional — skip if absent)
- Nexus memory at `.opencode/memory/` (required — part of Novahiz OS)
