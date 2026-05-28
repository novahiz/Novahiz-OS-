#!/usr/bin/env python3
"""
Novahiz Model CLI — gère la configuration des modèles LLM.
Usage:
  nv model list
  nv model show <tier>
  nv model set <tier> <model>
  nv model fallback <tier> <n> <model>
  nv model agent <agent> <tier>
  nv model push [--force]
  nv model reset
"""
import json
import os
import re
import sys
from copy import deepcopy

HOME = os.path.expanduser("~")
CONFIG_DIR = os.path.join(HOME, ".opencode", "config")
AGENTS_DIR = os.path.join(HOME, ".opencode", "agents")
REGISTRY_PATH = os.path.join(CONFIG_DIR, "agent-registry.json")
NOVAHIZ_REGISTRY_PATH = os.path.join(HOME, ".opencode", "registry", "novahiz-registry.json")
MODEL_ROUTER_PATH = os.path.join(CONFIG_DIR, "model-router.json")
OPENCODE_JSON_PATH = os.path.join(HOME, ".opencode", "opencode.json")
AGENTS_MD_PATH = os.path.join(HOME, ".opencode", "AGENTS.md")

TIERS = ["flash", "smart", "premium"]
TIER_MODELS = {
    "flash": "openrouter/qwen/qwen3.5-9b",
    "smart": "opencode/qwen3.5-plus",
    "premium": "openrouter/qwen/qwen3.6-plus",
}

