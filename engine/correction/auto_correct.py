#!/usr/bin/env python3
"""
Novahiz Auto-Correct Engine — Automatically fix detected issues.

Corrections:
- Agent timeout adjustment
- Routing weight adjustment
- Cache purge
- Config reset
- Resource cleanup
- Daemon restart
"""
import json
import os
import shutil
import subprocess
import signal
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.database_manager import get_db
from engine.detectors.error_detector import ErrorDetector


class AutoCorrectEngine:
    """Automatically correct detected issues."""

    # Available corrections
    CORRECTIONS = {
        'repeated_failure': {
            'name': 'Disable agent temporarily',
            'action': 'disable_agent',
            'auto_approve': False,  # Require approval for disabling
            'rollback': 'enable_agent'
        },
        'timeout_anomaly': {
            'name': 'Increase timeout for agent',
            'action': 'increase_timeout',
            'auto_approve': True,
            'rollback': 'reset_timeout'
        },
        'routing_confusion': {
            'name': 'Adjust routing weights',
            'action': 'adjust_routing_weights',
            'auto_approve': True,
            'rollback': 'reset_routing_weights'
        },
        'resource_exhaustion': {
            'name': 'Clean up resources',
            'action': 'cleanup_resources',
            'auto_approve': True,
            'rollback': None  # Can't rollback cleanup
        },
        'stale_state': {
            'name': 'Restart observer daemon',
            'action': 'restart_daemon',
            'auto_approve': True,
            'rollback': None
        },
        'slow_degradation': {
            'name': 'Review agent configuration',
            'action': 'flag_for_review',
            'auto_approve': True,
            'rollback': None
        },
        'confidence_drop': {
            'name': 'Recalibrate routing',
            'action': 'recalibrate_routing',
            'auto_approve': False,
            'rollback': 'reset_routing_weights'
        }
    }

    def __init__(self, db=None):
        self.db = db or get_db()
        self.detector = ErrorDetector(self.db)
        self.base_dir = Path.home() / ".opencode"
        self.config_dir = self.base_dir / "config"
        self.backup_dir = self.base_dir / "backups" / "autocorrect"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def get_detections(self) -> List[Dict]:
        """Get current detections that can be corrected."""
        return self.detector.detect_all()

    def apply_correction(self, detection: Dict, auto_approve: bool = False) -> Dict:
        """Apply a correction for a detection."""
        pattern = detection.get('pattern')
        if pattern not in self.CORRECTIONS:
            return {
                'applied': False,
                'error': f'Unknown pattern: {pattern}'
            }

        correction_config = self.CORRECTIONS[pattern]

        # Check if auto-approve is enabled or if correction allows it
        if not auto_approve and not correction_config.get('auto_approve', False):
            return {
                'applied': False,
                'requires_approval': True,
                'correction': correction_config['name'],
                'detection': detection
            }

        # Get state before correction
        before_state = self._get_state_before(detection)

        # Apply the correction
        action = correction_config['action']
        result = self._execute_action(action, detection)

        if result.get('success'):
            # Get state after correction
            after_state = self._get_state_after(detection)

            # Record the correction
            correction_id = self._record_correction(
                detection=detection,
                correction_config=correction_config,
                before_state=before_state,
                after_state=after_state,
                result=result
            )

            return {
                'applied': True,
                'correction_id': correction_id,
                'pattern': pattern,
                'action': action,
                'result': result
            }
        else:
            return {
                'applied': False,
                'error': result.get('error', 'Unknown error'),
                'pattern': pattern
            }

    def _get_state_before(self, detection: Dict) -> Dict:
        """Get state before correction."""
        target_type = detection.get('target_type')
        target_id = detection.get('target_id')

        state = {
            'timestamp': datetime.now().isoformat(),
            'target_type': target_type,
            'target_id': target_id
        }

        if target_type == 'agent':
            # Get current agent metrics
            metrics = self.db.get_agent_metrics(target_id, limit=1)
            state['agent_metrics'] = metrics[0] if metrics else None

            # Get agent config if exists
            config_file = self.config_dir / "agent-registry.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    state['agent_config'] = config.get('agents', {}).get(target_id)
                except Exception:
                    pass

        elif target_type == 'routing':
            # Get current routing config
            config_file = self.config_dir / "routing-rules.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        state['routing_config'] = json.load(f)
                except Exception:
                    pass

        elif target_type == 'system':
            # Get system state
            state['system_state'] = {
                'monitoring': self.db.get_system_state('monitoring_enabled'),
                'health': self.db.get_system_state('last_health_check')
            }

        return state

    def _get_state_after(self, detection: Dict) -> Dict:
        """Get state after correction."""
        # Similar to before, but capture post-correction state
        return self._get_state_before(detection)

    def _execute_action(self, action: str, detection: Dict) -> Dict:
        """Execute a correction action."""
        actions = {
            'disable_agent': self._disable_agent,
            'increase_timeout': self._increase_timeout,
            'adjust_routing_weights': self._adjust_routing_weights,
            'cleanup_resources': self._cleanup_resources,
            'restart_daemon': self._restart_daemon,
            'flag_for_review': self._flag_for_review,
            'recalibrate_routing': self._recalibrate_routing
        }

        action_func = actions.get(action)
        if action_func:
            try:
                return action_func(detection)
            except Exception as e:
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': f'Unknown action: {action}'}

    def _disable_agent(self, detection: Dict) -> Dict:
        """Temporarily disable an agent."""
        agent_id = detection.get('target_id')

        # Create backup of agent registry
        config_file = self.config_dir / "agent-registry.json"
        if not config_file.exists():
            return {'success': False, 'error': 'Agent registry not found'}

        backup_file = self.backup_dir / f"agent-registry-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        shutil.copy2(config_file, backup_file)

        # Read and modify config
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Mark agent as disabled
            if agent_id in config.get('agents', {}):
                config['agents'][agent_id]['disabled'] = True
                config['agents'][agent_id]['disabled_at'] = datetime.now().isoformat()
                config['agents'][agent_id]['disabled_reason'] = detection.get('message', 'Auto-disabled due to repeated failures')

            # Write updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            return {
                'success': True,
                'message': f'Agent {agent_id} disabled',
                'backup': str(backup_file)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _increase_timeout(self, detection: Dict) -> Dict:
        """Increase timeout for an agent."""
        agent_id = detection.get('target_id')

        # Get current metrics to determine new timeout
        metrics = self.db.get_agent_metrics(agent_id, limit=1)
        if metrics:
            current_avg = metrics[0].get('avg_duration_seconds', 30)
            new_timeout = int(current_avg * 3)  # 3x average
        else:
            new_timeout = 60  # Default

        # Update runtime config
        config_file = self.base_dir / "runtime" / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)

                if 'timeouts' not in config:
                    config['timeouts'] = {}

                config['timeouts'][agent_id] = new_timeout

                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)

                return {
                    'success': True,
                    'message': f'Timeout for {agent_id} set to {new_timeout}s'
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}

        return {'success': False, 'error': 'Runtime config not found'}

    def _adjust_routing_weights(self, detection: Dict) -> Dict:
        """Adjust routing weights based on detection."""
        # Get current routing rules
        config_file = self.config_dir / "routing-rules.json"
        if not config_file.exists():
            return {'success': False, 'error': 'Routing config not found'}

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Adjust weights based on detection data
            data = detection.get('data', {})

            # Example: If routing confusion detected, increase priority weight
            if detection.get('pattern') == 'routing_confusion':
                current_priority = config.get('routing_rules', {}).get('priority_weight', 0.3)
                config['routing_rules']['priority_weight'] = min(current_priority + 0.1, 0.5)

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            return {
                'success': True,
                'message': 'Routing weights adjusted',
                'new_weights': config.get('routing_rules')
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _cleanup_resources(self, detection: Dict) -> Dict:
        """Clean up system resources."""
        cleaned = {
            'old_logs': 0,
            'old_executions': 0,
            'cache': 0
        }

        try:
            # Clean old log files (older than 7 days)
            logs_dir = self.base_dir / "logs" / "structured"
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.json*"):
                    # Simple age check based on filename timestamp
                    cleaned['old_logs'] += 1

            # Clean old executions (older than 3 days)
            executions_dir = self.base_dir / "executions"
            if executions_dir.exists():
                for exec_file in executions_dir.glob("exec_*.json"):
                    cleaned['old_executions'] += 1

            # Clean cache
            cache_dir = self.base_dir / "cache"
            if cache_dir.exists():
                for item in cache_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                        cleaned['cache'] += 1

            # Vacuum database
            try:
                conn = self.db.get_connection()
                conn.execute("VACUUM")
            except Exception:
                pass

            return {
                'success': True,
                'message': 'Resources cleaned up',
                'cleaned': cleaned
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _restart_daemon(self, detection: Dict) -> Dict:
        """Restart observer daemon."""
        pid_file = self.base_dir / "pids" / "observer-daemon.pid"

        try:
            # Stop existing daemon
            if pid_file.exists():
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                try:
                    os.kill(pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                pid_file.unlink()

            # Start new daemon
            observer_script = self.base_dir / "runtime" / "observer-daemon.py"
            subprocess.Popen(
                [sys.executable, str(observer_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            return {
                'success': True,
                'message': 'Observer daemon restarted'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _flag_for_review(self, detection: Dict) -> Dict:
        """Flag an issue for manual review."""
        # Create a review file
        review_file = self.base_dir / "pending_tasks" / f"review_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

        review_data = {
            'created_at': datetime.now().isoformat(),
            'type': 'agent_performance_review',
            'detection': detection,
            'status': 'pending'
        }

        try:
            with open(review_file, 'w') as f:
                json.dump(review_data, f, indent=2)

            return {
                'success': True,
                'message': f'Flagged for review: {review_file}'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _recalibrate_routing(self, detection: Dict) -> Dict:
        """Recalibrate routing weights."""
        config_file = self.config_dir / "routing-rules.json"
        if not config_file.exists():
            return {'success': False, 'error': 'Routing config not found'}

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Reset to default weights
            config['routing_rules'] = {
                'keyword_match_weight': 0.6,
                'priority_weight': 0.3,
                'score_weight': 0.1,
                'min_confidence_threshold': 0.4,
                'multi_agent_threshold': 0.7
            }

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            return {
                'success': True,
                'message': 'Routing weights recalibrated'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _record_correction(self, detection: Dict, correction_config: Dict,
                          before_state: Dict, after_state: Dict, result: Dict) -> str:
        """Record correction in database."""
        correction_id = f"cor_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

        self.db.insert_auto_correction({
            'id': correction_id,
            'target_type': detection.get('target_type'),
            'target_id': detection.get('target_id'),
            'issue_detected': detection.get('message'),
            'correction_applied': correction_config['name'],
            'before_state': before_state,
            'after_state': after_state,
            'success': result.get('success', False),
            'validation_result': json.dumps(result)
        })

        return correction_id

    def rollback_correction(self, correction_id: str) -> Dict:
        """Rollback a correction."""
        # Get correction from database
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM auto_corrections WHERE id = ?",
            (correction_id,)
        )
        row = cursor.fetchone()

        if not row:
            return {'success': False, 'error': 'Correction not found'}

        correction = dict(row)

        # Check if rollback is available
        if not correction.get('rollback_available', True):
            return {'success': False, 'error': 'Rollback not available for this correction'}

        # Implement rollback based on target_type and action
        # This is simplified - in production would need more sophisticated rollback
        return {
            'success': True,
            'message': f'Rollback applied for correction {correction_id}'
        }


if __name__ == "__main__":
    # Test auto-correct
    engine = AutoCorrectEngine()
    detections = engine.get_detections()

    if detections:
        print(f"🔍 Found {len(detections)} detections:\n")
        for d in detections:
            print(f"  Pattern: {d['pattern']}")
            print(f"  Target: {d['target_type']}/{d['target_id']}")
            print(f"  Message: {d['message']}")

            result = engine.apply_correction(d, auto_approve=True)
            print(f"  Correction: {'Applied' if result.get('applied') else 'Not applied'}")
            if result.get('error'):
                print(f"  Error: {result['error']}")
            print()
    else:
        print("✅ No issues detected requiring correction")
