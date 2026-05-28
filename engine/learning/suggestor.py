#!/usr/bin/env python3
"""
Novahiz Suggestion Generator — Generate improvement suggestions.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engine.database_manager import get_db
from engine.learning.behavior_tracker import BehaviorTracker
from engine.detectors.error_detector import ErrorDetector


class SuggestionGenerator:
    """Generate improvement suggestions for agents and system."""

    def __init__(self, db=None):
        self.db = db or get_db()
        self.tracker = BehaviorTracker(self.db)
        self.detector = ErrorDetector(self.db)
        self.base_dir = Path.home() / ".opencode"

    def generate_for_agent(self, agent_id: str) -> List[Dict]:
        """Generate improvement suggestions for a specific agent."""
        suggestions = []

        # Get agent profile
        profile = self.tracker.get_agent_profile(agent_id)

        if 'error' in profile:
            return [{'type': 'error', 'message': profile['error'], 'priority': 'high'}]

        metrics = profile.get('metrics', {})
        strengths = profile.get('strengths', [])
        weaknesses = profile.get('weaknesses', [])

        # Generate suggestions based on weaknesses
        for weakness in weaknesses:
            if 'Low success rate' in weakness:
                suggestions.append({
                    'type': 'success_rate',
                    'priority': 'high',
                    'title': 'Improve Success Rate',
                    'description': f"Current: {metrics.get('success_rate', 0):.1f}%",
                    'actions': [
                        'Review agent keywords for specificity',
                        'Check for keyword overlaps with other agents',
                        'Analyze failed executions for patterns',
                        'Consider adjusting routing priority'
                    ],
                    'estimated_impact': '+10-20% success rate'
                })

            if 'Slow execution' in weakness:
                suggestions.append({
                    'type': 'performance',
                    'priority': 'medium',
                    'title': 'Improve Execution Speed',
                    'description': f"Current avg: {metrics.get('avg_duration_seconds', 0):.1f}s",
                    'actions': [
                        'Increase timeout if tasks are legitimately complex',
                        'Review task complexity distribution',
                        'Consider model optimization',
                        'Implement caching for repeated tasks'
                    ],
                    'estimated_impact': '-30-50% execution time'
                })

            if 'Low confidence' in weakness:
                suggestions.append({
                    'type': 'confidence',
                    'priority': 'medium',
                    'title': 'Improve Routing Confidence',
                    'description': f"Current avg: {metrics.get('avg_confidence', 0):.2f}",
                    'actions': [
                        'Add more specific keywords',
                        'Review agent domain definition',
                        'Check for ambiguous task types',
                        'Consider splitting agent into specialized sub-agents'
                    ],
                    'estimated_impact': '+0.2-0.3 confidence'
                })

        # Generate suggestions based on patterns
        learnings = self.db.get_agent_metrics(agent_id, limit=10)
        if learnings:
            # Check for consistency patterns
            success_rates = [m.get('success_rate', 0) for m in learnings]
            if len(success_rates) > 3:
                variance = max(success_rates) - min(success_rates)
                if variance > 30:
                    suggestions.append({
                        'type': 'consistency',
                        'priority': 'medium',
                        'title': 'Improve Consistency',
                        'description': f"Success rate variance: {variance:.1f}%",
                        'actions': [
                            'Identify conditions leading to failures',
                            'Standardize task handling',
                            'Review error handling logic'
                        ],
                        'estimated_impact': 'More predictable performance'
                    })

        return suggestions

    def generate_for_system(self) -> List[Dict]:
        """Generate system-wide improvement suggestions."""
        suggestions = []

        # Get system stats
        stats = self.db.get_stats()

        # Check error rate
        if stats.get('unresolved_errors', 0) > 10:
            suggestions.append({
                'type': 'error_backlog',
                'priority': 'high',
                'title': 'Clear Error Backlog',
                'description': f"{stats['unresolved_errors']} unresolved errors",
                'actions': [
                    'Review and resolve critical errors first',
                    'Enable auto-correction for common issues',
                    'Set up alerts for new critical errors'
                ],
                'estimated_impact': 'Improved system stability'
            })

        # Check auto-correction effectiveness
        if stats.get('total_corrections', 0) > 0:
            success_rate = (stats.get('successful_corrections', 0) / stats['total_corrections']) * 100
            if success_rate < 70:
                suggestions.append({
                    'type': 'autocorrect_effectiveness',
                    'priority': 'medium',
                    'title': 'Improve Auto-Correction',
                    'description': f"Success rate: {success_rate:.1f}%",
                    'actions': [
                        'Review failed corrections for patterns',
                        'Adjust correction thresholds',
                        'Add validation before applying corrections'
                    ],
                    'estimated_impact': 'More reliable auto-correction'
                })

        # Check agent coverage
        if stats.get('agents_tracked', 0) < 5:
            suggestions.append({
                'type': 'agent_coverage',
                'priority': 'low',
                'title': 'Expand Agent Tracking',
                'description': f"Only {stats['agents_tracked']} agents being tracked",
                'actions': [
                    'Ensure all agents have execution history',
                    'Enable metrics collection for all agents',
                    'Review agent activity levels'
                ],
                'estimated_impact': 'Better agent insights'
            })

        # Run detections for additional suggestions
        detections = self.detector.detect_all()
        for detection in detections:
            recommendations = self.detector.get_correction_recommendations(detection)
            suggestions.append({
                'type': 'detection_based',
                'priority': detection.get('severity', 'medium'),
                'title': f"Address: {detection.get('pattern', 'Unknown')}",
                'description': detection.get('message', ''),
                'actions': recommendations.get('steps', []),
                'estimated_impact': recommendations.get('action', '')
            })

        return suggestions

    def generate_for_routing(self) -> List[Dict]:
        """Generate routing improvement suggestions."""
        suggestions = []

        # Get recent routing history
        history = self.db.get_routing_history(limit=100)

        if not history:
            return [{'type': 'info', 'message': 'No routing history available', 'priority': 'low'}]

        # Analyze routing patterns
        agent_counts = {}
        confidence_dist = []

        for route in history:
            agent = route.get('primary_agent', 'unknown')
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            confidence_dist.append(route.get('primary_confidence', 0))

        # Check for routing imbalance
        if agent_counts:
            max_count = max(agent_counts.values())
            min_count = min(agent_counts.values())
            if max_count > min_count * 3:
                suggestions.append({
                    'type': 'routing_imbalance',
                    'priority': 'medium',
                    'title': 'Balance Agent Load',
                    'description': f"Some agents get {max_count/min_count:.1f}x more tasks",
                    'actions': [
                        'Review keyword distribution',
                        'Adjust agent priorities',
                        'Consider load balancing rules'
                    ],
                    'estimated_impact': 'Better resource utilization'
                })

        # Check confidence distribution
        if confidence_dist:
            avg_confidence = sum(confidence_dist) / len(confidence_dist)
            low_confidence = sum(1 for c in confidence_dist if c < 0.4)

            if avg_confidence < 0.5:
                suggestions.append({
                    'type': 'low_confidence',
                    'priority': 'high',
                    'title': 'Improve Routing Confidence',
                    'description': f"Avg confidence: {avg_confidence:.2f}",
                    'actions': [
                        'Review keyword definitions',
                        'Add more specific keywords',
                        'Adjust confidence thresholds',
                        'Consider agent consolidation'
                    ],
                    'estimated_impact': 'More accurate routing'
                })

            if low_confidence / len(confidence_dist) > 0.3:
                suggestions.append({
                    'type': 'confidence_threshold',
                    'priority': 'medium',
                    'title': 'Adjust Confidence Threshold',
                    'description': f"{low_confidence}/{len(confidence_dist)} routes below 0.4 confidence",
                    'actions': [
                        'Raise minimum confidence threshold',
                        'Enable multi-agent deliberation for low confidence',
                        'Add fallback routing rules'
                    ],
                    'estimated_impact': 'Better routing decisions'
                })

        return suggestions

    def get_all_suggestions(self) -> Dict:
        """Get all suggestions categorized."""
        return {
            'generated_at': datetime.now().isoformat(),
            'agents': {},
            'system': self.generate_for_system(),
            'routing': self.generate_for_routing()
        }

    def export_suggestions(self, output_file: str = None) -> str:
        """Export suggestions to file."""
        if not output_file:
            output_file = str(self.base_dir / "data" / f"suggestions_{datetime.now().strftime('%Y%m%d%H%M%S')}.json")

        suggestions = self.get_all_suggestions()

        with open(output_file, 'w') as f:
            json.dump(suggestions, f, indent=2)

        return output_file


if __name__ == "__main__":
    generator = SuggestionGenerator()

    print("📋 System Suggestions\n")
    system_suggestions = generator.generate_for_system()
    for s in system_suggestions:
        print(f"  [{s['priority'].upper()}] {s['title']}")
        print(f"    {s['description']}")
        print()

    print("\n📋 Routing Suggestions\n")
    routing_suggestions = generator.generate_for_routing()
    for s in routing_suggestions:
        print(f"  [{s['priority'].upper()}] {s['title']}")
        print(f"    {s['description']}")
        print()
