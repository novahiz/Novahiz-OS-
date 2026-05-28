#!/usr/bin/env python3
"""
Novahiz Learning Engine — Enable agents to learn from experience.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from engine._path import ensure as _; _()

from engine.database_manager import get_db
from engine.learning.behavior_tracker import BehaviorTracker


class LearningEngine:
    """Enable agents to learn and improve from experience."""

    LEARNING_TYPES = {
        'keyword_optimization': {
            'description': 'Adjust agent keywords based on success patterns',
            'auto_apply': False,
            'impact': 'high'
        },
        'routing_weight': {
            'description': 'Adjust routing priority based on performance',
            'auto_apply': True,
            'impact': 'medium'
        },
        'model_selection': {
            'description': 'Learn best model for each task type',
            'auto_apply': True,
            'impact': 'medium'
        },
        'prompt_improvement': {
            'description': 'Optimize system prompts based on outcomes',
            'auto_apply': False,
            'impact': 'high'
        },
        'context_enhancement': {
            'description': 'Improve context for specific task types',
            'auto_apply': True,
            'impact': 'low'
        }
    }

    def __init__(self, db=None):
        self.db = db or get_db()
        self.tracker = BehaviorTracker(self.db)
        self.base_dir = Path.home() / ".opencode"

    def learn_from_execution(self, agent_id: str, execution_data: Dict) -> Dict:
        """Learn from a single execution."""
        learning_results = {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'learnings': [],
            'applied': []
        }

        # Track execution
        tracking = self.tracker.track_execution(agent_id, execution_data)

        # Analyze outcome
        success = execution_data.get('status') == 'completed'
        confidence = execution_data.get('confidence', 0)
        duration = execution_data.get('duration', 0)

        # Generate learnings based on outcome
        if success and confidence > 0.7:
            # Positive reinforcement learning
            learning_results['learnings'].append({
                'type': 'positive_pattern',
                'data': {
                    'confidence_range': f'{confidence:.2f}',
                    'outcome': 'success'
                },
                'description': 'High confidence led to success'
            })

        elif not success:
            # Failure analysis learning
            learning_results['learnings'].append({
                'type': 'failure_analysis',
                'data': {
                    'confidence': confidence,
                    'duration': duration,
                    'complexity': execution_data.get('complexity', 'MEDIUM')
                },
                'description': 'Analyze failure conditions'
            })

        # Apply auto-learnings
        for learning in learning_results['learnings']:
            if self.LEARNING_TYPES.get(learning['type'], {}).get('auto_apply', False):
                applied = self._apply_learning(agent_id, learning)
                if applied:
                    learning_results['applied'].append(learning['type'])

        return learning_results

    def learn_from_patterns(self, agent_id: str) -> Dict:
        """Learn from detected behavior patterns."""
        profile = self.tracker.get_agent_profile(agent_id)

        if 'error' in profile:
            return {'error': profile['error']}

        learnings = {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'pattern_learnings': [],
            'suggestions': []
        }

        metrics = profile.get('metrics', {})
        strengths = profile.get('strengths', [])
        weaknesses = profile.get('weaknesses', [])

        # Learn from strengths
        for strength in strengths:
            if 'High success rate' in strength:
                learnings['pattern_learnings'].append({
                    'type': 'strength_reinforcement',
                    'data': {'strength': strength},
                    'action': 'Maintain current configuration'
                })

        # Learn from weaknesses (generate improvement suggestions)
        for weakness in weaknesses:
            if 'Low success rate' in weakness:
                learnings['suggestions'].append({
                    'type': 'keyword_review',
                    'priority': 'high',
                    'description': 'Review and refine agent keywords'
                })

            if 'Slow execution' in weakness:
                learnings['suggestions'].append({
                    'type': 'timeout_adjustment',
                    'priority': 'medium',
                    'description': 'Adjust timeout or optimize processing'
                })

        # Store learnings
        for learning in learnings['pattern_learnings']:
            self.db.insert_learning({
                'agent_id': agent_id,
                'lesson_type': 'pattern',
                'lesson_data': learning,
                'applied': True,
                'impact_score': 0.5
            })

        return learnings

    def _apply_learning(self, agent_id: str, learning: Dict) -> bool:
        """Apply a learning to agent configuration."""
        learning_type = learning.get('type')

        if learning_type == 'positive_pattern':
            # Reinforce successful patterns
            return self._reinforce_pattern(agent_id, learning)

        elif learning_type == 'routing_weight':
            # Adjust routing weight
            return self._adjust_routing_weight(agent_id, learning)

        return False

    def _reinforce_pattern(self, agent_id: str, learning: Dict) -> bool:
        """Reinforce a successful pattern."""
        # This would update agent configuration
        # For now, just record the reinforcement
        self.db.insert_learning({
            'agent_id': agent_id,
            'lesson_type': 'reinforcement',
            'lesson_data': learning,
            'applied': True,
            'confidence': 0.8
        })
        return True

    def _adjust_routing_weight(self, agent_id: str, learning: Dict) -> bool:
        """Adjust routing weight for an agent."""
        config_file = self.base_dir / "config" / "agent-registry.json"
        if not config_file.exists():
            return False

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            if agent_id in config.get('agents', {}):
                # Increase score based on success
                current_score = config['agents'][agent_id].get('score', 90)
                new_score = min(current_score + 1, 100)
                config['agents'][agent_id]['score'] = new_score

                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)

                return True
        except Exception:
            pass

        return False

    def get_learning_history(self, agent_id: str = None, limit: int = 50) -> List[Dict]:
        """Get learning history."""
        conn = self.db.get_connection()

        if agent_id:
            cursor = conn.execute("""
                SELECT * FROM agent_learning
                WHERE agent_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (agent_id, limit))
        else:
            cursor = conn.execute("""
                SELECT * FROM agent_learning
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def apply_pending_learnings(self, agent_id: str = None) -> Dict:
        """Apply pending learnings."""
        conn = self.db.get_connection()

        if agent_id:
            cursor = conn.execute("""
                SELECT * FROM agent_learning
                WHERE agent_id = ? AND applied = FALSE
            """, (agent_id,))
        else:
            cursor = conn.execute("""
                SELECT * FROM agent_learning
                WHERE applied = FALSE
            """)

        pending = [dict(row) for row in cursor.fetchall()]

        applied = []
        for learning in pending:
            success = self._apply_learning(learning['agent_id'], learning)
            if success:
                # Mark as applied
                conn.execute("""
                    UPDATE agent_learning
                    SET applied = TRUE, applied_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), learning['id']))
                applied.append(learning['id'])

        conn.commit()

        return {
            'pending_count': len(pending),
            'applied_count': len(applied),
            'applied_ids': applied
        }

    def export_learnings(self, agent_id: str = None) -> str:
        """Export learnings to JSON file."""
        learnings = self.get_learning_history(agent_id)

        export_file = self.base_dir / "data" / f"learnings_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

        with open(export_file, 'w') as f:
            json.dump({
                'exported_at': datetime.now().isoformat(),
                'agent_id': agent_id,
                'learnings': learnings
            }, f, indent=2)

        return str(export_file)


if __name__ == "__main__":
    engine = LearningEngine()

    # Get learning history
    learnings = engine.get_learning_history(limit=10)

    if learnings:
        print(f"📚 Recent Learnings ({len(learnings)}):\n")
        for l in learnings:
            print(f"  Agent: {l['agent_id']}")
            print(f"  Type: {l['lesson_type']}")
            print(f"  Applied: {l['applied']}")
            print()
    else:
        print("No learnings recorded yet")
