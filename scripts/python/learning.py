#!/usr/bin/env python3
"""
Novahiz OS - Learning System
ML-based recommendations using rule-based approach
(no sklearn - lightweight version)
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter

HOME = os.path.expanduser("~")
DATA_DIR = os.path.join(HOME, ".opencode", "data")
NOVAHIZ_DB = os.path.join(DATA_DIR, "novahiz.db")
SKILLS_DB = os.path.join(DATA_DIR, "skills-index.db")
TASKS_DB = os.path.join(DATA_DIR, "tasks-history.db")

class NovahizLearner:
    def __init__(self):
        self.conn = sqlite3.connect(NOVAHIZ_DB)
        self.skills_conn = sqlite3.connect(SKILLS_DB)
        self.tasks_conn = sqlite3.connect(TASKS_DB)
        
        self.domain_patterns = self.load_domain_patterns()
        self.success_patterns = self.load_success_patterns()
    
    def close(self):
        self.conn.close()
        self.skills_conn.close()
        self.tasks_conn.close()
    
    def load_domain_patterns(self):
        """Load domain patterns from historical data"""
        patterns = defaultdict(list)
        
        cursor = self.tasks_conn.cursor()
        cursor.execute("""
            SELECT domain, primary_agent, COUNT(*) as count 
            FROM tasks 
            WHERE success = 1 
            GROUP BY domain, primary_agent
        """)
        
        for row in cursor.fetchall():
            domain, agent, count = row
            patterns[domain].append((agent, count))
        
        for domain in patterns:
            patterns[domain].sort(key=lambda x: x[1], reverse=True)
        
        return patterns
    
    def load_success_patterns(self):
        """Load success patterns from task history"""
        patterns = defaultdict(lambda: {'success': 0, 'total': 0})
        
        cursor = self.tasks_conn.cursor()
        cursor.execute("""
            SELECT primary_agent, classification, success 
            FROM tasks 
            WHERE primary_agent IS NOT NULL
        """)
        
        for row in cursor.fetchall():
            agent, classification, success = row
            key = f"{agent}:{classification}"
            patterns[key]['total'] += 1
            if success:
                patterns[key]['success'] += 1
        
        return patterns
    
    def recommend_agent(self, task_text, classification, domain):
        """Recommend best agent based on learning"""
        recommendations = []
        
        if domain in self.domain_patterns:
            for agent, count in self.domain_patterns[domain][:3]:
                success_rate = self.get_agent_success_rate(agent, classification)
                score = count * success_rate
                recommendations.append({
                    'agent': agent,
                    'score': score,
                    'confidence': success_rate,
                    'reason': f'Best performer for {domain} domain'
                })
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, score FROM agents 
            WHERE domain = ? AND status = 'active'
            ORDER BY score DESC LIMIT 3
        """, (domain,))
        
        for row in cursor.fetchall():
            agent_id, name, agent_score = row
            
            if not any(r['agent'] == name for r in recommendations):
                success_rate = self.get_agent_success_rate(name, classification)
                recommendations.append({
                    'agent': name,
                    'score': agent_score * success_rate,
                    'confidence': success_rate,
                    'reason': f'High score agent for {domain}'
                })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:3]
    
    def get_agent_success_rate(self, agent_name, classification=None):
        """Calculate agent success rate"""
        key = f"{agent_name}:{classification}" if classification else agent_name
        
        if key in self.success_patterns:
            data = self.success_patterns[key]
            if data['total'] > 0:
                return data['success'] / data['total']
        
        cursor = self.conn.cursor()
        if classification:
            cursor.execute("""
                SELECT success FROM tasks 
                WHERE primary_agent = ? AND classification = ?
            """, (agent_name, classification))
        else:
            cursor.execute("""
                SELECT success FROM tasks 
                WHERE primary_agent = ?
            """, (agent_name,))
        
        rows = cursor.fetchall()
        if not rows:
            return 0.7
        
        successes = sum(1 for row in rows if row[0])
        return successes / len(rows)
    
    def learn_from_task(self, task_id, task_text, agent, success, duration):
        """Learn from task execution"""
        cursor = self.tasks_conn.cursor()
        cursor.execute("SELECT domain, classification FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        
        if row:
            domain, classification = row
            
            if success:
                self.domain_patterns[domain].append((agent, 1))
                self.domain_patterns[domain].sort(key=lambda x: x[1], reverse=True)
                self.domain_patterns[domain] = self.domain_patterns[domain][:10]
            
            key = f"{agent}:{classification}"
            if key not in self.success_patterns:
                self.success_patterns[key] = {'success': 0, 'total': 0}
            
            self.success_patterns[key]['total'] += 1
            if success:
                self.success_patterns[key]['success'] += 1
    
    def suggest_improvements(self, agent_id):
        """Suggest improvements for an agent"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, domain FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        
        if not row:
            return []
        
        agent_name, domain = row
        
        suggestions = []
        
        success_rate = self.get_agent_success_rate(agent_name)
        if success_rate < 0.8:
            suggestions.append({
                'type': 'performance',
                'message': f'Success rate is {success_rate:.0%} - below optimal threshold',
                'action': 'Consider additional training or support agents'
            })
        
        cursor = self.tasks_conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE primary_agent = ? AND status = 'failed'
        """, (agent_name,))
        
        failures = cursor.fetchone()[0]
        if failures > 5:
            suggestions.append({
                'type': 'quality',
                'message': f'{failures} failed tasks - review error patterns',
                'action': 'Check logs for common failure reasons'
            })
        
        if success_rate > 0.95:
            suggestions.append({
                'type': 'optimization',
                'message': f'Success rate is {success_rate:.0%} - excellent performance',
                'action': 'Agent is performing optimally'
            })
        
        return suggestions
    
    def get_learning_stats(self):
        """Get learning statistics"""
        agents_cursor = self.conn.cursor()
        
        agents_cursor.execute("SELECT COUNT(*) FROM agents")
        total_agents = agents_cursor.fetchone()[0]
        
        tasks_cursor = self.tasks_conn.cursor()
        
        tasks_cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = tasks_cursor.fetchone()[0]
        
        tasks_cursor.execute("SELECT COUNT(*) FROM tasks WHERE success = 1")
        successful_tasks = tasks_cursor.fetchone()[0]
        
        success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        tasks_cursor.execute("""
            SELECT primary_agent, COUNT(*) as count 
            FROM tasks 
            GROUP BY primary_agent 
            ORDER BY count DESC 
            LIMIT 5
        """)
        
        top_agents = [{'agent': row[0], 'tasks': row[1]} for row in tasks_cursor.fetchall()]
        
        tasks_cursor.execute("""
            SELECT domain, COUNT(*) as count 
            FROM tasks 
            GROUP BY domain 
            ORDER BY count DESC
        """)
        
        top_domains = [{'domain': row[0], 'tasks': row[1]} for row in tasks_cursor.fetchall()]
        
        return {
            'total_agents': total_agents,
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'success_rate': success_rate,
            'top_agents': top_agents,
            'top_domains': top_domains,
            'patterns_learned': len(self.domain_patterns)
        }
    
    def predict_task_outcome(self, task_text, agent, classification):
        """Predict task outcome based on historical patterns"""
        agent_success = self.get_agent_success_rate(agent, classification)
        classification_base = self.get_classification_success_rate(classification)
        
        predicted_success = (agent_success + classification_base) / 2
        
        confidence = 'high' if predicted_success > 0.85 else 'medium' if predicted_success > 0.7 else 'low'
        
        return {
            'predicted_success_rate': predicted_success,
            'confidence': confidence,
            'agent_strength': agent_success,
            'classification_strength': classification_base
        }
    
    def get_classification_success_rate(self, classification):
        """Get success rate by classification"""
        cursor = self.tasks_conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE classification = ? AND success = 1
        """, (classification,))
        
        successes = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE classification = ?
        """, (classification,))
        
        total = cursor.fetchone()[0]
        
        return (successes / total) if total > 0 else 0.7
    
    def get_agent_recommendations(self, limit=10):
        """Get overall agent recommendations"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, name, domain, score 
            FROM agents 
            WHERE status = 'active'
            ORDER BY score DESC
            LIMIT ?
        """, (limit,))
        
        recommendations = []
        
        for row in cursor.fetchall():
            agent_id, name, domain, score = row
            success_rate = self.get_agent_success_rate(name)
            
            recommendations.append({
                'agent_id': agent_id,
                'agent': name,
                'domain': domain,
                'score': score,
                'success_rate': success_rate,
                'recommendation': 'high' if success_rate > 0.85 else 'medium' if success_rate > 0.7 else 'low'
            })
        
        recommendations.sort(key=lambda x: x['success_rate'], reverse=True)
        return recommendations

def main():
    learner = NovahizLearner()
    
    print("\n╔════════════════════════════════════════════╗")
    print("║         NOVAHIZ LEARNING SYSTEM          ║")
    print("╚════════════════════════════════════════════╝\n")
    
    stats = learner.get_learning_stats()
    print("Learning Statistics:")
    print(f"  Total Agents: {stats['total_agents']}")
    print(f"  Total Tasks: {stats['total_tasks']}")
    print(f"  Successful Tasks: {stats['successful_tasks']}")
    print(f"  Overall Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Patterns Learned: {stats['patterns_learned']}")
    
    print("\nTop Agents:")
    for item in stats['top_agents']:
        print(f"  • {item['agent']}: {item['tasks']} tasks")
    
    print("\nTop Domains:")
    for item in stats['top_domains']:
        print(f"  • {item['domain']}: {item['tasks']} tasks")
    
    print("\nAgent Recommendations:")
    for rec in learner.get_agent_recommendations(5):
        print(f"  • {rec['agent']} ({rec['domain']}) - {rec['success_rate']:.0%} success rate")
    
    learner.close()

if __name__ == "__main__":
    main()