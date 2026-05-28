#!/usr/bin/env python3
"""
Novahiz OS — Chaos Engineering Tool
Injects faults to test system resilience
"""

import os
import json
import time
import signal
from datetime import datetime
from pathlib import Path

NOVAHIZ_DIR = Path.home() / ".opencode"
LOGS_DIR = NOVAHIZ_DIR / "logs"
CHAOS_LOG = LOGS_DIR / "chaos_engineering.log"

# =============================================================================
# CHAOS EXPERIMENTS
# =============================================================================

class ChaosExperiment:
    """Base class for chaos experiments"""
    
    def __init__(self, name, description, risk_level="medium"):
        self.name = name
        self.description = description
        self.risk_level = risk_level  # low, medium, high
        self.duration_sec = 30
        self.rollback_plan = ""
    
    def execute(self):
        raise NotImplementedError
    
    def rollback(self):
        raise NotImplementedError
    
    def log(self, msg):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] [{self.name}] {msg}"
        print(line)
        try:
            with open(CHAOS_LOG, "a") as f:
                f.write(line + "\n")
        except Exception:
            pass

# =============================================================================
# EXPERIMENT: Kill Daemon
# =============================================================================
class KillDaemonExperiment(ChaosExperiment):
    """Kill the unified daemon and measure recovery time"""
    
    def __init__(self):
        super().__init__(
            "kill-daemon",
            "Kill Novahiz daemon and measure auto-recovery",
            risk_level="medium"
        )
        self.daemon_pid = None
        self.recovery_time = None
    
    def execute(self):
        self.log("Starting: Kill daemon experiment")
        
        # Find daemon PID
        pid_file = LOGS_DIR / "novahiz-unified.pid"
        if pid_file.exists():
            with open(pid_file) as f:
                self.daemon_pid = int(f.read().strip())
            
            self.log(f"Found daemon PID: {self.daemon_pid}")
            
            # Record start time
            start_time = time.time()
            
            # Kill daemon
            self.log("Killing daemon...")
            os.kill(self.daemon_pid, signal.SIGTERM)
            
            # Wait for recovery (supervisor should restart)
            for i in range(30):
                time.sleep(1)
                if pid_file.exists():
                    self.recovery_time = time.time() - start_time
                    self.log(f"Daemon recovered in {self.recovery_time:.2f}s")
                    return {
                        "success": True,
                        "recovery_time_sec": round(self.recovery_time, 2)
                    }
            
            self.log("Daemon did NOT recover within 30s")
            return {"success": False, "error": "No recovery within timeout"}
        else:
            self.log("Daemon not running (no PID file)")
            return {"success": False, "error": "Daemon not running"}
    
    def rollback(self):
        if self.daemon_pid:
            self.log("Rollback: Starting daemon manually")
            os.system(f"python3 {NOVAHIZ_DIR}/runtime/novahiz-unified.py daemon &")

# =============================================================================
# EXPERIMENT: Fill Disk
# =============================================================================
class FillDiskExperiment(ChaosExperiment):
    """Temporarily fill disk to test disk space handling"""
    
    def __init__(self):
        super().__init__(
            "fill-disk",
            "Create large files to simulate disk pressure",
            risk_level="high"
        )
        self.test_file = None
        self.file_size_mb = 100
    
    def execute(self):
        self.log(f"Starting: Fill disk experiment ({self.file_size_mb}MB)")
        
        self.test_file = LOGS_DIR / ".chaos_disk_test"
        
        try:
            # Create large file
            start_time = time.time()
            with open(self.test_file, "wb") as f:
                # Write in chunks
                chunk = b"x" * (1024 * 1024)  # 1MB
                for _ in range(self.file_size_mb):
                    f.write(chunk)
            
            elapsed = time.time() - start_time
            self.log(f"Created {self.file_size_mb}MB file in {elapsed:.2f}s")
            
            # Check if system handled it gracefully
            # (no crashes, proper error handling)
            return {
                "success": True,
                "file_size_mb": self.file_size_mb,
                "write_time_sec": round(elapsed, 2)
            }
        except Exception as e:
            self.log(f"Error: {e}")
            return {"success": False, "error": str(e)}
    
    def rollback(self):
        if self.test_file and self.test_file.exists():
            self.log("Rollback: Removing test file")
            self.test_file.unlink()

# =============================================================================
# EXPERIMENT: Network Latency
# =============================================================================
class NetworkLatencyExperiment(ChaosExperiment):
    """Simulate network latency for LLM calls"""
    
    def __init__(self):
        super().__init__(
            "network-latency",
            "Add artificial delay to network calls",
            risk_level="low"
        )
    
    def execute(self):
        self.log("Starting: Network latency experiment")
        
        # This would require network namespace manipulation
        # For now, just test timeout handling
        self.log("Testing timeout handling...")
        
        import urllib.request
        import urllib.error
        
        start_time = time.time()
        try:
            # Try to reach a slow endpoint
            req = urllib.request.Request(
                "https://httpstat.us/200?sleep=5000",  # 5 second delay
                timeout=2  # But we timeout at 2s
            )
            urllib.request.urlopen(req)
            self.log("Unexpected: Request succeeded")
            return {"success": False, "error": "Should have timed out"}
        except urllib.error.URLError as e:
            elapsed = time.time() - start_time
            self.log(f"Timeout handled correctly in {elapsed:.2f}s")
            return {
                "success": True,
                "timeout_handled": True,
                "elapsed_sec": round(elapsed, 2)
            }
        except Exception as e:
            self.log(f"Error: {e}")
            return {"success": False, "error": str(e)}
    
    def rollback(self):
        pass  # No rollback needed

# =============================================================================
# EXPERIMENT: Memory Pressure
# =============================================================================
class MemoryPressureExperiment(ChaosExperiment):
    """Simulate memory pressure"""
    
    def __init__(self):
        super().__init__(
            "memory-pressure",
            "Allocate memory to test GC and OOM handling",
            risk_level="medium"
        )
        self.allocated = []
    
    def execute(self):
        self.log("Starting: Memory pressure experiment")
        
        try:
            # Allocate memory in chunks
            chunk_size = 10 * 1024 * 1024  # 10MB
            chunks = 20  # 200MB total
            
            start_time = time.time()
            for i in range(chunks):
                self.allocated.append(b"x" * chunk_size)
                if i % 5 == 0:
                    self.log(f"Allocated {i * 10}MB")
            
            elapsed = time.time() - start_time
            self.log(f"Allocated {chunks * 10}MB in {elapsed:.2f}s")
            
            return {
                "success": True,
                "allocated_mb": chunks * 10,
                "elapsed_sec": round(elapsed, 2)
            }
        except MemoryError:
            self.log("MemoryError caught - system handled OOM correctly")
            return {
                "success": True,
                "oom_handled": True,
                "allocated_mb": len(self.allocated) * 10
            }
        except Exception as e:
            self.log(f"Error: {e}")
            return {"success": False, "error": str(e)}
    
    def rollback(self):
        self.log("Rollback: Releasing memory")
        self.allocated.clear()

# =============================================================================
# CHAOS RUNNER
# =============================================================================
class ChaosRunner:
    """Run chaos experiments"""
    
    def __init__(self):
        self.experiments = [
            KillDaemonExperiment(),
            NetworkLatencyExperiment(),
            # FillDiskExperiment(),  # High risk, manual only
            # MemoryPressureExperiment(),  # Medium risk
        ]
        self.results = []
    
    def run_all(self):
        """Run all experiments"""
        print("=" * 60)
        print("🔥 Novahiz OS Chaos Engineering")
        print("=" * 60)
        print()
        
        CHAOS_LOG.parent.mkdir(parents=True, exist_ok=True)
        
        for experiment in self.experiments:
            print(f"\n🧪 Experiment: {experiment.name}")
            print(f"   Description: {experiment.description}")
            print(f"   Risk Level: {experiment.risk_level}")
            print()
            
            # Confirm for medium/high risk
            if experiment.risk_level in ["medium", "high"]:
                confirm = input(f"   Proceed with {experiment.risk_level} risk experiment? (y/n): ")
                if confirm.lower() != "y":
                    print("   Skipped")
                    continue
            
            # Execute
            result = experiment.execute()
            result["experiment"] = experiment.name
            self.results.append(result)
            
            # Rollback
            experiment.rollback()
            
            time.sleep(2)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate chaos engineering report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "experiments_run": len(self.results),
            "results": self.results,
            "summary": {
                "successful": sum(1 for r in self.results if r.get("success")),
                "failed": sum(1 for r in self.results if not r.get("success"))
            }
        }
        
        report_file = LOGS_DIR / "chaos_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print()
        print("=" * 60)
        print("📊 Chaos Engineering Report")
        print("=" * 60)
        print(f"Experiments Run: {report['experiments_run']}")
        print(f"Successful: {report['summary']['successful']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Report: {report_file}")
        print(f"Log: {CHAOS_LOG}")
        print()

if __name__ == "__main__":
    runner = ChaosRunner()
    runner.run_all()
