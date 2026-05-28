#!/usr/bin/env python3
"""Novahiz OS — Post-Install Validation"""
import os, sys, json, subprocess, shutil
from pathlib import Path

GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
NC = '\033[0m'

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.environ.get("NOVAHIZ_DIR", os.path.join(HOME, ".opencode"))
NOVAHIZ = Path(NOVAHIZ_DIR)

passed, failed = 0, 0

def check(label, condition, fix_hint=""):
    global passed, failed
    if condition:
        print(f"  {GREEN}✓{NC} {label}")
        passed += 1
    else:
        print(f"  {RED}✗{NC} {label}")
        failed += 1
        if fix_hint:
            print(f"    {YELLOW}Fix:{NC} {fix_hint}")

def main():
    global passed, failed
    
    print(f"\n{CYAN}{BOLD}━━━ NOVAHIZ OS — POST-INSTALL VALIDATION ━━━{NC}\n")

    # System
    print(f"  {BOLD}SYSTEM{NC}")
    check("Python 3.10+", sys.version_info >= (3, 10),
          "Install Python 3.10+: python3 --version")
    check("Node.js 18+", subprocess.run(["node", "-e", 
          "process.exit(Number(process.version.slice(1).split('.')[0] < 18))"],
          capture_output=True).returncode == 0,
          "Install Node.js 18+: node --version")
    check("Git installed", shutil.which("git") is not None)
    check("curl available", shutil.which("curl") is not None)
    print()

    # Novahiz directory structure
    print(f"  {BOLD}DIRECTORY STRUCTURE{NC}")
    check("Engine modules", (NOVAHIZ / "engine" / "__init__.py").exists())
    check("MCP server", (NOVAHIZ / "mcp" / "novahiz-mcp.py").exists())
    check("Runtime engine", (NOVAHIZ / "runtime" / "novahiz-unified.py").exists())
    check("Agent configs", len(list(NOVAHIZ.glob("agents/*.yaml"))) >= 20)
    check("Skills directory", (NOVAHIZ / "skills").exists() or (NOVAHIZ / ".agents" / "skills").exists())
    check("CLI tools", (NOVAHIZ / "bin" / "nv").exists() or (NOVAHIZ / "bin" / "novahiz").exists())
    check("OpenCode config", (NOVAHIZ / "opencode.json").exists())
    check("Model router", (NOVAHIZ / "config" / "model-router.json").exists())
    check("Agent registry", (NOVAHIZ / "config" / "agent-registry.json").exists())
    print()

    # MCP verification
    print(f"  {BOLD}MCP SERVERS{NC}")
    mcp_files = list((NOVAHIZ / "mcp").glob("*.py"))
    check(f"MCP scripts ({len(mcp_files)} found)", len(mcp_files) >= 5)
    
    if (NOVAHIZ / "opencode.json").exists():
        with open(NOVAHIZ / "opencode.json") as f:
            config = json.load(f)
        mcp_count = len(config.get("mcp", {}))
        check(f"MCP entries in config ({mcp_count})", mcp_count >= 3)
    print()

    # Environment
    print(f"  {BOLD}ENVIRONMENT{NC}")
    env_file = Path(HOME) / ".novahiz" / ".env"
    check("API keys file", env_file.exists() and env_file.stat().st_mode & 0o600 == 0o600)
    if env_file.exists():
        keys = [l.split("=")[0] for l in env_file.read_text().splitlines() if "=" in l]
        check(f"Keys configured: {', '.join(keys)}", bool(keys))
    print()

    # Obsidian vault
    vault = Path(HOME) / "Documents" / "llm-wiki"
    print(f"  {BOLD}OBSIDIAN{NC}")
    check("Vault directory", vault.exists())
    check("Vault config", (vault / ".obsidian" / "app.json").exists())
    print()

    # CLI
    print(f"  {BOLD}CLI ACCESS{NC}")
    check("In PATH", shutil.which("nv") is not None or shutil.which("novahiz") is not None)

    # Results
    total = passed + failed
    print(f"\n  {'─' * 40}")
    if failed == 0:
        print(f"\n  {GREEN}{BOLD}ALL {total} CHECKS PASSED{NC}  🚀 Novahiz OS ready!")
    else:
        pct = int(passed / total * 100) if total else 0
        print(f"\n  {YELLOW}{BOLD}{passed}/{total} passed ({pct}%) — {failed} need attention{NC}")
        if failed == 1:
            print(f"  {YELLOW}→ Run the check manually and fix{NC}")
    print()

if __name__ == "__main__":
    main()
