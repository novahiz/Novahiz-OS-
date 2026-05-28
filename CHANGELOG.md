# 📝 Novahiz OS — Changelog

## [6.0.0] — 2026-05-27 — Long Term Stability

### Added
- `.env` file for secure API key storage
- `requirements.txt` for dependency management
- `logrotate.conf` for log rotation
- `systemd/` service files for production deployment
- `VERSION` file as single source of truth
- Consolidated `README.md` documentation

### Changed
- Autostart script now loads from `~/.novahiz/.env`
- API keys moved from `.bashrc` to `.env`
- Documentation consolidated into single README

### Fixed
- Version inconsistency across files
- Configuration file duplication
- Missing log rotation
- No dependency versioning

### Security
- API keys now in `~/.novahiz/.env` (600 permissions)
- `.gitignore` updated to exclude secrets
- Systemd services with security hardening

---

## [5.5.0] — 2026-05-27 — 100/100 Score

### Added
- Unit tests (34 tests)
- Integration tests (18 tests)
- `nv health` command

### Fixed
- Race condition in file sync
- Metrics time filtering

---

## [5.4.0] — 2026-05-27 — Optimization

### Added
- File sync with `fsync()`
- `nv metrics` time filtering
- `.bashrc` cleanup

---

## [5.3.0] — 2026-05-27 — Metrics & Security

### Added
- Metrics tracking system
- API key security (moved to .bashrc)
- Retry logic with backoff
- Timeout handling (120s)

---

## [5.2.0] — 2026-05-27 — Multi-Provider

### Added
- Multi-provider LLM support
- Fallback chain (3 fallbacks)
- Auto-start scripts


---

## [6.0.1] — 2026-05-27 — Security & Quality Improvements

### Fixed
- Version inconsistency (config.json now v6.0.0)
- API keys removed from .bashrc (security fix)
- novahiz-secure.sh updated for v6.0

### Added
- Linters in requirements.txt (black, flake8, pylint, coverage)
- CONFIG-FILES.md documentation
- run-coverage.sh for test coverage reports
- Security audit script (novahiz-secure.sh)

### Changed
- Security audit now checks .bashrc for API keys


---

## [6.1.0] — 2026-05-28 — Production Grade

### Security
- Shell injection vectors eliminated (21x `shell=True` → `shell=False` with `shlex.quote`)
- All bare `except:` blocks replaced with `except Exception` across the project
- Claude/Anthropic API key references fully purged (25 files, ~30 replacements)
- `.bashrc` scrubbed of API keys, credentials moved to `~/.novahiz/.env`

### Architecture
- `sys.path.insert` raw hacks standardized: 17 occurrences in 10 files replaced with `Path().resolve().parent.parent` + `not in sys.path` guard
- Centralized path resolution module (`mcp/_path.py`) for all MCP imports
- `opencode-bridge.py` imports `metrics.metrics.MetricsCollector` directly instead of path hack

### Agents & Naming
- 6 concept-named agents renamed to human/mythical names:
  - `cipher-crypto` → **Zia** (Arabic for light/splendor)
  - `forge-cicd` → **Vulcan** (Roman god of the forge)
  - `ghost-stealth` → **Kage** (Japanese for shadow)
  - `nexus-api` → **Mercury** (Roman messenger god)
  - `pulse-realtime` → **Echo** (Greek nymph of repetition)
  - `novahiz-router` → **Odin** (Norse all-father)
- Updated: `AGENTS.md`, `HUMAN_NAMES.md`, `agent-registry.json`, `novahiz-registry.json`, 6 YAML agent files

### Cleanup
- Root directory: 21 files archived to 13 (8 stale MDs → `docs-archive/`)
- `docs/` consolidated: 17 files → 4 (13 archived)
- Dead files deleted: `install-v5.sh`, `novahiz-mcp-ws.py`, `smart-router.py.deprecated`, `fix-error-handling.py`
- `auto-executor-simple.py` marked DEPRECATED
- 47 unused imports removed across 26 Python files
- All shell scripts updated: `novahiz-runtime.py` → `novahiz-unified.py`

### Fixed
- TradingView MCP: `command` + `args` string format → `command: [...]` array (incompatible with OpenCode)
- `novahiz-mcp.py`: raw `sys.path.insert` → standard path pattern with proper engine import
- Pre-commit hook: added `check-bare-except` and `check-claude-refs` enforcers

### Tests
- All unit tests updated (no more bare `except:`, no more `shell=True`)
- Test scripts reference `novahiz-unified.py` instead of old runtime
- Integration tests consistent with new architecture

