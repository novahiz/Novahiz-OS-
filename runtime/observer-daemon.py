#!/usr/bin/env python3
"""
Novahiz Observer Daemon — Real-time monitoring core.

Watches:
- executions/ directory for new executions
- logs/structured/ for error patterns
- MCP servers health
- Daemon processes
- System resources

Detects:
- Execution failures
- Timeouts
- Routing errors
- Resource exhaustion
- Anomalies
"""
import os
import sys
import json
import time
import hashlib
import sqlite3
import subprocess
import threading
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from typing import Optional, Dict, List, Any, Tuple

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from engine.database_manager import get_db, init_db

# Configuration
BASE_DIR = Path.home() / ".opencode"
EXECUTIONS_DIR = BASE_DIR / "executions"
LOGS_DIR = BASE_DIR / "logs" / "structured"
PIDS_DIR = BASE_DIR / "pids"
DAEMON_PID_FILE = PIDS_DIR / "observer-daemon.pid"

POLL_INTERVAL = 2  # seconds
LOG_TAIL_SIZE = 100  # lines to tail from each log file

# Error patterns to detect in logs
ERROR_PATTERNS = [
    "error", "ERROR", "Error",
    "failed", "FAILED", "Failed",
    "exception", "EXCEPTION", "Exception",
    "timeout", "TIMEOUT", "Timeout",
    "critical", "CRITICAL", "Critical",
    "crash", "CRASH", "Crash",
    "unreachable", "UNREACHABLE",
    "connection refused", "CONNECTION REFUSED",
    "rate limit", "RATE LIMIT",
    "out of memory", "OUT OF MEMORY",
    "disk full", "DISK FULL",
]

SEVERITY_KEYWORDS = {
    'critical': ['critical', 'CRITICAL', 'fatal', 'FATAL', 'crash', 'CRASH'],
    'high': ['error', 'ERROR', 'failed', 'FAILED', 'exception', 'EXCEPTION'],
    'medium': ['warning', 'WARNING', 'warn', 'WARN', 'timeout', 'TIMEOUT'],
    'low': ['notice', 'NOTICE', 'info', 'INFO', 'debug', 'DEBUG'],
}


