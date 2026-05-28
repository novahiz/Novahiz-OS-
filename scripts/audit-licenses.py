#!/usr/bin/env python3
"""
Novahiz OS - SBOM & License Auditor
Generates Software Bill of Materials and checks license compliance
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("docs/compliance")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# License categories
ALLOWED_LICENSES = {
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC",
    "Unlicense", "CC0-1.0", "WTFPL", "0BSD", "MulanPSL-2.0"
}

WARNING_LICENSES = {
    "LGPL-2.1", "LGPL-3.0", "MPL-2.0", "EPL-1.0", "EPL-2.0",
    "CDDL-1.0", "CPL-1.0"
}

FORBIDDEN_LICENSES = {
    "GPL-2.0", "GPL-3.0", "AGPL-3.0", "SSPL-1.0", "CPAL-1.0",
    "EUPL-1.1", "RPL-1.5"
}


def audit_python_packages():
    """Audit Python packages using pip-licenses or manual parsing"""
    print("🐍 Auditing Python packages...")
    
    sbom = {
        "packages": [],
        "summary": {"allowed": 0, "warning": 0, "forbidden": 0, "unknown": 0}
    }
    
    try:
        # Try pip-licenses first
        result = subprocess.run(
            ["pip-licenses", "--format=json", "--with-license-text"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            for pkg in packages:
                license_name = pkg.get("License", "UNKNOWN")
                category = categorize_license(license_name)
                
                sbom["packages"].append({
                    "name": pkg.get("Name", "unknown"),
                    "version": pkg.get("Version", "0.0.0"),
                    "license": license_name,
                    "category": category
                })
                sbom["summary"][category] += 1
            return sbom
    except Exception as e:
        print(f"  pip-licenses failed: {e}")
    
    # Fallback: parse pip list
    try:
        result = subprocess.run(
            ["pip", "list", "--format=json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            for pkg in packages:
                sbom["packages"].append({
                    "name": pkg.get("name", "unknown"),
                    "version": pkg.get("version", "0.0.0"),
                    "license": "UNKNOWN",
                    "category": "unknown"
                })
                sbom["summary"]["unknown"] += 1
    except Exception as e:
        print(f"  pip list failed: {e}")
    
    return sbom


def audit_npm_packages():
    """Audit NPM packages"""
    print("📦 Auditing NPM packages...")
    
    sbom = {
        "packages": [],
        "summary": {"allowed": 0, "warning": 0, "forbidden": 0, "unknown": 0}
    }
    
    package_lock = Path("package-lock.json")
    if not package_lock.exists():
        print("  No package-lock.json found")
        return sbom
    
    try:
        with open(package_lock) as f:
            lock_data = json.load(f)
        
        packages = lock_data.get("packages", {})
        for pkg_path, pkg_info in packages.items():
            if pkg_path == "":
                continue  # Root package
            
            license_name = pkg_info.get("license", "UNKNOWN")
            category = categorize_license(license_name)
            
            # Extract package name from path (node_modules/@scope/name)
            name = pkg_path.replace("node_modules/", "")
            
            sbom["packages"].append({
                "name": name,
                "version": pkg_info.get("version", "0.0.0"),
                "license": license_name,
                "category": category
            })
            sbom["summary"][category] += 1
            
    except Exception as e:
        print(f"  NPM audit failed: {e}")
    
    return sbom


def categorize_license(license_str):
    """Categorize a license"""
    if not license_str or license_str == "UNKNOWN":
        return "unknown"
    
    license_upper = license_str.upper()
    
    for forbidden in FORBIDDEN_LICENSES:
        if forbidden.upper() in license_upper:
            return "forbidden"
    
    for warning in WARNING_LICENSES:
        if warning.upper() in license_upper:
            return "warning"
    
    for allowed in ALLOWED_LICENSES:
        if allowed.upper() in license_upper:
            return "allowed"
    
    return "unknown"


def generate_sbom():
    """Generate complete SBOM"""
    print("=" * 60)
    print("📋 Novahiz OS SBOM Generator")
    print("=" * 60)
    print()
    
    python_sbom = audit_python_packages()
    npm_sbom = audit_npm_packages()
    
    # Combine results
    combined = {
        "version": "1.0",
        "generated": datetime.now().isoformat(),
        "project": "Novahiz OS",
        "python": python_sbom,
        "npm": npm_sbom,
        "total_summary": {
            "allowed": python_sbom["summary"]["allowed"] + npm_sbom["summary"]["allowed"],
            "warning": python_sbom["summary"]["warning"] + npm_sbom["summary"]["warning"],
            "forbidden": python_sbom["summary"]["forbidden"] + npm_sbom["summary"]["forbidden"],
            "unknown": python_sbom["summary"]["unknown"] + npm_sbom["summary"]["unknown"]
        }
    }
    
    # Save SBOM
    sbom_file = OUTPUT_DIR / "sbom.json"
    with open(sbom_file, "w") as f:
        json.dump(combined, f, indent=2)
    print(f"\n✅ SBOM saved: {sbom_file}")
    
    # Generate license report
    report = generate_license_report(combined)
    report_file = OUTPUT_DIR / "licenses.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"✅ License report saved: {report_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Allowed:   {combined['total_summary']['allowed']}")
    print(f"Warning:   {combined['total_summary']['warning']}")
    print(f"Forbidden: {combined['total_summary']['forbidden']}")
    print(f"Unknown:   {combined['total_summary']['unknown']}")
    
    if combined['total_summary']['forbidden'] > 0:
        print("\n🚨 FORBIDDEN LICENSES DETECTED!")
        print("Action required: Remove or replace packages with GPL/AGPL licenses")
        return False
    elif combined['total_summary']['warning'] > 0:
        print("\n⚠️  WARNING LICENSES DETECTED")
        print("Review: LGPL/MPL may require source disclosure")
        return True
    else:
        print("\n✅ All licenses compliant!")
        return True


def generate_license_report(sbom):
    """Generate markdown license report"""
    report = """# Novahiz OS - License Compliance Report