DEFAULT_CONFIG = {
    "v": "2.0",
    "enabled": True,
    "tiers": {
        "flash": {
            "primary": "openrouter/qwen/qwen3.5-9b",
            "fallbacks": ["openrouter/qwen/qwen3.5-flash-02-23"],
            "description": "Fast, cheap — Q&A, formatting, search, syntax",
            "targetRatio": 0.6,
        },
        "smart": {
            "primary": "opencode/qwen3.5-plus",
            "fallbacks": ["openrouter/qwen/qwen3.6-flash", "openrouter/z-ai/glm-4.7"],
            "description": "Balanced — build, refactor, features, tests",
            "targetRatio": 0.3,
        },
        "premium": {
            "primary": "openrouter/qwen/qwen3.6-plus",
            "fallbacks": ["openrouter/moonshotai/kimi-k2.5", "openrouter/z-ai/glm-5"],
            "description": "Powerful — architecture, security, strategy, crisis",
            "targetRatio": 0.1,
        },
    },
    "budget": {"premiumPerSession": 5, "autoDowngrade": True, "downgradeTo": "smart"},
    "agentOverrides": {
        "neo-security": "premium", "cipher-crypto": "premium",
        "phoenix-crisis": "premium", "arthur-architecture": "premium",
        "novahiz-router": "smart", "athena-initialization": "smart",
        "kenzo-performance": "smart", "luna-design": "smart",
        "malik-database": "smart", "sarah-quality": "smart",
        "ralph-execution": "smart", "victor-strategy": "smart",
        "ralph-browser": "smart", "nexus-api": "smart",
        "ryu-design": "smart", "orion-devops": "smart",
        "vega-legal": "smart", "elias-marketing": "smart",
        "samuel-legal": "smart", "ghost-stealth": "smart",
        "atlas-memory": "flash", "forge-cicd": "flash",
        "pulse-realtime": "flash", "simon-data": "flash",
    },
    "domainRouting": {
        "security": "premium", "cryptography": "premium",
        "architecture": "premium", "crisis": "premium", "system-design": "premium",
        "design": "smart", "performance": "smart", "database": "smart",
        "api": "smart", "execution": "smart", "build": "smart",
        "marketing": "smart", "strategy": "smart", "quality": "smart",
        "legal": "smart", "devops": "smart", "infra": "smart",
        "backend": "smart", "auth": "smart", "audit": "smart",
        "test": "smart", "bug": "smart", "refactor": "smart",
        "seo": "smart", "plan": "smart", "sql": "smart",
        "ui": "smart", "ux": "smart", "init": "smart",
        "stealth": "smart", "compliance": "smart", "route": "smart", "routing": "smart",
        "memory": "flash", "status": "flash", "metrics": "flash",
        "health": "flash", "cicd": "flash", "realtime": "flash",
        "data": "flash", "analytics": "flash", "browser": "flash",
    },
    "complexityMapping": {"SIMPLE": "flash", "MEDIUM": "smart", "COMPLEX": "premium"},
    "councilRules": {
        "minDomainsForPremium": 3,
        "securityAlwaysPremium": True,
        "architectureAlwaysPremium": True,
        "statusAlwaysFlash": True,
    },
}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def load_config():
    if not os.path.isfile(MODEL_ROUTER_PATH):
        eprint("Config introuvable. Utilisation du défaut.")
        return deepcopy(DEFAULT_CONFIG)
    with open(MODEL_ROUTER_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(MODEL_ROUTER_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
    print(f"  model-router.json")


def get_tier_primary(tier):
    return TIER_MODELS.get(tier, "inconnu")


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_list(args):
    cfg = load_config()
    tiers = cfg.get("tiers", {})
    print(f"\n{' TIERS ':=^60}")
    for tier, info in tiers.items():
        fallbacks = info.get("fallbacks", [])
        fb_str = ", ".join(fallbacks) if fallbacks else "aucun"
        print(f"  {tier.upper():8s} \u2192 {info['primary']}")
        print(f"           fallbacks: {fb_str}")
        print()

    overrides = cfg.get("agentOverrides", {})
    print(f"{' AGENTS PAR TIER ':=^60}")
    for t in TIERS:
        agents = [a for a, tier in sorted(overrides.items()) if tier == t]
        if agents:
            print(f"  {t.upper():8s} ({len(agents)}): {', '.join(agents)}")
    print(f"{'═' * 60}\n")


def cmd_show(args):
    if not args or args[0] not in TIERS:
        print("Usage: nv model show <flash|smart|premium>")
        return
    tier = args[0]
    cfg = load_config()
    info = cfg.get("tiers", {}).get(tier, {})
    if not info:
        print(f"Tier '{tier}' introuvable.")
        return
    print(f"\n  Tier:      {tier.upper()}")
    print(f"  Primary:   {info['primary']}")
    print(f"  Fallbacks: {', '.join(info.get('fallbacks', [])) or 'aucun'}")
    print(f"  Ratio:     {info.get('targetRatio', 'N/A')}")
    print(f"  Agents:    ", end="")
    overrides = cfg.get("agentOverrides", {})
    agents = [a for a, t in sorted(overrides.items()) if t == tier]
    print(", ".join(agents) if agents else "aucun")
    print()


def cmd_set(args):
    if len(args) < 2 or args[0] not in TIERS:
        print("Usage: nv model set <flash|smart|premium> <model>")
        return
    tier, model = args[0], args[1]
    if not model.strip():
        print("Le nom du modèle ne peut pas être vide.")
        return
    cfg = load_config()
    if tier not in cfg.get("tiers", {}):
        print(f"Tier '{tier}' inconnu.")
        return
    old = cfg["tiers"][tier]["primary"]
    cfg["tiers"][tier]["primary"] = model
    cfg["lastUpdated"] = "2026-05-28T16:00:00"
    save_config(cfg)
    print(f"  {tier.upper()}: {old} \u2192 {model}")


def cmd_fallback(args):
    if len(args) < 3 or args[0] not in TIERS:
        print("Usage: nv model fallback <flash|smart|premium> <1|2> <model>")
        return
    tier, n_str, model = args[0], args[1], args[2]
    try:
        n = int(n_str) - 1
        if n < 0:
            raise ValueError
    except ValueError:
        print("Le numéro doit être 1 ou 2.")
        return
    cfg = load_config()
    fallbacks = cfg["tiers"][tier].get("fallbacks", [])
    while len(fallbacks) <= n:
        fallbacks.append("")
    old = fallbacks[n] if n < len(fallbacks) else ""
    fallbacks[n] = model
    cfg["tiers"][tier]["fallbacks"] = fallbacks
    cfg["lastUpdated"] = "2026-05-28T16:00:00"
    save_config(cfg)
    print(f"  {tier.upper()} fallback #{n_str}: {old or 'vide'} \u2192 {model}")


def cmd_agent(args):
    if len(args) < 2 or args[1] not in TIERS:
        print("Usage: nv model agent <agent> <flash|smart|premium>")
        return
    agent, tier = args[0], args[1]
    cfg = load_config()
    overrides = cfg.setdefault("agentOverrides", {})
    old = overrides.get(agent, "non défini")
    overrides[agent] = tier
    cfg["lastUpdated"] = "2026-05-28T16:00:00"
    save_config(cfg)
    print(f"  {agent}: {old} \u2192 {tier}")


def _model_name(tier):
    return TIER_MODELS.get(tier)


def cmd_push(args):
    force = "--force" in args
    cfg = load_config()
    overrides = cfg.get("agentOverrides", {})
    todo = []  # (kind, description, apply_callable)

    # Phase 1 : calculer les changements sans écrire
    if os.path.isdir(AGENTS_DIR):
        for fname in sorted(os.listdir(AGENTS_DIR)):
            if not fname.endswith(".yaml"):
                continue
            agent_id = fname.replace(".yaml", "")
            tier = overrides.get(agent_id)
            if not tier:
                continue
            model = _model_name(tier)
            if not model:
                continue
            fpath = os.path.join(AGENTS_DIR, fname)
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
            old_model = None
            m = re.search(r'^model:\s*(\S+)', content, re.MULTILINE)
            if m:
                old_model = m.group(1)
            if old_model != model:
                todo.append(("yaml", f"YAML  {fname:30s}  model: {old_model or '?'} \u2192 {model}",
                             lambda p=fpath, t=tier, m=model: _apply_yaml(p, t, m)))

    if os.path.isfile(REGISTRY_PATH):
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            reg = json.load(f)
        dirty = False
        for agent_id, info in reg.get("agents", {}).items():
            tier = overrides.get(agent_id)
            if not tier:
                continue
            model = _model_name(tier)
            if not model:
                continue
            if info.get("model") != model:
                todo.append(("reg", f"REG   agent-registry.json/{agent_id:25s}  model: {info.get('model','?')} \u2192 {model}", None))
                dirty = True
        if dirty:
            todo.append(("reg_save", "  (sauvegarde agent-registry.json)", lambda: _apply_registry(REGISTRY_PATH, overrides)))

    if os.path.isfile(NOVAHIZ_REGISTRY_PATH):
        with open(NOVAHIZ_REGISTRY_PATH, encoding="utf-8") as f:
            reg2 = json.load(f)
        dirty = False
        for entry in reg2.get("agents", []):
            agent_id = entry.get("id") or entry.get("name")
            tier = overrides.get(agent_id)
            if not tier:
                continue
            model = _model_name(tier)
            if not model:
                continue
            if entry.get("model") != model:
                todo.append(("reg", f"REG   novahiz-registry.json/{agent_id:25s}  model: {entry.get('model','?')} \u2192 {model}", None))
                dirty = True
        if dirty:
            todo.append(("reg_save", "  (sauvegarde novahiz-registry.json)", lambda: _apply_registry(NOVAHIZ_REGISTRY_PATH, overrides)))

    if os.path.isfile(AGENTS_MD_PATH):
        with open(AGENTS_MD_PATH, encoding="utf-8") as f:
            content = f.read()
        changed = 0
        for line in content.split("\n"):
            m = re.match(r'^\|\s*\*\*(.+?)\*\*', line)
            if m:
                agent_id = m.group(1).lower()
                tier = overrides.get(agent_id)
                if tier:
                    model = _model_name(tier)
                    if model:
                        parts = line.split("|")
                        if len(parts) >= 6 and parts[4].strip() != model:
                            changed += 1
        if changed:
            todo.append(("md", f"MD    AGENTS.md  ({changed} agent(s))", lambda: _apply_agents_md(overrides)))

    premium_model = _model_name("premium")
    if premium_model and os.path.isfile(OPENCODE_JSON_PATH):
        with open(OPENCODE_JSON_PATH, encoding="utf-8") as f:
            oc = json.load(f)
        if oc.get("model") != premium_model:
            todo.append(("opencode", f"JSON  opencode.json          model: {oc.get('model','?')} \u2192 {premium_model}",
                         lambda: _apply_opencode_json(premium_model)))

    if not todo:
        print("  Aucun changement nécessaire \u2014 tout est à jour.")
        return

    print(f"\n  {len(todo)} changement(s) détecté(s) :\n")
    for _, desc, _ in todo:
        print(f"  {desc}")

    if not force:
        try:
            resp = input("\n  Appliquer ces changements ? (Y/n) ").strip().lower()
            if resp not in ("", "y", "yes", "o", "oui"):
                print("  Annulé.")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n  Annulé.")
            return

    # Phase 2 : appliquer
    for _, desc, apply_fn in todo:
        if apply_fn:
            apply_fn()
    print("  Push terminé.")


def _apply_yaml(fpath, tier, model):
    with open(fpath, encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'^modelTier:\s*\S+', f'modelTier: {tier}', content, count=1, flags=re.MULTILINE)
    content = re.sub(r'^model:\s*\S+', f'model: {model}', content, count=1, flags=re.MULTILINE)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)


def _apply_registry(path, overrides):
    with open(path, encoding="utf-8") as f:
        reg = json.load(f)
    agents = reg.get("agents", {}) if isinstance(reg.get("agents"), dict) else {}
    if not agents:
        agents = {e.get("id") or e.get("name"): e for e in reg.get("agents", []) if e.get("id") or e.get("name")}
    for agent_id, info in agents.items():
        tier = overrides.get(agent_id)
        tmodel = _model_name(tier)
        if tmodel and info.get("model") != tmodel:
            info["model"] = tmodel
    with open(path, "w", encoding="utf-8") as f:
        json.dump(reg, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _apply_agents_md(overrides):
    with open(AGENTS_MD_PATH, encoding="utf-8") as f:
        lines = f.read().split("\n")
    new_lines = []
    for line in lines:
        m = re.match(r'^\|\s*\*\*(.+?)\*\*', line)
        if m:
            agent_id = m.group(1).lower()
            tier = overrides.get(agent_id)
            if tier:
                tmodel = _model_name(tier)
                if tmodel:
                    parts = line.split("|")
                    if len(parts) >= 6 and parts[4].strip() != tmodel:
                        parts[4] = f" {tmodel} "
                        line = "|".join(parts)
        new_lines.append(line)
    with open(AGENTS_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))


def _apply_opencode_json(premium_model):
    with open(OPENCODE_JSON_PATH, encoding="utf-8") as f:
        oc = json.load(f)
    oc["model"] = premium_model
    with open(OPENCODE_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(oc, f, indent=2, ensure_ascii=False)
        f.write("\n")


def cmd_reset(args):
    print("  Reset vers la configuration usine :")
    print(f"    flash:   {TIER_MODELS['flash']}")
    print(f"    smart:   {TIER_MODELS['smart']}")
    print(f"    premium: {TIER_MODELS['premium']}")
    print(f"    24 agents répartis sur les 3 tiers")
    print(f"    + domainRouting, complexityMapping, councilRules")
    try:
        resp = input("\n  Confirmer le reset ? (y/N) ").strip().lower()
        if resp not in ("y", "yes", "o", "oui"):
            print("  Annulé.")
            return
    except (EOFError, KeyboardInterrupt):
        print("\n  Annulé.")
        return
    save_config(DEFAULT_CONFIG)
    print("  Config réinitialisée. Lance 'nv model push' pour synchroniser les fichiers.")


COMMANDS = {
    "list": cmd_list,
    "show": cmd_show,
    "set": cmd_set,
    "fallback": cmd_fallback,
    "agent": cmd_agent,
    "push": cmd_push,
    "reset": cmd_reset,
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    sub = sys.argv[2:]
    if cmd == "help" or cmd not in COMMANDS:
        print(__doc__)
        return

    COMMANDS[cmd](sub)


if __name__ == "__main__":
    main()
