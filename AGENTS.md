# Novahiz OS — Agent Registry

**Total: 24 agents** (updated 1.8)

| Agent | Domain | Type | Model | Routing keywords |
|-------|--------|------|-------|------------------|
| **arthur-architecture** | Architecture | subagent | anthropic/claude-3-5-sonnet | architecture, refactor |
| **athena-initialization** | Initialization | subagent | anthropic/claude-3-5-sonnet | init, bootstrap |
| **atlas-memory** | Memory | subagent | anthropic/claude-3-5-sonnet | memory |
| **cipher-crypto** | General | simulated | openrouter/qwen/qwen3.6-plus | crypto |
| **elias-marketing** | Marketing | subagent | anthropic/claude-3-5-sonnet | marketing, seo |
| **forge-cicd** | CI/CD | simulated | opencode/qwen3.5-plus | cicd |
| **ghost-stealth** | Stealth | simulated | opencode/qwen3.5-plus | — |
| **kenzo-performance** | Performance | subagent | anthropic/claude-3-5-sonnet | performance |
| **luna-design** | Design | subagent | anthropic/claude-3-5-sonnet | design, ui, ux |
| **malik-database** | Database | subagent | anthropic/claude-3-5-sonnet | database, sql |
| **neo-security** | Security | subagent | anthropic/claude-3-5-sonnet | security, auth |
| **nexus-api** | API | simulated | opencode/qwen3.5-plus | api |
| **novahiz-router** | General | primary | anthropic/claude-3-5-sonnet | — |
| **orion-devops** | DevOps | simulated | opencode/qwen3.5-plus | devops, infra |
| **phoenix-crisis** | Crisis | simulated | opencode/qwen3.5-plus | crisis, incident |
| **pulse-realtime** | Realtime | simulated | opencode/qwen3.5-plus | realtime |
| **ralph-browser** | BrowserAutomation | subagent | anthropic/claude-3-5-sonnet | browser |
| **ralph-execution** | Execution | subagent | anthropic/claude-3-5-sonnet | backend, execution, build |
| **ryu-design** | Design | simulated | opencode/qwen3.5-plus | ryu |
| **samuel-legal** | General | simulated | opencode/qwen3.5-plus | — |
| **sarah-quality** | Quality | subagent | anthropic/claude-3-5-sonnet | audit, bug, test |
| **simon-data** | General | simulated | opencode/qwen3.5-plus | data, analytics |
| **vega-legal** | Legal | simulated | opencode/qwen3.5-plus | legal |
| **victor-strategy** | Strategy | subagent | anthropic/claude-3-5-sonnet | strategy, plan |

## CLI Routing

```bash
nv route "build a rest api"     # -> nexus-api (api keyword)
nv route "fix security bug"     # -> neo-security (security takes priority over bug)
nv route "ui design"            # -> luna-design
nv route "database performance" # -> kenzo-performance (performance before database)
```

Use `nv route <task>` for routing and `nv debug` for routing diagnostics.

## Chrome MCP Commands

```powershell
nv chrome-start    # Lance Chrome avec remote debugging (profil isole)
nv chrome-stop     # Arrete Chrome MCP
nv chrome-status   # Verifie si Chrome MCP tourne
```

Chrome MCP utilise un profil isole dans `.opencode/chrome-profile-mcp` -- aucun impact sur le Chrome principal. Le lancement est automatique au demarrage de chaque session.

## Continuity Protocol (AUTO — no manual steps needed)

The `novahiz-synthesis` skill auto-loads at every session boot (`autoInvokeOnBoot: true`).

**What it does automatically:**
1. Queries Supermemory for last 5 session summaries + key decisions
2. Reads Obsidian LLM Wiki index (`~/Documents/llm-wiki/index.md`)
3. Reads Nexus context (`memory/05_Context/`)
4. Injects all previous context so this session continues seamlessly

**At session end (auto-save):**
1. Saves session summary to Supermemory (`type: session-summary`)
2. Updates Nexus context files (current.md, recent-sessions.md)
3. Updates Obsidian wiki if knowledge was created

**This applies to EVERY project — no configuration needed.**

## Token-Optimized Boot Chain
1. novahiz-evolution → health check
2. **novahiz-synthesis → continuity context (Supermemory + Wiki + Nexus)**
3. novahiz-nexus → session recovery
4. novahiz-metrics → observability
5. Browser readiness → Chrome MCP
6. novahiz-auto → message classification
