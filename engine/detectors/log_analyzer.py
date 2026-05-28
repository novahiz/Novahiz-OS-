#!/usr/bin/env python3
"""
Novahiz Log Analyzer — Analyze structured logs for patterns.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class LogAnalyzer:
    """Analyze structured logs for patterns and anomalies."""

    def __init__(self, logs_dir: str = None):
        self.logs_dir = Path(logs_dir) if logs_dir else Path.home() / ".opencode" / "logs" / "structured"
        self.error_counts = defaultdict(int)
        self.pattern_cache = {}

    def analyze_all(self) -> Dict:
        """Analyze all structured logs."""
        if not self.logs_dir.exists():
            return {'error': 'Logs directory not found'}

        results = {
            'analyzed_at': datetime.now().isoformat(),
            'files_analyzed': 0,
            'total_entries': 0,
            'error_count': 0,
            'warning_count': 0,
            'by_source': {},
            'by_level': defaultdict(int),
            'recent_errors': [],
            'patterns': []
        }

        for log_file in self.logs_dir.glob("*_structured.json"):
            file_results = self.analyze_file(log_file)
            results['files_analyzed'] += 1
            results['total_entries'] += file_results.get('entries', 0)
            results['error_count'] += file_results.get('errors', 0)
            results['warning_count'] += file_results.get('warnings', 0)

            source = log_file.stem.replace('_structured', '')
            results['by_source'][source] = file_results

            for level, count in file_results.get('by_level', {}).items():
                results['by_level'][level] += count

            results['recent_errors'].extend(file_results.get('recent_errors', [])[:5])

        # Convert defaultdict to dict for JSON serialization
        results['by_level'] = dict(results['by_level'])

        # Detect patterns across all logs
        results['patterns'] = self.detect_patterns(results)

        return results

    def analyze_file(self, log_file: Path) -> Dict:
        """Analyze a single log file."""
        results = {
            'file': log_file.name,
            'entries': 0,
            'errors': 0,
            'warnings': 0,
            'by_level': defaultdict(int),
            'recent_errors': [],
            'time_range': {'start': None, 'end': None}
        }

        try:
            with open(log_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        results['entries'] += 1

                        level = entry.get('level', 'info').lower()
                        results['by_level'][level] += 1

                        if level in ['error', 'fatal', 'critical']:
                            results['errors'] += 1
                            results['recent_errors'].append({
                                'timestamp': entry.get('timestamp', entry.get('time')),
                                'message': entry.get('message', entry.get('msg', ''))[:200],
                                'source': log_file.stem
                            })

                        elif level in ['warning', 'warn']:
                            results['warnings'] += 1

                        # Track time range
                        ts = entry.get('timestamp', entry.get('time'))
                        if ts:
                            if not results['time_range']['start']:
                                results['time_range']['start'] = ts
                            results['time_range']['end'] = ts

                    except json.JSONDecodeError:
                        continue

        except Exception as e:
            results['error'] = str(e)

        # Convert defaultdict
        results['by_level'] = dict(results['by_level'])

        return results

    def detect_patterns(self, results: Dict) -> List[Dict]:
        """Detect patterns across log analysis."""
        patterns = []

        # High error rate pattern
        if results['total_entries'] > 0:
            error_rate = results['error_count'] / results['total_entries']
            if error_rate > 0.1:  # More than 10% errors
                patterns.append({
                    'pattern': 'high_error_rate',
                    'severity': 'high',
                    'message': f"High error rate: {error_rate*100:.1f}%",
                    'data': {'error_rate': error_rate, 'threshold': 0.1}
                })

        # Source-specific patterns
        for source, data in results.get('by_source', {}).items():
            if data.get('errors', 0) > 10:
                patterns.append({
                    'pattern': 'error_source',
                    'severity': 'medium',
                    'message': f"Source {source} has {data['errors']} errors",
                    'data': {'source': source, 'error_count': data['errors']}
                })

        return patterns

    def get_errors_by_category(self, limit: int = 50) -> List[Dict]:
        """Get recent errors categorized."""
        errors = []

        for log_file in self.logs_dir.glob("*_structured.json"):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            level = entry.get('level', '').lower()

                            if level in ['error', 'fatal', 'critical']:
                                errors.append({
                                    'timestamp': entry.get('timestamp', entry.get('time')),
                                    'source': log_file.stem,
                                    'level': level,
                                    'message': entry.get('message', entry.get('msg', ''))[:200],
                                    'category': self._categorize_message(entry.get('message', ''))
                                })

                                if len(errors) >= limit:
                                    return errors

                        except json.JSONDecodeError:
                            continue

            except Exception:
                continue

        # Sort by timestamp
        errors.sort(key=lambda x: x.get('timestamp', '') or '', reverse=True)
        return errors

    def _categorize_message(self, message: str) -> str:
        """Categorize an error message."""
        message_lower = message.lower()

        categories = {
            'connection': ['connection', 'network', 'socket', 'timeout', 'refused'],
            'authentication': ['auth', 'token', 'permission', 'unauthorized', 'forbidden'],
            'resource': ['memory', 'disk', 'cpu', 'quota', 'limit'],
            'configuration': ['config', 'setting', 'environment', 'variable'],
            'data': ['database', 'query', 'sql', 'data', 'record'],
            'api': ['api', 'endpoint', 'request', 'response', 'http'],
            'parsing': ['parse', 'json', 'xml', 'format', 'syntax'],
        }

        for category, keywords in categories.items():
            if any(kw in message_lower for kw in keywords):
                return category

        return 'general'

    def tail_errors(self, lines: int = 20) -> List[Dict]:
        """Tail recent errors from all logs."""
        all_errors = []

        for log_file in self.logs_dir.glob("*_structured.json"):
            try:
                with open(log_file, 'r') as f:
                    file_errors = []
                    for line in f:
                        try:
                            entry = json.loads(line)
                            level = entry.get('level', '').lower()

                            if level in ['error', 'fatal', 'critical']:
                                file_errors.append({
                                    'timestamp': entry.get('timestamp', entry.get('time')),
                                    'source': log_file.stem,
                                    'level': level,
                                    'message': entry.get('message', entry.get('msg', ''))[:200]
                                })
                        except json.JSONDecodeError:
                            continue

                    all_errors.extend(file_errors[-lines:])

            except Exception:
                continue

        # Sort by timestamp and return most recent
        all_errors.sort(key=lambda x: x.get('timestamp', '') or '', reverse=True)
        return all_errors[:lines]


if __name__ == "__main__":
    analyzer = LogAnalyzer()
    results = analyzer.analyze_all()

    print(f"📊 Log Analysis Results\n")
    print(f"  Files analyzed: {results.get('files_analyzed', 0)}")
    print(f"  Total entries:  {results.get('total_entries', 0)}")
    print(f"  Errors:         {results.get('error_count', 0)}")
    print(f"  Warnings:       {results.get('warning_count', 0)}")

    if results.get('patterns'):
        print(f"\n🔍 Patterns detected:")
        for p in results['patterns']:
            print(f"  [{p['severity'].upper()}] {p['message']}")

    if results.get('recent_errors'):
        print(f"\n❌ Recent errors:")
        for e in results['recent_errors'][:5]:
            print(f"  [{e['source']}] {e['message'][:80]}...")
