#!/usr/bin/env python3
"""
NovaHiz OS — Smart Router v2.0
Multi-criteria scoring + Memory RAG + Dynamic evaluations
"""
import sys, os, json, re
from datetime import datetime
from pathlib import Path

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
MEMORY_DIR = os.path.join(NOVAHIZ_DIR, "memory")
CONFIG_DIR = os.path.join(NOVAHIZ_DIR, "config")

# === AGENT SCORING MATRIX ===
# Each agent has domain weights for multi-keyword matching
AGENT_PROFILES = {
    "luna-design": {"domains": ["design", "ui", "ux", "frontend", "interface", "visual"], "priority": 95, "type": "subagent"},
    "ryu-design": {"domains": ["design", "japanese", "minimalist", "zen", "ryu"], "priority": 90, "type": "simulated"},
    "kenzo-performance": {"domains": ["performance", "optimization", "speed", "bundle", "lazy"], "priority": 95, "type": "subagent"},
    "malik-database": {"domains": ["database", "sql", "schema", "migration", "orm", "data"], "priority": 95, "type": "subagent"},
    "nexus-api": {"domains": ["api", "rest", "graphql", "endpoint", "route", "http"], "priority": 90, "type": "simulated"},
    "neo-security": {"domains": ["security", "auth", "vulnerability", "audit", "encrypt", "token"], "priority": 95, "type": "subagent"},
    "cipher-crypto": {"domains": ["crypto", "cryptography", "cipher", "hash", "blockchain"], "priority": 90, "type": "simulated"},
    "sarah-quality": {"domains": ["quality", "test", "bug", "audit", "review", "lint"], "priority": 95, "type": "subagent"},
    "arthur-architecture": {"domains": ["architecture", "refactor", "pattern", "module", "structure"], "priority": 95, "type": "subagent"},
    "elias-marketing": {"domains": ["marketing", "seo", "content", "growth", "campaign"], "priority": 95, "type": "subagent"},
    "victor-strategy": {"domains": ["strategy", "plan", "roadmap", "decision", "prioritize"], "priority": 95, "type": "subagent"},
    "ralph-execution": {"domains": ["execution", "build", "backend", "implement", "deploy"], "priority": 95, "type": "subagent"},
    "ralph-browser": {"domains": ["browser", "automation", "scrape", "screenshot", "puppeteer"], "priority": 90, "type": "subagent"},
    "atlas-memory": {"domains": ["memory", "context", "retrieve", "rag", "embed"], "priority": 95, "type": "subagent"},
    "orion-devops": {"domains": ["devops", "infra", "kubernetes", "docker", "ci", "cd"], "priority": 90, "type": "simulated"},
    "forge-cicd": {"domains": ["cicd", "pipeline", "github", "actions", "workflow"], "priority": 90, "type": "simulated"},
    "phoenix-crisis": {"domains": ["crisis", "incident", "emergency", "outage", "fire"], "priority": 95, "type": "simulated"},
    "pulse-realtime": {"domains": ["realtime", "websocket", "stream", "socket", "live"], "priority": 90, "type": "simulated"},
    "simon-data": {"domains": ["data", "analytics", "metrics", "dashboard", "insight"], "priority": 90, "type": "simulated"},
    "vega-legal": {"domains": ["legal", "compliance", "gdpr", "privacy", "terms"], "priority": 90, "type": "simulated"},
    "samuel-legal": {"domains": ["legal", "contract", "advisor", "strategy"], "priority": 85, "type": "simulated"},
    "athena-initialization": {"domains": ["init", "bootstrap", "setup", "scaffold", "project"], "priority": 95, "type": "subagent"},
    "ghost-stealth": {"domains": ["stealth", "silent", "background", "ghost"], "priority": 85, "type": "simulated"},
    "novahiz-router": {"domains": ["route", "routing", "orchestrate", "dispatch"], "priority": 100, "type": "primary"},
}

