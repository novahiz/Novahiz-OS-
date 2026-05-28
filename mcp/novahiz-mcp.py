#!/usr/bin/env python3
"""
NovaHiz MCP Server v4.0 — Engine-Driven Full Automation
Moteur de routage intelligent + exécution + scoreboard + council
Utilise engine/ (modulaire) pour toutes les opérations.
"""
import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path

# Ajoute engine/ au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine import AgentRegistry, Router, Scoreboard, Executor
from engine.plugin import PluginManager

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
CONFIG_DIR = os.path.join(NOVAHIZ_DIR, "config")
LOGS_DIR = os.path.join(NOVAHIZ_DIR, "logs")
EXECUTIONS_DIR = os.path.join(NOVAHIZ_DIR, "executions")

for d in [CONFIG_DIR, LOGS_DIR, EXECUTIONS_DIR]:
    os.makedirs(d, exist_ok=True)

# Instances globales du moteur
_registry = AgentRegistry()
_router = Router(_registry)
_scoreboard = Scoreboard()
_executor = Executor()
_plugin_manager = PluginManager()
_plugin_manager.load_all()


# =============================================================================
# LOGGING
# =============================================================================
def log(level, msg):
    log_file = os.path.join(LOGS_DIR, "mcp-server-v4.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{level}] {msg}\n")
    except Exception:
        pass


# =============================================================================
# TOOL HANDLERS
# =============================================================================

def handle_route(task: str) -> dict:
    """Route une tâche vers l'agent optimal."""
    log("INFO", f"Routing: {task}")
    result = _router.route(task)
    if result["success"]:
        log("INFO", f"Routed to {result['primary']['agent_id']} ({result['primary']['confidence']})")
    return result


def handle_execute(agent: str, task: str, mode: str = "opencode") -> dict:
    """Exécute une tâche avec un agent spécifique."""
    log("INFO", f"Execute: {agent} → {task[:50]}")
    result = _executor.execute(agent, task, mode)
    return result


def handle_auto(task: str, mode: str = "opencode") -> dict:
    """Route + Execute automatiquement."""
    log("INFO", f"Auto: {task[:50]}")
    route_result = _router.route(task)
    if not route_result["success"]:
        return {"success": False, "error": "Routing failed", "route_result": route_result}
    agent = route_result["primary"]["agent_id"]
    exec_result = _executor.execute(agent, task, mode)
    return {
        "success": True,
        "agent": agent,
        "confidence": route_result["primary"]["confidence"],
        "complexity": route_result["complexity"],
        "execution": exec_result,
    }


def handle_council(task: str) -> dict:
    """Délibération multi-agent (Council des sages)."""
    log("INFO", f"Council: {task[:50]}")
    multi = _router.route_multi(task, max_agents=5)
    if not multi["success"]:
        return multi
    return {
        "success": True,
        "task": task,
        "complexity": multi["complexity"],
        "agents": multi["agents"],
        "count": multi["count"],
        "method": "weighted_deliberation",
        "consensus_threshold": 0.6,
    }


def handle_list_agents() -> dict:
    """Liste tous les agents disponibles."""
    log("INFO", "Listing agents")
    agents = _registry.list()
    return {"success": True, "count": len(agents), "agents": agents}


def handle_search(query: str) -> dict:
    """Cherche des agents par mot-clé."""
    log("INFO", f"Search: {query}")
    results = _registry.search(query)
    return {"success": True, "query": query, "count": len(results), "agents": results}


def handle_health() -> dict:
    """Health check complet."""
    log("INFO", "Health check")
    plugins = _plugin_manager.list_all()
    checks = {
        "registry_loaded": _registry.load(),
        "agents_count": _registry.count(),
        "executions_dir": os.path.isdir(EXECUTIONS_DIR),
        "logs_dir": os.path.isdir(LOGS_DIR),
        "engine_module": True,
        "plugins": len(plugins),
        "plugin_setup": [p.to_dict() if hasattr(p, 'to_dict') else str(p) for p in _plugin_manager.list_active()],
    }
    all_ok = all(isinstance(v, bool) and v for v in checks.values() if isinstance(v, bool))
    stats = _scoreboard.get_stats()
    return {
        "success": all_ok,
        "status": "healthy" if all_ok else "degraded",
        "checks": checks,
        "plugins": [p.to_dict() for p in plugins],
        "stats": stats,
        "timestamp": datetime.now().isoformat(),
    }


def handle_execution_status(execution_id: str = None) -> dict:
    """Statut des exécutions."""
    return _executor.status(execution_id)


def handle_scoreboard(agent_id: str = None) -> dict:
    """Scoreboard des agents."""
    return _scoreboard.get_stats(agent_id)


def handle_history(limit: int = 20) -> dict:
    """Historique des exécutions."""
    history = _scoreboard.get_history(limit)
    return {"success": True, "count": len(history), "history": history}


def handle_plugin_info() -> dict:
    """Info sur les plugins chargés."""
    plugins = _plugin_manager.list_all()
    return {
        "success": True,
        "count": len(plugins),
        "plugins": [p.to_dict() for p in plugins],
    }


def handle_execute_and_delegate(agent: str, task: str) -> dict:
    """
    Execute et crée un fichier de délégation pour OpenCode subagent.
    Le fichier .task.json est détectable par les skills Novahiz.
    """
    log("INFO", f"Execute+Delegate: {agent} → {task[:50]}")
    exec_result = _executor.execute(agent, task, mode="opencode")

    # Créer un fichier de délégation visible par les subagents
    if exec_result.get("success"):
        delegation = {
            "agent": agent,
            "task": task,
            "execution_id": exec_result.get("execution_id", "unknown"),
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "instructions": f"Execute this task as {agent} using OpenCode subagent tools.",
        }
        delegation_path = os.path.join(
            EXECUTIONS_DIR,
            f"delegation_{exec_result.get('execution_id', 'unknown')}.task.json",
        )
        try:
            with open(delegation_path, "w", encoding="utf-8") as f:
                json.dump(delegation, f, indent=2, ensure_ascii=False)
            exec_result["delegation_file"] = delegation_path
        except Exception as e:
            exec_result["delegation_warning"] = str(e)

    return exec_result


# =============================================================================
# MCP TOOL DEFINITIONS
# =============================================================================
MCP_TOOLS = {
    "novahiz_route": {
        "description": "Route a task to the optimal Novahiz agent using smart-router (multi-criteria scoring)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The task to route"},
            },
            "required": ["task"],
        },
        "handler": lambda task: handle_route(task),
    },
    "novahiz_execute": {
        "description": "Execute a task with a specific Novahiz agent",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string", "description": "Agent ID"},
                "task": {"type": "string", "description": "The task to execute"},
                "mode": {
                    "type": "string",
                    "enum": ["direct", "opencode"],
                    "description": "Execution mode (default: opencode)",
                },
            },
            "required": ["agent", "task"],
        },
        "handler": lambda agent, task, mode="opencode": handle_execute(agent, task, mode),
    },
    "novahiz_auto": {
        "description": "AUTOMATIC: Route AND execute a task with the optimal agent (FULLY AUTOMATED)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The task to route and execute"},
                "mode": {
                    "type": "string",
                    "enum": ["direct", "opencode"],
                    "description": "Execution mode (default: opencode)",
                },
            },
            "required": ["task"],
        },
        "handler": lambda task, mode="opencode": handle_auto(task, mode),
    },
    "novahiz_council": {
        "description": "Multi-agent deliberation (Council of Sages). Routes to top 3-5 agents for complex tasks.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "The complex task for council deliberation"},
            },
            "required": ["task"],
        },
        "handler": lambda task: handle_council(task),
    },
    "novahiz_list_agents": {
        "description": "List all available Novahiz agents with their domains and scores",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "handler": lambda: handle_list_agents(),
    },
    "novahiz_search": {
        "description": "Search for agents by keyword",
        "inputSchema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
            "required": ["query"],
        },
        "handler": lambda query: handle_search(query),
    },
    "novahiz_health": {
        "description": "System health check",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "handler": lambda: handle_health(),
    },
    "novahiz_execution_status": {
        "description": "Get execution status",
        "inputSchema": {
            "type": "object",
            "properties": {
                "execution_id": {"type": "string", "description": "Execution ID (optional)"},
            },
            "required": [],
        },
        "handler": lambda execution_id=None: handle_execution_status(execution_id),
    },
    "novahiz_scoreboard": {
        "description": "Get agent scoreboard stats",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent ID (optional, returns all if empty)"},
            },
            "required": [],
        },
        "handler": lambda agent_id=None: handle_scoreboard(agent_id),
    },
    "novahiz_history": {
        "description": "Get execution history",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "number", "description": "Max entries (default: 20)"},
            },
            "required": [],
        },
        "handler": lambda limit=20: handle_history(limit),
    },
    "novahiz_plugin_info": {
        "description": "Get info on all loaded plugins",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
        "handler": lambda: handle_plugin_info(),
    },
    "novahiz_execute_and_delegate": {
        "description": "Execute a task with a specific agent AND create a delegation file for OpenCode subagents",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent": {"type": "string", "description": "Agent ID"},
                "task": {"type": "string", "description": "The task to execute"},
            },
            "required": ["agent", "task"],
        },
        "handler": lambda agent, task: handle_execute_and_delegate(agent, task),
    },
}


