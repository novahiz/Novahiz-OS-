#!/usr/bin/env python3
"""
Novahiz OS CLI — v2.0

Usage:  nv <command> [args]

Commandes:
  ROUTAGE
    route <task>          Router une tâche vers le meilleur agent
    council <task>        Délibération multi-agent (Council)
    execute <agent> <t>   Exécuter une tâche avec un agent spécifique
    auto <task>           Router + exécuter automatiquement

  AGENTS
    agents                Lister les 24 agents disponibles
    search <query>        Chercher un agent par mot-clé
    score [agent]         Voir les scores de performance
    history [n]           Historique des dernières exécutions

  MODÈLES (nv model)
    model list            Configuration complète des modèles LLM
    model show <tier>     Détail d'un tier (flash/smart/premium)
    model set <t> <m>     Changer le modèle primary d'un tier
    model fallback <t> <n> <m>  Changer un fallback
    model agent <a> <t>   Déplacer un agent vers un tier
    model push            Synchroniser YAML + registres
    model reset           Retour à la configuration usine

  SYSTÈME
    health                Health check complet
    status [id]           Statut d'une exécution
    plugins               Lister les plugins chargés
    monitor start|stop|status  Monitoring daemon
    system health         Santé système détaillée

  OUTILS
    errors [filter]       Voir les erreurs
    autocorrect run       Lancer l'auto-correction
    learn <agent>         Apprentissages d'un agent

  help                    Affiche cette aide
"""
import json
import os
import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from engine import AgentRegistry, Router, Scoreboard, Executor
from engine.plugin import PluginManager


# ── ANSI colors ──────────────────────────────────────────────
class C:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    RESET = "\033[0m"


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def error(msg):
    print(f"  {C.RED}✗{C.RESET} {msg}")


def ok(msg):
    print(f"  {C.GREEN}✓{C.RESET} {msg}")


def info(msg):
    print(f"  {C.CYAN}→{C.RESET} {msg}")


# ── Command handlers ────────────────────────────────────────

def cmd_route(args):
    if not args:
        error("Usage: nv route <task>")
        return
    task = " ".join(args)
    router = Router()
    result = router.route(task)
    if result.get("success"):
        p = result["primary"]
        info(f"Routé vers {C.BOLD}{p['agent_id']}{C.RESET} (confiance: {p['confidence']})")
        if result.get("alternatives"):
            alts = ", ".join(a["agent_id"] for a in result["alternatives"])
            info(f"Alternatives: {alts}")
    print_json(result)


def cmd_council(args):
    if not args:
        error("Usage: nv council <task>")
        return
    task = " ".join(args)
    router = Router()
    result = router.route_multi(task, max_agents=5)
    if result.get("success"):
        agents = [a["agent_id"] for a in result.get("agents", [])]
        info(f"Council avec {len(agents)} agents: {', '.join(agents)}")
    print_json(result)


def cmd_execute(args):
    if len(args) < 2:
        error("Usage: nv execute <agent> <task>")
        return
    agent = args[0]
    task = " ".join(args[1:])
    info(f"Exécution avec {C.BOLD}{agent}{C.RESET}...")
    executor = Executor()
    result = executor.execute(agent, task)
    if result.get("success"):
        ok(f"Tâche exécutée (ID: {result.get('execution_id', '?')})")
    print_json(result)


def cmd_auto(args):
    if not args:
        error("Usage: nv auto <task>")
        return
    task = " ".join(args)
    router = Router()
    route_result = router.route(task)
    if not route_result["success"]:
        error("Échec du routage")
        print_json(route_result)
        return
    agent = route_result["primary"]["agent_id"]
    info(f"Routé vers {C.BOLD}{agent}{C.RESET} → exécution...")
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
    if exec_result.get("success"):
        ok("Terminé")


def cmd_agents(args):
    registry = AgentRegistry()
    registry.load()
    agents = registry.list()
    print(f"\n  {C.BOLD}{len(agents)} agents disponibles{C.RESET}\n")
    for a in agents:
        score_str = f"{a['score']}/100"
        icon = "🧠" if a.get("type") in ("subagent", "primary") else "⚙️"
        print(f"  {icon} {C.CYAN}{a['id']:25s}{C.RESET}  {a['domain']:15s}  score={score_str:7s}")
    print()


def cmd_search(args):
    if not args:
        error("Usage: nv search <query>")
        return
    query = " ".join(args)
    registry = AgentRegistry()
    registry.load()
    results = registry.search(query)
    if results:
        print(f"\n  {len(results)} résultat(s) pour '{query}':\n")
        for a in results:
            print(f"  {C.CYAN}{a['id']:25s}{C.RESET}  {a['domain']:15s}  score={a['score']}")
        print()
    else:
        error(f"Aucun agent trouvé pour '{query}'")


def cmd_health(args):
    registry = AgentRegistry()
    router = Router()
    scoreboard = Scoreboard()
    pm = PluginManager()

    reg_ok = registry.load()
    plugins = pm.discover()
    stats = scoreboard.get_stats()

    status = f"{C.GREEN}HEALTHY{C.RESET}" if reg_ok else f"{C.RED}DEGRADED{C.RESET}"
    print(f"\n  {C.BOLD}NOVAHIZ OS — Health Check{C.RESET}\n")
    print(f"  Registry     {C.GREEN}●{C.RESET if reg_ok else C.RED+'✗'+C.RESET}  {registry.count()} agents")
    print(f"  Plugins      {C.CYAN}●{C.RESET}  {len(plugins)} découverts")
    for p in plugins:
        print(f"              · {p.name} v{p.version}")
    print(f"  Exécutions   {stats['total_tasks']} tasks, {stats['success_rate']}% succès")
    print(f"  Scoreboard   {stats['total_agents']} agents suivis")
    print(f"  Status:      {status}\n")


