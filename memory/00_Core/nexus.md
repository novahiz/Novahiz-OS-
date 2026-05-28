---
name: novahiz-nexus
description: Novahiz NTM Memory Engine. Use when the user mentions "nexus", "memory", "recall", "tree memory", "store context", "remember this", "NTM", or any task involving persistent memory, context retrieval, tree-based memory, or information recall across sessions.
hidden: true
---

# Novahiz Nexus — Tree Memory Engine

## Core Mission
Manage the Novahiz Tree Memory (NTM) across 5 hierarchical branches. Enable sub-millisecond context retrieval via nexus.json indexes.

## Branch Architecture

```
memory/
├── 00_Core/           # System rules, protocols, constitution
├── 01_Agents/         # Agent council & identity manifests
├── 02_Projects/      # Active projects & missions
├── 03_Patterns/      # Reusable patterns & design decisions
├── 04_Archives/      # Historical & externalized data (NEVER DELETE)
└── nexus.json        # Global brain map — cross-branch search index
```

## Memory Operations

### STORE — Store a memory node
**When:** User says "remember", "store this", "save context", or you need to persist important information.

**How:**
1. Classify the information into the correct branch
2. Create a dated file: `YYYY-MM-DD_title.md`
3. Update the branch `nexus.json` with: `{ "id": "title", "path": "...", "summary": "...", "tags": [...] }`
4. If critical, also update the global `nexus.json`

### RECALL — Retrieve memory
**When:** User asks "what do you remember about X", "do you recall", "from our last session", or you need context.

**How:**
1. Read the relevant `nexus.json` (branch-level or global)
2. Load the most relevant `.md` files
3. Synthesize the context for the user

### SEARCH — Cross-branch search
**When:** User asks "search memory", "find everything about X", or you need to locate distributed knowledge.

**How:**
1. Parse all `nexus.json` files (branch + global)
2. Match against tags, summaries, and keywords
3. Return ranked results with paths

## Nexus.json Format
```json
{
  "version": "1.0.0",
  "branch": "01_Agents",
  "lastUpdated": "2026-05-10",
  "nodes": [
    {
      "id": "elias_growth",
      "path": "01_Agents/elias/manifest.md",
      "summary": "Growth Architect — specializes in GTM, SEO, and growth loops",
      "tags": ["growth", "marketing", "gtm", "seo"],
      "priority": "high"
    }
  ]
}
```

## Hard Rules
- **NEVER delete from `04_Archives`** — use versioning instead
- **Atlas is the only authorized agent** for memory fragmentation
- **Update `nexus.json` after every major mission**
- **Always classify before storing** — wrong branch = degraded recall

## Fragmentation (Atlas Protocol)
When a branch exceeds 50 nodes, or a node becomes too complex, trigger fragmentation:
1. Split the node into focused sub-nodes
2. Update the parent nexus.json with references
3. Create a new child nexus.json for the fragment
