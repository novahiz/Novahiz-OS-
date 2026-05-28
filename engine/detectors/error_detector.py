#!/usr/bin/env python3
"""
Novahiz Error Detector — Detect patterns and anomalies.

Detects:
- Repeated failures
- Slow degradation
- Routing confusion
- Resource exhaustion
- Stale state
- Timeout anomalies
"""
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.database_manager import get_db


class ErrorDetector:
    """Detect error patterns and anomalies."""

    # Detection patterns
    PATTERNS = {
        'repeated_failure': {
            'description': 'Agent fails 3+ times in 10 minutes',
            'threshold': 3,
            'window_minutes': 10,
            'severity': 'high'
        },
        'slow_degradation': {
            'description': 'Success rate dropping over time',
            'threshold': 0.15,  # 15% drop
            'window_hours': 24,
            'severity': 'medium'
        },
        'routing_confusion': {
            'description': 'Multiple agents with similar confidence',
            'threshold': 0.1,  # 10% difference
            'severity': 'low'
        },
        'timeout_anomaly': {
            'description': 'Execution time > 2x average',
            'threshold': 2.0,
            'severity': 'medium'
        },
        'resource_exhaustion': {
            'description': 'Memory/CPU growing unbounded',
            'threshold': 0.9,  # 90%
            'severity': 'critical'
        },
        'stale_state': {
            'description': 'No updates in 24 hours',
            'threshold_hours': 24,
            'severity': 'medium'
        },
        'confidence_drop': {
            'description': 'Routing confidence consistently low',
            'threshold': 0.4,
            'window_count': 5,
            'severity': 'medium'
        }
    }

    def __init__(self, db=None):
        self.db = db or get_db()
        self.detection_history = []

    def detect_all(self) -> List[Dict]:
        """Run all detections."""
        detections = []

        detections.extend(self.detect_repeated_failures())
        detections.extend(self.detect_slow_degradation())
        detections.extend(self.detect_routing_confusion())
        detections.extend(self.detect_timeout_anomalies())
        detections.extend(self.detect_resource_exhaustion())
        detections.extend(self.detect_stale_state())
        detections.extend(self.detect_confidence_drop())

        return detections

    def detect_repeated_failures(self) -> List[Dict]:
        """Detect repeated agent failures."""
        detections = []
        errors = self.db.get_unresolved_errors(limit=100)

        # Group by agent and category
        failure_groups = defaultdict(list)
        for error in errors:
            if error.get('category') == 'execution':
                context = error.get('context', {})
                agent = context.get('agent', 'unknown')
                failure_groups[agent].append(error)

        # Check thresholds
        pattern = self.PATTERNS['repeated_failure']
        for agent, failures in failure_groups.items():
            if len(failures) >= pattern['threshold']:
                detection = {
                    'pattern': 'repeated_failure',
                    'severity': pattern['severity'],
                    'target_type': 'agent',
                    'target_id': agent,
                    'message': f"Agent {agent} failed {len(failures)} times (threshold: {pattern['threshold']})",
                    'data': {
                        'failure_count': len(failures),
                        'threshold': pattern['threshold'],
                        'error_ids': [f['id'] for f in failures]
                    },
                    'suggested_correction': f"temporarily_disable_{agent}"
                }
                detections.append(detection)

        return detections

    def detect_slow_degradation(self) -> List[Dict]:
        """Detect success rate degradation over time."""
        detections = []
        pattern = self.PATTERNS['slow_degradation']

        # Get all agents with metrics
        agents = set()
        metrics = self.db.get_agent_metrics(limit=1000)
        for m in metrics:
            agents.add(m.get('agent_id'))

        for agent in agents:
            agent_metrics = [m for m in metrics if m.get('agent_id') == agent]
            if len(agent_metrics) < 2:
                continue

            # Sort by timestamp
            agent_metrics.sort(key=lambda x: x.get('timestamp', ''))

            # Compare recent vs older
            mid = len(agent_metrics) // 2
            older = agent_metrics[:mid]
            recent = agent_metrics[mid:]

            if older and recent:
                older_avg = sum(m.get('success_rate', 0) for m in older) / len(older)
                recent_avg = sum(m.get('success_rate', 0) for m in recent) / len(recent)

                drop = older_avg - recent_avg
                if drop >= pattern['threshold'] * 100:  # Convert to percentage
                    detection = {
                        'pattern': 'slow_degradation',
                        'severity': pattern['severity'],
                        'target_type': 'agent',
                        'target_id': agent,
                        'message': f"Agent {agent} success rate dropped from {older_avg:.1f}% to {recent_avg:.1f}%",
                        'data': {
                            'older_avg': older_avg,
                            'recent_avg': recent_avg,
                            'drop': drop,
                            'threshold': pattern['threshold'] * 100
                        },
                        'suggested_correction': "review_agent_performance"
                    }
                    detections.append(detection)

        return detections

    def detect_routing_confusion(self) -> List[Dict]:
        """Detect routing confusion (multiple agents with similar confidence)."""
        detections = []
        pattern = self.PATTERNS['routing_confusion']

        # Get recent routing history
        history = self.db.get_routing_history(limit=100)

        # Group by task hash (similar tasks)
        task_groups = defaultdict(list)
        for route in history:
            task_hash = route.get('task_hash')
            if task_hash:
                task_groups[task_hash].append(route)

        # Check for confusion
        for task_hash, routes in task_groups.items():
            if len(routes) < 2:
                continue

            # Check if different agents were tried
            agents = set(r.get('primary_agent') for r in routes)
            if len(agents) > 1:
                confidences = [r.get('primary_confidence', 0) for r in routes]
                if confidences:
                    diff = max(confidences) - min(confidences)
                    if diff <= pattern['threshold']:
                        detection = {
                            'pattern': 'routing_confusion',
                            'severity': pattern['severity'],
                            'target_type': 'routing',
                            'target_id': task_hash,
                            'message': f"Routing confusion: {len(agents)} agents tried with similar confidence",
                            'data': {
                                'agents': list(agents),
                                'confidence_diff': diff,
                                'threshold': pattern['threshold']
                            },
                            'suggested_correction': "adjust_routing_weights"
                        }
                        detections.append(detection)

        return detections

    def detect_timeout_anomalies(self) -> List[Dict]:
        """Detect timeout anomalies."""
        detections = []
        pattern = self.PATTERNS['timeout_anomaly']

        # Get agent metrics
        metrics = self.db.get_agent_metrics(limit=1000)

        # Group by agent
        agent_metrics = defaultdict(list)
        for m in metrics:
            agent_metrics[m.get('agent_id')].append(m)

        for agent, mets in agent_metrics.items():
            if len(mets) < 2:
                continue

            # Calculate average duration
            durations = [m.get('avg_duration_seconds', 0) for m in mets if m.get('avg_duration_seconds', 0) > 0]
            if not durations:
                continue

            avg_duration = sum(durations) / len(durations)
            max_duration = max(durations)

            if max_duration > avg_duration * pattern['threshold']:
                detection = {
                    'pattern': 'timeout_anomaly',
                    'severity': pattern['severity'],
                    'target_type': 'agent',
                    'target_id': agent,
                    'message': f"Agent {agent} has timeout anomaly: {max_duration:.1f}s vs {avg_duration:.1f}s avg",
                    'data': {
                        'max_duration': max_duration,
                        'avg_duration': avg_duration,
                        'ratio': max_duration / avg_duration,
                        'threshold': pattern['threshold']
                    },
                    'suggested_correction': "increase_timeout_for_agent"
                }
                detections.append(detection)

        return detections

    def detect_resource_exhaustion(self) -> List[Dict]:
        """Detect resource exhaustion patterns."""
        detections = []
        pattern = self.PATTERNS['resource_exhaustion']

        # Get recent performance metrics
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT * FROM performance_metrics
            WHERE metric_type IN ('cpu', 'memory', 'disk')
            ORDER BY timestamp DESC
            LIMIT 100
        """)

        metrics = [dict(row) for row in cursor.fetchall()]

        # Check for high resource usage
        for metric in metrics:
            value = metric.get('value', 0)
            metric_name = metric.get('metric_name', '')

            if value >= pattern['threshold'] * 100:  # Convert to percentage
                detection = {
                    'pattern': 'resource_exhaustion',
                    'severity': pattern['severity'],
                    'target_type': 'system',
                    'target_id': metric_name,
                    'message': f"Resource exhaustion: {metric_name} at {value:.1f}%",
                    'data': {
                        'metric_name': metric_name,
                        'value': value,
                        'threshold': pattern['threshold'] * 100
                    },
                    'suggested_correction': f"cleanup_{metric_name}"
                }
                detections.append(detection)
                break  # Only one resource exhaustion alert at a time

        return detections

    def detect_stale_state(self) -> List[Dict]:
        """Detect stale state (no updates)."""
        detections = []
        pattern = self.PATTERNS['stale_state']

        # Check system state
        health = self.db.get_system_state('last_health_check')
        if health:
            timestamp = health.get('timestamp')
            if timestamp:
                last_update = datetime.fromisoformat(timestamp)
                hours_since = (datetime.now() - last_update).total_seconds() / 3600

                if hours_since >= pattern['threshold_hours']:
                    detection = {
                        'pattern': 'stale_state',
                        'severity': pattern['severity'],
                        'target_type': 'system',
                        'target_id': 'health_check',
                        'message': f"No health check in {hours_since:.1f} hours",
                        'data': {
                            'last_update': timestamp,
                            'hours_since': hours_since,
                            'threshold': pattern['threshold_hours']
                        },
                        'suggested_correction': "restart_observer_daemon"
                    }
                    detections.append(detection)

        return detections

    def detect_confidence_drop(self) -> List[Dict]:
        """Detect consistently low routing confidence."""
        detections = []
        pattern = self.PATTERNS['confidence_drop']

        # Get recent routing history
        history = self.db.get_routing_history(limit=pattern['window_count'] * 2)

        if len(history) < pattern['window_count']:
            return detections

        # Check recent confidence values
        recent = history[:pattern['window_count']]
        low_confidence = [r for r in recent if r.get('primary_confidence', 0) < pattern['threshold']]

        if len(low_confidence) >= pattern['window_count'] * 0.6:  # 60% low
            detection = {
                'pattern': 'confidence_drop',
                'severity': pattern['severity'],
                'target_type': 'routing',
                'target_id': 'global',
                'message': f"Low routing confidence: {len(low_confidence)}/{len(recent)} routes below {pattern['threshold']}",
                'data': {
                    'low_count': len(low_confidence),
                    'total': len(recent),
                    'threshold': pattern['threshold']
                },
                'suggested_correction': "recalibrate_routing_weights"
            }
            detections.append(detection)

        return detections

    def get_correction_recommendations(self, detection: Dict) -> Dict:
        """Get detailed correction recommendations for a detection."""
        pattern = detection.get('pattern')
        data = detection.get('data', {})

        recommendations = {
            'repeated_failure': {
                'action': 'Investigate agent failures',
                'steps': [
                    'Review error logs for the agent',
                    'Check if agent dependencies are available',
                    'Verify agent configuration',
                    'Consider temporary disable if critical'
                ],
                'auto_correctable': True,
                'auto_correction': 'disable_agent_temporarily'
            },
            'slow_degradation': {
                'action': 'Review agent performance',
                'steps': [
                    'Analyze recent task changes',
                    'Check for model degradation',
                    'Review keyword matching',
                    'Consider retraining or reconfiguration'
                ],
                'auto_correctable': False
            },
            'routing_confusion': {
                'action': 'Adjust routing weights',
                'steps': [
                    'Review keyword overlaps',
                    'Adjust agent priorities',
                    'Consider merging similar agents',
                    'Add more specific keywords'
                ],
                'auto_correctable': True,
                'auto_correction': 'adjust_routing_weights'
            },
            'timeout_anomaly': {
                'action': 'Adjust timeout settings',
                'steps': [
                    'Check for network issues',
                    'Review task complexity',
                    'Adjust timeout for specific agent',
                    'Consider load balancing'
                ],
                'auto_correctable': True,
                'auto_correction': 'increase_timeout'
            },
            'resource_exhaustion': {
                'action': 'Clean up resources',
                'steps': [
                    'Clear old log files',
                    'Purge old executions',
                    'Vacuum database',
                    'Restart daemon processes'
                ],
                'auto_correctable': True,
                'auto_correction': 'cleanup_resources'
            },
            'stale_state': {
                'action': 'Restart monitoring',
                'steps': [
                    'Check observer daemon status',
                    'Restart daemon if needed',
                    'Verify database connectivity',
                    'Check for system issues'
                ],
                'auto_correctable': True,
                'auto_correction': 'restart_daemon'
            },
            'confidence_drop': {
                'action': 'Recalibrate routing',
                'steps': [
                    'Review routing rules',
                    'Check keyword definitions',
                    'Adjust confidence thresholds',
                    'Consider adding new agents'
                ],
                'auto_correctable': False
            }
        }

        return recommendations.get(pattern, {
            'action': 'Manual investigation required',
            'steps': ['Review detection data', 'Consult logs', 'Take appropriate action'],
            'auto_correctable': False
        })


if __name__ == "__main__":
    # Test detection
    detector = ErrorDetector()
    detections = detector.detect_all()

    if detections:
        print(f"🔍 Detected {len(detections)} issues:\n")
        for d in detections:
            print(f"  [{d['severity'].upper()}] {d['pattern']}")
            print(f"    Target: {d['target_type']}/{d['target_id']}")
            print(f"    Message: {d['message']}")
            print()
    else:
        print("✅ No issues detected")
