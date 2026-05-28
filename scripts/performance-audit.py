#!/usr/bin/env python3
"""
Novahiz OS — Performance Audit Tool
Comprehensive performance analysis: memory, CPU, latency, bottlenecks
"""

import os
import sys
import json
import time
import subprocess
import resource
import threading
from datetime import datetime
from pathlib import Path
from collections import defaultdict

NOVAHIZ_DIR = Path.home() / ".opencode"
OUTPUT_DIR = NOVAHIZ_DIR / "docs" / "performance"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# MEMORY ANALYSIS
# =============================================================================
def analyze_memory():
    """Analyze memory usage"""
    print("🧠 Memory Analysis")
    print("-" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "process_memory": {},
        "recommendations": []
    }
    
    # Current process memory
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        results["process_memory"] = {
            "max_rss_kb": usage.ru_maxrss,
            "max_rss_mb": round(usage.ru_maxrss / 1024, 2),
            "shared_kb": usage.ru_ixrss,
            "data_kb": usage.ru_idrss + usage.ru_isrss,
            "stack_kb": usage.ru_maxrss
        }
        
        print(f"  Max RSS: {results['process_memory']['max_rss_mb']} MB")
        print(f"  Shared: {results['process_memory']['shared_kb']} KB")
        
        # Check for potential leaks
        if results['process_memory']['max_rss_mb'] > 500:
            results["recommendations"].append({
                "severity": "high",
                "issue": "High memory usage (>500MB)",
                "action": "Profile with heaptrack, check for memory leaks"
            })
    except Exception as e:
        print(f"  Error: {e}")
    
    # System memory (if available)
    try:
        with open("/proc/meminfo") as f:
            meminfo = {}
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().split()[0]
                    meminfo[key] = int(value)
            
            total_mb = meminfo.get("MemTotal", 0) / 1024
            available_mb = meminfo.get("MemAvailable", 0) / 1024
            used_percent = ((total_mb - available_mb) / total_mb) * 100
            
            results["system_memory"] = {
                "total_mb": round(total_mb, 2),
                "available_mb": round(available_mb, 2),
                "used_percent": round(used_percent, 2)
            }
            
            print(f"  System: {results['system_memory']['used_percent']}% used")
            
    except Exception:
        pass
    
    print()
    return results

# =============================================================================
# CPU ANALYSIS
# =============================================================================
def analyze_cpu():
    """Analyze CPU usage patterns"""
    print("⚡ CPU Analysis")
    print("-" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "cpu_count": os.cpu_count() or 1,
        "load_average": {},
        "recommendations": []
    }
    
    # Load average
    try:
        load = os.getloadavg()
        results["load_average"] = {
            "1min": round(load[0], 2),
            "5min": round(load[1], 2),
            "15min": round(load[2], 2)
        }
        
        print(f"  Load Average: {load[0]:.2f} (1min), {load[1]:.2f} (5min), {load[2]:.2f} (15min)")
        
        # Check if overloaded
        if load[0] > results["cpu_count"] * 2:
            results["recommendations"].append({
                "severity": "critical",
                "issue": f"CPU overloaded (load {load[0]:.2f} > {results['cpu_count'] * 2})",
                "action": "Reduce concurrent tasks, optimize hot paths"
            })
    except Exception:
        pass
    
    # CPU time for current process
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        results["cpu_time"] = {
            "user_sec": usage.ru_utime,
            "system_sec": usage.ru_stime,
            "total_sec": round(usage.ru_utime + usage.ru_stime, 2)
        }
        print(f"  CPU Time: {results['cpu_time']['total_sec']}s (user: {usage.ru_utime:.2f}s, sys: {usage.ru_stime:.2f}s)")
    except Exception:
        pass
    
    print()
    return results

