#!/usr/bin/env python3
"""
Novahiz OS — Metrics Dashboard
Generates visual reports and analytics from usage data
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

NOVAHIZ_DIR = Path.home() / ".opencode"
MEMORY_DIR = NOVAHIZ_DIR / "memory"
DASHBOARD_DIR = NOVAHIZ_DIR / "docs" / "dashboard"
DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)


class MetricsDashboard:
    """Generate metrics dashboard from usage data"""
    
    def __init__(self):
        self.metrics_file = MEMORY_DIR / "00_Core" / "metrics.json"
        self.executions_dir = NOVAHIZ_DIR / "executions"
        self.data = {}
        self.executions = []
    
    def load_data(self):
        """Load metrics and execution history"""
        # Load metrics
        if self.metrics_file.exists():
            with open(self.metrics_file) as f:
                self.data = json.load(f)
        
        # Load executions
        if self.executions_dir.exists():
            for exec_file in sorted(self.executions_dir.glob("exec_*.json")):
                try:
                    with open(exec_file) as f:
                        exec_data = json.load(f)
                        if exec_data.get("completed"):
                            self.executions.append(exec_data)
                except Exception:
                    pass
        
        print(f"📊 Loaded {len(self.executions)} executions")
    
    def generate_summary(self):
        """Generate executive summary"""
        summary = {
            "generated": datetime.now().isoformat(),
            "overview": {},
            "model_usage": {},
            "budget": {},
            "trends": {}
        }
        
        # Overview
        total_executions = len(self.executions)
        successful = sum(1 for e in self.executions if e.get("status") == "completed")
        failed = sum(1 for e in self.executions if e.get("status") == "failed")
        
        summary["overview"] = {
            "total_executions": total_executions,
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / max(total_executions, 1) * 100, 2)
        }
        
        # Model usage
        model_counts = defaultdict(int)
        tier_counts = defaultdict(int)
        provider_counts = defaultdict(int)
        total_tokens = 0
        
        for exec_data in self.executions:
            result = exec_data.get("result", {})
            model = result.get("model", "unknown")
            tier = exec_data.get("model_tier", "unknown")
            provider = result.get("provider", "unknown")
            tokens = result.get("tokens_used", 0)
            
            model_counts[model] += 1
            tier_counts[tier] += 1
            provider_counts[provider] += 1
            total_tokens += tokens
        
        summary["model_usage"] = {
            "by_model": dict(model_counts),
            "by_tier": dict(tier_counts),
            "by_provider": dict(provider_counts),
            "total_tokens": total_tokens
        }
        
        # Budget
        budget = self.data.get("premiumBudget", {})
        summary["budget"] = {
            "daily_limit": budget.get("daily_limit", 3),
            "used_today": budget.get("used_today", 0),
            "total_used": budget.get("total_used", 0),
            "blocked_count": budget.get("blocked_count", 0)
        }
        
        # Trends (last 7 days)
        daily_counts = defaultdict(int)
        for exec_data in self.executions:
            completed = exec_data.get("completed", "")
            if completed:
                day = completed[:10]  # YYYY-MM-DD
                daily_counts[day] += 1
        
        summary["trends"] = {
            "daily_executions": dict(sorted(daily_counts.items())[-7:])
        }
        
        return summary
    
    def generate_markdown_report(self, summary):
        """Generate markdown dashboard"""
        report = f"""# Novahiz OS — Metrics Dashboard

**Generated:** {summary['generated']}

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| Total Executions | {summary['overview']['total_executions']} |
| Success Rate | {summary['overview']['success_rate']}% |
| Successful | {summary['overview']['successful']} |
| Failed | {summary['overview']['failed']} |
| Total Tokens | {summary['model_usage']['total_tokens']:,} |

---

## 🤖 Model Usage

### By Tier

| Tier | Count | Percentage |
|------|-------|------------|
"""
        
        for tier, count in sorted(summary['model_usage']['by_tier'].items(), key=lambda x: -x[1]):
            pct = count * 100 / max(len(self.executions), 1)
            report += f"| {tier.capitalize()} | {count} | {pct:.1f}% |\n"
        
        report += f"""
