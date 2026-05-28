#!/usr/bin/env python3
"""
Novahiz OS — TODO/FIXME Tracker
Extracts, categorizes, and creates GitHub issues for technical debt
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

NOVAHIZ_DIR = Path.home() / ".opencode"
OUTPUT_FILE = NOVAHIZ_DIR / "docs" / "TECHNICAL_DEBT.md"
ISSUES_FILE = NOVAHIZ_DIR / ".github" / "todo-issues.json"

# Patterns to match
PATTERNS = {
    "TODO": r"#?\s*TODO[:\s]+(.+)",
    "FIXME": r"#?\s*FIXME[:\s]+(.+)",
    "HACK": r"#?\s*HACK[:\s]+(.+)",
    "XXX": r"#?\s*XXX[:\s]+(.+)",
    "BUG": r"#?\s*BUG[:\s]+(.+)",
    "DEPRECATED": r"#?\s*DEPRECATED[:\s]+(.+)",
}

PRIORITY_KEYWORDS = {
    "critical": ["critical", "urgent", "security", "crash", "data loss"],
    "high": ["important", "blocking", "performance", "broken"],
    "medium": ["should", "could", "improve", "refactor"],
    "low": ["nice", "optional", "cosmetic", "typo"],
}

def is_false_positive(line, file_path):
    """Check if a TODO match is a false positive"""
    line_stripped = line.strip()
    
    # Skip if it's in a regex pattern definition
    if 'r"' in line or "r'" in line:
        return True
    
    # Skip if it's in a print statement (not an actual TODO)
    if 'print(' in line and 'TODO' in line.upper():
        return True
    
    # Skip if it's describing the pattern itself (meta)
    if 'PATTERNS' in line or 'regex' in line.lower():
        return True
    
    # Skip lines that are just defining the pattern
    if ':\\s]+' in line or '[:\\s]' in line:
        return True
    
    # Skip if it's in the track-todos.py itself and about the tracker
    if 'track-todos' in str(file_path) and ('extract' in line.lower() or 'pattern' in line.lower()):
        return True
    
    return False


def extract_todos():
    """Extract all TODOs from codebase"""
    print("🔍 Extracting TODOs/FIXMEs...")
    print("=" * 50)
    
    todos = []
    
    # Files/patterns to EXCLUDE (meta-files, generated docs)
    exclude_patterns = [
        "node_modules", ".git", "backups", "__pycache__",
        "track-todos.py",  # Don't track the tracker itself
        "TECHNICAL_DEBT.md",  # Don't track generated report
        "AUDIT_",  # Don't track audit reports
    ]
    
    # Scan Python, JS, TS, Shell files (NOT markdown docs)
    for pattern in ["**/*.py", "**/*.js", "**/*.ts", "**/*.sh"]:
        for file_path in NOVAHIZ_DIR.glob(pattern):
            # Skip excluded paths
            path_str = str(file_path)
            if any(skip in path_str for skip in exclude_patterns):
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for line_num, line in enumerate(f, 1):
                        # Skip if it's a regex pattern definition or print statement
                        if 'r"' in line or "r'" in line or 'print(' in line:
                            continue
                        
                        for tag, regex in PATTERNS.items():
                            match = re.search(regex, line, re.IGNORECASE)
                            if match:
                                # Skip false positives
                                if is_false_positive(line, file_path):
                                    continue
                                
                                description = match.group(1).strip()
                                priority = detect_priority(description)
                                
                                todos.append({
                                    "tag": tag,
                                    "file": str(file_path.relative_to(NOVAHIZ_DIR)),
                                    "line": line_num,
                                    "description": description,
                                    "priority": priority,
                                    "created": datetime.now().isoformat()
                                })
            except Exception:
                pass
    
    print(f"Found {len(todos)} TODO(s)/FIXME(s)")
    return todos

def detect_priority(description):
    """Detect priority from description keywords"""
    desc_lower = description.lower()
    
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return priority
    
    # Default by tag
    if "FIXME" in description.upper() or "BUG" in description.upper():
        return "high"
    elif "HACK" in description.upper() or "XXX" in description.upper():
        return "medium"
    
    return "low"

def generate_markdown_report(todos):
    """Generate markdown report"""
    report = f"""# Novahiz OS — Technical Debt Tracker

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**Total Items:** {len(todos)}

---

## Summary