class ObserverDaemon:
    """Main observer daemon class."""

    def __init__(self):
        self.running = False
        self.db = None
        self.watched_files = {}  # file_path -> last_position
        self.seen_executions = set()  # Track processed executions
        self.error_counts = {}  # source -> count (for rate limiting)
        self.start_time = None
        self._lock = threading.Lock()

    def setup_signal_handlers(self):
        """Setup graceful shutdown handlers."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Observer Daemon received signal {signum}, shutting down...")
        self.stop()

    def start(self):
        """Start the observer daemon."""
        print("🔍 Starting Novahiz Observer Daemon...")

        # Initialize database
        if not os.path.exists(BASE_DIR / "data" / "novahiz_state.db"):
            print("📦 Initializing database...")
            init_db()

        self.db = get_db()
        self.running = True
        self.start_time = datetime.now()

        # Write PID file
        PIDS_DIR.mkdir(parents=True, exist_ok=True)
        with open(DAEMON_PID_FILE, 'w') as f:
            f.write(str(os.getpid()))

        # Enable monitoring in system state
        self.db.update_system_state('monitoring_enabled', {
            'enabled': True,
            'started_at': self.start_time.isoformat(),
            'pid': os.getpid()
        })

        print(f"✅ Observer Daemon started (PID: {os.getpid()})")
        print(f"   Poll interval: {POLL_INTERVAL}s")
        print(f"   Watching: {EXECUTIONS_DIR}, {LOGS_DIR}")

        # Main loop
        self._main_loop()

    def stop(self):
        """Stop the observer daemon."""
        self.running = False

        # Update system state
        if self.db:
            self.db.update_system_state('monitoring_enabled', {
                'enabled': False,
                'started_at': self.start_time.isoformat() if self.start_time else None,
                'stopped_at': datetime.now().isoformat(),
                'pid': None
            })

        # Remove PID file
        if DAEMON_PID_FILE.exists():
            DAEMON_PID_FILE.unlink()

        print("✅ Observer Daemon stopped")

    def _main_loop(self):
        """Main monitoring loop."""
        last_health_check = time.time()
        health_interval = 60  # seconds

        while self.running:
            try:
                # Check executions
                self._check_executions()

                # Check logs
                self._check_logs()

                # Check system health
                if time.time() - last_health_check >= health_interval:
                    self._check_system_health()
                    last_health_check = time.time()

                # Record performance metrics
                self._record_performance()

                time.sleep(POLL_INTERVAL)

            except Exception as e:
                self._log_error('daemon', 'high', 'observer_loop', str(e))
                time.sleep(POLL_INTERVAL * 2)  # Back off on error

    def _check_executions(self):
        """Check executions directory for new/failed executions."""
        if not EXECUTIONS_DIR.exists():
            return

        try:
            for exec_file in EXECUTIONS_DIR.glob("exec_*.json"):
                exec_id = exec_file.stem

                # Skip already processed
                if exec_id in self.seen_executions:
                    continue

                try:
                    with open(exec_file, 'r') as f:
                        exec_data = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    self._log_error(
                        'execution',
                        'medium',
                        'corrupt_file',
                        f"Failed to read execution file: {exec_file.name}",
                        context={'file': exec_file.name, 'error': str(e)}
                    )
                    continue

                self.seen_executions.add(exec_id)

                # Check execution status
                status = exec_data.get('status', 'unknown')
                agent = exec_data.get('agent', 'unknown')
                task = exec_data.get('task', '')[:100]

                # Record routing history
                self.db.insert_routing_history({
                    'task_hash': hashlib.md5(task.encode()).hexdigest(),
                    'task_preview': task,
                    'primary_agent': agent,
                    'primary_confidence': exec_data.get('confidence', 0),
                    'complexity': exec_data.get('complexity', 'MEDIUM'),
                    'success': status == 'completed'
                })

                # Check for failures
                if status == 'failed':
                    error_msg = exec_data.get('error', 'Unknown execution failure')
                    self._log_error(
                        'execution',
                        'high',
                        'execution_failed',
                        f"Execution failed: {error_msg}",
                        context={
                            'exec_id': exec_id,
                            'agent': agent,
                            'task': task
                        }
                    )

                    # Check for repeated failures
                    self._check_repeated_failures(agent)

                elif status == 'timeout':
                    self._log_error(
                        'execution',
                        'medium',
                        'execution_timeout',
                        f"Execution timed out for agent {agent}",
                        context={
                            'exec_id': exec_id,
                            'agent': agent,
                            'task': task
                        }
                    )

                # Update agent metrics
                self._update_agent_metrics(agent, exec_data)

        except Exception as e:
            self._log_error('daemon', 'medium', 'execution_check_error', str(e))

    def _check_logs(self):
        """Check structured logs for error patterns."""
        if not LOGS_DIR.exists():
            return

        try:
            for log_file in LOGS_DIR.glob("*_structured.json"):
                self._tail_log_file(log_file)
        except Exception as e:
            self._log_error('daemon', 'low', 'log_check_error', str(e))

    def _tail_log_file(self, log_file: Path):
        """Tail a log file for new errors."""
        try:
            file_path = str(log_file)
            last_pos = self.watched_files.get(file_path, 0)

            with open(log_file, 'r') as f:
                # If file is smaller than last position, it was rotated
                f.seek(0, 2)
                file_size = f.tell()
                if file_size < last_pos:
                    last_pos = 0
                    self.watched_files[file_path] = 0

                f.seek(last_pos)
                lines = f.readlines()

                # Update position
                self.watched_files[file_path] = f.tell()

                # Analyze new lines
                for line in lines[-LOG_TAIL_SIZE:]:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        log_entry = json.loads(line)
                        self._analyze_log_entry(log_entry, log_file.stem)
                    except json.JSONDecodeError:
                        # Not JSON, check for error patterns
                        self._check_line_for_errors(line, log_file.stem)

        except Exception as e:
            self._log_error('daemon', 'low', 'log_tail_error', f"Error tailing {log_file}: {e}")

    def _analyze_log_entry(self, entry: dict, source: str):
        """Analyze a structured log entry."""
        # Check for error level
        level = entry.get('level', '').lower()

        if level in ['error', 'fatal', 'critical']:
            message = entry.get('message', entry.get('msg', 'Unknown error'))
            severity = 'critical' if level in ['fatal', 'critical'] else 'high'

            self._log_error(
                source,
                severity,
                'log_error',
                message,
                context=entry
            )

        # Check message for error patterns
        message = entry.get('message', entry.get('msg', ''))
        if message:
            self._check_line_for_errors(str(message), source)

    def _check_line_for_errors(self, line: str, source: str):
        """Check a log line for error patterns."""
        # Determine severity
        severity = 'low'
        for sev, keywords in SEVERITY_KEYWORDS.items():
            if any(kw in line for kw in keywords):
                severity = sev
                break

        if severity in ['low', 'notice', 'info', 'debug']:
            return  # Skip low severity

        # Check for specific error patterns
        for pattern in ERROR_PATTERNS:
            if pattern.lower() in line.lower():
                # Rate limit similar errors
                error_key = f"{source}:{pattern}"
                self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

                # Only log if not too frequent
                if self.error_counts[error_key] <= 5:
                    self._log_error(
                        source,
                        severity,
                        'pattern_detected',
                        f"Error pattern detected: {pattern}",
                        context={'line': line[:200], 'pattern': pattern}
                    )
                break

    def _check_system_health(self):
        """Check overall system health."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.db.insert_performance_metric({
                'metric_type': 'cpu',
                'metric_name': 'cpu_usage',
                'value': cpu_percent,
                'unit': '%',
                'source': 'observer',
                'threshold_warning': 70,
                'threshold_critical': 90
            })

            # Memory usage
            memory = psutil.virtual_memory()
            self.db.insert_performance_metric({
                'metric_type': 'memory',
                'metric_name': 'memory_usage',
                'value': memory.percent,
                'unit': '%',
                'source': 'observer',
                'threshold_warning': 70,
                'threshold_critical': 90
            })

            # Disk usage
            disk = psutil.disk_usage(str(BASE_DIR))
            self.db.insert_performance_metric({
                'metric_type': 'disk',
                'metric_name': 'disk_usage',
                'value': disk.percent,
                'unit': '%',
                'source': 'observer',
                'threshold_warning': 80,
                'threshold_critical': 95
            })

            # Check MCP servers
            self._check_mcp_servers()

            # Update health check timestamp
            self.db.update_system_state('last_health_check', {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'cpu': cpu_percent,
                'memory': memory.percent,
                'disk': disk.percent
            })

        except Exception as e:
            self._log_error('daemon', 'high', 'health_check_failed', str(e))

    def _check_mcp_servers(self):
        """Check if MCP servers are running."""
        mcp_processes = []

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []))
                    if 'mcp' in cmdline.lower() and 'observer' not in cmdline.lower():
                        mcp_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline[:100]
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not mcp_processes:
                self._log_error(
                    'daemon',
                    'medium',
                    'no_mcp_servers',
                    'No MCP server processes detected',
                    context={'checked_at': datetime.now().isoformat()}
                )
            else:
                # Record as performance metric
                self.db.insert_performance_metric({
                    'metric_type': 'process',
                    'metric_name': 'mcp_servers_running',
                    'value': len(mcp_processes),
                    'unit': 'count',
                    'source': 'observer',
                    'threshold_warning': 0,  # Alert if 0
                    'threshold_critical': 0
                })

        except Exception as e:
            self._log_error('daemon', 'low', 'mcp_check_error', str(e))

    def _record_performance(self):
        """Record daemon performance metrics."""
        try:
            # Get daemon process
            process = psutil.Process(os.getpid())

            # Memory
            mem_info = process.memory_info()
            self.db.insert_performance_metric({
                'metric_type': 'memory',
                'metric_name': 'observer_memory',
                'value': mem_info.rss / 1024 / 1024,  # MB
                'unit': 'MB',
                'source': 'observer_daemon',
                'threshold_warning': 500,
                'threshold_critical': 1000
            })

            # CPU
            cpu_percent = process.cpu_percent()
            self.db.insert_performance_metric({
                'metric_type': 'cpu',
                'metric_name': 'observer_cpu',
                'value': cpu_percent,
                'unit': '%',
                'source': 'observer_daemon',
                'threshold_warning': 50,
                'threshold_critical': 80
            })

        except Exception as e:
            pass  # Don't log errors from performance recording

    def _check_repeated_failures(self, agent: str):
        """Check for repeated agent failures."""
        # Get recent failures for this agent
        recent_errors = self.db.get_unresolved_errors(limit=10)
        agent_failures = [
            e for e in recent_errors
            if e.get('category') == 'execution' and agent in str(e.get('context', {}))
        ]

        if len(agent_failures) >= 3:
            self.db.insert_alert({
                'alert_type': 'error',
                'severity': 'high',
                'title': f"Repeated failures for agent {agent}",
                'message': f"Agent {agent} has failed {len(agent_failures)} times recently",
                'context': {'agent': agent, 'failure_count': len(agent_failures)}
            })

    def _update_agent_metrics(self, agent: str, exec_data: dict):
        """Update metrics for an agent."""
        try:
            # Get existing metrics
            existing = self.db.get_agent_metrics(agent, limit=1)

            if existing:
                prev = existing[0]
                tasks_completed = prev.get('tasks_completed', 0) + (1 if exec_data.get('status') == 'completed' else 0)
                tasks_failed = prev.get('tasks_failed', 0) + (1 if exec_data.get('status') == 'failed' else 0)

                # Calculate new averages
                duration = exec_data.get('duration', 0)
                prev_avg = prev.get('avg_duration_seconds', 0)
                new_avg = ((prev_avg * prev.get('tasks_completed', 0)) + duration) / max(tasks_completed, 1)

                success_rate = (tasks_completed / max(tasks_completed + tasks_failed, 1)) * 100
            else:
                tasks_completed = 1 if exec_data.get('status') == 'completed' else 0
                tasks_failed = 1 if exec_data.get('status') == 'failed' else 0
                new_avg = exec_data.get('duration', 0)
                success_rate = 100 if tasks_completed else 0

            self.db.insert_agent_metric({
                'agent_id': agent,
                'tasks_completed': tasks_completed,
                'tasks_failed': tasks_failed,
                'avg_duration_seconds': new_avg,
                'success_rate': success_rate,
                'error_rate': 100 - success_rate
            })

        except Exception as e:
            self._log_error('daemon', 'low', 'metrics_update_error', str(e))

    def _log_error(self, source: str, severity: str, category: str, message: str, context: dict = None):
        """Log an error to the database."""
        try:
            error_id = f"err_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            self.db.insert_error({
                'id': error_id,
                'source': source,
                'severity': severity,
                'category': category,
                'message': message,
                'context': context or {},
                'timestamp': datetime.now().isoformat()
            })

            # Create alert for high/critical errors
            if severity in ['critical', 'high']:
                self.db.insert_alert({
                    'alert_type': 'error',
                    'severity': severity,
                    'title': f"{category.replace('_', ' ').title()}",
                    'message': message,
                    'context': context or {}
                })

        except Exception as e:
            print(f"Failed to log error: {e}", file=sys.stderr)


