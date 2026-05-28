#!/usr/bin/env python3
"""
Novahiz Monitoring CLI — Command-line interface for monitoring.

Commands:
  nv monitor start          Start monitoring daemon
  nv monitor stop           Stop monitoring daemon
  nv monitor status         Get monitoring status
  nv errors [filter]        View errors
  nv errors resolve <id>    Resolve an error
  nv autocorrect enable     Enable auto-correction
  nv autocorrect disable    Disable auto-correction
  nv autocorrect status     Get auto-correction status
  nv autocorrect run        Run auto-correction
  nv agents metrics         View agent metrics
  nv agents learn <agent>   View agent learnings
  nv agents improve <agent> Get improvement suggestions
  nv system health          Get system health
  nv system state           Get system state
  nv db query <sql>         Query database (debug)
  nv report generate        Generate report
"""
import json
import os
import sys
import signal
import subprocess
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.database_manager import get_db, init_db
from engine.detectors.error_detector import ErrorDetector
from engine.correction.auto_correct import AutoCorrectEngine
from engine.learning.suggestor import SuggestionGenerator
from engine.learning.behavior_tracker import BehaviorTracker

# Configuration
BASE_DIR = Path.home() / ".opencode"
OBSERVER_SCRIPT = BASE_DIR / "runtime" / "observer-daemon.py"
PID_FILE = BASE_DIR / "pids" / "observer-daemon.pid"


def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))


def ensure_db():
    """Ensure database is initialized."""
    db_path = BASE_DIR / "data" / "novahiz_state.db"
    if not db_path.exists():
        print("📦 Initializing database...")
        init_db()
    return get_db()


# ============================================================================
# MONITOR COMMANDS
# ============================================================================

