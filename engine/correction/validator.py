#!/usr/bin/env python3
"""
Novahiz Correction Validator — Validate corrections before/after application.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.database_manager import get_db


class CorrectionValidator:
    """Validate corrections before and after application."""

    def __init__(self, db=None):
        self.db = db or get_db()
        self.base_dir = Path.home() / ".opencode"

    def validate_before(self, correction_plan: Dict) -> Dict:
        """Validate a correction before applying."""
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'risk_level': 'low',  # low, medium, high
            'recommendations': []
        }

        target_type = correction_plan.get('target_type')
        action = correction_plan.get('action')

        # Check risk level based on action
        high_risk_actions = ['disable_agent', 'reset_config', 'delete_data']
        medium_risk_actions = ['adjust_routing_weights', 'increase_timeout', 'restart_daemon']

        if action in high_risk_actions:
            validation['risk_level'] = 'high'
            validation['recommendations'].append('Manual review recommended')
        elif action in medium_risk_actions:
            validation['risk_level'] = 'medium'

        # Check if target exists
        if target_type == 'agent':
            agent_id = correction_plan.get('target_id')
            if not self._agent_exists(agent_id):
                validation['valid'] = False
                validation['errors'].append(f'Agent {agent_id} not found')

            # Check if agent is critical
            if self._is_critical_agent(agent_id):
                validation['warnings'].append(f'{agent_id} is a critical agent')
                validation['risk_level'] = 'high'

        elif target_type == 'system':
            # Check system state before system-wide changes
            monitoring = self.db.get_system_state('monitoring_enabled')
            if not monitoring.get('enabled'):
                validation['warnings'].append('Monitoring is not enabled')

        # Check recent corrections for same target
        recent = self.db.get_recent_corrections(limit=5)
        target_corrections = [
            c for c in recent
            if c.get('target_id') == correction_plan.get('target_id')
        ]

        if len(target_corrections) >= 3:
            validation['warnings'].append('Multiple recent corrections for this target')
            validation['recommendations'].append('Consider manual investigation')

        # Check if backup exists
        if not correction_plan.get('backup_created', False):
            validation['warnings'].append('No backup created')
            validation['recommendations'].append('Create backup before proceeding')

        return validation

    def validate_after(self, correction_id: str) -> Dict:
        """Validate results after correction application."""
        validation = {
            'valid': True,
            'success': False,
            'issues': [],
            'metrics_before': {},
            'metrics_after': {}
        }

        # Get correction from database
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM auto_corrections WHERE id = ?",
            (correction_id,)
        )
        row = cursor.fetchone()

        if not row:
            validation['valid'] = False
            validation['issues'].append('Correction not found')
            return validation

        correction = dict(row)

        # Parse states
        try:
            validation['metrics_before'] = json.loads(correction.get('before_state', '{}'))
            validation['metrics_after'] = json.loads(correction.get('after_state', '{}'))
        except json.JSONDecodeError:
            validation['issues'].append('Could not parse state data')

        # Check if correction was successful
        if correction.get('success'):
            validation['success'] = True
        else:
            validation['issues'].append('Correction reported failure')

        # Validate specific correction types
        target_type = correction.get('target_type')
        target_id = correction.get('target_id')

        if target_type == 'agent':
            # Check agent metrics improved
            metrics = self.db.get_agent_metrics(target_id, limit=1)
            if metrics:
                current = metrics[0]
                error_rate = current.get('error_rate', 100)

                if error_rate > 50:
                    validation['issues'].append(f'Agent still has high error rate: {error_rate}%')

        elif target_type == 'system':
            # Check system health
            health = self.db.get_system_state('last_health_check')
            if not health.get('timestamp'):
                validation['issues'].append('System health check not updated')

        return validation

    def _agent_exists(self, agent_id: str) -> bool:
        """Check if an agent exists in registry."""
        config_file = self.base_dir / "config" / "agent-registry.json"
        if not config_file.exists():
            return False

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            return agent_id in config.get('agents', {})
        except Exception:
            return False

    def _is_critical_agent(self, agent_id: str) -> bool:
        """Check if an agent is critical (high priority)."""
        config_file = self.base_dir / "config" / "agent-registry.json"
        if not config_file.exists():
            return False

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            agent = config.get('agents', {}).get(agent_id, {})
            return agent.get('priority', 3) == 1
        except Exception:
            return False

    def create_backup(self, target_type: str, target_id: str = None) -> str:
        """Create backup before correction."""
        backup_dir = self.base_dir / "backups" / "autocorrect"
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_file = backup_dir / f"backup_{target_type}_{timestamp}.json"

        if target_type == 'agent':
            # Backup agent registry
            config_file = self.base_dir / "config" / "agent-registry.json"
            if config_file.exists():
                import shutil
                shutil.copy2(config_file, backup_file)

        elif target_type == 'routing':
            # Backup routing config
            config_file = self.base_dir / "config" / "routing-rules.json"
            if config_file.exists():
                import shutil
                shutil.copy2(config_file, backup_file)

        elif target_type == 'system':
            # Backup system state
            state = {
                'monitoring': self.db.get_system_state('monitoring_enabled'),
                'autocorrect': self.db.get_system_state('autocorrect_enabled'),
                'health': self.db.get_system_state('last_health_check')
            }
            with open(backup_file, 'w') as f:
                json.dump(state, f, indent=2)

        return str(backup_file) if backup_file.exists() else None


if __name__ == "__main__":
    validator = CorrectionValidator()

    # Test validation
    test_plan = {
        'target_type': 'agent',
        'target_id': 'neo-security',
        'action': 'disable_agent',
        'backup_created': False
    }

    result = validator.validate_before(test_plan)
    print("Validation Result:")
    print(f"  Valid: {result['valid']}")
    print(f"  Risk: {result['risk_level']}")
    print(f"  Warnings: {result['warnings']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Recommendations: {result['recommendations']}")