# =============================================================================
# LATENCY BENCHMARK
# =============================================================================
def benchmark_latency():
    """Benchmark common operations latency"""
    print("⏱️ Latency Benchmark")
    print("-" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "benchmarks": {},
        "recommendations": []
    }
    
    # File I/O latency
    try:
        test_file = OUTPUT_DIR / ".latency_test"
        iterations = 100
        
        start = time.perf_counter()
        for i in range(iterations):
            with open(test_file, "w") as f:
                f.write(f"test {i}")
            with open(test_file, "r") as f:
                f.read()
        elapsed = time.perf_counter() - start
        avg_latency = (elapsed / iterations) * 1000  # ms
        
        results["benchmarks"]["file_io"] = {
            "iterations": iterations,
            "avg_latency_ms": round(avg_latency, 3),
            "total_sec": round(elapsed, 3)
        }
        print(f"  File I/O: {avg_latency:.3f}ms avg ({iterations} iterations)")
        
        if avg_latency > 10:
            results["recommendations"].append({
                "severity": "medium",
                "issue": f"Slow file I/O ({avg_latency:.3f}ms)",
                "action": "Consider SSD, reduce sync writes, use buffering"
            })
        
        test_file.unlink()
    except Exception as e:
        print(f"  File I/O Error: {e}")
    
    # JSON serialization latency
    try:
        test_data = {"key": "value", "number": 42, "list": list(range(100))}
        iterations = 1000
        
        start = time.perf_counter()
        for _ in range(iterations):
            json.dumps(test_data)
            json.loads(json.dumps(test_data))
        elapsed = time.perf_counter() - start
        avg_latency = (elapsed / iterations) * 1000  # ms
        
        results["benchmarks"]["json_serialization"] = {
            "iterations": iterations,
            "avg_latency_ms": round(avg_latency, 3),
            "total_sec": round(elapsed, 3)
        }
        print(f"  JSON (de)serialization: {avg_latency:.3f}ms avg ({iterations} iterations)")
    except Exception as e:
        print(f"  JSON Error: {e}")
    
    # HTTP request latency (if OpenRouter configured)
    try:
        import urllib.request
        start = time.perf_counter()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1",
            headers={"HTTP-Referer": "https://novahiz.local"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            response.read()
        elapsed = time.perf_counter() - start
        
        results["benchmarks"]["http_request"] = {
            "endpoint": "openrouter.ai",
            "latency_ms": round(elapsed * 1000, 3)
        }
        print(f"  HTTP Request (OpenRouter): {elapsed * 1000:.3f}ms")
        
        if elapsed > 1:
            results["recommendations"].append({
                "severity": "medium",
                "issue": f"Slow HTTP response ({elapsed * 1000:.3f}ms)",
                "action": "Check network, consider caching, use connection pooling"
            })
    except Exception:
        print(f"  HTTP Request: Skipped (network unavailable)")
    
    print()
    return results

# =============================================================================
# DAEMON PERFORMANCE
# =============================================================================
def analyze_daemon_performance():
    """Analyze daemon execution performance"""
    print("🔄 Daemon Performance")
    print("-" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "execution_stats": {},
        "recommendations": []
    }
    
    # Read execution files
    exec_dir = NOVAHIZ_DIR / "executions"
    if exec_dir.exists():
        exec_files = list(exec_dir.glob("exec_*.json"))
        
        if exec_files:
            durations = []
            success_count = 0
            
            for exec_file in exec_files:
                try:
                    with open(exec_file) as f:
                        data = json.load(f)
                    
                    if data.get("started") and data.get("completed"):
                        start = datetime.fromisoformat(data["started"])
                        end = datetime.fromisoformat(data["completed"])
                        duration = (end - start).total_seconds()
                        durations.append(duration)
                    
                    if data.get("status") == "completed":
                        success_count += 1
                except Exception:
                    pass
            
            if durations:
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                min_duration = min(durations)
                
                results["execution_stats"] = {
                    "total_executions": len(exec_files),
                    "success_rate": round(success_count / len(exec_files) * 100, 2),
                    "avg_duration_sec": round(avg_duration, 2),
                    "min_duration_sec": round(min_duration, 2),
                    "max_duration_sec": round(max_duration, 2)
                }
                
                print(f"  Total Executions: {len(exec_files)}")
                print(f"  Success Rate: {results['execution_stats']['success_rate']}%")
                print(f"  Avg Duration: {avg_duration:.2f}s")
                print(f"  Min/Max: {min_duration:.2f}s / {max_duration:.2f}s")
                
                if avg_duration > 30:
                    results["recommendations"].append({
                        "severity": "high",
                        "issue": f"Slow execution avg ({avg_duration:.2f}s)",
                        "action": "Optimize LLM calls, use faster models, implement caching"
                    })
            else:
                print(f"  No execution data found")
        else:
            print(f"  No execution files found")
    else:
        print(f"  Executions directory not found")
    
    print()
    return results

# =============================================================================
# GENERATE REPORT
# =============================================================================
def generate_report():
    """Generate comprehensive performance report"""
    print("=" * 60)
    print("🚀 Novahiz OS Performance Audit")
    print("=" * 60)
    print()
    
    # Run all analyses
    memory = analyze_memory()
    cpu = analyze_cpu()
    latency = benchmark_latency()
    daemon = analyze_daemon_performance()
    
    # Compile report
    report = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "memory": memory,
        "cpu": cpu,
        "latency": latency,
        "daemon": daemon
    }
    
    # Collect all recommendations
    all_recommendations = []
    for section in [memory, cpu, latency, daemon]:
        all_recommendations.extend(section.get("recommendations", []))
    
    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_recommendations.sort(key=lambda x: severity_order.get(x["severity"], 4))
    
    report["recommendations"] = all_recommendations
    
    # Save JSON report
    json_file = OUTPUT_DIR / "audit_report.json"
    with open(json_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Save markdown summary
    md_file = OUTPUT_DIR / "AUDIT_REPORT.md"
    with open(md_file, "w") as f:
        f.write(f"# Novahiz OS Performance Audit Report\n\n")
        f.write(f"**Generated:** {report['generated']}\n\n")
        
        f.write(f"## Summary\n\n")
        f.write(f"- Memory: {memory['process_memory'].get('max_rss_mb', 'N/A')} MB\n")
        f.write(f"- CPU Count: {cpu['cpu_count']}\n")
        f.write(f"- Load Average: {cpu['load_average'].get('1min', 'N/A')}\n")
        f.write(f"- Total Recommendations: {len(all_recommendations)}\n\n")
        
        if all_recommendations:
            f.write(f"## Recommendations\n\n")
            for i, rec in enumerate(all_recommendations, 1):
                icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(rec["severity"], "⚪")
                f.write(f"### {i}. {icon} [{rec['severity'].upper()}] {rec['issue']}\n\n")
                f.write(f"**Action:** {rec['action']}\n\n")
        
        f.write(f"## Detailed Results\n\n")
        f.write(f"See `audit_report.json` for complete data.\n")
    
    print("=" * 60)
    print(f"✅ Audit complete!")
    print(f"   JSON: {json_file}")
    print(f"   Markdown: {md_file}")
    print(f"   Recommendations: {len(all_recommendations)}")
    print()
    
    if all_recommendations:
        print("🔴 Critical/High Priority:")
        for rec in all_recommendations:
            if rec["severity"] in ["critical", "high"]:
                print(f"   - {rec['issue']}")
    else:
        print("✅ No performance issues detected!")
    
    print()
    
    return report

if __name__ == "__main__":
    generate_report()
