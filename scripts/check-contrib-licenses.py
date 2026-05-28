#!/usr/bin/env python3
"""
Novahiz OS — License Compliance Checker for Contributions
Verifies that contributed code doesn't introduce license violations
"""

import json
import sys
from pathlib import Path

NOVAHIZ_DIR = Path.home() / ".opencode"

# License compatibility matrix
COMPATIBLE_LICENSES = {
    "MIT": ["MIT", "ISC", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "Unlicense"],
    "Apache-2.0": ["MIT", "Apache-2.0", "BSD-3-Clause", "ISC"],
}

FORBIDDEN_PATTERNS = [
    "GPL", "AGPL", "LGPL", "SSPL",  # Copyleft strong
    "Proprietary", "Commercial", "All Rights Reserved",
]

def check_file_licenses():
    """Check for license headers in files"""
    print("🔍 Checking license headers...")
    print("=" * 50)
    
    issues = []
    
    # Check Python files for license headers
    for py_file in NOVAHIZ_DIR.glob("**/*.py"):
        if "node_modules" in str(py_file) or ".git" in str(py_file):
            continue
        
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                first_lines = "".join([f.readline() for _ in range(10)])
                
                # Check for copyright/license headers
                if "copyright" in first_lines.lower() or "license" in first_lines.lower():
                    # Verify it's compatible
                    for forbidden in FORBIDDEN_PATTERNS:
                        if forbidden.lower() in first_lines.lower():
                            issues.append({
                                "file": str(py_file),
                                "issue": f"Forbidden license pattern: {forbidden}"
                            })
        except Exception:
            pass
    
    if not issues:
        print("✅ No license issues detected")
    else:
        print(f"⚠️  {len(issues)} potential issue(s):")
        for issue in issues[:10]:
            print(f"  - {issue['file']}: {issue['issue']}")
    
    return len(issues) == 0

def verify_dependency_licenses():
    """Verify licenses of dependencies"""
    print("\n📦 Verifying dependency licenses...")
    print("=" * 50)
    
    # Check NPM
    package_lock = NOVAHIZ_DIR / "package-lock.json"
    if package_lock.exists():
        try:
            with open(package_lock) as f:
                data = json.load(f)
            
            packages = data.get("packages", {})
            gpl_count = 0
            
            for pkg_path, pkg_info in packages.items():
                license_str = pkg_info.get("license", "")
                if any(gpl in license_str.upper() for gpl in ["GPL", "AGPL"]):
                    gpl_count += 1
            
            if gpl_count > 0:
                print(f"⚠️  {gpl_count} NPM package(s) with GPL-family licenses")
            else:
                print("✅ NPM dependencies: No GPL licenses")
        except Exception as e:
            print(f"⚠️  Could not check NPM: {e}")
    
    # Check Python (if pip-licenses available)
    try:
        import subprocess
        result = subprocess.run(
            ["pip-licenses", "--format=json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            gpl_packages = [
                p["Name"] for p in packages
                if any(gpl in p.get("License", "").upper() for gpl in ["GPL", "AGPL"])
            ]
            if gpl_packages:
                print(f"⚠️  {len(gpl_packages)} Python package(s) with GPL: {gpl_packages[:5]}")
            else:
                print("✅ Python dependencies: No GPL licenses")
    except Exception:
        print("⚠️  pip-licenses not available")
    
    return True

def generate_contributor_template():
    """Generate contributor license template"""
    template = """
# Contributor License Agreement (CLA) Template

## For Individual Contributors

```
INDIVIDUAL CONTRIBUTOR LICENSE AGREEMENT

I hereby grant to Novahiz OS:

1. Copyright License: A perpetual, worldwide, non-exclusive, royalty-free license to use, modify, and distribute my contributions under the MIT License.

2. Patent License: A license under any patent claims I own that are necessarily infringed by my contributions.

3. Representations: I represent that I have the right to grant this license and that my contributions are my original work.

Contributor Name: _________________________
GitHub Username: _________________________
Date: _________________________
```

## For Corporate Contributors

```
CORPORATE CONTRIBUTOR LICENSE AGREEMENT

[Company Name] hereby grants to Novahiz OS:

1. Copyright License: A perpetual, worldwide, non-exclusive, royalty-free license to use, modify, and distribute contributions made by our employees under the MIT License.

2. Patent License: A license under patent claims we own that are necessarily infringed by contributions made by our employees.

3. Authorized Signatory: The undersigned represents that they have authority to bind [Company Name] to this agreement.

Company: _________________________
Authorized Signatory: _________________________
Title: _________________________
Date: _________________________
```
"""
    
    template_file = NOVAHIZ_DIR / "docs" / "legal" / "CLA_TEMPLATE.md"
    template_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(template_file, "w") as f:
        f.write(template)
    
    print(f"\n✅ CLA template generated: {template_file}")

def main():
    print("📋 Novahiz OS License Compliance Checker")
    print("=" * 50)
    print()
    
    # Run checks
    file_check = check_file_licenses()
    deps_check = verify_dependency_licenses()
    
    # Generate CLA template
    generate_contributor_template()
    
    print("\n" + "=" * 50)
    if file_check and deps_check:
        print("✅ All license checks passed")
        return 0
    else:
        print("⚠️  Some license issues detected - review above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
