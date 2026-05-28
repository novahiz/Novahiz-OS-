#!/usr/bin/env python3
"""
Novahiz Tool-Aware Skill Loader v1.9.1
Generates compact skill manifests per tool context budget.
All 59 skills linked everywhere — descriptions adapt to budget.
"""
import json, sys, os, shutil, math
from pathlib import Path

AGENTS_DIR = Path.home() / ".opencode" / ".agents"
SKILLS_DIR = AGENTS_DIR / "skills"
CONFIG_DIR = AGENTS_DIR.parent / "config" / "tools"
NTM_DIR = AGENTS_DIR.parent / "config" / "ntm"
NTM_STATE = NTM_DIR / "state.json"

NC = os.environ.get("NOVAHIZ_NOCOLOR") == "1"
def S(t): return f"\033[{t}]m" if not NC else ""
B,G,R,Y,C,Z = S("1"),S("92"),S("91"),S("93"),S("96"),S("0")
def g(t): return f"{G}✓{Z} {t}"
def r(t): return f"{R}✗{Z} {t}"
def y(t): return f"{Y}!{Z} {t}"
def b(t): return f"{B}{t}{Z}"

TOOL_PATHS = {
    "opencode": Path.home() / ".opencode" / ".agents" / "skills",
    # "claude": supprimé — legacy, plus utilisé
    "hermes":   Path.home() / ".hermes" / "skills",
    "codex":    Path.home() / ".codex" / "skills",
    "cursor":   Path.home() / ".cursor" / "skills",
    "windsurf": Path.home() / ".codeium" / "windsurf" / "skills",
    "goose":    Path.home() / ".config" / "goose" / "skills",
    "cline":    Path.home() / ".config" / "cline" / "skills",
    "plandex":  Path.home() / ".config" / "plandex" / "skills",
}

def load_profile(tool_id):
    p = CONFIG_DIR / f"{tool_id}.json"
    if p.exists(): return json.loads(p.read_text())
    t = CONFIG_DIR / "_template.json"
    if t.exists(): return json.loads(t.read_text())
    return None

def get_all_skills():
    if not SKILLS_DIR.exists(): return []
    return sorted([d.name for d in SKILLS_DIR.iterdir() if d.is_dir() and (d / "SKILL.md").exists()])

def parse_skill_description(skill_dir):
    md_file = skill_dir / "SKILL.md"
    if not md_file.exists(): return None, []
    text = md_file.read_text()
    name = skill_dir.name
    description = ""
    triggers = []
    for line in text.splitlines():
        if line.startswith("description:"):
            description = line[12:].strip().strip('"').strip("'")
        elif line.startswith("triggers:"):
            trig_part = line[9:].strip()
            if trig_part.startswith("["):
                trig_part = trig_part.strip("[]")
                triggers = [t.strip().strip('"').strip("'") for t in trig_part.split(",")]
    return description, triggers

def compute_budget_bytes(profile):
    budget_pct = profile.get("constraints", {}).get("contextBudget")
    if budget_pct is None: return None
    ctx_window = profile.get("constraints", {}).get("assumedContextTokens", 128000)
    token_budget = int(ctx_window * (budget_pct / 100))
    char_budget = int(token_budget * 3.5)
    overhead = len(get_all_skills()) * 15
    return max(100, char_budget - overhead)

def split_skills_by_priority(profile, all_skills):
    priority = profile.get("skills", {}).get("loadPriority", [])
    priority_set = set(priority)
    immediate = [s for s in priority if s in all_skills]
    rest = [s for s in all_skills if s not in priority_set]
    return immediate, rest

def truncate_descriptions(all_skills, profile):
    budget = compute_budget_bytes(profile)
    if budget is None: return None
    max_chars = profile.get("skills", {}).get("summaryMaxChars", 120)
    budget_pct = profile.get("constraints", {}).get("contextBudget")
    floor_chars = 10 if (budget_pct and budget_pct <= 3) else 25
    immediate, rest = split_skills_by_priority(profile, all_skills)
    ordered = immediate + rest

    index = {"budgetBytes": budget, "totalSkills": len(all_skills), "priority": True, "skills": []}
    available = budget - 100

    for skill_name in ordered:
        skill_dir = SKILLS_DIR / skill_name
        desc, triggers = parse_skill_description(skill_dir)
        if not desc: desc = skill_name
        if len(desc) > max_chars: desc = desc[:max_chars-3] + "..."

        entry = {"id": skill_name, "desc": desc}
        cost = len(json.dumps(entry)) + 2

        if cost > available:
            shorter = desc[:max(1, floor_chars)]
            entry = {"id": skill_name, "desc": shorter}
            cost = len(json.dumps(entry)) + 2

        if cost <= available:
            index["skills"].append(entry)
            available -= cost

    return index

def generate_compact_skill(skill_dir, dest_dir, max_chars):
    """Copy a skill but with a compact SKILL.md description."""
    skill_name = skill_dir.name
    dest = dest_dir / skill_name
    if dest.exists():
        if dest.is_symlink(): dest.unlink()
        elif dest.is_dir(): shutil.rmtree(dest)

    shutil.copytree(skill_dir, dest)
    md_file = dest / "SKILL.md"
    if md_file.exists():
        text = md_file.read_text()
        lines = text.splitlines()
        new_lines = []
        for line in lines:
            if line.startswith("description:"):
                desc = line[12:].strip().strip('"').strip("'")
                if len(desc) > max_chars:
                    desc = desc[:max_chars-3] + "..."
                    new_lines.append(f'description: "{desc}"')
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        md_file.write_text("\n".join(new_lines))

    pycache = dest / "__pycache__"
    if pycache.exists(): shutil.rmtree(pycache)

