#!/usr/bin/env python3
"""
Novahiz OS — RGPD Compliance Tools
Data export, deletion, and consent management
"""

import json
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path
import zipfile

HOME = Path.home()
NOVAHIZ_DIR = HOME / ".opencode"

# =============================================================================
# DATA EXPORT (Art. 15, 20 GDPR)
# =============================================================================
def export_data(output_dir: str = None):
    """Export all user data (Right to Access + Portability)"""
    if not output_dir:
        output_dir = NOVAHIZ_DIR / "data_export"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_file = output_dir / f"novahiz_data_export_{timestamp}.zip"
    
    print("📦 Novahiz OS Data Export")
    print("=" * 50)
    print(f"Export directory: {output_dir}")
    print()
    
    # Files to export
    export_paths = {
        "config": NOVAHIZ_DIR / "runtime" / "config.json",
        "metrics": NOVAHIZ_DIR / "memory" / "00_Core" / "metrics.json",
        "agents": NOVAHIZ_DIR / "memory" / "01_Agents",
        "projects": NOVAHIZ_DIR / "memory" / "02_Projects",
        "patterns": NOVAHIZ_DIR / "memory" / "03_Patterns",
        "constitution": NOVAHIZ_DIR / "memory" / "00_Core" / "constitution.md",
        "logs": NOVAHIZ_DIR / "logs",
        "compliance": NOVAHIZ_DIR / "docs" / "compliance",
    }
    
    # Create manifest
    manifest = {
        "export_date": datetime.now().isoformat(),
        "user": os.environ.get("USER", "unknown"),
        "version": "1.0",
        "files": []
    }
    
    # Copy files
    temp_dir = output_dir / "temp_export"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    for name, path in export_paths.items():
        if path.exists():
            if path.is_file():
                shutil.copy2(path, temp_dir / path.name)
                manifest["files"].append({
                    "name": name,
                    "type": "file",
                    "path": str(path),
                    "size": path.stat().st_size
                })
                print(f"  ✓ {name}: {path.name}")
            elif path.is_dir():
                dest = temp_dir / name
                shutil.copytree(path, dest, dirs_exist_ok=True)
                file_count = sum(1 for _ in path.rglob("*") if _is_file(_))
                manifest["files"].append({
                    "name": name,
                    "type": "directory",
                    "path": str(path),
                    "files": file_count
                })
                print(f"  ✓ {name}: {file_count} files")
    
    # Write manifest
    manifest_file = temp_dir / "export_manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Create ZIP
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in temp_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(temp_dir)
                zipf.write(file, arcname)
    
    # Cleanup temp
    shutil.rmtree(temp_dir)
    
    print()
    print("=" * 50)
    print(f"✅ Export complete: {zip_file}")
    print(f"   Size: {zip_file.stat().st_size / 1024:.1f} KB")
    print()
    print("📋 Your rights:")
    print("   - Review exported data")
    print("   - Request correction (Art. 16)")
    print("   - Request deletion (Art. 17)")
    print()
    
    return str(zip_file)

def _is_file(path):
    return path.is_file()

# =============================================================================
# DATA DELETION (Art. 17 GDPR - Right to Erasure)
# =============================================================================
def delete_data(selective: bool = False):
    """Delete user data (Right to Erasure / "Right to be Forgotten")"""
    print("🗑️  Novahiz OS Data Deletion")
    print("=" * 50)
    
    if selective:
        print("Selective deletion mode")
        print()
        print("Select what to delete:")
        print("  1. Usage metrics only")
        print("  2. Logs only")
        print("  3. Metrics + Logs")
        print("  4. Everything (full reset)")
        print()
        
        choice = input("Choice (1-4): ").strip()
        
        if choice == "1":
            delete_file(NOVAHIZ_DIR / "memory" / "00_Core" / "metrics.json")
        elif choice == "2":
            delete_dir(NOVAHIZ_DIR / "logs")
        elif choice == "3":
            delete_file(NOVAHIZ_DIR / "memory" / "00_Core" / "metrics.json")
            delete_dir(NOVAHIZ_DIR / "logs")
        elif choice == "4":
            confirm = input("⚠️  This will delete ALL data. Type 'DELETE' to confirm: ")
            if confirm == "DELETE":
                full_reset()
            else:
                print("Cancelled")
                return
    else:
        confirm = input("⚠️  Delete all personal data? Type 'DELETE' to confirm: ")
        if confirm == "DELETE":
            full_reset()
        else:
            print("Cancelled")
            return

