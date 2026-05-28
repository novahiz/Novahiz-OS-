# Novahiz OS — Agent Registry

**Total: 24 agents** (updated 1.8)

| Agent | Name | Domain | Type | Model | Routing keywords |
|-------|------|--------|------|-------|------------------|
| **arthur-architecture** | Arthur | Architecture | subagent | openrouter/qwen/qwen3.6-plus | architecture, refactor |
| **athena-initialization** | Athena | Initialization | subagent | opencode/qwen3.5-plus | init, bootstrap |
| **atlas-memory** | Atlas | Memory | subagent | openrouter/qwen/qwen3.5-9b | memory |
| **cipher-crypto** | Zia | General | simulated | openrouter/qwen/qwen3.6-plus | crypto |
| **elias-marketing** | Elias | Marketing | subagent | opencode/qwen3.5-plus | marketing, seo |
| **forge-cicd** | Vulcan | CI/CD | simulated | openrouter/qwen/qwen3.5-9b | cicd |
| **ghost-stealth** | Kage | Stealth | simulated | opencode/qwen3.5-plus | — |
| **kenzo-performance** | Kenzo | Performance | subagent | opencode/qwen3.5-plus | performance |
| **luna-design** | Luna | Design | subagent | opencode/qwen3.5-plus | design, ui, ux |
| **malik-database** | Malik | Database | subagent | opencode/qwen3.5-plus | database, sql |
| **neo-security** | Neo | Security | subagent | openrouter/qwen/qwen3.6-plus | security, auth |
| **nexus-api** | Mercury | API | simulated | opencode/qwen3.5-plus | api |
| **novahiz-router** | Odin | General | primary | opencode/qwen3.5-plus | — |
| **orion-devops** | Orion | DevOps | simulated | opencode/qwen3.5-plus | devops, infra |
| **phoenix-crisis** | Phoenix | Crisis | simulated | openrouter/qwen/qwen3.6-plus | crisis, incident |
| **pulse-realtime** | Echo | Realtime | simulated | openrouter/qwen/qwen3.5-9b | realtime |
| **ralph-browser** | Ralph | BrowserAutomation | subagent | opencode/qwen3.5-plus | browser |
| **ralph-execution** | Ralph | Execution | subagent | opencode/qwen3.5-plus | backend, execution, build |
| **ryu-design** | Ryù | Design | simulated | opencode/qwen3.5-plus | ryu |
| **samuel-legal** | Samuel | General | simulated | opencode/qwen3.5-plus | — |
| **sarah-quality** | Sarah | Quality | subagent | opencode/qwen3.5-plus | audit, bug, test |
| **simon-data** | Simon | General | simulated | openrouter/qwen/qwen3.5-9b | data, analytics |
| **vega-legal** | Vega | Legal | simulated | opencode/qwen3.5-plus | legal |
| **victor-strategy** | Victor | Strategy | subagent | opencode/qwen3.5-plus | strategy, plan |

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
