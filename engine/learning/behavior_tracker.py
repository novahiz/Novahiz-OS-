#!/usr/bin/env python3
"""
Novahiz Behavior Tracker — Track agent behavior patterns.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.database_manager import get_db


class BehaviorTracker:
    """Track and analyze agent behavior patterns."""

    def __init__(self, db=None):
        self.db = db or get_db()
        self.base_dir = Path.home() / ".opencode"

    def track_execution(self, agent_id: str, execution_data: Dict) -> Dict:
        """Track a single execution for pattern analysis."""
        pattern_data = {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'status': execution_data.get('status', 'unknown'),
            'duration': execution_data.get('duration', 0),
            'confidence': execution_data.get('confidence', 0),
            'task_preview': execution_data.get('task', '')[:100],
            'complexity': execution_data.get('complexity', 'MEDIUM'),
            'model_used': execution_data.get('model', 'unknown')
        }

        # Detect patterns
        patterns = self._detect_patterns(agent_id, pattern_data)

        # Store learning if patterns detected
        if patterns:
            for pattern in patterns:
                self.db.insert_learning({
                    'agent_id': agent_id,
                    'lesson_type': 'pattern',
                    'lesson_data': pattern,
                    'source_task_id': execution_data.get('id'),
                    'confidence': pattern.get('confidence', 0.5)
                })

        return {
            'tracked': True,
            'patterns_detected': len(patterns),
            'patterns': patterns
        }

    def _detect_patterns(self, agent_id: str, current: Dict) -> List[Dict]:
        """Detect patterns from current execution."""
        patterns = []

        # Get recent executions for this agent
        metrics = self.db.get_agent_metrics(agent_id, limit=20)

        if len(metrics) < 5:
            return patterns  # Not enough data

        # Pattern: Consistent success with specific complexity
        success_by_complexity = defaultdict(list)
        for m in metrics:
            complexity = 'MEDIUM'  # Default, would need to track per-execution
            success = m.get('success_rate', 0) > 80
            success_by_complexity[complexity].append(success)

        # Pattern: Time-based performance
        durations = [m.get('avg_duration_seconds', 0) for m in metrics]
        if durations:
            avg_duration = sum(durations) / len(durations)
            if current.get('duration', 0) > avg_duration * 2:
                patterns.append({
                    'type': 'slow_execution',
                    'description': f'Execution {current.get("duration", 0):.1f}s vs avg {avg_duration:.1f}s',
                    'confidence': 0.8,
                    'suggestion': 'Consider caching or optimization'
                })

        # Pattern: Confidence vs Success correlation
        confidences = [m.get('avg_confidence', 0) for m in metrics if m.get('avg_confidence', 0) > 0]
        success_rates = [m.get('success_rate', 0) for m in metrics]

        if confidences and success_rates:
            # Simple correlation check
            high_conf_success = sum(1 for c, s in zip(confidences, success_rates) if c > 0.7 and s > 80)
            if high_conf_success / len(confidences) > 0.8:
                patterns.append({
                    'type': 'high_confidence_reliable',
                    'description': 'High confidence predictions are reliable',
                    'confidence': 0.9,
                    'suggestion': 'Trust confidence scores for this agent'
                })

        return patterns

    def get_agent_profile(self, agent_id: str) -> Dict:
        """Get comprehensive behavior profile for an agent."""
        profile = {
            'agent_id': agent_id,
            'generated_at': datetime.now().isoformat(),
            'metrics': {},
            'patterns': [],
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }

        # Get metrics
        metrics = self.db.get_agent_metrics(agent_id, limit=50)
        if not metrics:
            profile['error'] = 'No metrics found'
            return profile

        # Calculate aggregate metrics
        total_tasks = sum(m.get('tasks_completed', 0) + m.get('tasks_failed', 0) for m in metrics)
        total_success = sum(m.get('tasks_completed', 0) for m in metrics)
        overall_success_rate = (total_success / max(total_tasks, 1)) * 100

        avg_duration = sum(m.get('avg_duration_seconds', 0) for m in metrics) / max(len(metrics), 1)
        avg_confidence = sum(m.get('avg_confidence', 0) for m in metrics) / max(len(metrics), 1)

        profile['metrics'] = {
            'total_tasks': total_tasks,
            'success_rate': overall_success_rate,
            'avg_duration_seconds': avg_duration,
            'avg_confidence': avg_confidence,
            'error_rate': 100 - overall_success_rate
        }

        # Identify strengths
        if overall_success_rate > 90:
            profile['strengths'].append('High success rate')
        if avg_duration < 10:
            profile['strengths'].append('Fast execution')
        if avg_confidence > 0.7:
            profile['strengths'].append('High confidence predictions')

        # Identify weaknesses
        if overall_success_rate < 70:
            profile['weaknesses'].append('Low success rate')
        if avg_duration > 60:
            profile['weaknesses'].append('Slow execution')
        if avg_confidence < 0.4:
            profile['weaknesses'].append('Low confidence predictions')

        # Generate recommendations
        if overall_success_rate < 70:
            profile['recommendations'].append('Review agent configuration and keywords')
        if avg_duration > 60:
            profile['recommendations'].append('Consider timeout adjustment or optimization')
        if avg_confidence < 0.4:
            profile['recommendations'].append('Improve routing keyword specificity')

        # Get learning history
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT * FROM agent_learning
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (agent_id,))

        learnings = [dict(row) for row in cursor.fetchall()]
        profile['learnings'] = learnings

        return profile

    def compare_agents(self, agent_ids: List[str]) -> Dict:
        """Compare multiple agents."""
        comparison = {
            'agents': {},
            'ranking': [],
            'best_performer': None,
            'fastest': None,
            'most_confident': None
        }

        for agent_id in agent_ids:
            profile = self.get_agent_profile(agent_id)
            comparison['agents'][agent_id] = profile

            if 'error' not in profile:
                comparison['ranking'].append({
                    'agent_id': agent_id,
                    'success_rate': profile['metrics'].get('success_rate', 0),
                    'avg_duration': profile['metrics'].get('avg_duration_seconds', 0)
                })

        # Sort by success rate
        comparison['ranking'].sort(key=lambda x: x['success_rate'], reverse=True)

        if comparison['ranking']:
            comparison['best_performer'] = comparison['ranking'][0]['agent_id']
            comparison['fastest'] = min(
                comparison['ranking'],
                key=lambda x: x['avg_duration']
            )['agent_id']
            comparison['most_confident'] = max(
                comparison['ranking'],
                key=lambda x: x['success_rate']
            )['agent_id']

        return comparison

    def get_optimal_agent_for_task(self, task_preview: str, complexity: str = 'MEDIUM') -> Dict:
        """Suggest optimal agent based on task characteristics."""
        # Get all agent profiles
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT DISTINCT agent_id FROM agent_metrics
        """)
        agent_ids = [row['agent_id'] for row in cursor.fetchall()]

        if not agent_ids:
            return {'error': 'No agents available'}

        # Score each agent
        scores = []
        for agent_id in agent_ids:
            profile = self.get_agent_profile(agent_id)

            if 'error' in profile:
                continue

            metrics = profile.get('metrics', {})
            score = {
                'agent_id': agent_id,
                'success_score': metrics.get('success_rate', 0),
                'speed_score': max(0, 100 - metrics.get('avg_duration_seconds', 100)),
                'confidence_score': metrics.get('avg_confidence', 0) * 100,
                'overall': 0
            }

            # Calculate overall score
            score['overall'] = (
                score['success_score'] * 0.5 +
                score['speed_score'] * 0.3 +
                score['confidence_score'] * 0.2
            )

            scores.append(score)

        # Sort by overall score
        scores.sort(key=lambda x: x['overall'], reverse=True)

        return {
            'suggested_agent': scores[0]['agent_id'] if scores else None,
            'alternatives': [s['agent_id'] for s in scores[1:4]],
            'scores': scores
        }


if __name__ == "__main__":
    tracker = BehaviorTracker()

    # Get all agents
    import json
    config_file = Path.home() / ".opencode" / "config" / "agent-registry.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
        agent_ids = list(config.get('agents', {}).keys())[:5]  # Test with first 5

        print("📊 Agent Behavior Profiles\n")
        for agent_id in agent_ids:
            profile = tracker.get_agent_profile(agent_id)
            if 'error' not in profile:
                print(f"  {agent_id}:")
                print(f"    Success: {profile['metrics'].get('success_rate', 0):.1f}%")
                print(f"    Avg Duration: {profile['metrics'].get('avg_duration_seconds', 0):.1f}s")
                print(f"    Strengths: {profile['strengths']}")
                print()