| Priority | Count | Percentage |
|----------|-------|------------|
| 🔴 Critical | {sum(1 for t in todos if t['priority'] == 'critical')} | {sum(1 for t in todos if t['priority'] == 'critical') * 100 // max(len(todos), 1)}% |
| 🟠 High | {sum(1 for t in todos if t['priority'] == 'high')} | {sum(1 for t in todos if t['priority'] == 'high') * 100 // max(len(todos), 1)}% |
| 🟡 Medium | {sum(1 for t in todos if t['priority'] == 'medium')} | {sum(1 for t in todos if t['priority'] == 'medium') * 100 // max(len(todos), 1)}% |
| 🟢 Low | {sum(1 for t in todos if t['priority'] == 'low')} | {sum(1 for t in todos if t['priority'] == 'low') * 100 // max(len(todos), 1)}% |

---

## By Tag

| Tag | Count |
|-----|-------|
| TODO | {sum(1 for t in todos if t['tag'] == 'TODO')} |
| FIXME | {sum(1 for t in todos if t['tag'] == 'FIXME')} |
| HACK | {sum(1 for t in todos if t['tag'] == 'HACK')} |
| XXX | {sum(1 for t in todos if t['tag'] == 'XXX')} |
| BUG | {sum(1 for t in todos if t['tag'] == 'BUG')} |
| DEPRECATED | {sum(1 for t in todos if t['tag'] == 'DEPRECATED')} |

---

## Critical & High Priority Items

"""
    
    # Critical and High items
    critical_high = [t for t in todos if t["priority"] in ["critical", "high"]]
    
    if critical_high:
        for todo in sorted(critical_high, key=lambda x: x["priority"]):
            icon = "🔴" if todo["priority"] == "critical" else "🟠"
            report += f"### {icon} [{todo['tag']}] {todo['file']}:{todo['line']}\n\n"
            report += f"**Description:** {todo['description']}\n\n"
            report += f"**Action:** Create GitHub issue and assign\n\n"
            report += "---\n\n"
    else:
        report += "*No critical or high priority items!*\n\n"
    
    # All items table
    report += """## All Items

| Priority | Tag | File | Line | Description |
|----------|-----|------|------|-------------|
"""
    
    for todo in sorted(todos, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}[x["priority"]]):
        icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[todo["priority"]]
        desc = todo["description"][:50] + "..." if len(todo["description"]) > 50 else todo["description"]
        report += f"| {icon} | {todo['tag']} | {todo['file']} | {todo['line']} | {desc} |\n"
    
    report += f"""
---

## How to Use This Report

1. **Review** critical/high items first
2. **Create GitHub issues** for each item
3. **Assign** to appropriate milestone
4. **Track progress** in GitHub Projects
5. **Re-run** this script regularly

## Automation

```bash
# Generate report
python3 scripts/track-todos.py

# View report
cat docs/TECHNICAL_DEBT.md
```

---

*Last Updated: {datetime.now().strftime("%Y-%m-%d")}*
"""
    
    # Save report
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"✅ Report saved: {OUTPUT_FILE}")
    return report

def generate_github_issues(todos):
    """Generate GitHub issues JSON for bulk import"""
    issues = []
    
    for todo in todos:
        if todo["priority"] in ["critical", "high"]:
            issues.append({
                "title": f"[{todo['tag']}] {todo['description'][:60]}",
                "body": f"""
**File:** `{todo['file']}`  
**Line:** {todo['line']}  
**Priority:** {todo['priority']}

### Description

{todo['description']}

### Action Required

- [ ] Review and understand the issue
- [ ] Create fix/implementation plan
- [ ] Implement solution
- [ ] Add tests
- [ ] Update documentation

---

*Auto-generated by track-todos.py*
""",
                "labels": [
                    todo["tag"].lower(),
                    f"priority:{todo['priority']}",
                    "technical-debt"
                ],
                "assignees": [],
                "milestone": "Technical Debt"
            })
    
    if issues:
        ISSUES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(ISSUES_FILE, "w", encoding="utf-8") as f:
            json.dump({"issues": issues}, f, indent=2)
        print(f"✅ GitHub issues template: {ISSUES_FILE} ({len(issues)} issues)")

def main():
    print("📋 Novahiz OS TODO/FIXME Tracker")
    print("=" * 50)
    print()
    
    # Extract todos
    todos = extract_todos()
    
    if not todos:
        print("✅ No TODOs/FIXMEs found! Great job!")
        return 0
    
    print()
    
    # Generate report
    generate_markdown_report(todos)
    
    # Generate GitHub issues
    generate_github_issues(todos)
    
    print()
    print("=" * 50)
    print("📊 Summary:")
    print(f"   Critical: {sum(1 for t in todos if t['priority'] == 'critical')}")
    print(f"   High: {sum(1 for t in todos if t['priority'] == 'high')}")
    print(f"   Medium: {sum(1 for t in todos if t['priority'] == 'medium')}")
    print(f"   Low: {sum(1 for t in todos if t['priority'] == 'low')}")
    print()
    print("Next steps:")
    print("   1. Review docs/TECHNICAL_DEBT.md")
    print("   2. Create GitHub issues for critical/high items")
    print("   3. Assign to milestones")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
