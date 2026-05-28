#!/usr/bin/env python3
"""
Novahiz Monitoring MCP Server — Expose monitoring tools via MCP.

Tools:
- nv_monitor_start: Start monitoring daemon
- nv_monitor_stop: Stop monitoring daemon
- nv_monitor_status: Get monitoring status
- nv_get_errors: Get detected errors
- nv_get_agent_metrics: Get agent metrics
- nv_trigger_autocorrect: Trigger auto-correction
- nv_get_alerts: Get active alerts
- nv_acknowledge_alert: Acknowledge an alert
- nv_get_system_health: Get system health
- nv_get_recent_corrections: Get recent auto-corrections
"""
import os
import sys
import json
import signal
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from engine.database_manager import get_db, init_db
from engine.detectors.error_detector import ErrorDetector

# Configuration
BASE_DIR = Path.home() / ".opencode"
OBSERVER_SCRIPT = BASE_DIR / "runtime" / "observer-daemon.py"
PID_FILE = BASE_DIR / "pids" / "observer-daemon.pid"

# Create MCP server
app = Server("novahiz-monitoring")


@app.list_tools()
async def list_tools():
    """List available monitoring tools."""
    return [
        Tool(
            name="nv_monitor_start",
            description="Start the Novahiz monitoring daemon",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="nv_monitor_stop",
            description="Stop the Novahiz monitoring daemon",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="nv_monitor_status",
            description="Get the status of the monitoring daemon",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="nv_get_errors",
            description="Get detected errors from the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20, "description": "Maximum number of errors to return"},
                    "severity": {"type": "string", "description": "Filter by severity (critical, high, medium, low)"},
                    "unresolved_only": {"type": "boolean", "default": True, "description": "Only return unresolved errors"}
                },
                "required": []
            }
        ),
        Tool(
            name="nv_get_agent_metrics",
            description="Get metrics for agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Specific agent ID"},
                    "limit": {"type": "integer", "default": 10, "description": "Number of records to return"}
                },
                "required": []
            }
        ),
        Tool(
            name="nv_trigger_autocorrect",
            description="Trigger auto-correction for detected issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "detection_id": {"type": "string", "description": "Specific detection to correct"},
                    "auto_approve": {"type": "boolean", "default": False, "description": "Auto-approve corrections"}
                },
                "required": []
            }
        ),
        Tool(
            name="nv_get_alerts",
            description="Get active alerts",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20, "description": "Maximum alerts to return"},
                    "severity": {"type": "string", "description": "Filter by severity"}
                },
                "required": []
            }
        ),
        Tool(
            name="nv_acknowledge_alert",
            description="Acknowledge an alert",
            inputSchema={
                "type": "object",
                "properties": {
                    "alert_id": {"type": "string", "description": "ID of the alert to acknowledge"}
                },
                "required": ["alert_id"]
            }
        ),
        Tool(
            name="nv_get_system_health",
            description="Get overall system health status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="nv_get_recent_corrections",
            description="Get recent auto-corrections",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20, "description": "Number of corrections to return"}
                },
                "required": []
            }
        ),
        Tool(
            name="nv_run_detections",
            description="Run error detection patterns",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="nv_get_stats",
            description="Get database statistics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    try:
        # Ensure database is initialized
        if not os.path.exists(BASE_DIR / "data" / "novahiz_state.db"):
            init_db()

        db = get_db()

        if name == "nv_monitor_start":
            return await monitor_start()

        elif name == "nv_monitor_stop":
            return await monitor_stop()

        elif name == "nv_monitor_status":
            return await monitor_status()

        elif name == "nv_get_errors":
            return await get_errors(db, arguments)

        elif name == "nv_get_agent_metrics":
            return await get_agent_metrics(db, arguments)

        elif name == "nv_trigger_autocorrect":
            return await trigger_autocorrect(db, arguments)

        elif name == "nv_get_alerts":
            return await get_alerts(db, arguments)

        elif name == "nv_acknowledge_alert":
            return await acknowledge_alert(db, arguments)

        elif name == "nv_get_system_health":
            return await get_system_health(db)

        elif name == "nv_get_recent_corrections":
            return await get_recent_corrections(db, arguments)

        elif name == "nv_run_detections":
            return await run_detections()

        elif name == "nv_get_stats":
            return await get_stats(db)

        else:
            return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


async def monitor_start():
    """Start monitoring daemon."""
    # Check if already running
    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGCONT)
            return [TextContent(
                type="text",
                text=json.dumps({"success": True, "message": "Monitoring daemon already running", "pid": pid}, indent=2)
            )]
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
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": "Monitoring daemon started",
                "pid": process.pid
            }, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def monitor_stop():
    """Stop monitoring daemon."""
    if not PID_FILE.exists():
        return [TextContent(
            type="text",
            text=json.dumps({"success": True, "message": "Monitoring daemon not running"}, indent=2)
        )]

    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink()
        return [TextContent(
            type="text",
            text=json.dumps({"success": True, "message": f"Monitoring daemon stopped (PID: {pid})"}, indent=2)
        )]
    except ProcessLookupError:
        PID_FILE.unlink()
        return [TextContent(
            type="text",
            text=json.dumps({"success": True, "message": "Daemon was not running, cleaned up PID file"}, indent=2)
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": str(e)}, indent=2)
        )]