def main():
    """Main entry point."""
    daemon = ObserverDaemon()
    daemon.setup_signal_handlers()

    if len(sys.argv) > 1:
        if sys.argv[1] == "stop":
            # Find and stop running daemon
            if DAEMON_PID_FILE.exists():
                with open(DAEMON_PID_FILE, 'r') as f:
                    pid = int(f.read().strip())
                try:
                    os.kill(pid, signal.SIGTERM)
                    print(f"✅ Stopped Observer Daemon (PID: {pid})")
                    DAEMON_PID_FILE.unlink()
                except ProcessLookupError:
                    print("⚠️  Daemon not running")
                    DAEMON_PID_FILE.unlink()
            else:
                print("⚠️  No PID file found, daemon may not be running")
            return

        elif sys.argv[1] == "status":
            if DAEMON_PID_FILE.exists():
                with open(DAEMON_PID_FILE, 'r') as f:
                    pid = int(f.read().strip())
                try:
                    proc = psutil.Process(pid)
                    if 'observer' in ' '.join(proc.cmdline()).lower():
                        print(f"✅ Observer Daemon running (PID: {pid})")
                        print(f"   Status: {proc.status()}")
                        print(f"   CPU: {proc.cpu_percent()}%")
                        print(f"   Memory: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
                        return
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            print("❌ Observer Daemon not running")
            return

    try:
        daemon.start()
    except KeyboardInterrupt:
        daemon.stop()


if __name__ == "__main__":
    main()
