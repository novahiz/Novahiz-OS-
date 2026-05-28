#!/usr/bin/env python3
"""Novahiz OS — Apply model configuration from .env to JSON configs.

Reads ~/.novahiz/.env and applies NOVAHIZ_PREMIUM/SMART/FLASH_MODEL
and _FALLBACKS to config/model-router.json and opencode.json.

Usage:
    python apply-env-models.py          # Apply overrides (default)
    python apply-env-models.py --reset  # Restore from git HEAD
    python apply-env-models.py --diff   # Show changes without writing
"""
import os, sys, json, subprocess
from pathlib import Path

HOME = Path.home()
NOVAHIZ_DIR = Path(os.environ.get("NOVAHIZ_DIR", HOME / ".opencode"))
ENV_FILE = HOME / ".novahiz" / ".env"

MODEL_ROUTER = NOVAHIZ_DIR / "config" / "model-router.json"
OPENCODE_CONFIG = NOVAHIZ_DIR / "opencode.json"

ENV_VARS = {
    "NOVAHIZ_PREMIUM_MODEL":     ["tiers", "premium", "primary"],
    "NOVAHIZ_PREMIUM_FALLBACKS": ["tiers", "premium", "fallbacks"],
    "NOVAHIZ_SMART_MODEL":       ["tiers", "smart", "primary"],
    "NOVAHIZ_SMART_FALLBACKS":   ["tiers", "smart", "fallbacks"],
    "NOVAHIZ_FLASH_MODEL":       ["tiers", "flash", "primary"],
    "NOVAHIZ_FLASH_FALLBACKS":   ["tiers", "flash", "fallbacks"],
    "NOVAHIZ_PREMIUM_BUDGET":    ["budget", "premiumPerSession"],
}

OPENCODE_VARS = {
    "OPENCODE_DEFAULT_MODEL": "model",
    "OPENCODE_SMALL_MODEL": "small_model",
}


def log(msg, color=""):
    print(f"{color}{msg}\033[0m")


def parse_env(filepath):
    """Parse env file manually — no external deps needed."""
    vals = {}
    if not filepath.exists():
        return vals
    for line in filepath.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        val = val.strip("\"'\t ")
        vals[key] = val
    return vals


def deep_set(doc, path, value):
    """Set a nested dict value by path list."""
    parent = doc
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = value


def deep_get(doc, path):
    """Get a nested dict value by path list."""
    parent = doc
    for key in path:
        if isinstance(parent, dict):
            parent = parent.get(key)
        else:
            return None
    return parent


def git_restore(filepath):
    """Restore a file from git HEAD if in a repo."""
    try:
        subprocess.run(
            ["git", "checkout", "HEAD", "--", str(filepath)],
            cwd=str(NOVAHIZ_DIR),
            capture_output=True, text=True, check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    args = set(sys.argv[1:])
    show_diff = "--diff" in args
    do_reset = "--reset" in args

    # ── Parse .env ──
    env = parse_env(ENV_FILE)

    # ── Read config files ──
    router = {}
    opencode = {}
    for f in [MODEL_ROUTER, OPENCODE_CONFIG]:
        if not f.exists():
            log(f"  ✗ {f.name}: not found — skipping", "\033[93m")

    if MODEL_ROUTER.exists():
        router = json.loads(MODEL_ROUTER.read_text())
    if OPENCODE_CONFIG.exists():
        opencode = json.loads(OPENCODE_CONFIG.read_text())

    changes = []

    # ── Reset ──
    if do_reset:
        r1 = git_restore(MODEL_ROUTER) if MODEL_ROUTER.exists() else False
        r2 = git_restore(OPENCODE_CONFIG) if OPENCODE_CONFIG.exists() else False
        if r1 or r2:
            restored = [n for n, r in [
                ("model-router.json", r1), ("opencode.json", r2)
            ] if r]
            log(f"  ✓ Restored from git: {', '.join(restored)}", "\033[92m")
        else:
            log("  ✗ Git not available — cannot reset. Edit files manually.", "\033[93m")
            return 1
        return 0

    # ── Apply model-router overrides ──
    for var, path in ENV_VARS.items():
        raw = env.get(var)
        if raw is None or raw == "":
            continue

        old = deep_get(router, path)

        if var.endswith("_FALLBACKS"):
            new = [m.strip() for m in raw.split(",") if m.strip()]
        elif var == "NOVAHIZ_PREMIUM_BUDGET":
            try:
                new = int(raw)
            except ValueError:
                log(f"  ! {var}={raw}: invalid int, skipped", "\033[93m")
                continue
        else:
            new = raw

        if old == new:
            continue

        deep_set(router, path, new)
        changes.append((var, old, new))

    # ── Apply opencode.json overrides ──
    for var, key in OPENCODE_VARS.items():
        raw = env.get(var)
        if raw is None or raw == "":
            continue

        old = opencode.get(key)
        if old == raw:
            continue

        opencode[key] = raw
        changes.append((var, old, raw))

    # ── Diff mode ──
    if show_diff:
        if changes:
            log("\n  Pending changes:\n", "\033[96m")
            for var, old, new in changes:
                old_str = json.dumps(old) if not isinstance(old, str) else old
                new_str = json.dumps(new) if not isinstance(new, str) else new
                log(f"    {var}")
                log(f"      - {old_str}")
                log(f"      + {new_str}")
        else:
            log("  No changes (env matches config)", "\033[92m")
        return 0

    # ── Apply ──
    if not changes:
        log("  ✓ No model overrides to apply (env matches config)", "\033[92m")
        return 0

    # Update timestamp
    if "lastUpdated" in router:
        from datetime import datetime
        router["lastUpdated"] = datetime.now().isoformat()

    if MODEL_ROUTER.exists():
        MODEL_ROUTER.write_text(json.dumps(router, indent=2) + "\n")
    if OPENCODE_CONFIG.exists():
        OPENCODE_CONFIG.write_text(json.dumps(opencode, indent=2) + "\n")

    log(f"  ✓ Applied {len(changes)} model override(s):", "\033[92m")
    for var, old, new in changes:
        old_str = json.dumps(old) if not isinstance(old, str) else old
        new_str = json.dumps(new) if not isinstance(new, str) else new
        log(f"    {var}: {old_str} → {new_str}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
