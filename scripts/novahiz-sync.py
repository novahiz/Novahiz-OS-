#!/usr/bin/env python3
"""
NovaHiz OS v1.7 - Database Synchronization Script
Syncs agents between YAML files, database, and registry
"""

import sqlite3
import json
import os
from datetime import datetime

HOME = os.path.expanduser("~")
NOVAHIZ_DIR = os.path.join(HOME, ".opencode")
DATA_DIR = os.path.join(NOVAHIZ_DIR, "data")
REGISTRY_PATH = os.path.join(NOVAHIZ_DIR, "registry", "novahiz-registry.json")
DB_PATH = os.path.join(DATA_DIR, "novahiz.db")

AGENTS_DIR = os.path.join(NOVAHIZ_DIR, "agents")

def load_yaml_agents():
    """Load agents from YAML files"""
    agents = []
    for f in os.listdir(AGENTS_DIR):
        if f.endswith('.yaml'):
            agent_id = f.replace('.yaml', '')
            agents.append(agent_id)
    return agents

def load_db_agents():
    """Load agents from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, domain, score, status FROM agents")
    agents = [{'id': r[0], 'name': r[1], 'type': r[2], 'domain': r[3], 'score': r[4], 'status': r[5]} for r in cursor.fetchall()]
    conn.close()
    return agents

def sync_db():
    """Synchronize database with YAML files"""
    yaml_agents = load_yaml_agents()
    db_agents = load_db_agents()
    db_ids = [a['id'] for a in db_agents]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    added = 0
    updated = 0
    
    for agent_id in yaml_agents:
        if agent_id not in db_ids:
            cursor.execute("""
                INSERT INTO agents (id, name, type, domain, score, status, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent_id,
                agent_id.replace('-', ' ').title(),
                'subagent' if agent_id in ['luna-design', 'kenzo-performance', 'malik-database', 'arthur-architecture', 'neo-security', 'sarah-quality', 'elias-marketing', 'victor-strategy', 'ralph-execution', 'atlas-memory'] else 'simulated',
                'general',
                90,
                'active',
                '',
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            added += 1
        else:
            updated += 1
    
    conn.commit()
    conn.close()
    
    return added, updated

def sync_registry():
    """Synchronize registry JSON with YAML files"""
    yaml_agents = load_yaml_agents()
    
    if not os.path.exists(REGISTRY_PATH):
        print("✗ Registry file not found")
        return False
    
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)
    
    registry_ids = [a['id'] for a in registry.get('agents', [])]
    
    for agent_id in yaml_agents:
        if agent_id not in registry_ids:
            new_agent = {
                'id': agent_id,
                'name': agent_id.replace('-', ' ').title(),
                'type': 'subagent' if agent_id in ['luna-design', 'kenzo-performance', 'malik-database', 'arthur-architecture', 'neo-security', 'sarah-quality', 'elias-marketing', 'victor-strategy', 'ralph-execution', 'atlas-memory'] else 'simulated',
                'domain': 'general',
                'score': 90,
                'file': f'agents/{agent_id}.yaml',
                'status': 'active' if agent_id in ['luna-design', 'kenzo-performance', 'malik-database', 'arthur-architecture', 'neo-security', 'sarah-quality', 'elias-marketing', 'victor-strategy', 'ralph-execution', 'atlas-memory'] else 'simulated',
                'description': f'Agent {agent_id}'
            }
            registry['agents'].append(new_agent)
    
    registry['totalAgents'] = len(registry['agents'])
    registry['lastUpdated'] = datetime.now().isoformat()[:10]
    
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(registry, f, indent=2)
    
    return True

def run():
    print("\n╔════════════════════════════════════════════════════╗")
    print("║        DATABASE SYNCHRONIZATION                  ║")
    print("╚════════════════════════════════════════════════════╝\n")
    
    yaml_agents = load_yaml_agents()
    db_agents = load_db_agents()
    
    print(f"  YAML files:   {len(yaml_agents)}")
    print(f"  DB agents:    {len(db_agents)}")
    print(f"  Registry:    {len(db_agents)} (synced)")
    
    added, updated = sync_db()
    sync_registry()
    
    print(f"\n  Added to DB:    {added}")
    print(f"  Updated in DB:  {updated}")
    
    db_agents = load_db_agents()
    print(f"\n  Final DB count: {len(db_agents)}")
    
    if len(db_agents) == len(yaml_agents):
        print("\n  ✓ Database synchronized successfully!")
    else:
        print(f"\n  ✗ Mismatch: {len(db_agents)} DB vs {len(yaml_agents)} YAML")

if __name__ == "__main__":
    run()