def cmd_status(args):
    executor = Executor()
    exec_id = args[0] if args else None
    result = executor.status(exec_id)
    print_json(result)


def cmd_score(args):
    scoreboard = Scoreboard()
    agent_id = args[0] if args else None
    result = scoreboard.get_stats(agent_id)
    if agent_id:
        a = result
        icon = "✅" if a.get("success", 0) == a.get("tasks", 0) else "⚠️"
        print(f"\n  {C.CYAN}{agent_id}{C.RESET}")
        print(f"  {icon}  Tâches: {a.get('tasks', 0)} | Succès: {a.get('success', 0)} | Score: {a.get('score', 0)}\n")
    else:
        print_json(result)


def cmd_history(args):
    scoreboard = Scoreboard()
    try:
        limit = int(args[0]) if args else 20
    except (ValueError, IndexError):
        print(f"{C.RED}✗ Le nombre doit être un entier valide.{C.RESET}")
        return
    result = scoreboard.get_history(limit)
    if result:
        print(f"\n  {C.BOLD}Dernières {len(result)} exécutions:{C.RESET}\n")
        for h in reversed(result):
            icon = "✅" if h.get("success") else "❌"
            dur = h.get("duration", 0)
            dur_str = f"{dur:.1f}s" if dur else ""
            print(f"  {icon} {C.CYAN}{h['agent']:25s}{C.RESET} {h['task'][:50]:50s} {dur_str}")
        print()
    else:
        print("  Aucun historique")


def cmd_plugins(args):
    pm = PluginManager()
    plugins = pm.discover()
    if plugins:
        print(f"\n  {C.BOLD}{len(plugins)} plugin(s):{C.RESET}\n")
        for p in plugins:
            status = "✅" if os.path.isfile(os.path.join(p.path, "plugin.py")) else "⚠️"
            print(f"  {status} {C.CYAN}{p.name:25s}{C.RESET} v{p.version:8s}  {p.description}")
        print()
    else:
        print("  Aucun plugin installé")
        info("Crée un dossier dans ~/.opencode/plugins/<nom>/ avec plugin.json + plugin.py")


def cmd_model(args):
    """Délègue à model_cli.py."""
    if not args or args[0] == "help":
        print("""
  nv model — Configuration des modèles LLM

  Commandes:
    list                  Affiche toute la configuration
    show <tier>           Détail d'un tier (flash/smart/premium)
    set <tier> <model>    Change le modèle primary
    fallback <tier> <n> <model>  Change le fallback N°1/2
    agent <a> <tier>      Déplace un agent vers un tier
    push                  Synchronise tous les fichiers
    reset                 Retour à la config usine

  Exemples:
    nv model list
    nv model set premium openrouter/qwen/qwen3.6-plus
    nv model agent neo-security premium
    nv model push
""")
        return
    from scripts.model_cli import main as model_main
    sys.argv = ['model-cli'] + args
    model_main()


def cmd_monitor(args):
    from scripts.monitoring_cli import main as monitor_main
    sys.argv = ['monitoring-cli', 'monitor'] + args
    monitor_main()


def cmd_errors(args):
    from scripts.monitoring_cli import main as monitor_main
    sys.argv = ['monitoring-cli', 'errors'] + args
    monitor_main()


def cmd_autocorrect(args):
    from scripts.monitoring_cli import main as monitor_main
    sys.argv = ['monitoring-cli', 'autocorrect'] + args
    monitor_main()


def cmd_agents_learn(args):
    from scripts.monitoring_cli import main as monitor_main
    sys.argv = ['monitoring-cli', 'agents', 'learn'] + args
    monitor_main()


def cmd_system(args):
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
    "model": cmd_model,
    "monitor": cmd_monitor,
    "errors": cmd_errors,
    "autocorrect": cmd_autocorrect,
    "learn": cmd_agents_learn,
    "system": cmd_system,
    "help": cmd_help,
}


def suggest(cmd, known):
    """Trouve la commande la plus proche (Damerau-Levenshtein simple)."""
    best, best_score = None, 999
    for k in known:
        if k == cmd:
            return cmd
        d = sum(1 for a, b in zip(cmd, k) if a != b) + abs(len(cmd) - len(k))
        if d < best_score:
            best_score = d
            best = k
    if best_score <= 3:
        return best
    return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    # help explicite
    if cmd in ("help", "-h", "--help"):
        print(__doc__)
        return

    # commande inconnue → suggestion
    if cmd not in COMMANDS:
        error(f"Commande inconnue: '{cmd}'")
        suggestion = suggest(cmd, list(COMMANDS.keys()))
        if suggestion and suggestion != cmd:
            info(f"Commande la plus proche: '{suggestion}'")
        print("  Tape 'nv help' pour la liste complète.")
        return

    COMMANDS[cmd](args)


if __name__ == "__main__":
    main()
