#!/usr/bin/env python3
"""
Model Router — Select optimal LLM model based on task complexity and agent
Integrates with Novahiz MCP for full agent + model routing
"""
import json
import re
from datetime import datetime

# =============================================================================
# MODEL TIERS
# =============================================================================
MODELS = {
    "flash": {
        "name": "Flash",
        "description": "Fast, cheap, simple tasks",
        "use_cases": ["simple questions", "basic code", "explanations", "quick fixes"],
        "cost": "low",
        "speed": "fast",
        "quality": "good"
    },
    "smart": {
        "name": "Smart",
        "description": "Balanced, most tasks",
        "use_cases": ["feature development", "API design", "debugging", "refactoring"],
        "cost": "medium",
        "speed": "medium",
        "quality": "very good"
    },
    "premium": {
        "name": "Premium",
        "description": "Most powerful, complex tasks",
        "use_cases": ["architecture", "complex systems", "security audit", "production code"],
        "cost": "high",
        "speed": "slow",
        "quality": "excellent"
    }
}

# =============================================================================
# KEYWORD CLASSIFICATION
# =============================================================================
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
    ]
}

# Agent-specific model preferences
AGENT_MODEL_PREFERENCES = {
    # Design agents → smart (creative tasks need good models)
    "luna-design": "smart",
    "ryu-design": "smart",
    
    # Security → premium (critical)
    "neo-security": "premium",
    "cipher-crypto": "premium",
    "ghost-stealth": "premium",
    
    # Architecture → premium
    "arthur-architecture": "premium",
    
    # Database → smart
    "malik-database": "smart",
    
    # Performance → smart
    "kenzo-performance": "smart",
    
    # Quality → smart
    "sarah-quality": "smart",
    
    # Marketing/Strategy → smart
    "elias-marketing": "smart",
    "victor-strategy": "smart",
    
    # Execution → depends on task
    "ralph-execution": "smart",
    "ralph-browser": "smart",
    
    # API → smart
    "nexus-api": "smart",
    
    # DevOps/CI-CD → smart
    "forge-cicd": "smart",
    "orion-devops": "smart",
    
    # Data → smart
    "simon-data": "smart",
    
    # Legal → premium (critical)
    "vega-legal": "premium",
    "samuel-legal": "premium",
    
    # Crisis → premium
    "phoenix-crisis": "premium",
    
    # Default → smart
    "default": "smart"
}

# =============================================================================
# MODEL SELECTION
# =============================================================================
def classify_complexity(task: str) -> str:
    """Classify task complexity based on keywords"""
    task_lower = task.lower()
    
    scores = {"flash": 0, "smart": 0, "premium": 0}
    
    for tier, keywords in COMPLEXITY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in task_lower:
                scores[tier] += 1
    
    # Return highest scoring tier
    return max(scores, key=scores.get)

def select_model(task: str, agent: str = None) -> dict:
    """
    Select optimal model based on task and agent
    Returns: {model, tier, reason, confidence}
    """
    # Get agent preference
    agent_pref = AGENT_MODEL_PREFERENCES.get(agent, "smart")
    
    # Get task complexity
    task_complexity = classify_complexity(task)
    
    # Combine: use higher of the two (safer)
    tier_order = {"flash": 0, "smart": 1, "premium": 2}
    
    if tier_order[task_complexity] > tier_order[agent_pref]:
        selected_tier = task_complexity
        reason = f"Task complexity ({task_complexity}) > agent preference ({agent_pref})"
    else:
        selected_tier = agent_pref
        reason = f"Agent preference ({agent_pref}) based on domain"
    
    # Boost to premium for certain keywords regardless
    task_lower = task.lower()
    if any(kw in task_lower for kw in ["security", "production", "critical", "audit", "vulnerability"]):
        selected_tier = "premium"
        reason = "Critical/Security task → premium model"
    
    model_info = MODELS[selected_tier]
    
    return {
        "model": f"opencode/qwen3.5-plus" if selected_tier == "smart" else 
                 f"opencode/qwen3.5-plus" if selected_tier == "premium" else
                 f"opencode/qwen3.5-plus",  # Adjust based on available models
        "tier": selected_tier,
        "tier_name": model_info["name"],
        "reason": reason,
        "confidence": "high" if task_complexity == agent_pref else "medium",
        "task_complexity": task_complexity,
        "agent_preference": agent_pref,
        "model_info": model_info
    }

def get_model_recommendation(task: str, agent: str = None) -> str:
    """Get human-readable model recommendation"""
    result = select_model(task, agent)
    
    return f"""
🎯 Model Recommendation
═══════════════════════════════════════
Task: {task[:80]}...
Agent: {agent or 'Not specified'}

Selected: {result['tier_name']} ({result['tier']})
Reason: {result['reason']}
Confidence: {result['confidence']}

Model Info:
  - Use cases: {', '.join(result['model_info']['use_cases'][:3])}
  - Cost: {result['model_info']['cost']}
  - Speed: {result['model_info']['speed']}
  - Quality: {result['model_info']['quality']}
═══════════════════════════════════════
"""

# =============================================================================
# INTEGRATION WITH MCP
# =============================================================================
def enhance_execution_with_model(execution_data: dict) -> dict:
    """Add model selection to execution data"""
    agent = execution_data.get("agent")
    task = execution_data.get("task")
    
    model_result = select_model(task, agent)
    
    execution_data["model"] = model_result
    execution_data["model_selected_at"] = datetime.now().isoformat()
    
    return execution_data

# =============================================================================
# CLI
# =============================================================================
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
