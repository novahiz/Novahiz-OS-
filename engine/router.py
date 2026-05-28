"""
Router — Moteur de routage intelligent.
Utilise : matching keywords + priorité + score → confidence score.
Score dynamique depuis scoreboard.json (feedback loop).

Flow:
  1. Classifie la complexité (SIMPLE / MEDIUM / COMPLEX)
  2. Match keywords avec chaque agent
  3. Calcule le confidence score (keyword_match * 0.6 + priority * 0.3 + score * 0.1)
  4. Retourne le(s) meilleur(s) agent(s)

Configuration externalisée dans ~/.opencode/config/routing-rules.json
"""
from __future__ import annotations
import json
import os
import re
import time

from .registry import AgentRegistry

SCOREBOARD_PATH = os.path.expanduser("~/.opencode/config/scoreboard.json")

# Poids de scoring par défaut (surchargés par routing-rules.json)
DEFAULT_WEIGHTS = {"keyword_match_weight": 0.6, "priority_weight": 0.3, "score_weight": 0.1}
MIN_CONFIDENCE = 0.4
MULTI_AGENT_THRESHOLD = 0.7

DEFAULT_COMPLEXITY_KEYWORDS = {
    "SIMPLE": ["how", "what", "explain", "simple", "quick", "basic", "define", "show"],
    "MEDIUM": ["build", "create", "implement", "fix", "optimize", "configure", "add", "update", "refactor"],
    "COMPLEX": ["architecture", "system", "design", "scale", "enterprise", "production", "multi", "distributed", "highload"],
}

ROUTING_RULES_PATH = os.path.expanduser("~/.opencode/config/routing-rules.json")


def _load_routing_config() -> dict:
    """Charge la configuration depuis routing-rules.json (pas de cache — appel unique par init)."""
    try:
        with open(ROUTING_RULES_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


_routing_config_cache: dict | None = None


class RouteResult:
    """Résultat du routage pour un agent."""

    def __init__(self, agent_id: str, agent_info: dict, confidence: float, match_reason: str):
        self.agent_id = agent_id
        self.agent_info = agent_info
        self.confidence = round(confidence, 3)
        self.match_reason = match_reason

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.agent_info.get("name", ""),
            "domain": self.agent_info.get("domain", ""),
            "type": self.agent_info.get("type", ""),
            "confidence": self.confidence,
            "match_reason": self.match_reason,
        }

    def __repr__(self):
        return f"<RouteResult {self.agent_id}: {self.confidence}>"


