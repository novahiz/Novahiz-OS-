"""
Executor — Exécute les tâches via les subagents OpenCode.
Crée des fichiers d'exécution → OpenCode les détecte et les exécute.
"""
import json
import os
import time
from datetime import datetime

from .scoring import Scoreboard

EXEC_DIR = os.path.expanduser("~/.opencode/executions")


class Executor:
    """Gère l'exécution des tâches et la mise à jour du scoreboard."""

    def __init__(self):
        self.scoreboard = Scoreboard()
        os.makedirs(EXEC_DIR, exist_ok=True)

    def execute(self, agent_id: str, task: str, mode: str = "opencode") -> dict:
        """
        Exécute une tâche via un agent.
        mode="opencode": crée un fichier que OpenCode peut détecter (recommandé)
        mode="direct": crée un fichier d'exécution simple
        """
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        timestamp = datetime.now().isoformat()
        t_start = time.time()

        execution = {
            "id": execution_id,
            "agent": agent_id,
            "task": task,
            "mode": mode,
            "status": "pending",
            "created": timestamp,
            "updated": timestamp,
            "t_start": t_start,
        }

        # Sauvegarde le fichier d'exécution
        file_path = os.path.join(EXEC_DIR, f"{execution_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(execution, f, indent=2)

        # Si mode opencode, crée aussi un fichier de requête que OpenCode peut intercepter
        if mode == "opencode":
            request_file = os.path.join(EXEC_DIR, "current_request.json")
            with open(request_file, "w", encoding="utf-8") as f:
                json.dump({
                    "type": "opencode_subagent_call",
                    "agent": agent_id,
                    "task": task,
                    "execution_id": execution_id,
                    "timestamp": timestamp,
                    "callback": os.path.join(EXEC_DIR, "current_response.json"),
                }, f, indent=2)

        # Le vrai résultat sera enregistré dans le scoreboard
        # quand complete() sera appelé plus tard.

        return {
            "success": True,
            "execution_id": execution_id,
            "agent": agent_id,
            "task": task,
            "status": "pending",
            "instructions": {
                "action": "execute_subagent",
                "subagent": agent_id,
                "prompt": task,
            },
        }

    def complete(self, execution_id: str, success: bool, duration: float | None = None):
        """Marque une exécution comme terminée et met à jour le scoreboard avec le vrai résultat."""
        file_path = os.path.join(EXEC_DIR, f"{execution_id}.json")
        try:
            with open(file_path, encoding="utf-8") as f:
                execution = json.load(f)
            execution["status"] = "completed" if success else "failed"
            execution["success"] = success
            execution["updated"] = datetime.now().isoformat()

            # Calcul de la durée réelle
            t_start = execution.get("t_start")
            if duration is not None:
                real_duration = duration
            elif t_start:
                real_duration = time.time() - t_start
            else:
                real_duration = 0.0
            execution["duration"] = round(real_duration, 2)

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(execution, f, indent=2)

            # Mise à jour du scoreboard avec le vrai résultat
            self.scoreboard.record_execution(
                agent_id=execution.get("agent", "unknown"),
                task=execution.get("task", ""),
                success=success,
                duration=real_duration,
                metadata={"execution_id": execution_id, "status": execution["status"]},
            )
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def status(self, execution_id: str | None = None) -> dict:
        """Statut d'une ou toutes les exécutions."""
        if execution_id:
            file_path = os.path.join(EXEC_DIR, f"{execution_id}.json")
            try:
                with open(file_path, encoding="utf-8") as f:
                    return {"success": True, "execution": json.load(f)}
            except FileNotFoundError:
                return {"success": False, "error": f"Execution {execution_id} not found"}

        # Liste les 20 dernières
        executions = []
        try:
            files = sorted(os.listdir(EXEC_DIR), reverse=True)[:20]
            for fname in files:
                if fname.startswith("exec_") and fname.endswith(".json"):
                    with open(os.path.join(EXEC_DIR, fname), encoding="utf-8") as f:
                        executions.append(json.load(f))
        except OSError:
            pass

        return {"success": True, "count": len(executions), "executions": executions}

    def list_agents_with_stats(self) -> list[dict]:
        """Liste les agents avec leurs stats du scoreboard."""
        registry_items = self._get_registry_agents()
        stats = self.scoreboard.get_stats()
        agents_list = []
        for a in registry_items:
            agents_list.append({
                "id": a["id"],
                "name": a.get("name", ""),
                "domain": a.get("domain", ""),
                "type": a.get("type", ""),
                "score": a.get("score", 0),
                "description": a.get("description", ""),
                "tasks": 0,
                "success": 0,
            })
        return agents_list

    def _get_registry_agents(self):
        try:
            from .registry import AgentRegistry
            reg = AgentRegistry()
            reg.load()
            return reg.list()
        except Exception:
            return []
