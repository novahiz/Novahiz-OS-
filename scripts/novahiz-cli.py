#!/usr/bin/env python3
"""
Novahiz CLI — Point d'entrée en ligne de commande.
Usage:
  nv route <task>       Router une tâche
  nv council <task>     Délibération multi-agent
  nv execute <a> <t>    Exécuter avec un agent
  nv auto <task>        Router + exécuter automatiquement
  nv agents             Lister les agents
  nv search <q>         Chercher des agents
  nv health             Health check
  nv status [id]        Statut exécution
  nv score [agent]      Scoreboard
  nv history [n]        Historique
  nv plugins            Lister les plugins
  nv monitor start      Démarrer monitoring
  nv monitor stop       Arrêter monitoring
  nv monitor status     Status monitoring
  nv errors [filter]    Voir erreurs
  nv autocorrect run    Lancer auto-correction
  nv learn <agent>      Apprentissages agent
  nv system health      Santé système
  nv help               Aide
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine import AgentRegistry, Router, Scoreboard, Executor
from engine.plugin import PluginManager


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_route(args):
    if not args:
        print("❌ Usage: nv route <task>")
        return
    task = " ".join(args)
    router = Router()
    result = router.route(task)
    print_json(result)


def cmd_council(args):
    if not args:
        print("❌ Usage: nv council <task>")
        return
    task = " ".join(args)
    router = Router()
    result = router.route_multi(task, max_agents=5)
    print_json(result)


def cmd_execute(args):
    if len(args) < 2:
        print("❌ Usage: nv execute <agent> <task>")
        return
    agent = args[0]
    task = " ".join(args[1:])
    executor = Executor()
    result = executor.execute(agent, task)
    print_json(result)


def cmd_auto(args):
    if not args:
        print("❌ Usage: nv auto <task>")
        return
    task = " ".join(args)
    router = Router()
    route_result = router.route(task)
    if not route_result["success"]:
        print_json({"success": False, "error": "Routing failed", "route": route_result})
        return
    agent = route_result["primary"]["agent_id"]
    executor = Executor()
    exec_result = executor.execute(agent, task)
    print_json({
        "success": True,
        "task": task,
        "agent": agent,
        "confidence": route_result["primary"]["confidence"],
        "complexity": route_result["complexity"],
        "alternatives": route_result.get("alternatives", []),
        "execution": exec_result,
    })


def cmd_agents(args):
    registry = AgentRegistry()
    registry.load()
    agents = registry.list()
    print(f"🧠 {len(agents)} agents disponibles:\n")
    for a in agents:
        score_str = f"{a['score']}/100"
        print(f"  {a['id']:25s}  {a['domain']:15s}  score={score_str:7s}  {a['description']}")


def cmd_search(args):
    if not args:
        print("❌ Usage: nv search <query>")
        return
    query = " ".join(args)
    registry = AgentRegistry()
    registry.load()
    results = registry.search(query)
    if results:
        print(f"🔍 {len(results)} résultat(s) pour '{query}':\n")
        for a in results:
            print(f"  {a['id']:25s}  {a['domain']:15s}  score={a['score']}")
    else:
        print(f"❌ Aucun agent trouvé pour '{query}'")


def cmd_health(args):
    registry = AgentRegistry()
    router = Router()
    scoreboard = Scoreboard()
    executor = Executor()
    pm = PluginManager()

    reg_ok = registry.load()
    plugins = pm.discover()

    checks = {
        "registry": reg_ok,
        "agents_count": registry.count(),
        "plugins": len(plugins),
        "executions_dir": os.path.isdir(os.path.join(os.path.expanduser("~/.opencode"), "executions")),
    }
    stats = scoreboard.get_stats()

    print(f"📊 NOVAHIZ OS HEALTH\n")
    print(f"  Registry:     {'✅' if reg_ok else '❌'} ({registry.count()} agents)")
    print(f"  Plugins:      {len(plugins)} découverts")
    if plugins:
        for p in plugins:
            print(f"    · {p.name} v{p.version}")
    print(f"  Executions:   {stats['total_tasks']} tasks, {stats['success_rate']}% success")
    print(f"  Scoreboard:   {stats['total_agents']} agents suivis")
    print(f"  Status:       {'✅ HEALTHY' if all(v if isinstance(v, bool) else True for v in checks.values()) else '⚠️ DEGRADED'}")


def cmd_status(args):
    executor = Executor()
    exec_id = args[0] if args else None
    result = executor.status(exec_id)
    print_json(result)


def cmd_score(args):
    scoreboard = Scoreboard()
    agent_id = args[0] if args else None
    result = scoreboard.get_stats(agent_id)
    print_json(result)


def cmd_history(args):
    scoreboard = Scoreboard()
    limit = int(args[0]) if args else 20
    result = scoreboard.get_history(limit)
    if result:
        print(f"📜 {len(result)} entrées d'historique:\n")
        for h in reversed(result):
            icon = "✅" if h.get("success") else "❌"
            print(f"  {icon} {h['agent']:25s} {h['task'][:50]:50s} {h.get('duration', 0):.1f}s")
    else:
        print("📜 Aucun historique")


def cmd_plugins(args):
    pm = PluginManager()
    plugins = pm.discover()
    if plugins:
        print(f"🔌 {len(plugins)} plugin(s):\n")
        for p in plugins:
            status = "✅" if os.path.isfile(os.path.join(p.path, "plugin.py")) else "⚠️"
            print(f"  {status} {p.name:25s} v{p.version:8s}  {p.description}")
    else:
        print("🔌 Aucun plugin installé")
        print("   → Crée un dossier dans ~/.opencode/plugins/<nom>/ avec plugin.json + plugin.py")


def cmd_monitor(args):
    """Delegate to monitoring CLI."""
    from scripts.monitoring_cli import main as monitor_main
    # Prepend 'monitor' to args
    sys.argv = ['monitoring-cli', 'monitor'] + args
    monitor_main()


def cmd_errors(args):
    """Delegate to monitoring CLI errors."""
    from scripts.monitoring_cli import main as monitor_main
    sys.argv = ['monitoring-cli', 'errors'] + args
    monitor_main()


def cmd_autocorrect(args):
    """Delegate to monitoring CLI autocorrect."""
    from scripts.monitoring_cli import main as monitor_main
    sys.argv = ['monitoring-cli', 'autocorrect'] + args
    monitor_main()


def cmd_agents_learn(args):
    """View agent learnings."""
    from scripts.monitoring_cli import main as monitor_main
    sys.argv = ['monitoring-cli', 'agents', 'learn'] + args
    monitor_main()


def cmd_system(args):
    """Delegate to monitoring CLI system."""
    from scripts.monitoring_cli import main as monitor_main
    sys.argv = ['monitoring-cli', 'system'] + args
    monitor_main()


def cmd_help(args):
    print(__doc__)


COMMANDS = {
    "route": cmd_route,
    "council": cmd_council,
    "execute": cmd_execute,
    "auto": cmd_auto,
    "agents": cmd_agents,
    "search": cmd_search,
    "health": cmd_health,
    "status": cmd_status,
    "score": cmd_score,
    "history": cmd_history,
    "plugins": cmd_plugins,
    "monitor": cmd_monitor,
    "errors": cmd_errors,
    "autocorrect": cmd_autocorrect,
    "learn": cmd_agents_learn,
    "system": cmd_system,
    "help": cmd_help,
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]
    COMMANDS[cmd](args)


if __name__ == "__main__":
    main()