def delete_file(path):
    """Delete a file"""
    try:
        if path.exists():
            path.unlink()
            print(f"  ✓ Deleted: {path}")
        else:
            print(f"  - Not found: {path}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

def delete_dir(path):
    """Delete a directory"""
    try:
        if path.exists():
            shutil.rmtree(path)
            print(f"  ✓ Deleted: {path}")
        else:
            print(f"  - Not found: {path}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

def full_reset():
    """Full system reset"""
    print("Performing full reset...")
    
    # Keep: config, memory structure, docs
    # Delete: logs, metrics, executions, backups
    
    delete_dir(NOVAHIZ_DIR / "logs")
    delete_dir(NOVAHIZ_DIR / "executions")
    delete_dir(NOVAHIZ_DIR / "backups")
    delete_file(NOVAHIZ_DIR / "memory" / "00_Core" / "metrics.json")
    
    # Recreate empty directories
    (NOVAHIZ_DIR / "logs").mkdir(parents=True, exist_ok=True)
    (NOVAHIZ_DIR / "executions").mkdir(parents=True, exist_ok=True)
    
    print()
    print("✅ Full reset complete")
    print("   - Logs deleted")
    print("   - Metrics deleted")
    print("   - Executions deleted")
    print("   - Config preserved")

# =============================================================================
# CONSENT MANAGEMENT (Art. 7 GDPR)
# =============================================================================
def manage_consent():
    """Manage user consent preferences"""
    consent_file = NOVAHIZ_DIR / "config" / "privacy.json"
    
    # Load current consent
    if consent_file.exists():
        with open(consent_file) as f:
            consent = json.load(f)
    else:
        consent = {
            "analytics": False,
            "error_reporting": False,
            "telemetry": False,
            "last_updated": None
        }
    
    print("🔐 Consent Management")
    print("=" * 50)
    print()
    print("Current preferences:")
    print(f"  Analytics: {'✅ Enabled' if consent.get('analytics') else '❌ Disabled'}")
    print(f"  Error Reporting: {'✅ Enabled' if consent.get('error_reporting') else '❌ Disabled'}")
    print(f"  Telemetry: {'✅ Enabled' if consent.get('telemetry') else '❌ Disabled'}")
    print()
    print("Update preferences:")
    print("  1. Enable all")
    print("  2. Disable all (recommended)")
    print("  3. Custom")
    print()
    
    choice = input("Choice (1-3): ").strip()
    
    if choice == "1":
        consent["analytics"] = True
        consent["error_reporting"] = True
        consent["telemetry"] = True
    elif choice == "2":
        consent["analytics"] = False
        consent["error_reporting"] = False
        consent["telemetry"] = False
    elif choice == "3":
        consent["analytics"] = input("Enable analytics? (y/n): ").lower() == "y"
        consent["error_reporting"] = input("Enable error reporting? (y/n): ").lower() == "y"
        consent["telemetry"] = input("Enable telemetry? (y/n): ").lower() == "y"
    
    consent["last_updated"] = datetime.now().isoformat()
    
    # Save
    consent_file.parent.mkdir(parents=True, exist_ok=True)
    with open(consent_file, "w") as f:
        json.dump(consent, f, indent=2)
    
    print()
    print("✅ Consent preferences saved")
    print(f"   Location: {consent_file}")

# =============================================================================
# CLI
# =============================================================================
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    if cmd == "export":
        export_data()
    elif cmd == "delete":
        delete_data(selective=True)
    elif cmd == "consent":
        manage_consent()
    elif cmd == "reset":
        confirm = input("⚠️  Full system reset? Type 'RESET': ")
        if confirm == "RESET":
            full_reset()
    else:
        print("Novahiz OS RGPD Tools")
        print("=" * 50)
        print()
        print("Commands:")
        print("  export   — Export all your data (Art. 15, 20)")
        print("  delete   — Delete your data (Art. 17)")
        print("  consent  — Manage consent preferences (Art. 7)")
        print("  reset    — Full system reset")
        print()
        print("Usage: python3 rgpd_tools.py <command>")