def sync_for_tool(tool_id, profile=None):
    if profile is None: profile = load_profile(tool_id)
    if profile is None: print(r(f"No profile for {tool_id}")); return

    target_dir = TOOL_PATHS.get(tool_id)
    if target_dir is None: print(y(f"Unknown tool: {tool_id}")); return

    method = profile.get("install", {}).get("method", "symlink")
    max_chars = profile.get("skills", {}).get("summaryMaxChars", 600)
    all_skills = get_all_skills()
    immediate, rest = split_skills_by_priority(profile, all_skills)
    ordered = immediate + rest

    target_dir.mkdir(parents=True, exist_ok=True)
    linked = 0

    if target_dir.resolve() == SKILLS_DIR.resolve():
        print(f"  {C}i{Z} Source == target, counting existing skills...")
        linked = len(all_skills)
    else:
        for skill_name in ordered:
            src = SKILLS_DIR / skill_name
            dest = target_dir / skill_name
            if not src.exists(): continue

            if dest.exists():
                if dest.is_symlink(): dest.unlink()
                elif dest.is_dir(): shutil.rmtree(dest)

            if method == "copy":
                generate_compact_skill(src, target_dir, max_chars)
            else:
                dest.symlink_to(src)
            linked += 1

    index = truncate_descriptions(all_skills, profile)
    budget = compute_budget_bytes(profile)
    total_bytes = 0
    if index:
        index_file = target_dir / ".skill-index.json"
        index_file.write_text(json.dumps(index, indent=2))
        total_bytes = len(json.dumps(index))
        index_msg = f" manifest: {total_bytes}B / {budget}B budget"
    else:
        index_file = target_dir / ".novahiz-meta.json"
        meta = {"tool": tool_id, "version": "1.8", "totalSkills": linked, "method": method}
        index_file.write_text(json.dumps(meta, indent=2))
        index_msg = ""

    print(f"\n{b(f'Sync: {tool_id}')}\n")
    print(f"  {G}✓{Z} Skills: {linked}")
    print(f"  {C}i{Z} Method: {method}")
    if index_msg: print(f"  {C}i{Z}{index_msg}")
    budget_pct = profile.get("constraints", {}).get("contextBudget")
    if budget_pct: print(f"  {Y}!{Z} Context budget: {budget_pct}% ({budget}B for descriptions)")
    print()

def cmd_sync(args):
    tool_id = args.tool or "all"
    if tool_id == "all":
        for tid in TOOL_PATHS:
            p = load_profile(tid)
            sync_for_tool(tid, p)
    else:
        sync_for_tool(tool_id)

def cmd_list(args):
    from pathlib import Path
    all_skills = get_all_skills()
    print(f"\n{b('Skills: ' + str(len(all_skills)))}\n")
    if args.tool:
        profile = load_profile(args.tool)
        if profile:
            index = truncate_descriptions(all_skills, profile)
            if index:
                for s in index["skills"]:
                    print(f"  {C}{s['id']:40s}{Z} {s['desc'][:50]}")
            else:
                for s in all_skills:
                    print(f"  {C}{s:40s}{Z}")
    else:
        for s in all_skills:
            print(f"  {C}{s:40s}{Z}")
    print()

def cmd_profile(args):
    profile = load_profile(args.tool)
    if not profile: print(r(f"No profile for {args.tool}")); return
    print(f"\n{b(f'Profile: {args.tool}')}\n")
    print(f"  All skills: yes (59)")
    print(f"  Context budget: {profile.get('constraints',{}).get('contextBudget','∞')}%")
    print(f"  Install: {profile.get('install',{}).get('method','symlink')}")
    print(f"  Identity: {profile.get('identity',{}).get('fileName','AGENTS.md')}")
    print(f"  Novahiz: {profile.get('novahiz',{}).get('enabled','yes')}")

def cmd_health(args):
    print(f"\n{b('Tool Profiles Health')}\n")
    ok, bad = 0, 0
    for tid in TOOL_PATHS:
        profile = load_profile(tid)
        target = TOOL_PATHS[tid]
        if profile and target.exists():
            linked = len([f for f in target.iterdir() if not f.name.startswith(".")])
            manifest = target / ".skill-index.json"
            has_manifest = "manifest ✓" if manifest.exists() else ""
            print(f"  {G}✓{Z} {tid:12s} {linked:2d}/59 skills {has_manifest}")
            ok += 1
        elif profile:
            print(f"  {Y}!{Z} {tid:12s} not synced")
            bad += 1
        else:
            print(f"  {R}✗{Z} {tid:12s} no profile")
            bad += 1
    print(f"\n  STATUS: {b('HEALTHY') if bad==0 else b(f'{bad} tools not synced')}\n")

def main():
    import argparse
    p = argparse.ArgumentParser(prog="novahiz skills")
    sub = p.add_subparsers()
    sy = sub.add_parser("sync"); sy.add_argument("--tool","-t",default="all"); sy.set_defaults(fn=cmd_sync)
    ls = sub.add_parser("list"); ls.add_argument("--tool","-t"); ls.set_defaults(fn=cmd_list)
    pf = sub.add_parser("profile"); pf.add_argument("tool"); pf.set_defaults(fn=cmd_profile)
    hl = sub.add_parser("health"); hl.set_defaults(fn=cmd_health)
    args = p.parse_args(sys.argv[2:] if len(sys.argv) > 2 else [])
    if hasattr(args, "fn"): args.fn(args)
    else: p.print_help()

if __name__ == "__main__": main()