# === SKILL MAPPING ===
SKILL_MAP = {
    "luna-design": "ui-ux-pro-max",
    "ryu-design": "frontend-design",
    "kenzo-performance": "vercel-react-best-practices",
    "malik-database": "xlsx",
    "nexus-api": "novahiz-selection",
    "neo-security": "webapp-testing",
    "cipher-crypto": "webapp-testing",
    "sarah-quality": "requesting-code-review",
    "arthur-architecture": "improve-codebase-architecture",
    "elias-marketing": "content-strategy",
    "victor-strategy": "writing-plans",
    "ralph-execution": "executing-plans",
    "ralph-browser": "agent-browser",
    "atlas-memory": "novahiz-nexus",
    "orion-devops": "deploy-to-vercel",
    "forge-cicd": "deploy-to-vercel",
    "phoenix-crisis": "page-cro",
    "pulse-realtime": "webapp-testing",
    "simon-data": "xlsx",
    "vega-legal": "novahiz-constitution",
    "samuel-legal": "pricing-strategy",
    "athena-initialization": "to-prd",
    "ghost-stealth": "systematic-debugging",
    "novahiz-router": "novahiz-selection",
}

# === AGENT PERFORMANCE SCOREBOARD (dynamic) ===
def load_scoreboard():
    path = os.path.join(CONFIG_DIR, "scoreboard.json")
    if os.path.isfile(path):
        try:
            with open(path, encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    # Default scoreboard
    return {
        "agents": {aid: {"tasks": 0, "success": 0, "avg_time": 0, "score": profile["priority"]} 
                   for aid, profile in AGENT_PROFILES.items()},
        "updated": datetime.now().isoformat()
    }

def save_scoreboard(sb):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    path = os.path.join(CONFIG_DIR, "scoreboard.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sb, f, indent=2)

def update_scoreboard(agent_id, success=True, duration=0):
    sb = load_scoreboard()
    if agent_id in sb["agents"]:
        a = sb["agents"][agent_id]
        a["tasks"] += 1
        if success:
            a["success"] += 1
        # Exponential moving average for time
        a["avg_time"] = 0.8 * a["avg_time"] + 0.2 * duration if duration else a["avg_time"]
        # Recalculate score: base priority + success rate bonus
        success_rate = a["success"] / a["tasks"] if a["tasks"] > 0 else 0
        base = AGENT_PROFILES.get(agent_id, {}).get("priority", 80)
        a["score"] = base + (success_rate * 10)  # Up to +10 bonus
    sb["updated"] = datetime.now().isoformat()
    save_scoreboard(sb)
    return sb["agents"].get(agent_id, {}).get("score", 0)

# === MEMORY RAG INTEGRATION ===
def load_memory_context():
    """Load recent memory nodes for RAG-enhanced routing"""
    nexus_path = os.path.join(MEMORY_DIR, "nexus.json")
    if not os.path.isfile(nexus_path):
        return []
    try:
        with open(nexus_path, encoding='utf-8') as f:
            nexus = json.load(f)
        # Get recent nodes (last 20)
        nodes = nexus.get("nodes", [])[-20:]
        return nodes
    except:
        return []

def extract_memory_keywords(nodes):
    """Extract keywords from memory nodes for routing context"""
    keywords = set()
    for node in nodes:
        content = node.get("content", "")
        tags = node.get("tags", [])
        # Extract words > 3 chars
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        keywords.update(words)
        keywords.update(t.lower() for t in tags)
    return keywords

# === SMART ROUTING ALGORITHM ===
def score_agent(task_text, agent_id, memory_keywords=None):
    """
    Multi-criteria scoring:
    - Keyword match count (weighted)
    - Memory context boost
    - Historical performance
    - Domain priority
    """
    task_lower = task_text.lower()
    profile = AGENT_PROFILES.get(agent_id, {})
    if not profile:
        return 0
    
    # 1. Keyword matching with position weight
    keyword_score = 0
    for kw in profile["domains"]:
        # Exact word boundary match = 2 points
        if re.search(r'\b' + re.escape(kw) + r'\b', task_lower):
            keyword_score += 2
        # Partial match = 1 point
        elif kw in task_lower:
            keyword_score += 1
    
    # 2. Memory context boost
    memory_boost = 0
    if memory_keywords:
        for kw in profile["domains"]:
            if kw in memory_keywords:
                memory_boost += 1.5
    
    # 3. Historical performance
    sb = load_scoreboard()
    perf_score = sb["agents"].get(agent_id, {}).get("score", 0) / 10  # Normalize to 0-10
    
    # 4. Base priority
    base_priority = profile["priority"] / 10  # Normalize to 0-10
    
    # Final score
    total = keyword_score + memory_boost + perf_score + base_priority
    return round(total, 2)

def route_task_smart(task_text):
    """
    Smart routing with multi-criteria scoring
    Returns: (best_agent_id, skill, confidence, all_scores)
    """
    # Load memory context
    memory_nodes = load_memory_context()
    memory_keywords = extract_memory_keywords(memory_nodes) if memory_nodes else set()
    
    # Score all agents
    scores = {}
    for agent_id in AGENT_PROFILES:
        score = score_agent(task_text, agent_id, memory_keywords)
        if score > 0:
            scores[agent_id] = score
    
    if not scores:
        return None, None, 0, {}
    
    # Sort by score
    sorted_agents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_agent = sorted_agents[0][0]
    best_score = sorted_agents[0][1]
    
    # Confidence calculation (0-100)
    confidence = min(100, int(best_score * 10))
    
    # Get skill
    skill = SKILL_MAP.get(best_agent, "novahiz-selection")
    
    return best_agent, skill, confidence, scores

# === CLI INTERFACE ===
def cmd_route(task):
    """Route task with smart scoring"""
    agent, skill, confidence, scores = route_task_smart(task)
    
    if not agent:
        print(json.dumps({
            "task": task,
            "agent": None,
            "skill": None,
            "confidence": 0,
            "message": "No matching agent found"
        }, indent=2))
        return
    
    # Top 3 candidates
    top3 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    result = {
        "task": task,
        "agent": agent,
        "skill": skill,
        "confidence": confidence,
        "top_candidates": [{"agent": a, "score": s} for a, s in top3],
        "memory_context": len(load_memory_context())
    }
    print(json.dumps(result, indent=2))

def cmd_scoreboard():
    """Show current scoreboard"""
    sb = load_scoreboard()
    print(json.dumps(sb, indent=2))

def cmd_update(agent_id, success=True, duration=0):
    """Update agent performance"""
    score = update_scoreboard(agent_id, success, duration)
    print(json.dumps({"agent": agent_id, "new_score": score}))

def cmd_memory():
    """Show memory context keywords"""
    nodes = load_memory_context()
    keywords = extract_memory_keywords(nodes)
    print(json.dumps({
        "nodes_loaded": len(nodes),
        "keywords": list(keywords)[:50],
        "total_keywords": len(keywords)
    }, indent=2))

def cmd_test():
    """Test routing with sample tasks"""
    tests = [
        "build a rest api with authentication",
        "optimize database queries for performance",
        "design a landing page with modern ui",
        "fix security vulnerability in auth endpoint",
        "setup ci/cd pipeline for deployment",
        "create data analytics dashboard",
    ]
    
    results = []
    for task in tests:
        agent, skill, conf, scores = route_task_smart(task)
        results.append({
            "task": task,
            "agent": agent,
            "skill": skill,
            "confidence": conf
        })
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: smart-router.py <command> [args]"}))
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "route" and len(sys.argv) > 2:
        task = " ".join(sys.argv[2:])
        cmd_route(task)
    elif cmd == "scoreboard":
        cmd_scoreboard()
    elif cmd == "update" and len(sys.argv) > 2:
        agent_id = sys.argv[2]
        success = sys.argv[3] == "true" if len(sys.argv) > 3 else True
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        cmd_update(agent_id, success, duration)
    elif cmd == "memory":
        cmd_memory()
    elif cmd == "test":
        cmd_test()
    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))
        sys.exit(1)
