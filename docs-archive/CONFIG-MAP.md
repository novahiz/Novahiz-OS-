# 🗺️ Novahiz OS — Configuration Map v6.1

**Goal:** Understand which config file does what

---

## Current State (4 files)

| File | Purpose | Can Consolidate? |
|------|---------|------------------|
| `~/.novahiz/.env` | Secrets (API keys) | ❌ No (security) |
| `~/.opencode/runtime/config.json` | Runtime settings | ✅ Keep |
| `~/.config/opencode/opencode.jsonc` | OpenCode Desktop | ❌ No (IDE config) |
| `~/.config/opencode/mcp.json` | MCP routing | ⚠️ Can merge with opencode.jsonc |

---

## Recommended Structure (v6.1)

```
~/.novahiz/
  └── .env                    # Secrets only (DO NOT TOUCH)

~/.opencode/
  ├── runtime/
  │   └── config.json         # Runtime config (agents, providers, timeouts)
  ├── VERSION                 # Version info
  └── README.md               # Main documentation

~/.config/opencode/
  ├── opencode.jsonc          # OpenCode Desktop + MCP servers (MERGED)
  └── mcp.json                # → DELETE (merge into opencode.jsonc)
```

---

## Migration Plan

### Phase 1 (Done)
- ✅ `.env` for secrets
- ✅ `runtime/config.json` for runtime

### Phase 2 (TODO)
- [ ] Merge `mcp.json` into `opencode.jsonc`
- [ ] Remove `mcp.json`
- [ ] Update documentation

### Phase 3 (Future)
- [ ] Add config validation script
- [ ] Add config schema (JSON Schema)

---

## Config Validation Script

```bash
# Check all configs are valid
~/.opencode/scripts/validate-configs.sh
```

---

[Novahiz OS v6.1 — Configuration Map]
