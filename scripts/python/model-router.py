#!/usr/bin/env python3
"""
Model Router — Select optimal LLM model based on task complexity and agent
Integrates with Novahiz MCP for full agent + model routing

Lit la configuration depuis config/model-router.json
"""
import json
import os
from datetime import datetime

HOME = os.path.expanduser("~")
MODEL_ROUTER_PATH = os.path.join(HOME, ".opencode", "config", "model-router.json")


def load_config():
    try:
        with open(MODEL_ROUTER_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "tiers": {
                "flash": {"primary": "openrouter/qwen/qwen3.5-9b", "fallbacks": []},
                "smart": {"primary": "opencode/qwen3.5-plus", "fallbacks": []},
                "premium": {"primary": "openrouter/qwen/qwen3.6-plus", "fallbacks": []},
            },
            "agentOverrides": {},
        }


MODELS = {
    "flash": {"name": "Flash", "description": "Fast, cheap, simple tasks", "use_cases": ["simple questions", "basic code", "explanations", "quick fixes"], "cost": "low", "speed": "fast", "quality": "good"},
    "smart": {"name": "Smart", "description": "Balanced, most tasks", "use_cases": ["feature development", "API design", "debugging", "refactoring"], "cost": "medium", "speed": "medium", "quality": "very good"},
    "premium": {"name": "Premium", "description": "Most powerful, complex tasks", "use_cases": ["architecture", "complex systems", "security audit", "production code"], "cost": "high", "speed": "slow", "quality": "excellent"},
}

COMPLEXITY_KEYWORDS = {
    "flash": [
        "simple", "quick", "basic", "explain", "what is", "how to",
        "fix typo", "format", "convert", "list", "show", "example"
    ],
    "smart": [
        "build", "create", "implement", "feature", "api", "function",
        "debug", "optimize", "refactor", "test", "integrate", "configure"
    ],
    "premium": [
        "architecture", "system design", "microservice", "scalability",
        "security audit", "production", "enterprise", "complex",
        "multi-tenant", "high availability", "distributed", "critical"
    ],
}

def _load_agent_preferences():
    """Charge les préférences depuis model-router.json (agentOverrides).
    Fallback: tous les agents non listés → 'smart'."""
    cfg = load_config()
    overrides = cfg.get("agentOverrides", {})
    prefs = dict(overrides)
    prefs.setdefault("default", "smart")
    return prefs


def get_model_name(tier):
    """Récupère le nom du modèle primary depuis model-router.json ou défaut."""
    cfg = load_config()
    tiers = cfg.get("tiers", {})
    info = tiers.get(tier, {})
    primary = info.get("primary")
    if primary:
        return primary
    # Fallback: mapping statique
    return {
        "flash": "openrouter/qwen/qwen3.5-9b",
        "smart": "opencode/qwen3.5-plus",
        "premium": "openrouter/qwen/qwen3.6-plus",
    }.get(tier, "opencode/qwen3.5-plus")


def classify_complexity(task):
    """Classify task complexity based on keywords"""
    task_lower = task.lower()
    scores = {"flash": 0, "smart": 0, "premium": 0}
    for tier, keywords in COMPLEXITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in task_lower:
                scores[tier] += 1
    return max(scores, key=scores.get)


def select_model(task, agent=None):
    """
    Select optimal model based on task and agent
    Lit les noms de modèles ET les préférences agent depuis config/model-router.json
    """
    agent_prefs = _load_agent_preferences()
    agent_pref = agent_prefs.get(agent, agent_prefs.get("default", "smart"))
    task_complexity = classify_complexity(task)

    tier_order = {"flash": 0, "smart": 1, "premium": 2}

    if tier_order[task_complexity] > tier_order[agent_pref]:
        selected_tier = task_complexity
        reason = f"Task complexity ({task_complexity}) > agent preference ({agent_pref})"
    else:
        selected_tier = agent_pref
        reason = f"Agent preference ({agent_pref}) based on domain"

    task_lower = task.lower()
    if any(kw in task_lower for kw in ["security", "production", "critical", "audit", "vulnerability"]):
        selected_tier = "premium"
        reason = "Critical/Security task -> premium model"

    model_name = get_model_name(selected_tier)
    model_info = MODELS[selected_tier]

    return {
        "model": model_name,
        "tier": selected_tier,
        "tier_name": model_info["name"],
        "reason": reason,
        "confidence": "high" if task_complexity == agent_pref else "medium",
        "task_complexity": task_complexity,
        "agent_preference": agent_pref,
        "model_info": model_info,
    }


def get_model_recommendation(task, agent=None):
    """Get human-readable model recommendation"""
    result = select_model(task, agent)
    return f"""
  Model Recommendation
  ===============================
  Task:  {task[:80]}...
  Agent: {agent or 'Not specified'}

  Selected: {result['tier_name']} ({result['tier']})
  Model:   {result['model']}
  Reason:  {result['reason']}
  Confidence: {result['confidence']}

  Model Info:
    - Use cases: {', '.join(result['model_info']['use_cases'][:3])}
    - Cost: {result['model_info']['cost']}
    - Speed: {result['model_info']['speed']}
    - Quality: {result['model_info']['quality']}
  ===============================
"""


def enhance_execution_with_model(execution_data):
    """Add model selection to execution data"""
    agent = execution_data.get("agent")
    task = execution_data.get("task")
    model_result = select_model(task, agent)
    execution_data["model"] = model_result
    execution_data["model_selected_at"] = datetime.now().isoformat()
    return execution_data


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 2:
        task = " ".join(sys.argv[2:])
        agent = sys.argv[1] if len(sys.argv) > 1 else None
        print(get_model_recommendation(task, agent))
    else:
        print("Model Router — Select optimal LLM model")
        print("=" * 50)
        print("")
        print("Usage:")
        print("  model-router.py [agent] <task>")
        print("")
        print("Examples:")
        print("  model-router.py luna-design \"Design a login form\"")
        print("  model-router.py neo-security \"Audit authentication flow\"")
        print("  model-router.py \"Explain dependency injection\"")
        print("")
        print("Available tiers:")
        for tier, info in MODELS.items():
            print(f"  {info['name']:10} — {info['description']}")