def cmd_monitor_start(args):
    """Start monitoring daemon."""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGCONT)
            print(f"✅ Monitoring daemon already running (PID: {pid})")
            return
        except (ProcessLookupError, ValueError):
            PID_FILE.unlink()

    # Start daemon
    try:
        process = subprocess.Popen(
            [sys.executable, str(OBSERVER_SCRIPT)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        print(f"✅ Monitoring daemon started (PID: {process.pid})")
    except Exception as e:
        print(f"❌ Failed to start: {e}")


def cmd_monitor_stop(args):
    """Stop monitoring daemon."""
    if not PID_FILE.exists():
        print("ℹ️  Monitoring daemon not running")
        return

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink()
        print(f"✅ Monitoring daemon stopped (PID: {pid})")
    except ProcessLookupError:
        PID_FILE.unlink()
        print("ℹ️  Daemon was not running, cleaned up PID file")
    except Exception as e:
        print(f"❌ Failed to stop: {e}")


def cmd_monitor_status(args):
    """Get monitoring status."""
    import psutil

    status = {"running": False}

    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            proc = psutil.Process(pid)
            if 'observer' in ' '.join(proc.cmdline()).lower():
                status = {
                    "running": True,
                    "pid": pid,
                    "status": proc.status(),
                    "cpu_percent": proc.cpu_percent(),
                    "memory_mb": round(proc.memory_info().rss / 1024 / 1024, 2),
                    "uptime": str(datetime.now() - datetime.fromtimestamp(proc.create_time()))
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
            pass

    print_json(status)


# ============================================================================
# ERROR COMMANDS
# ============================================================================

def cmd_errors(args):
    """View errors."""
    db = ensure_db()

    if args and args[0] == 'resolve' and len(args) > 1:
        # Resolve specific error
        error_id = args[1]
        conn = db.get_connection()
        conn.execute("""
            UPDATE errors
            SET resolved = TRUE, resolved_at = ?, resolved_by = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), 'user', error_id))
        conn.commit()
        print(f"✅ Error {error_id} resolved")
        return

    # Get errors
    limit = 20
    if args and args[-1].isdigit():
        limit = int(args[-1])

    errors = db.get_unresolved_errors(limit)
    print(f"📋 Unresolved Errors ({len(errors)}):\n")

    for e in errors:
        icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(e['severity'], '⚪')
        print(f"{icon} [{e['id'][:12]}] {e['category']}/{e['source']}")
        print(f"   {e['message'][:80]}")
        print(f"   {e['timestamp']}")
        print()


# ============================================================================
# AUTOCORRECT COMMANDS
# ============================================================================

def cmd_autocorrect_enable(args):
    """Enable auto-correction."""
    db = ensure_db()
    db.update_system_state('autocorrect_enabled', {
        'enabled': True,
        'threshold': 0.8,
        'enabled_at': datetime.now().isoformat()
    })
    print("✅ Auto-correction enabled")


def cmd_autocorrect_disable(args):
    """Disable auto-correction."""
    db = ensure_db()
    db.update_system_state('autocorrect_enabled', {
        'enabled': False,
        'disabled_at': datetime.now().isoformat()
    })
    print("✅ Auto-correction disabled")


def cmd_autocorrect_status(args):
    """Get auto-correction status."""
    db = ensure_db()
    status = db.get_system_state('autocorrect_enabled')
    stats = db.get_stats()

    print_json({
        'config': status,
        'stats': {
            'total_corrections': stats.get('total_corrections', 0),
            'successful_corrections': stats.get('successful_corrections', 0)
        }
    })


def cmd_autocorrect_run(args):
    """Run auto-correction."""
    db = ensure_db()
    engine = AutoCorrectEngine(db)

    detections = engine.get_detections()
    print(f"🔍 Found {len(detections)} issues\n")

    if not detections:
        print("✅ No issues requiring correction")
        return

    auto_approve = args and '--auto' in args

    for detection in detections:
        print(f"  Pattern: {detection['pattern']}")
        print(f"  Target: {detection['target_type']}/{detection['target_id']}")

        result = engine.apply_correction(detection, auto_approve=auto_approve)

        if result.get('applied'):
            print(f"  ✅ Correction applied")
        elif result.get('requires_approval'):
            print(f"  ⚠️  Requires approval (use --auto to auto-approve)")
        else:
            print(f"  ❌ Not applied: {result.get('error', 'Unknown')}")
        print()


# ============================================================================
# AGENT COMMANDS
# ============================================================================

def cmd_agents_metrics(args):
    """View agent metrics."""
    db = ensure_db()

    agent_id = args[0] if args else None
    metrics = db.get_agent_metrics(agent_id, limit=10)

    if not metrics:
        print("ℹ️  No metrics found")
        return

    print(f"📊 Agent Metrics ({len(metrics)} records):\n")
    for m in metrics:
        print(f"  {m['agent_id']}:")
        print(f"    Success: {m.get('success_rate', 0):.1f}%")
        print(f"    Duration: {m.get('avg_duration_seconds', 0):.1f}s")
        print(f"    Error Rate: {m.get('error_rate', 0):.1f}%")
        print(f"    {m['timestamp']}")
        print()


def cmd_agents_learn(args):
    """View agent learnings."""
    db = ensure_db()

    if not args:
        print("❌ Usage: nv agents learn <agent_id>")
        return

    agent_id = args[0]
    conn = db.get_connection()
    cursor = conn.execute("""
        SELECT * FROM agent_learning
        WHERE agent_id = ?
        ORDER BY timestamp DESC
        LIMIT 20
    """, (agent_id,))

    learnings = [dict(row) for row in cursor.fetchall()]

    print(f"📚 Agent Learnings for {agent_id} ({len(learnings)}):\n")
    for l in learnings:
        print(f"  [{l['lesson_type']}] {l['applied']}")
        print(f"    Confidence: {l.get('confidence', 0):.2f}")
        print(f"    Impact: {l.get('impact_score', 0):.2f}")
        print(f"    {l['timestamp']}")
        print()


def cmd_agents_improve(args):
    """Get improvement suggestions for agent."""
    if not args:
        print("❌ Usage: nv agents improve <agent_id>")
        return

    agent_id = args[0]
    generator = SuggestionGenerator()
    suggestions = generator.generate_for_agent(agent_id)

    print(f"💡 Improvement Suggestions for {agent_id} ({len(suggestions)}):\n")
    for s in suggestions:
        print(f"  [{s['priority'].upper()}] {s['title']}")
        print(f"    {s['description']}")
        print(f"    Actions: {', '.join(s['actions'][:3])}")
        print(f"    Impact: {s.get('estimated_impact', 'Unknown')}")
        print()


# ============================================================================
# SYSTEM COMMANDS
# ============================================================================

def cmd_system_health(args):
    """Get system health."""
    import psutil

    db = ensure_db()

    health = {
        'timestamp': datetime.now().isoformat(),
        'monitoring': db.get_system_state('monitoring_enabled'),
        'autocorrect': db.get_system_state('autocorrect_enabled'),
        'last_health_check': db.get_system_state('last_health_check'),
        'system': {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage(str(BASE_DIR)).percent
        },
        'stats': db.get_stats()
    }

    print_json(health)


def cmd_system_state(args):
    """Get system state."""
    db = ensure_db()
    conn = db.get_connection()
    cursor = conn.execute("SELECT * FROM system_state")
    states = [dict(row) for row in cursor.fetchall()]

    print_json({
        'states': states
    })


# ============================================================================
# DATABASE COMMANDS
# ============================================================================

def cmd_db_query(args):
    """Query database."""
    if not args:
        print("❌ Usage: nv db query <sql>")
        return

    db = ensure_db()
    query = ' '.join(args)

    try:
        results = db.run_query(query)
        print_json(results)
    except Exception as e:
        print(f"❌ Query failed: {e}")


# ============================================================================
# REPORT COMMANDS
# ============================================================================

def cmd_report_generate(args):
    """Generate monitoring report."""
    db = ensure_db()
    generator = SuggestionGenerator()

    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': db.get_stats(),
        'suggestions': generator.get_all_suggestions(),
        'active_alerts': db.get_active_alerts(),
        'recent_corrections': db.get_recent_corrections(10)
    }

    # Save report
    report_file = BASE_DIR / "data" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"✅ Report generated: {report_file}")
    print_json(report['summary'])


# ============================================================================
# HELP
# ============================================================================

def cmd_help(args):
    """Show help."""
    print(__doc__)


# ============================================================================
# MAIN
# ============================================================================

COMMANDS = {
    'monitor': {
        'start': cmd_monitor_start,
        'stop': cmd_monitor_stop,
        'status': cmd_monitor_status
    },
    'errors': cmd_errors,
    'autocorrect': {
        'enable': cmd_autocorrect_enable,
        'disable': cmd_autocorrect_disable,
        'status': cmd_autocorrect_status,
        'run': cmd_autocorrect_run
    },
    'agents': {
        'metrics': cmd_agents_metrics,
        'learn': cmd_agents_learn,
        'improve': cmd_agents_improve
    },
    'system': {
        'health': cmd_system_health,
        'state': cmd_system_state
    },
    'db': {
        'query': cmd_db_query
    },
    'report': {
        'generate': cmd_report_generate
    },
    'help': cmd_help
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == 'help':
        cmd_help(args)
        return

    if cmd not in COMMANDS:
        print(f"❌ Unknown command: {cmd}")
        print(__doc__)
        return

    handler = COMMANDS[cmd]

    # Handle nested commands (e.g., monitor start, agents metrics)
    if isinstance(handler, dict):
        if not args:
            print(f"❌ Usage: nv {cmd} <subcommand>")
            print(f"    Subcommands: {', '.join(handler.keys())}")
            return

        subcmd = args[0]
        subargs = args[1:]

        if subcmd in handler:
            handler[subcmd](subargs)
        else:
            print(f"❌ Unknown subcommand: {subcmd}")
            print(f"    Available: {', '.join(handler.keys())}")
    else:
        handler(args)


if __name__ == "__main__":
    main()
