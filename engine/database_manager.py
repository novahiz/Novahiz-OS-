#!/usr/bin/env python3
"""
Novahiz Database Manager — Initialize and manage SQLite database.
"""
import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path

DB_PATH = os.path.expanduser("~/.opencode/data/novahiz_state.db")
SCHEMA_PATH = os.path.expanduser("~/.opencode/data/schema.sql")


class DatabaseManager:
    """Manage Novahiz SQLite database."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.conn = None
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def close(self):
        """Close connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize(self) -> bool:
        """Initialize database from schema."""
        try:
            if not os.path.exists(SCHEMA_PATH):
                print(f"❌ Schema file not found: {SCHEMA_PATH}")
                return False

            self.connect()
            with open(SCHEMA_PATH, 'r') as f:
                schema_sql = f.read()

            self.conn.executescript(schema_sql)
            self.conn.commit()
            print(f"✅ Database initialized: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            return False
        finally:
            self.close()

    def get_connection(self) -> sqlite3.Connection:
        """Get or create connection."""
        if not self.conn:
            self.connect()
        return self.conn

    def insert_error(self, error_data: dict) -> str:
        """Insert error record."""
        conn = self.get_connection()
        error_id = error_data.get('id', f"err_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

        conn.execute("""
            INSERT OR REPLACE INTO errors
            (id, timestamp, source, severity, category, message, context, stack_trace)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            error_id,
            error_data.get('timestamp', datetime.now().isoformat()),
            error_data.get('source', 'unknown'),
            error_data.get('severity', 'medium'),
            error_data.get('category', 'general'),
            error_data.get('message', ''),
            json.dumps(error_data.get('context', {})),
            error_data.get('stack_trace')
        ))
        conn.commit()
        return error_id

    def insert_agent_metric(self, metric_data: dict) -> str:
        """Insert agent metric record."""
        conn = self.get_connection()
        metric_id = metric_data.get('id', f"met_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

        conn.execute("""
            INSERT OR REPLACE INTO agent_metrics
            (id, agent_id, timestamp, tasks_completed, tasks_failed, tasks_timeout,
             avg_duration_seconds, success_rate, keywords_triggered, patterns_detected,
             improvement_suggestions, error_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric_id,
            metric_data.get('agent_id'),
            metric_data.get('timestamp', datetime.now().isoformat()),
            metric_data.get('tasks_completed', 0),
            metric_data.get('tasks_failed', 0),
            metric_data.get('tasks_timeout', 0),
            metric_data.get('avg_duration_seconds', 0),
            metric_data.get('success_rate', 0),
            json.dumps(metric_data.get('keywords_triggered', [])),
            json.dumps(metric_data.get('patterns_detected', {})),
            json.dumps(metric_data.get('improvement_suggestions', [])),
            metric_data.get('error_rate', 0)
        ))
        conn.commit()
        return metric_id

    def insert_auto_correction(self, correction_data: dict) -> str:
        """Insert auto-correction record."""
        conn = self.get_connection()
        correction_id = correction_data.get('id', f"cor_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

        conn.execute("""
            INSERT INTO auto_corrections
            (id, timestamp, target_type, target_id, issue_detected, issue_id,
             correction_applied, before_state, after_state, success, rollback_available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            correction_id,
            correction_data.get('timestamp', datetime.now().isoformat()),
            correction_data.get('target_type'),
            correction_data.get('target_id'),
            correction_data.get('issue_detected'),
            correction_data.get('issue_id'),
            correction_data.get('correction_applied'),
            json.dumps(correction_data.get('before_state', {})),
            json.dumps(correction_data.get('after_state', {})),
            correction_data.get('success', False),
            correction_data.get('rollback_available', True)
        ))
        conn.commit()
        return correction_id

    def insert_learning(self, learning_data: dict) -> str:
        """Insert agent learning record."""
        conn = self.get_connection()
        learning_id = learning_data.get('id', f"lrn_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

        conn.execute("""
            INSERT INTO agent_learning
            (id, agent_id, timestamp, lesson_type, lesson_data, source_task_id,
             applied, impact_score, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            learning_id,
            learning_data.get('agent_id'),
            learning_data.get('timestamp', datetime.now().isoformat()),
            learning_data.get('lesson_type'),
            json.dumps(learning_data.get('lesson_data', {})),
            learning_data.get('source_task_id'),
            learning_data.get('applied', False),
            learning_data.get('impact_score', 0),
            learning_data.get('confidence', 0)
        ))
        conn.commit()
        return learning_id

    def update_system_state(self, key: str, value: dict, updated_by: str = 'system') -> bool:
        """Update system state."""
        conn = self.get_connection()

        conn.execute("""
            INSERT OR REPLACE INTO system_state (key, value, last_updated, updated_by)
            VALUES (?, ?, ?, ?)
        """, (key, json.dumps(value), datetime.now().isoformat(), updated_by))
        conn.commit()
        return True

    def get_system_state(self, key: str) -> dict:
        """Get system state by key."""
        conn = self.get_connection()
        cursor = conn.execute("SELECT value FROM system_state WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            return json.loads(row['value'])
        return {}

    def get_unresolved_errors(self, limit: int = 50) -> list:
        """Get unresolved errors."""
        conn = self.get_connection()
        cursor = conn.execute("""
            SELECT * FROM errors
            WHERE resolved = FALSE
            ORDER BY
                CASE severity
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                timestamp DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_agent_metrics(self, agent_id: str = None, limit: int = 10) -> list:
        """Get agent metrics."""
        conn = self.get_connection()
        if agent_id:
            cursor = conn.execute("""
                SELECT * FROM agent_metrics
                WHERE agent_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_id, limit))
        else:
            cursor = conn.execute("""
                SELECT * FROM agent_metrics
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_active_alerts(self) -> list:
        """Get active alerts."""
        conn = self.get_connection()
        cursor = conn.execute("""
            SELECT * FROM view_active_alerts
        """)
        return [dict(row) for row in cursor.fetchall()]

    def insert_alert(self, alert_data: dict) -> str:
        """Insert alert record."""
        conn = self.get_connection()
        alert_id = alert_data.get('id', f"alt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

        conn.execute("""
            INSERT INTO alerts
            (id, timestamp, alert_type, severity, title, message, context)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            alert_id,
            alert_data.get('timestamp', datetime.now().isoformat()),
            alert_data.get('alert_type'),
            alert_data.get('severity', 'medium'),
            alert_data.get('title'),
            alert_data.get('message'),
            json.dumps(alert_data.get('context', {}))
        ))
        conn.commit()
        return alert_id

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = 'user') -> bool:
        """Acknowledge an alert."""
        conn = self.get_connection()
        conn.execute("""
            UPDATE alerts
            SET acknowledged = TRUE, acknowledged_at = ?, acknowledged_by = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), acknowledged_by, alert_id))
        conn.commit()
        return True

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        conn = self.get_connection()
        conn.execute("""
            UPDATE alerts
            SET resolved = TRUE, resolved_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), alert_id))
        conn.commit()
        return True

    def get_recent_corrections(self, limit: int = 20) -> list:
        """Get recent auto-corrections."""
        conn = self.get_connection()
        cursor = conn.execute("""
            SELECT * FROM view_recent_corrections
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_routing_history(self, limit: int = 50) -> list:
        """Get routing history."""
        conn = self.get_connection()
        cursor = conn.execute("""
            SELECT * FROM routing_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def insert_routing_history(self, routing_data: dict) -> str:
        """Insert routing history record."""
        conn = self.get_connection()
        routing_id = routing_data.get('id', f"rte_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

        conn.execute("""
            INSERT INTO routing_history
            (id, timestamp, task_hash, task_preview, primary_agent, primary_confidence,
             alternative_agents, complexity, routing_duration_ms, keywords_matched, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            routing_id,
            routing_data.get('timestamp', datetime.now().isoformat()),
            routing_data.get('task_hash'),
            routing_data.get('task_preview', '')[:100],
            routing_data.get('primary_agent'),
            routing_data.get('primary_confidence', 0),
            json.dumps(routing_data.get('alternative_agents', [])),
            routing_data.get('complexity', 'MEDIUM'),
            routing_data.get('routing_duration_ms', 0),
            json.dumps(routing_data.get('keywords_matched', [])),
            routing_data.get('success', False)
        ))
        conn.commit()
        return routing_id

    def insert_performance_metric(self, metric_data: dict) -> str:
        """Insert performance metric."""
        conn = self.get_connection()
        metric_id = metric_data.get('id', f"prm_{datetime.now().strftime('%Y%m%d%H%M%S%f')}")

        conn.execute("""
            INSERT INTO performance_metrics
            (id, timestamp, metric_type, metric_name, value, unit, source,
             threshold_warning, threshold_critical)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric_id,
            metric_data.get('timestamp', datetime.now().isoformat()),
            metric_data.get('metric_type'),
            metric_data.get('metric_name'),
            metric_data.get('value'),
            metric_data.get('unit'),
            metric_data.get('source'),
            metric_data.get('threshold_warning'),
            metric_data.get('threshold_critical')
        ))
        conn.commit()

        # Check if alert should be triggered
        if metric_data.get('value', 0) >= (metric_data.get('threshold_critical') or float('inf')):
            self.insert_alert({
                'alert_type': 'performance',
                'severity': 'critical',
                'title': f"Critical: {metric_data.get('metric_name')}",
                'message': f"{metric_data.get('metric_name')} = {metric_data.get('value')} {metric_data.get('unit')}",
                'context': metric_data
            })
        elif metric_data.get('value', 0) >= (metric_data.get('threshold_warning') or float('inf')):
            self.insert_alert({
                'alert_type': 'performance',
                'severity': 'high',
                'title': f"Warning: {metric_data.get('metric_name')}",
                'message': f"{metric_data.get('metric_name')} = {metric_data.get('value')} {metric_data.get('unit')}",
                'context': metric_data
            })

        return metric_id

    def run_query(self, query: str, params: tuple = ()) -> list:
        """Run custom query (for CLI debug)."""
        conn = self.get_connection()
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> dict:
        """Get database statistics."""
        conn = self.get_connection()

        stats = {}

        # Error stats
        cursor = conn.execute("SELECT COUNT(*) as count FROM errors")
        stats['total_errors'] = cursor.fetchone()['count']

        cursor = conn.execute("SELECT COUNT(*) as count FROM errors WHERE resolved = FALSE")
        stats['unresolved_errors'] = cursor.fetchone()['count']

        # Agent metrics stats
        cursor = conn.execute("SELECT COUNT(DISTINCT agent_id) as count FROM agent_metrics")
        stats['agents_tracked'] = cursor.fetchone()['count']

        # Auto-correction stats
        cursor = conn.execute("SELECT COUNT(*) as count FROM auto_corrections")
        stats['total_corrections'] = cursor.fetchone()['count']

        cursor = conn.execute("SELECT COUNT(*) as count FROM auto_corrections WHERE success = TRUE")
        stats['successful_corrections'] = cursor.fetchone()['count']

        # Learning stats
        cursor = conn.execute("SELECT COUNT(*) as count FROM agent_learning")
        stats['total_learnings'] = cursor.fetchone()['count']

        # Alert stats
        cursor = conn.execute("SELECT COUNT(*) as count FROM alerts WHERE resolved = FALSE")
        stats['active_alerts'] = cursor.fetchone()['count']

        # Routing stats
        cursor = conn.execute("SELECT COUNT(*) as count FROM routing_history")
        stats['total_routings'] = cursor.fetchone()['count']

        return stats


# Singleton instance
_db_manager = None


def get_db() -> DatabaseManager:
    """Get database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.connect()
    return _db_manager


def init_db() -> bool:
    """Initialize database."""
    db = DatabaseManager()
    return db.initialize()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        success = init_db()
        sys.exit(0 if success else 1)
    else:
        print("Usage: python3 database_manager.py init")
        print("       Import and use get_db() in your code")
