# Novahiz OS — Technical Debt Tracker

**Generated:** 2026-05-27 14:41  
**Total Items:** 4

---

## Summary

| Priority | Count | Percentage |
|----------|-------|------------|
| 🔴 Critical | 0 | 0% |
| 🟠 High | 2 | 50% |
| 🟡 Medium | 0 | 0% |
| 🟢 Low | 2 | 50% |

---

## By Tag

| Tag | Count |
|-----|-------|
| TODO | 0 |
| FIXME | 0 |
| HACK | 0 |
| XXX | 0 |
| BUG | 4 |
| DEPRECATED | 0 |

---

## Critical & High Priority Items

### 🟠 [BUG] scripts/novahiz-cli.js:21

**Description:** (args) => toggleDebug(args),

**Action:** Create GitHub issue and assign

---

### 🟠 [BUG] scripts/novahiz-cli.js:262

**Description:** <on/off> Toggle debug mode                 ║

**Action:** Create GitHub issue and assign

---

## All Items

| Priority | Tag | File | Line | Description |
|----------|-----|------|------|-------------|
| 🟠 | BUG | scripts/novahiz-cli.js | 21 | (args) => toggleDebug(args), |
| 🟠 | BUG | scripts/novahiz-cli.js | 262 | <on/off> Toggle debug mode                 ║ |
| 🟢 | BUG | engine/tests/test_engine.py | 83 | in authentication") |
| 🟢 | BUG | scripts/novahiz-cli.js | 219 | mode ${args && args[0] === 'on' ? 'enabled' : 'dis... |

---

## How to Use This Report

1. **Review** critical/high items first
2. **Create GitHub issues** for each item
3. **Assign** to appropriate milestone
4. **Track progress** in GitHub Projects
5. **Re-run** this script regularly

## Automation

```bash
# Generate report
python3 scripts/track-todos.py

# View report
cat docs/TECHNICAL_DEBT.md
```

---

*Last Updated: 2026-05-27*