### By Provider

| Provider | Count |
|----------|-------|
"""
        
        for provider, count in sorted(summary['model_usage']['by_provider'].items(), key=lambda x: -x[1]):
            report += f"| {provider} | {count} |\n"
        
        report += f"""
### Top Models

| Model | Count |
|-------|-------|
"""
        
        top_models = sorted(summary['model_usage']['by_model'].items(), key=lambda x: -x[1])[:5]
        for model, count in top_models:
            model_short = model.split("/")[-1][:30]
            report += f"| {model_short} | {count} |\n"
        
        report += f"""
---

## 💰 Budget Status

| Metric | Value |
|--------|-------|
| Daily Limit | {summary['budget']['daily_limit']} |
| Used Today | {summary['budget']['used_today']} |
| Total Used (All Time) | {summary['budget']['total_used']} |
| Times Blocked | {summary['budget']['blocked_count']} |

---

## 📈 Trends (Last 7 Days)

| Date | Executions |
|------|------------|
"""
        
        for date, count in summary['trends']['daily_executions'].items():
            report += f"| {date} | {count} |\n"
        
        report += f"""
---

## 🎯 Recommendations

"""
        
        # Generate recommendations based on data
        recommendations = []
        
        if summary['overview']['success_rate'] < 95:
            recommendations.append("### ⚠️ Success Rate Below Target\n\nTarget: 95% | Current: {0}%\n\n**Action:** Review failed executions for common patterns\n".format(
                summary['overview']['success_rate']
            ))
        
        if summary['budget']['blocked_count'] > 0:
            recommendations.append("### 💰 Budget Limits Hit\n\nPremium budget blocked {0} times.\n\n**Action:** Consider increasing limit or optimizing tier selection\n".format(
                summary['budget']['blocked_count']
            ))
        
        # Check tier distribution
        tier_dist = summary['model_usage']['by_tier']
        premium_pct = tier_dist.get('premium', 0) * 100 / max(len(self.executions), 1)
        if premium_pct > 50:
            recommendations.append("### ⚠️ High Premium Usage\n\n{0:.1f}% of executions use premium tier.\n\n**Action:** Review if premium tier is necessary for all tasks\n".format(premium_pct))
        
        if not recommendations:
            recommendations.append("### ✅ All Systems Healthy\n\nNo critical issues detected. Keep monitoring!\n")
        
        report += "".join(recommendations)
        
        report += f"""
---

## 🔗 Quick Links

- [Performance Audit](./performance/AUDIT_REPORT.md)
- [Technical Debt](./TECHNICAL_DEBT.md)
- [API Documentation](./API.md)
- [Architecture](./ARCHITECTURE.md)

---

*Dashboard auto-generated by metrics-dashboard.py*
"""
        
        # Save report
        report_file = DASHBOARD_DIR / "DASHBOARD.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"✅ Dashboard saved: {report_file}")
        return report_file
    
    def generate_json_export(self, summary):
        """Generate JSON export for external tools"""
        export_file = DASHBOARD_DIR / "metrics_export.json"
        with open(export_file, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"✅ JSON export: {export_file}")
    
    def run(self):
        """Generate complete dashboard"""
        print("=" * 60)
        print("📊 Novahiz OS Metrics Dashboard Generator")
        print("=" * 60)
        print()
        
        self.load_data()
        
        if not self.executions:
            print("⚠️  No execution data found")
            print("   Run some tasks first, then regenerate dashboard")
            return
        
        summary = self.generate_summary()
        self.generate_markdown_report(summary)
        self.generate_json_export(summary)
        
        print()
        print("=" * 60)
        print("✅ Dashboard generation complete!")
        print()
        print("View dashboard:")
        print(f"  cat {DASHBOARD_DIR}/DASHBOARD.md")
        print()


if __name__ == "__main__":
    dashboard = MetricsDashboard()
    dashboard.run()
