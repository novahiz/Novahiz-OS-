#!/usr/bin/env python3
"""
Novahiz OS - Task Tracker
Tracks all tasks and their execution across agents
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from enum import Enum

HOME = os.path.expanduser("~")
DATA_DIR = os.path.join(HOME, ".opencode", "data")
TASKS_DB = os.path.join(DATA_DIR, "tasks-history.db")

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

class TaskClassification(Enum):
    SIMPLE = "SIMPLE"
    MEDIUM = "MEDIUM"
    COMPLEX = "COMPLEX"

class TaskTracker:
    def __init__(self):
        self.conn = sqlite3.connect(TASKS_DB)
    
    def close(self):
        self.conn.close()
    
    def create_task(self, task_text, classification="MEDIUM", domain="general", primary_agent=None):
        """Create a new task"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (
                task_text, classification, domain, primary_agent, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (task_text, classification, domain, primary_agent, TaskStatus.PENDING.value, datetime.now().isoformat()))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def start_task(self, task_id, primary_agent, supporting_agents=None):
        """Start executing a task"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tasks SET 
                status = ?,
                primary_agent = ?,
                supporting_agents = ?
            WHERE id = ?
        """, (TaskStatus.IN_PROGRESS.value, primary_agent, 
              json.dumps(supporting_agents) if supporting_agents else None, task_id))
        
        self.conn.commit()
    
    def complete_task(self, task_id, success=True, output=None, error=None):
        """Complete a task"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tasks SET 
                status = ?,
                success = ?,
                output = ?,
                error = ?,
                completed_at = ?
            WHERE id = ?
        """, (
            TaskStatus.COMPLETED.value if success else TaskStatus.FAILED.value,
            success,
            output,
            error,
            datetime.now().isoformat(),
            task_id
        ))
        
        self.conn.commit()
    
    def block_task(self, task_id, reason):
        """Block a task"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tasks SET 
                status = ?,
                error = ?
            WHERE id = ?
        """, (TaskStatus.BLOCKED.value, reason, task_id))
        
        self.conn.commit()
    
    def get_task(self, task_id):
        """Get task by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        columns = ['id', 'task_text', 'classification', 'domain', 'primary_agent',
                   'supporting_agents', 'duration', 'status', 'success', 'output',
                   'error', 'created_at', 'completed_at']
        
        return dict(zip(columns, row))
    
    def get_tasks_by_status(self, status, limit=50):
        """Get tasks by status"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?
        """, (status, limit))
        
        columns = ['id', 'task_text', 'classification', 'domain', 'primary_agent',
                   'supporting_agents', 'duration', 'status', 'success', 'output',
                   'error', 'created_at', 'completed_at']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_tasks_by_agent(self, agent_id, limit=50):
        """Get tasks by primary agent"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE primary_agent = ? 
            ORDER BY created_at DESC LIMIT ?
        """, (agent_id, limit))
        
        columns = ['id', 'task_text', 'classification', 'domain', 'primary_agent',
                   'supporting_agents', 'duration', 'status', 'success', 'output',
                   'error', 'created_at', 'completed_at']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_tasks_by_domain(self, domain, limit=50):
        """Get tasks by domain"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks WHERE domain = ? ORDER BY created_at DESC LIMIT ?
        """, (domain, limit))
        
        columns = ['id', 'task_text', 'classification', 'domain', 'primary_agent',
                   'supporting_agents', 'duration', 'status', 'success', 'output',
                   'error', 'created_at', 'completed_at']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_pending_tasks(self, limit=50):
        """Get all pending tasks"""
        return self.get_tasks_by_status(TaskStatus.PENDING.value, limit)
    
    def get_in_progress_tasks(self, limit=50):
        """Get all in-progress tasks"""
        return self.get_tasks_by_status(TaskStatus.IN_PROGRESS.value, limit)
    
    def get_failed_tasks(self, limit=50):
        """Get all failed tasks"""
        return self.get_tasks_by_status(TaskStatus.FAILED.value, limit)
    
    def get_recent_tasks(self, limit=20):
        """Get recent tasks"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
        
        columns = ['id', 'task_text', 'classification', 'domain', 'primary_agent',
                   'supporting_agents', 'duration', 'status', 'success', 'output',
                   'error', 'created_at', 'completed_at']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_task_stats(self):
        """Get task statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'in_progress'")
        in_progress = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
        completed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'failed'")
        failed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'blocked'")
        blocked = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM tasks 
            WHERE status = 'completed' AND success = 1
        """)
        success = cursor.fetchone()[0]
        
        total = pending + in_progress + completed + failed + blocked
        success_rate = (success / completed * 100) if completed > 0 else 0
        
        return {
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'completed': completed,
            'failed': failed,
            'blocked': blocked,
            'success_count': success,
            'success_rate': success_rate
        }
    
    def search_tasks(self, query, limit=50):
        """Search tasks by text"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE task_text LIKE ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (f'%{query}%', limit))
        
        columns = ['id', 'task_text', 'classification', 'domain', 'primary_agent',
                   'supporting_agents', 'duration', 'status', 'success', 'output',
                   'error', 'created_at', 'completed_at']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def classify_task(self, task_text):
        """Classify a task (SIMPLE/MEDIUM/COMPLEX)"""
        text_lower = task_text.lower()
        
        simple_keywords = ['read', 'check', 'show', 'list', 'get', 'simple', 'quick']
        complex_keywords = ['design', 'architecture', 'create', 'build', 'implement', 
                           'refactor', 'system', 'complete', 'complex']
        
        score = 0
        for kw in simple_keywords:
            if kw in text_lower:
                score -= 1
        for kw in complex_keywords:
            if kw in text_lower:
                score += 1
        
        if score <= -1:
            return TaskClassification.SIMPLE.value
        elif score >= 1:
            return TaskClassification.COMPLEX.value
        else:
            return TaskClassification.MEDIUM.value
    
    def get_tasks_by_date_range(self, start_date, end_date):
        """Get tasks within a date range"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE created_at >= ? AND created_at <= ?
            ORDER BY created_at DESC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        columns = ['id', 'task_text', 'classification', 'domain', 'primary_agent',
                   'supporting_agents', 'duration', 'status', 'success', 'output',
                   'error', 'created_at', 'completed_at']
        
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def main():
    tracker = TaskTracker()
    
    print("\n╔════════════════════════════════════════════╗")
    print("║         NOVAHIZ TASK TRACKER              ║")
    print("╚════════════════════════════════════════════╝\n")
    
    stats = tracker.get_task_stats()
    print("Task Statistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  In Progress: {stats['in_progress']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    
    print("\nRecent Tasks:")
    for task in tracker.get_recent_tasks(5):
        status_icon = "●" if task['status'] == 'completed' else "○" if task['status'] == 'pending' else "◐"
        print(f"  {status_icon} [{task['classification']}] {task['task_text'][:50]}...")
    
    tracker.close()

if __name__ == "__main__":
    main()