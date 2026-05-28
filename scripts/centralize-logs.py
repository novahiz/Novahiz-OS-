#!/usr/bin/env python3
"""
Novahiz OS - Log Centralization Script
Converts logs to structured JSON and prepares for Loki/ELK ingestion
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime

LOGS_DIR = Path("logs")
OUTPUT_DIR = Path("logs/structured")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Log patterns to parse
LOG_PATTERNS = [
    # Novahiz runtime format: [2026-05-27 12:18:43] [INFO] Message
    r'\[(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(?P<level>\w+)\] (?P<message>.+)',
    # Generic format: 2026-05-27T12:18:43 - INFO - Message
    r'(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}) - (?P<level>\w+) - (?P<message>.+)',
]


def parse_log_line(line):
    """Parse a log line into structured format"""
    line = line.strip()
    if not line:
        return None
    
    for pattern in LOG_PATTERNS:
        match = re.match(pattern, line)
        if match:
            return {
                "timestamp": match.group("timestamp"),
                "level": match.group("level").upper(),
                "message": match.group("message"),
                "raw": line
            }
    
    # Fallback: unstructured log
    return {
        "timestamp": datetime.now().isoformat(),
        "level": "INFO",
        "message": line,
        "raw": line,
        "unstructured": True
    }


def process_log_file(log_file):
    """Process a single log file"""
    print(f"Processing: {log_file}")
    
    structured_logs = []
    error_count = 0
    warning_count = 0
    
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                parsed = parse_log_line(line)
                if parsed:
                    parsed["source"] = str(log_file)
                    parsed["line"] = line_num
                    
                    if parsed["level"] == "ERROR":
                        error_count += 1
                    elif parsed["level"] == "WARNING":
                        warning_count += 1
                    
                    structured_logs.append(parsed)
    except Exception as e:
        print(f"  Error reading {log_file}: {e}")
        return None
    
    # Save structured output
    output_file = OUTPUT_DIR / f"{log_file.stem}_structured.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(structured_logs, f, indent=2)
    
    # Save as newline-delimited JSON for Loki
    loki_file = OUTPUT_DIR / f"{log_file.stem}_loki.jsonl"
    with open(loki_file, "w", encoding="utf-8") as f:
        for log in structured_logs:
            f.write(json.dumps(log) + "\n")
    
    return {
        "file": str(log_file),
        "total": len(structured_logs),
        "errors": error_count,
        "warnings": warning_count,
        "output": str(output_file)
    }


def main():
    print("=" * 60)
    print("📝 Novahiz OS Log Centralization")
    print("=" * 60)
    print()
    
    if not LOGS_DIR.exists():
        print(f"❌ Logs directory not found: {LOGS_DIR}")
        sys.exit(1)
    
    # Find all log files
    log_files = list(LOGS_DIR.glob("*.log"))
    
    if not log_files:
        print("No log files found")
        sys.exit(0)
    
    print(f"Found {len(log_files)} log file(s)")
    print()
    
    # Process each file
    results = []
    for log_file in log_files:
        result = process_log_file(log_file)
        if result:
            results.append(result)
    
    # Summary
    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    total_logs = 0
    total_errors = 0
    total_warnings = 0
    
    for r in results:
        print(f"{r['file']}: {r['total']} logs ({r['errors']} errors, {r['warnings']} warnings)")
        total_logs += r["total"]
        total_errors += r["errors"]
        total_warnings += r["warnings"]
    
    print()
    print(f"Total: {total_logs} log entries")
    print(f"Errors: {total_errors}")
    print(f"Warnings: {total_warnings}")
    print()
    print(f"Structured logs saved to: {OUTPUT_DIR}")
    print()
    
    # Generate Loki config template
    generate_loki_config()
    
    if total_errors > 0:
        print("⚠️  Errors detected - review logs/structured/")
        return 1
    return 0


def generate_loki_config():
    """Generate Promtail config template"""
    config = """# Promtail Configuration for Novahiz OS
# Copy to /etc/promtail/config.yml

server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  - job_name: novahiz-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: novahiz
          __path__: /home/novahiz/.opencode/logs/*.log
    
    pipeline_stages:
      - regex:
          expression: '^\\[(?P<timestamp>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2})\\] \\[(?P<level>\\w+)\\] (?P<message>.+)'
      - labels:
          - level
      - timestamp:
          source: timestamp
          format: '2006-01-02 15:04:05'
"""
    
    config_file = OUTPUT_DIR / "promtail-config.yml"
    with open(config_file, "w") as f:
        f.write(config)
    print(f"✅ Promtail config: {config_file}")


if __name__ == "__main__":
    sys.exit(main())
