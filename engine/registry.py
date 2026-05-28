"""
Agent Registry — Charge et gère le registre des 24 agents.
Source unique de vérité : ~/.opencode/config/agent-registry.json
"""
import json
import os
from typing import Any

REGISTRY_PATH = os.path.expanduser("~/.opencode/config/agent-registry.json")


class AgentRegistry:
    """Charge, valide et interroge le registre d'agents."""

    def __init__(self, path: str = REGISTRY_PATH):
        self.path = path
        self._data: dict[str, Any] = {}
        self._agents: dict[str, dict] = {}
        self._loaded = False

    def load(self) -> bool:
        """Charge le registre depuis le fichier JSON."""
        try:
            with open(self.path, encoding="utf-8") as f:
                self._data = json.load(f)
            self._agents = self._data.get("agents", {})
            self._loaded = True
            return True
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            self._agents = {}
            self._loaded = False
            return False

    @property
    def agents(self) -> dict[str, dict]:
        if not self._loaded:
            self.load()
        return self._agents

    @property
    def routing_rules(self) -> dict:
        if not self._loaded:
            self.load()
        return self._data.get("routing_rules", {})

    def get(self, agent_id: str) -> dict | None:
        return self.agents.get(agent_id)

    def list(self) -> list[dict]:
        """Retourne la liste de tous les agents avec leur metadata."""
        return [
            {
                "id": aid,
                "name": a.get("name", ""),
                "domain": a.get("domain", ""),
                "type": a.get("type", ""),
                "model": a.get("model", ""),
                "score": a.get("score", 0),
                "priority": a.get("priority", 99),
                "keywords": a.get("keywords", []),
                "complexity": a.get("complexity", []),
                "description": a.get("description", ""),
            }
            for aid, a in self.agents.items()
        ]

    def search(self, query: str) -> list[dict]:
        """Cherche des agents par mot-clé (insensible à la casse)."""
        q = query.lower()
        results = []
        for a in self.list():
            if q in a["id"].lower() or q in a["domain"].lower() or q in a["name"].lower():
                results.append(a)
                continue
            for kw in a["keywords"]:
                if q in kw.lower():
                    results.append(a)
                    break
        return results

    def count(self) -> int:
        return len(self.agents)

    def reload(self) -> bool:
        """Force le rechargement depuis le fichier."""
        self._loaded = False
        return self.load()