async def monitor_status():
    """Get monitoring daemon status."""
    import psutil

    status = {
        "running": False,
        "pid": None,
        "uptime": None,
        "memory_mb": None,
        "cpu_percent": None
    }

    if PID_FILE.exists():
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            proc = psutil.Process(pid)
            if 'observer' in ' '.join(proc.cmdline()).lower():
                status.update({
                    "running": True,
                    "pid": pid,
                    "uptime": str(datetime.now() - datetime.fromtimestamp(proc.create_time())),
                    "memory_mb": round(proc.memory_info().rss / 1024 / 1024, 2),
                    "cpu_percent": proc.cpu_percent()
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
            pass

    return [TextContent(
        type="text",
        text=json.dumps(status, indent=2)
    )]


async def get_errors(db, args: dict):
    """Get errors from database."""
    limit = args.get('limit', 20)
    severity = args.get('severity')
    unresolved_only = args.get('unresolved_only', True)

    errors = db.get_unresolved_errors(limit) if unresolved_only else db.run_query(
        "SELECT * FROM errors ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )

    # Filter by severity if specified
    if severity:
        errors = [e for e in errors if e.get('severity') == severity]

    return [TextContent(
        type="text",
        text=json.dumps({
            "count": len(errors),
            "errors": errors
        }, indent=2, default=str)
    )]


async def get_agent_metrics(db, args: dict):
    """Get agent metrics."""
    agent_id = args.get('agent_id')
    limit = args.get('limit', 10)

    metrics = db.get_agent_metrics(agent_id, limit)

    return [TextContent(
        type="text",
        text=json.dumps({
            "count": len(metrics),
            "metrics": metrics
        }, indent=2, default=str)
    )]


async def trigger_autocorrect(db, args: dict):
    """Trigger auto-correction."""
    # Import auto-correct engine
    from engine.correction.auto_correct import AutoCorrectEngine

    engine = AutoCorrectEngine(db)
    detections = engine.get_detections()

    if not detections:
        return [TextContent(
            type="text",
            text=json.dumps({"success": True, "message": "No issues detected requiring correction"}, indent=2)
        )]

    corrections_applied = []
    for detection in detections:
        result = engine.apply_correction(detection, auto_approve=args.get('auto_approve', False))
        if result.get('applied'):
            corrections_applied.append(result)

    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "detections_count": len(detections),
            "corrections_applied": len(corrections_applied),
            "corrections": corrections_applied
        }, indent=2, default=str)
    )]


async def get_alerts(db, args: dict):
    """Get active alerts."""
    alerts = db.get_active_alerts()

    # Filter by severity if specified
    severity = args.get('severity')
    if severity:
        alerts = [a for a in alerts if a.get('severity') == severity]

    limit = args.get('limit', 20)
    alerts = alerts[:limit]

    return [TextContent(
        type="text",
        text=json.dumps({
            "count": len(alerts),
            "alerts": alerts
        }, indent=2, default=str)
    )]


async def acknowledge_alert(db, args: dict):
    """Acknowledge an alert."""
    alert_id = args.get('alert_id')
    if not alert_id:
        return [TextContent(
            type="text",
            text=json.dumps({"success": False, "error": "alert_id required"}, indent=2)
        )]

    db.acknowledge_alert(alert_id)
    return [TextContent(
        type="text",
        text=json.dumps({"success": True, "message": f"Alert {alert_id} acknowledged"}, indent=2)
    )]


async def get_system_health(db):
    """Get system health."""
    import psutil

    # Get system state
    monitoring = db.get_system_state('monitoring_enabled')
    health_check = db.get_system_state('last_health_check')
    autocorrect = db.get_system_state('autocorrect_enabled')

    # Get current system metrics
    health = {
        "monitoring": monitoring,
        "autocorrect": autocorrect,
        "last_health_check": health_check,
        "system": {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage(str(BASE_DIR)).percent
        },
        "stats": db.get_stats()
    }

    return [TextContent(
        type="text",
        text=json.dumps(health, indent=2, default=str)
    )]


async def get_recent_corrections(db, args: dict):
    """Get recent auto-corrections."""
    limit = args.get('limit', 20)
    corrections = db.get_recent_corrections(limit)

    return [TextContent(
        type="text",
        text=json.dumps({
            "count": len(corrections),
            "corrections": corrections
        }, indent=2, default=str)
    )]


async def run_detections():
    """Run error detections."""
    detector = ErrorDetector()
    detections = detector.detect_all()

    return [TextContent(
        type="text",
        text=json.dumps({
            "count": len(detections),
            "detections": detections
        }, indent=2, default=str)
    )]


async def get_stats(db):
    """Get database statistics."""
    stats = db.get_stats()
    return [TextContent(
        type="text",
        text=json.dumps(stats, indent=2)
    )]


async def main():
    """Run the MCP server."""
    # Initialize database if needed
    if not os.path.exists(BASE_DIR / "data" / "novahiz_state.db"):
        init_db()

    print("🔍 Starting Novahiz Monitoring MCP Server...")
    print(f"   Database: {BASE_DIR / 'data' / 'novahiz_state.db'}")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
