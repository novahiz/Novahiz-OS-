# 📋 Novahiz OS — Configuration Files

**Version:** 6.0.0  
**Last Updated:** 2026-05-27

---

## Overview

Novahiz OS uses 4 configuration files, each with a specific role:

| File | Purpose | Edit Frequency |
|------|---------|----------------|
| `~/.novahiz/.env` | **Secrets** (API keys) | Rarely |
| `~/.opencode/runtime/config.json` | **Runtime** settings | Occasionally |
| `~/.config/opencode/opencode.jsonc` | **OpenCode Desktop** config | Rarely |
| `~/.config/opencode/mcp.json` | **MCP Server** routing | Rarely |

---

## 1. ~/.novahiz/.env — Secrets

**Purpose:** Secure storage for API keys and sensitive environment variables.

**Permissions:** 600 (owner read/write only)

**Contents:**
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENCODE_ZEN_API_KEY=sk-TnPvEk-xxxxx
NOVAHIZ_TIMEOUT=120
NOVAHIZ_MAX_RETRIES=3
```

**⚠️ Never commit this file to git.**

---

## 2. ~/.opencode/runtime/config.json — Runtime

**Purpose:** Runtime daemon configuration (agent routing, providers, timeouts).

**Permissions:** 600 (contains no secrets since v6.0)

**Contents:**
```json
{
  "version": "6.0.0",
  "max_concurrent": 5,
  "timeout": 120,
  "providers": { ... },
  "agents": { ... }
}
```

**Safe to version control** (no API keys).

---

## 3. ~/.config/opencode/opencode.jsonc — OpenCode Desktop

**Purpose:** OpenCode Desktop IDE configuration (MCP servers, extensions, settings).

**Location:** User config directory (separate from Novahiz installation).

**Contents:**
```jsonc
{
  "mcpServers": {
    "novahiz": {
      "command": "python3",
      "args": ["~/.opencode/mcp/novahiz-mcp-http.py"]
    }
  }
}
```

**Managed by:** OpenCode Desktop (auto-updated on plugin install).

---

## 4. ~/.config/opencode/mcp.json — MCP Routing

**Purpose:** MCP (Model Context Protocol) server routing configuration.

**Contents:**
```json
{
  "novahiz": {
    "url": "http://127.0.0.1:8765",
    "tools": ["route", "execute", "auto", ...]
  }
}
```

**Managed by:** Novahiz MCP setup script.

---

## Synchronization

### When to Sync

| Action | Files to Sync |
|--------|---------------|
| Version update | `VERSION`, `runtime/config.json`, `README.md` |
| New API key | `.env` only |
| New MCP tool | `mcp.json`, `opencode.jsonc` |

### Version Consistency Check

```bash
# Check all versions match
grep -r "version" ~/.opencode/VERSION ~/.opencode/runtime/config.json ~/.opencode/README.md
```

**Expected:** All show `6.0.0`

---

## Security

### ✅ Secure (v6.0)
- API keys in `~/.novahiz/.env` (600 permissions)
- `.env` excluded from git via `.gitignore`
- No secrets in `config.json`

### ❌ Insecure (pre-v6.0)
- API keys in `.bashrc` (visible in process list)
- API keys in `config.json` (could be committed)

---

## Backup Strategy

```bash
# Backup all configs
tar -czf ~/backups/novahiz-config-$(date +%Y%m%d).tar.gz \
    ~/.novahiz/.env \
    ~/.opencode/runtime/config.json \
    ~/.config/opencode/opencode.jsonc \
    ~/.config/opencode/mcp.json
```

**Restore:**
```bash
tar -xzf ~/backups/novahiz-config-YYYYMMDD.tar.gz -C ~/
chmod 600 ~/.novahiz/.env
```

---

[Novahiz OS v6.0 — Configuration Files]
