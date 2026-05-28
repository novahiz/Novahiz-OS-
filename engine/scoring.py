"""
Scoreboard — Suivi des exécutions et scores des agents.
Met à jour ~/.opencode/config/scoreboard.json à chaque exécution.
"""
import json
import os
from datetime import datetime
from typing import Any

SCOREBOARD_PATH = os.path.expanduser("~/.opencode/config/scoreboard.json")


class Scoreboard:
    """Enregistre les exécutions et met à jour les scores des agents."""

    def __init__(self, path: str = SCOREBOARD_PATH):
        self.path = path
        self._data: dict[str, Any] = {}
        self._loaded = False

    def load(self) -> bool:
        try:
            with open(self.path, encoding="utf-8") as f:
                self._data = json.load(f)
            self._loaded = True
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            self._data = {"version": "3.0", "agents": {}, "history": [], "updated": ""}
            self._loaded = True
            return False

    @property
    def agents(self) -> dict[str, dict]:
        if not self._loaded:
            self.load()
        return self._data.setdefault("agents", {})

    def _save(self):
        self._data["updated"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    def record_execution(self, agent_id: str, task: str, success: bool, duration: float, metadata: dict | None = None):
        """Enregistre une exécution et met à jour le score."""
        self.load()
        agents = self.agents

        if agent_id not in agents:
            agents[agent_id] = {"tasks": 0, "success": 0, "avg_time": 0.0, "score": 85}

        a = agents[agent_id]
        a["tasks"] = (a.get("tasks", 0) or 0) + 1
        a["success"] = (a.get("success", 0) or 0) + (1 if success else 0)
        old_avg = a.get("avg_time", 0) or 0
        a["avg_time"] = round((old_avg * (a["tasks"] - 1) + duration) / a["tasks"], 2)

        # Ajustement dynamique du score
        if success:
            a["score"] = min(100, (a.get("score", 85) or 85) + 0.5)
        else:
            a["score"] = max(50, (a.get("score", 85) or 85) - 2)

        # Historique
        history = self._data.setdefault("history", [])
        history.append({
            "agent": agent_id,
            "task": task[:100],
            "success": success,
            "duration": round(duration, 2),
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        })
        if len(history) > 1000:
            self._data["history"] = history[-1000:]

        self._save()

    def get_stats(self, agent_id: str | None = None) -> dict:
        """Stats globales ou pour un agent spécifique."""
        self.load()
        if agent_id:
            a = self.agents.get(agent_id)
            if a:
                return {"agent": agent_id, **a}
            return {"agent": agent_id, "error": "Agent not found"}
        agents = self.agents
        total_tasks = sum(a.get("tasks", 0) for a in agents.values())
        total_success = sum(a.get("success", 0) for a in agents.values())
        return {
            "total_agents": len(agents),
            "total_tasks": total_tasks,
            "total_success": total_success,
            "success_rate": round(total_success / max(total_tasks, 1) * 100, 1),
        }

    def get_history(self, limit: int = 20) -> list[dict]:
        self.load()
        return self._data.get("history", [])[-limit:]

    def reset(self, agent_id: str | None = None):
        """Reset scores pour un agent ou tous."""
        self.load()
        if agent_id:
            if agent_id in self.agents:
                self.agents[agent_id] = {"tasks": 0, "success": 0, "avg_time": 0.0, "score": 85}
        else:
            for a in self.agents:
                self.agents[a] = {"tasks": 0, "success": 0, "avg_time": 0.0, "score": 85}
        self._save()