# =============================================================================
# MCP SERVER LOOP (MCP Protocol v2024-11-05 compliant)
# =============================================================================
def run_mcp_server():
    """Run MCP server using stdio transport."""
    log("INFO", "Starting Novahiz MCP server v4.0 (stdio)")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                log("INFO", "STDIN closed, shutting down")
                break

            request = json.loads(line.strip())
            req_id = request.get("id")
            method = request.get("method", "")
            log("DEBUG", f"Request: {method} (id={req_id})")

            # Notification (no id) → no response
            if req_id is None:
                continue

            # Initialize
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "novahiz-mcp", "version": "4.0.0"},
                    },
                }
                log("INFO", "MCP initialized")

            # tools/list
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": [
                            {
                                "name": name,
                                "description": tool["description"],
                                "inputSchema": tool["inputSchema"],
                            }
                            for name, tool in MCP_TOOLS.items()
                        ]
                    },
                }
                log("INFO", f"Listed {len(MCP_TOOLS)} tools")

            # tools/call
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})

                if tool_name in MCP_TOOLS:
                    try:
                        handler = MCP_TOOLS[tool_name]["handler"]
                        result = handler(**arguments)
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(result, indent=2, ensure_ascii=False),
                                    }
                                ]
                            },
                        }
                        log("SUCCESS", f"Tool '{tool_name}' executed")
                    except Exception as e:
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(
                                            {"success": False, "error": str(e)},
                                            indent=2,
                                        ),
                                    }
                                ]
                            },
                        }
                        log("ERROR", f"Tool '{tool_name}' failed: {e}")
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
                    }

            # resources/list
            elif method == "resources/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"resources": []},
                }

            # prompts/list
            elif method == "prompts/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"prompts": []},
                }

            # Unknown method
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not supported: {method}"},
                }

            print(json.dumps(response), flush=True)

        except json.JSONDecodeError as e:
            log("ERROR", f"JSON decode error: {e}")
        except Exception as e:
            log("ERROR", f"Server error: {e}")

    log("INFO", "MCP server stopped")


# =============================================================================
# CLI MODE
# =============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mcp":
        run_mcp_server()
    elif len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "route" and len(sys.argv) > 2:
            print(json.dumps(handle_route(" ".join(sys.argv[2:])), indent=2))
        elif cmd == "auto" and len(sys.argv) > 2:
            print(json.dumps(handle_auto(" ".join(sys.argv[2:])), indent=2))
        elif cmd == "council" and len(sys.argv) > 2:
            print(json.dumps(handle_council(" ".join(sys.argv[2:])), indent=2))
        elif cmd == "execute" and len(sys.argv) > 3:
            print(json.dumps(handle_execute(sys.argv[2], " ".join(sys.argv[3:])), indent=2))
        elif cmd == "agents":
            print(json.dumps(handle_list_agents(), indent=2))
        elif cmd == "search" and len(sys.argv) > 2:
            print(json.dumps(handle_search(" ".join(sys.argv[2:])), indent=2))
        elif cmd == "health":
            print(json.dumps(handle_health(), indent=2))
        elif cmd == "status":
            eid = sys.argv[2] if len(sys.argv) > 2 else None
            print(json.dumps(handle_execution_status(eid), indent=2))
        elif cmd == "score":
            aid = sys.argv[2] if len(sys.argv) > 2 else None
            print(json.dumps(handle_scoreboard(aid), indent=2))
        elif cmd == "history":
            lim = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            print(json.dumps(handle_history(lim), indent=2))
