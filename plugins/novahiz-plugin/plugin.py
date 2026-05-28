"""
Novahiz Base Plugin — Enregistrement des routes et stats.
Chargé automatiquement par le PluginManager au démarrage du MCP server.
"""

import json
import os
from datetime import datetime

HISTORY_FILE = os.path.expanduser("~/.opencode/plugins/novahiz-plugin/history.json")


def info():
    return {
        "name": "novahiz-plugin",
        "version": "1.0.0",
        "description": "Enregistre les routes et les stats d'exécution",
    }


def setup(engine=None):
    """Called by PluginManager on startup."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    _log("Plugin loaded", {"status": "active"})
    return {"status": "setup_ok"}


def teardown():
    _log("Plugin shutdown", {})


def _log(event: str, data: dict):
    try:
        history = []
        if os.path.isfile(HISTORY_FILE):
            with open(HISTORY_FILE, encoding="utf-8") as f:
                history = json.load(f)
        history.append({
            "event": event,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        })
        if len(history) > 500:
            history = history[-500:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass
