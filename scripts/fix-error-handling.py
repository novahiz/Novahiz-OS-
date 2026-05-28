#!/usr/bin/env python3
"""
Auto-fix bare except statements in Novahiz OS codebase
"""
import os
import re
from pathlib import Path

def fix_file(filepath):
    """Fix bare except in a file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Fix bare except: -> except Exception:
    content = re.sub(r'\nexcept:\s*\n', '\nexcept Exception:\n', content)
    content = re.sub(r'except:$', 'except Exception:', content, flags=re.MULTILINE)
    
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    mcp_dir = Path.home() / ".opencode" / "mcp"
    runtime_dir = Path.home() / ".opencode" / "runtime"
    
    fixed = 0
    for d in [mcp_dir, runtime_dir]:
        for f in d.glob("*.py"):
            if fix_file(f):
                print(f"✅ Fixed: {f.name}")
                fixed += 1
    
    print(f"\nTotal files fixed: {fixed}")

if __name__ == "__main__":
    main()