**Generated:** {generated}

## Summary

| Category | Count |
|----------|-------|
| ✅ Allowed | {allowed} |
| ⚠️ Warning | {warning} |
| 🚨 Forbidden | {forbidden} |
| ❓ Unknown | {unknown} |

## Allowed Licenses

These licenses are approved for use in Novahiz OS:
- MIT
- Apache-2.0
- BSD-2-Clause, BSD-3-Clause
- ISC
- Unlicense, CC0-1.0

## Warning Licenses

These licenses require review (copyleft provisions):
- LGPL-2.1, LGPL-3.0
- MPL-2.0
- EPL-1.0, EPL-2.0

## Forbidden Licenses

These licenses are NOT allowed (strong copyleft):
- GPL-2.0, GPL-3.0
- AGPL-3.0
- SSPL-1.0

## Python Dependencies

| Package | Version | License | Status |
|---------|---------|---------|--------|
{python_rows}

## NPM Dependencies

| Package | Version | License | Status |
|---------|---------|---------|--------|
{npm_rows}

---

*Generated by Novahiz OS License Auditor*
"""
    
    # Build rows
    python_rows = ""
    for pkg in sbom["python"]["packages"][:50]:  # Limit to 50
        icon = {"allowed": "✅", "warning": "⚠️", "forbidden": "🚨", "unknown": "❓"}.get(pkg["category"], "❓")
        python_rows += f"| {pkg['name']} | {pkg['version']} | {pkg['license']} | {icon} |\n"
    
    npm_rows = ""
    for pkg in sbom["npm"]["packages"][:50]:  # Limit to 50
        icon = {"allowed": "✅", "warning": "⚠️", "forbidden": "🚨", "unknown": "❓"}.get(pkg["category"], "❓")
        npm_rows += f"| {pkg['name']} | {pkg['version']} | {pkg['license']} | {icon} |\n"
    
    return report.format(
        generated=sbom["generated"],
        allowed=sbom["total_summary"]["allowed"],
        warning=sbom["total_summary"]["warning"],
        forbidden=sbom["total_summary"]["forbidden"],
        unknown=sbom["total_summary"]["unknown"],
        python_rows=python_rows or "*No Python packages audited*",
        npm_rows=npm_rows or "*No NPM packages audited*"
    )


if __name__ == "__main__":
    success = generate_sbom()
    sys.exit(0 if success else 1)
