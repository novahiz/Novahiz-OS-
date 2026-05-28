#!/usr/bin/env python3
"""
Novahiz OS - Agent Memory
Tracks agent utilization and provides context retrieval
"""

import sqlite3
import os
from datetime import datetime

HOME = os.path.expanduser("~")
DATA_DIR = os.path.join(HOME, ".opencode", "data")
NOVAHIZ_DB = os.path.join(DATA_DIR, "novahiz.db")
TRACKING_DB = os.path.join(DATA_DIR, "agents-tracking.db")

class AgentMemory:
    def __init__(self):
        self.conn = sqlite3.connect(NOVAHIZ_DB)
        self.tracking_conn = sqlite3.connect(TRACKING_DB)
    
    def close(self):
        self.conn.close()
        self.tracking_conn.close()
    
    def record_activity(self, agent_id, agent_name, action, task, duration=0, success=True):
        """Record an agent activity"""
        cursor = self.tracking_conn.cursor()
        
        cursor.execute("""
            INSERT INTO agent_activity (
                agent_id, agent_name, action, task, duration, success, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (agent_id, agent_name, action, task, duration, success, datetime.now().isoformat()))
        
        self.tracking_conn.commit()
        
        cursor.execute("""
            UPDATE agents SET 
                usage_count = usage_count + 1,
                last_used = ?,
                success_count = success_count + ?
            WHERE id = ?
        """, (datetime.now().isoformat(), 1 if success else 0, agent_id))
        
        self.conn.commit()
    
    def get_agent_stats(self, agent_id):
        """Get agent statistics"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        agent = cursor.fetchone()
        
        if not agent:
            return None
        
        tracking_cursor = self.tracking_conn.cursor()
        tracking_cursor.execute("""
            SELECT COUNT(*), AVG(duration), SUM(CASE WHEN success THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
            FROM agent_activity WHERE agent_id = ?
        """, (agent_id,))
        stats = tracking_cursor.fetchone()
        
        return {
            'id': agent[0],
            'name': agent[1],
            'type': agent[2],
            'domain': agent[3],
            'score': agent[4],
            'status': agent[5],
            'usage_count': agent[14],
            'success_count': agent[16],
            'success_rate': agent[17],
            'last_used': agent[13],
            'recent_stats': {
                'total_tasks': stats[0],
                'avg_duration': stats[1],
                'success_rate_calc': stats[2]
            }
        }
    
    def get_recent_agents(self, limit=10):
        """Get recently used agents"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM agents 
            WHERE last_used IS NOT NULL 
            ORDER BY last_used DESC 
            LIMIT ?
        """, (limit,))
        
        columns = ['id', 'name', 'type', 'domain', 'score', 'status', 'file_path',
                   'description', 'specialty', 'origin', 'invoke_method', 'created_at',
                   'updated_at', 'last_used', 'usage_count', 'success_count', 'success_rate']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_top_agents(self, by='usage', limit=10):
        """Get top agents by usage or success"""
        cursor = self.conn.cursor()
        
        if by == 'usage':
            cursor.execute("""
                SELECT * FROM agents ORDER BY usage_count DESC LIMIT ?
            """, (limit,))
        elif by == 'success':
            cursor.execute("""
                SELECT * FROM agents ORDER BY success_rate DESC LIMIT ?
            """, (limit,))
        elif by == 'score':
            cursor.execute("""
                SELECT * FROM agents ORDER BY score DESC LIMIT ?
            """, (limit,))
        
        columns = ['id', 'name', 'type', 'domain', 'score', 'status', 'file_path',
                   'description', 'specialty', 'origin', 'invoke_method', 'created_at',
                   'updated_at', 'last_used', 'usage_count', 'success_count', 'success_rate']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_agents_by_domain(self, domain):
        """Get agents by domain"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE domain = ?", (domain,))
        
        columns = ['id', 'name', 'type', 'domain', 'score', 'status', 'file_path',
                   'description', 'specialty', 'origin', 'invoke_method', 'created_at',
                   'updated_at', 'last_used', 'usage_count', 'success_count', 'success_rate']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def search_agents(self, query):
        """Search agents by name, domain, or description"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM agents 
            WHERE name LIKE ? OR domain LIKE ? OR description LIKE ?
            LIMIT 20
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        columns = ['id', 'name', 'type', 'domain', 'score', 'status', 'file_path',
                   'description', 'specialty', 'origin', 'invoke_method', 'created_at',
                   'updated_at', 'last_used', 'usage_count', 'success_count', 'success_rate']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_activity_history(self, agent_id, limit=50):
        """Get activity history for an agent"""
        cursor = self.tracking_conn.cursor()
        cursor.execute("""
            SELECT * FROM agent_activity 
            WHERE agent_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (agent_id, limit))
        
        columns = ['id', 'agent_id', 'agent_name', 'action', 'task', 'duration', 'success', 'timestamp']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_memory_context(self, agent_id, recent_tasks=5):
        """Get memory context for an agent (recent tasks + stats)"""
        stats = self.get_agent_stats(agent_id)
        history = self.get_activity_history(agent_id, recent_tasks)
        
        return {
            'agent': stats,
            'recent_tasks': history,
            'context_ready': stats is not None
        }
    
    def update_agent_score(self, agent_id, new_score):
        """Update agent score based on performance"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE agents SET score = ?, updated_at = ? WHERE id = ?",
                      (new_score, datetime.now().isoformat(), agent_id))
        self.conn.commit()
    
    def reset_agent_stats(self, agent_id):
        """Reset agent usage statistics"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE agents SET 
                usage_count = 0,
                success_count = 0,
                success_rate = 0,
                last_used = NULL
            WHERE id = ?
        """, (agent_id,))
        
        tracking_cursor = self.tracking_conn.cursor()
        tracking_cursor.execute("DELETE FROM agent_activity WHERE agent_id = ?", (agent_id,))
        
        self.conn.commit()
        self.tracking_conn.commit()

def main():
    memory = AgentMemory()
    
    print("\n╔════════════════════════════════════════════╗")
    print("║         NOVAHIZ AGENT MEMORY                ║")
    print("╚════════════════════════════════════════════╝\n")
    
    print("Top Agents by Usage:")
    for agent in memory.get_top_agents('usage', 5):
        print(f"  • {agent['name']}: {agent['usage_count']} uses")
    
    print("\nTop Agents by Success Rate:")
    for agent in memory.get_top_agents('success', 5):
        print(f"  • {agent['name']}: {agent['success_rate']:.1f}%")
    
    print("\nRecent Agents:")
    for agent in memory.get_recent_agents(5):
        print(f"  • {agent['name']} ({agent['domain']}) - Last used: {agent['last_used']}")
    
    memory.close()

if __name__ == "__main__":
    main()