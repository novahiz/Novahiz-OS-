#!/usr/bin/env python3
"""
NTM Memory - Scoring NTM Memory — Scoring & Expiry System v1.9 Expiry System v1.9.1
Tracks, scores, and prunes memory nodes based on usage.
"""
import json, sys, os
from pathlib import Path
from datetime import datetime, timedelta

NTM_DIR = Path.home() / ".opencode" / "config" / "ntm"
NTM_STATE = NTM_DIR / "state.json"

NC = os.environ.get("NOVAHIZ_NOCOLOR") == "1"
def S(t): return f"\033[{t}m" if not NC else ""
B,G,R,Y,C,Z = S("1"),S("92"),S("91"),S("93"),S("96"),S("0")

def g(t): return f"{G}✓{Z} {t}"
def r(t): return f"{R}✗{Z} {t}"
def y(t): return f"{Y}!{Z} {t}"
def b(t): return f"{B}{t}{Z}"

DEFAULT_CONFIG = {
    "version": "1.8",
    "scoring": {
        "decayRate": 0.05,
        "boostOnAccess": 2.0,
        "boostOnDeliberation": 5.0,
        "minScore": 0.1,
        "maxScore": 100.0,
        "scoreHistoryWeight": 0.3
    },
    "expiry": {
        "enabled": True,
        "maxAgeDays": 30,
        "pruneBelowScore": 1.0,
        "pruneDryRun": False,
        "autoPruneSessions": 10,
        "runtimePrune": True,
        "keepDeliberations": True
    },
    "hotAgents": {
        "enabled": True,
        "maxHot": 5,
        "boostOnRecentUse": 10.0,
        "recentThresholdHours": 24,
        "scoreThreshold": 5.0
    },
    "tools": {}
}

def load_state():
    NTM_DIR.mkdir(parents=True, exist_ok=True)
    if NTM_STATE.exists():
        return json.loads(NTM_STATE.read_text())
    return {"nodes": {}, "hotAgents": {}, "sessions": 0, "lastPrune": None, "config": DEFAULT_CONFIG}

def save_state(state):
    NTM_DIR.mkdir(parents=True, exist_ok=True)
    NTM_STATE.write_text(json.dumps(state, indent=2))

def score_node(node, cfg):
    decay = cfg["decayRate"]
    boost = cfg["boostOnAccess"]
    score = node.get("score", 10.0)

    last = node.get("lastAccess")
    if last:
        days = (datetime.now() - datetime.fromisoformat(last)).days
        if days > 0:
            score *= max(0.3, 1.0 - (days * decay))

    accesses = node.get("accessCount", 0)
    prev_access = node.get("prevAccessCount", 0)
    if accesses > prev_access:
        score += (accesses - prev_access) * boost * 0.1
    node["prevAccessCount"] = accesses

    delibes = node.get("deliberationCount", 0)
    prev_delib = node.get("prevDeliberationCount", 0)
    if delibes > prev_delib:
        score += (delibes - prev_delib) * cfg["boostOnDeliberation"]
    node["prevDeliberationCount"] = delibes

    return min(cfg["maxScore"], max(cfg["minScore"], round(score, 2)))

def access_node(state, node_id, node_type):
    nodes = state.setdefault("nodes", {})
    node = nodes.setdefault(node_id, {"id": node_id, "type": node_type, "score": 10.0, "accessCount": 0, "deliberationCount": 0, "created": datetime.now().isoformat()})
    node["lastAccess"] = datetime.now().isoformat()
    node["accessCount"] += 1
    cfg = state.get("config", DEFAULT_CONFIG).get("scoring", DEFAULT_CONFIG["scoring"])
    node["score"] = score_node(node, cfg)

def deliberate_node(state, node_id, node_type):
    nodes = state.setdefault("nodes", {})
    node = nodes.setdefault(node_id, {"id": node_id, "type": node_type, "score": 10.0, "accessCount": 0, "deliberationCount": 0, "created": datetime.now().isoformat()})
    node["deliberationCount"] += 1
    cfg = state.get("config", DEFAULT_CONFIG).get("scoring", DEFAULT_CONFIG["scoring"])
    node["score"] = score_node(node, cfg)

def update_hot_agents(state, tool_id):
    cfg = state.get("config", DEFAULT_CONFIG).get("hotAgents", DEFAULT_CONFIG["hotAgents"])
    if not cfg["enabled"]:
        return
    hot = state.setdefault("hotAgents", {})
    now = datetime.now()
    threshold = now - timedelta(hours=cfg["recentThresholdHours"])

    agent_scores = []
    for node_id, node in state.get("nodes", {}).items():
        if node.get("type") != "agent":
            continue
        last = datetime.fromisoformat(node["lastAccess"]) if node.get("lastAccess") else None
        if last and last >= threshold:
            last_boost = node.get("lastBoost")
            if not last_boost or (now - datetime.fromisoformat(last_boost)) > timedelta(hours=cfg["recentThresholdHours"]):
                node["score"] += cfg["boostOnRecentUse"]
                node["lastBoost"] = now.isoformat()
        agent_scores.append((node_id, node.get("score", 0)))

    agent_scores.sort(key=lambda x: x[1], reverse=True)
    hot[tool_id] = [aid for aid, _ in agent_scores[:cfg["maxHot"]]]

def prune_nodes(state, dry_run=False):
    cfg = state.get("config", DEFAULT_CONFIG).get("expiry", DEFAULT_CONFIG["expiry"])
    if not cfg["enabled"]:
        return []

    removed = []
    nodes = state.get("nodes", {})
    max_age = timedelta(days=cfg["maxAgeDays"])
    now = datetime.now()

    for node_id, node in list(nodes.items()):
        if cfg["keepDeliberations"] and node.get("type") == "deliberation":
            continue

        score = node.get("score", 0)
        if score < cfg["pruneBelowScore"]:
            if not dry_run:
                del nodes[node_id]
            removed.append(node_id)
            continue

        created = datetime.fromisoformat(node.get("created", now.isoformat()))
        if now - created > max_age:
            if not dry_run:
                del nodes[node_id]
            removed.append(node_id)

    if not dry_run:
        state["lastPrune"] = now.isoformat()
    return removed

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        safe = text.encode('ascii', errors='replace').decode('ascii')
        print(safe)

def cmd_score(args):
    state = load_state()
    nodes = sorted(state.get("nodes", {}).values(), key=lambda x: x.get("score", 0), reverse=True)
    safe_print(f"\n{b('NTM Scores')}\n")
    safe_print(f"  {G}Score{Z}  {C}Type{Z}     {C}ID{Z}")
    safe_print(f"  {'-'*20}")
    for n in nodes[:20]:
        safe_print(f"  {n.get('score',0):6.2f}  {n.get('type',''):9s} {n.get('id','')}")
    safe_print(f"\n  Total nodes: {len(nodes)}")
    safe_print(f"  Sessions: {state.get('sessions',0)}")
    hot = state.get("hotAgents", {})
    if hot:
        safe_print(f"\n  Hot agents per tool:")
        for tool, agents in hot.items():
            safe_print(f"    {tool}: {', '.join(agents[:3])}")
    safe_print("")

def cmd_prune(args):
    state = load_state()
    cfg = state.get("config", DEFAULT_CONFIG).get("expiry", DEFAULT_CONFIG["expiry"])
    removed = prune_nodes(state, dry_run=args.dry_run)
    if args.dry_run:
        print(f"\n{y('DRY RUN')} — would remove {len(removed)} nodes:")
        for r in removed:
            print(f"  {r}")
    else:
        print(f"\n{g('Pruned')} {len(removed)} nodes")
        save_state(state)
    print()

def cmd_access(args):
    state = load_state()
    access_node(state, args.node_id, getattr(args, 'type', None) or "memory")
    state["sessions"] = state.get("sessions", 0) + 1
    update_hot_agents(state, args.node_id)
    save_state(state)
    node = state["nodes"].get(args.node_id, {})
    safe_print(g(f"Accessed: {args.node_id} (score: {node.get('score',0):.2f})"))

def cmd_deliberate(args):
    state = load_state()
    deliberate_node(state, args.node_id, getattr(args, 'type', None) or "agent")
    update_hot_agents(state, args.node_id)
    save_state(state)
    node = state["nodes"].get(args.node_id, {})
    safe_print(g(f"Deliberated: {args.node_id} (score: {node.get('score',0):.2f})"))

def cmd_config(args):
    state = load_state()
    cfg = state.get("config", DEFAULT_CONFIG)
    print(f"\n{b('NTM Config v'+cfg.get('version','?'))}\n")
    for section, data in cfg.items():
        if isinstance(data, dict):
            print(f"  {C}{section}{Z}:")
            for k, v in data.items():
                print(f"    {k}: {v}")
    print()

def cmd_hots(args):
    state = load_state()
    hot = state.get("hotAgents", {})
    if not hot:
        print(f"\n{y('No hot agents yet')}\n")
        return
    print(f"\n{b('Hot Agents')}\n")
    for tool, agents in hot.items():
        print(f"  {G}{tool}{Z}: {', '.join(agents)}")
    print()

def main():
    import argparse
    p = argparse.ArgumentParser(prog="novahiz ntm")
    sub = p.add_subparsers()

    sc = sub.add_parser("score", help="Show node scores")
    sc.set_defaults(fn=cmd_score)

    pr = sub.add_parser("prune", help="Prune expired nodes")
    pr.add_argument("--dry-run", action="store_true", help="Show what would be pruned")
    pr.set_defaults(fn=cmd_prune)

    ac = sub.add_parser("access", help="Record node access")
    ac.add_argument("node_id"); ac.add_argument("--type", default="memory")
    ac.set_defaults(fn=cmd_access)

    dl = sub.add_parser("deliberate", help="Record deliberation")
    dl.add_argument("node_id"); dl.add_argument("--type", default="agent")
    dl.set_defaults(fn=cmd_deliberate)

    cf = sub.add_parser("config", help="Show NTM config")
    cf.set_defaults(fn=cmd_config)

    ht = sub.add_parser("hots", help="Show hot agents")
    ht.set_defaults(fn=cmd_hots)

    if len(sys.argv) >= 3 and sys.argv[1] == "ntm":
        argv_start = 2
    else:
        argv_start = 1
    args = p.parse_args(sys.argv[argv_start:] if len(sys.argv) > argv_start else [])
    if hasattr(args, "fn"):
        args.fn(args)
    else:
        p.print_help()

if __name__ == "__main__":
    main()