class Router:
    """Routeur intelligent. Classe une tâche et trouve le meilleur agent."""

    def __init__(self, registry: AgentRegistry | None = None):
        self.registry = registry or AgentRegistry()
        self.registry.load()
        rules = self.registry.routing_rules
        self.weights = {
            "keyword_match": rules.get("keyword_match_weight", DEFAULT_WEIGHTS["keyword_match_weight"]),
            "priority": rules.get("priority_weight", DEFAULT_WEIGHTS["priority_weight"]),
            "score": rules.get("score_weight", DEFAULT_WEIGHTS["score_weight"]),
        }
        self.min_confidence = rules.get("min_confidence_threshold", MIN_CONFIDENCE)
        self.multi_threshold = rules.get("multi_agent_threshold", MULTI_AGENT_THRESHOLD)

        # Cache : charge routing-rules.json UNE fois dans __init__
        global _routing_config_cache
        if _routing_config_cache is None:
            _routing_config_cache = _load_routing_config()
        self._routing_cfg = _routing_config_cache
        self._complexity_keywords = self._routing_cfg.get("complexity_keywords", DEFAULT_COMPLEXITY_KEYWORDS)

        # Cache scoreboard avec TTL de 10s
        self._sb_cache: dict[str, float] | None = None
        self._sb_ts: float = 0
        self._sb_ttl = 10.0

    # ── Classification ──────────────────────────────────────────

    def classify(self, task: str) -> str:
        """Classifie la complexité: SIMPLE / MEDIUM / COMPLEX.
        Utilise les keywords chargés une fois dans __init__."""
        t = task.lower()
        kw = self._complexity_keywords
        complex_score = sum(1 for ckw in kw.get("COMPLEX", []) if ckw in t)
        if complex_score >= 2:
            return "COMPLEX"
        simple_score = sum(1 for skw in kw.get("SIMPLE", []) if skw in t)
        if simple_score >= 2:
            return "SIMPLE"
        medium_score = sum(1 for mkw in kw.get("MEDIUM", []) if mkw in t)
        if medium_score >= 1:
            return "MEDIUM"
        return "MEDIUM"

    # ── Scoreboard dynamique ───────────────────────────────────

    def _load_dynamic_scores(self) -> dict[str, float]:
        """Charge les scores depuis scoreboard.json avec cache TTL 10s."""
        now = time.time()
        if self._sb_cache is not None and (now - self._sb_ts) < self._sb_ttl:
            return self._sb_cache
        try:
            with open(SCOREBOARD_PATH, encoding="utf-8") as f:
                sb = json.load(f)
            self._sb_cache = {aid: info.get("score", 0) for aid, info in sb.get("agents", {}).items()}
            self._sb_ts = now
            return self._sb_cache
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    # ── Keyword matching ────────────────────────────────────────

    def _match_keywords(self, task: str, keywords: list[str]) -> tuple[float, str]:
        """Score de matching keywords (0.0 - 1.0). Utilise word boundaries."""
        t = task.lower()
        matched = []
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw.lower()) + r'\b', t):
                matched.append(kw)
        if not matched:
            return 0.0, ""
        score = min(1.0, len(matched) / max(len(keywords), 1) * 3)
        return round(score, 3), ", ".join(matched[:3])

    # ── Routage principal ──────────────────────────────────────

    def route(self, task: str) -> dict:
        """
        Route une tâche vers le meilleur agent.
        Retourne un dict structuré.
        """
        complexity = self.classify(task)
        agents = self.registry.list()
        dynamic_scores = self._load_dynamic_scores()

        # Filtrer par complexité
        compatible = [a for a in agents if complexity in a.get("complexity", [])]
        if not compatible:
            compatible = agents  # fallback: tous

        # Score chaque agent
        scored: list[RouteResult] = []
        for agent in compatible:
            kw_score, kw_reason = self._match_keywords(task, agent.get("keywords", []))
            if kw_score == 0.0:
                continue  # pas de match keywords → ignore

            priority_score = 1.0 - (agent.get("priority", 99) - 1) * 0.1  # prio 1 → 1.0, prio 2 → 0.9
            # Score dynamique depuis scoreboard.json (feedback loop), fallback statique
            agent_id = agent["id"]
            dyn_score = dynamic_scores.get(agent_id)
            score_val = (dyn_score if dyn_score is not None else agent.get("score", 0)) / 100.0

            confidence = (
                kw_score * self.weights["keyword_match"]
                + priority_score * self.weights["priority"]
                + score_val * self.weights["score"]
            )

            if confidence >= self.min_confidence:
                scored.append(RouteResult(
                    agent_id=agent["id"],
                    agent_info=agent,
                    confidence=confidence,
                    match_reason=kw_reason,
                ))

        # Trier par confidence descendant
        scored.sort(key=lambda r: r.confidence, reverse=True)

        if not scored:
            return {
                "success": False,
                "task": task,
                "complexity": complexity,
                "error": "No matching agent found",
            }

        best = scored[0]

        # Détection multi-agent (si plusieurs ont un score proche)
        multi = []
        for r in scored[1:]:
            if r.confidence >= best.confidence * self.multi_threshold:
                multi.append(r.to_dict())

        return {
            "success": True,
            "task": task,
            "complexity": complexity,
            "primary": best.to_dict(),
            "alternatives": multi,
            "total_candidates": len(scored),
        }

    def route_multi(self, task: str, max_agents: int = 3) -> dict:
        """
        Route vers jusqu'à `max_agents` agents pour des tâches complexes.
        Utile pour le Council (délibération multi-agent).
        """
        result = self.route(task)
        if not result["success"]:
            return result

        agents = [result["primary"]]
        for alt in result.get("alternatives", []):
            if len(agents) >= max_agents:
                break
            agents.append(alt)

        return {
            "success": True,
            "task": task,
            "complexity": result["complexity"],
            "agents": agents,
            "count": len(agents),
        }
