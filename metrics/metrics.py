#!/usr/bin/env python3
"""
Novahiz OS — Metrics Collector v5.4
Tracks usage statistics with time-based filtering
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

HOME = Path.home()
NOVAHIZ_DIR = HOME / ".opencode"
METRICS_DIR = NOVAHIZ_DIR / "metrics"
METRICS_FILE = METRICS_DIR / "usage.json"

METRICS_DIR.mkdir(exist_ok=True)

class MetricsCollector:
    def __init__(self):
        self.metrics = self._load()
    
    def _load(self):
        if METRICS_FILE.exists():
            try:
                return json.load(open(METRICS_FILE))
            except Exception:
                pass
        return {"version": "5.4.0", "started": datetime.now().isoformat(), "total_executions": 0, "successful_executions": 0, "failed_executions": 0, "total_tokens": 0, "total_cost_usd": 0.0, "by_agent": {}, "by_provider": {}, "by_model": {}, "by_tier": {}, "daily": {}, "hourly": {}, "errors": [], "last_updated": datetime.now().isoformat()}
    
    def record(self, result):
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        hour = now.strftime("%Y-%m-%d %H:00")
        self.metrics["total_executions"] += 1
        self.metrics["last_updated"] = now.isoformat()
        if result.get("success"):
            self.metrics["successful_executions"] += 1
        else:
            self.metrics["failed_executions"] += 1
        tokens = result.get("tokens_used", 0)
        self.metrics["total_tokens"] += tokens
        agent = result.get("agent", "unknown")
        self.metrics["by_agent"][agent] = self.metrics["by_agent"].get(agent, 0) + 1
        provider = result.get("provider", "unknown")
        self.metrics["by_provider"][provider] = self.metrics["by_provider"].get(provider, 0) + 1
        model = result.get("model", "unknown")
        self.metrics["by_model"][model] = self.metrics["by_model"].get(model, 0) + 1
        tier = result.get("model_tier", "unknown")
        self.metrics["by_tier"][tier] = self.metrics["by_tier"].get(tier, 0) + 1
        if today not in self.metrics["daily"]:
            self.metrics["daily"][today] = {"executions": 0, "tokens": 0, "successful": 0, "failed": 0}
        self.metrics["daily"][today]["executions"] += 1
        self.metrics["daily"][today]["tokens"] += tokens
        self.metrics["daily"][today]["successful"] += 1 if result.get("success") else 0
        self.metrics["daily"][today]["failed"] += 0 if result.get("success") else 1
        if hour not in self.metrics["hourly"]:
            self.metrics["hourly"][hour] = 0
        self.metrics["hourly"][hour] += 1
        if not result.get("success"):
            error = {"timestamp": now.isoformat(), "agent": agent, "error": result.get("error", "Unknown error")}
            self.metrics["errors"].append(error)
            self.metrics["errors"] = self.metrics["errors"][-100:]
        self.metrics["total_cost_usd"] = self.metrics["total_tokens"] * 0.0000001
        self._save()
    
    def _save(self):
        try:
            with open(METRICS_FILE, "w") as f:
                json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def get_stats(self, hours=24):
        """Get statistics for last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        cutoff_str = cutoff.strftime("%Y-%m-%d")
        
        # Filter daily stats for recent period
        recent_daily = {k: v for k, v in self.metrics["daily"].items() if k >= cutoff_str}
        
        # Calculate totals from recent
        recent_total = sum(d.get("executions", 0) for d in recent_daily.values())
        recent_success = sum(d.get("successful", 0) for d in recent_daily.values())
        recent_tokens = sum(d.get("tokens", 0) for d in recent_daily.values())
        
        total = max(1, self.metrics["total_executions"])
        recent_total = max(1, recent_total)
        
        return {
            "all_time": {
                "total_executions": self.metrics["total_executions"],
                "successful": self.metrics["successful_executions"],
                "failed": self.metrics["failed_executions"],
                "success_rate": f"{(self.metrics['successful_executions'] / total) * 100:.1f}%",
                "total_tokens": self.metrics["total_tokens"],
                "avg_tokens": self.metrics["total_tokens"] // total,
                "estimated_cost_usd": f"${self.metrics['total_cost_usd']:.4f}"
            },
            f"last_{hours}h": {
                "total_executions": recent_total,
                "successful": recent_success,
                "failed": recent_total - recent_success,
                "success_rate": f"{(recent_success / recent_total) * 100:.1f}%",
                "total_tokens": recent_tokens,
                "avg_tokens": recent_tokens // recent_total
            },
            "top_agents": sorted(self.metrics["by_agent"].items(), key=lambda x: x[1], reverse=True)[:5],
            "top_providers": sorted(self.metrics["by_provider"].items(), key=lambda x: x[1], reverse=True)[:3],
            "today": self.metrics["daily"].get(datetime.now().strftime("%Y-%m-%d"), {"executions": 0, "tokens": 0, "successful": 0})
        }
    
    def print_stats(self, hours=24):
        """Print formatted statistics"""
        stats = self.get_stats(hours)
        print("=" * 60)
        print("  NOVAHIZ OS — USAGE STATISTICS v5.4")
        print("=" * 60)
        print(f"\n📊 ALL TIME:")
        print(f"  Total Executions: {stats['all_time']['total_executions']}")
        print(f"  Successful: {stats['all_time']['successful']} ({stats['all_time']['success_rate']})")
        print(f"  Failed: {stats['all_time']['failed']}")
        print(f"  Total Tokens: {stats['all_time']['total_tokens']:,}")
        print(f"  Avg Tokens/Exec: {stats['all_time']['avg_tokens']:,}")
        print(f"  Est. Cost: {stats['all_time']['estimated_cost_usd']}")
        print(f"\n⏰ LAST {hours}H:")
        print(f"  Executions: {stats[f'last_{hours}h']['total_executions']}")
        print(f"  Successful: {stats[f'last_{hours}h']['successful']} ({stats[f'last_{hours}h']['success_rate']})")
        print(f"  Tokens: {stats[f'last_{hours}h']['total_tokens']:,}")
        print(f"\n🏆 TOP AGENTS:")
        for agent, count in stats['top_agents']:
            print(f"  - {agent}: {count}")
        print(f"\n🔌 TOP PROVIDERS:")
        for provider, count in stats['top_providers']:
            print(f"  - {provider}: {count}")
        print(f"\n📅 TODAY: {stats['today'].get('executions', 0)} executions, {stats['today'].get('successful', 0)} successful")
        print("=" * 60)

if __name__ == "__main__":
    import sys
    collector = MetricsCollector()
    hours = 24
    if len(sys.argv) > 1:
        if sys.argv[1] == "today":
            hours = 24
        elif sys.argv[1] == "week":
            hours = 168
        elif sys.argv[1].isdigit():
            hours = int(sys.argv[1])
    collector.print_stats(hours)
