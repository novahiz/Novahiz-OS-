#!/usr/bin/env python3
"""
Novahiz OS — Immutable State Manager
Provides atomic, versioned, immutable state updates
"""

import json
import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import threading

NOVAHIZ_DIR = Path.home() / ".opencode"
MEMORY_DIR = NOVAHIZ_DIR / "memory"
ARCHIVES_DIR = MEMORY_DIR / "04_Archives"

# Thread lock for atomic operations
_state_lock = threading.Lock()


class ImmutableState:
    """
    Immutable state manager with versioning and atomic updates.
    
    Usage:
        state = ImmutableState("metrics")
        new_state = state.update({"used_today": 5})
        state.commit(new_state, "Increment premium usage")
    """
    
    def __init__(self, name: str):
        self.name = name
        self.current_file = MEMORY_DIR / "00_Core" / f"{name}.json"
        self.archive_dir = ARCHIVES_DIR / name
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        self._current = None
        self._version = 0
        self._load()
    
    def _load(self):
        """Load current state"""
        if self.current_file.exists():
            try:
                with open(self.current_file, "r") as f:
                    data = json.load(f)
                    self._current = data
                    self._version = data.get("_version", 0)
            except Exception:
                self._current = {}
                self._version = 0
        else:
            self._current = {}
            self._version = 0
    
    def get(self, key: str = None, default: Any = None) -> Any:
        """Get value (read-only, no locks needed)"""
        if key is None:
            return dict(self._current)  # Return copy
        return self._current.get(key, default)
    
    def update(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new state with changes (immutable update).
        Returns new state dict (not committed yet).
        """
        new_state = dict(self._current)  # Copy
        new_state.update(changes)
        new_state["_version"] = self._version + 1
        new_state["_updated"] = datetime.now().isoformat()
        return new_state
    
    def commit(self, new_state: Dict[str, Any], message: str = "") -> bool:
        """
        Atomically commit new state.
        1. Archive current state
        2. Write new state to temp file
        3. Atomic rename
        """
        with _state_lock:
            try:
                # Archive current state
                if self._current:
                    archive_file = self.archive_dir / f"{self.name}_v{self._version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(archive_file, "w") as f:
                        json.dump(self._current, f, indent=2)
                
                # Write new state to temp
                temp_file = self.current_file.with_suffix(".tmp")
                with open(temp_file, "w") as f:
                    json.dump(new_state, f, indent=2)
                
                # Atomic rename
                temp_file.replace(self.current_file)
                
                # Update in-memory
                self._current = new_state
                self._version = new_state.get("_version", 0)
                
                # Log commit
                self._log_commit(message)
                
                return True
            except Exception as e:
                print(f"Commit failed: {e}")
                # Cleanup temp if exists
                if temp_file.exists():
                    temp_file.unlink()
                return False
    
    def _log_commit(self, message: str):
        """Log commit to evolution log"""
        evolution_log = MEMORY_DIR / "00_Core" / "evolution-log.md"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(evolution_log, "a") as f:
            f.write(f"\n## [{timestamp}] {self.name} v{self._version}\n\n")
            if message:
                f.write(f"**Change:** {message}\n\n")
            f.write(f"**State:**\n```json\n{json.dumps(self._current, indent=2)}\n```\n")
    
    def get_history(self, limit: int = 10) -> list:
        """Get list of archived versions"""
        archives = sorted(self.archive_dir.glob(f"{self.name}_*.json"), reverse=True)
        return [str(a) for a in archives[:limit]]
    
    def restore(self, version: int) -> bool:
        """Restore from archived version"""
        # Find archive file
        archive_files = list(self.archive_dir.glob(f"{self.name}_v{version}_*.json"))
        if not archive_files:
            print(f"Version {version} not found")
            return False
        
        # Load archived state
        with open(archive_files[0], "r") as f:
            archived_state = json.load(f)
        
        # Remove version metadata
        archived_state.pop("_version", None)
        archived_state.pop("_updated", None)
        
        # Commit as new version
        return self.commit(archived_state, f"Restored from v{version}")
    
    def get_hash(self) -> str:
        """Get SHA256 hash of current state"""
        return hashlib.sha256(
            json.dumps(self._current, sort_keys=True).encode()
        ).hexdigest()


# =============================================================================
# SINGLETON STATE MANAGERS
# =============================================================================

class StateManager:
    """Centralized state management"""
    
    _instance = None
    _states = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_state(self, name: str) -> ImmutableState:
        """Get or create state manager"""
        if name not in self._states:
            self._states[name] = ImmutableState(name)
        return self._states[name]
    
    def list_states(self) -> list:
        """List all managed states"""
        return list(self._states.keys())
    
    def snapshot_all(self) -> str:
        """Create snapshot of all states"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_dir = ARCHIVES_DIR / f"snapshot_{timestamp}"
        snapshot_dir.mkdir(parents=True, exist_ok=True)
        
        for name, state in self._states.items():
            snapshot_file = snapshot_dir / f"{name}.json"
            with open(snapshot_file, "w") as f:
                json.dump(state.get(), f, indent=2)
        
        return str(snapshot_dir)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_metrics_state() -> ImmutableState:
    """Get metrics state manager"""
    return StateManager().get_state("metrics")

def get_nexus_state() -> ImmutableState:
    """Get nexus state manager"""
    return StateManager().get_state("nexus")

def atomic_update_metrics(changes: Dict[str, Any], message: str = "") -> bool:
    """Atomically update metrics"""
    state = get_metrics_state()
    new_state = state.update(changes)
    return state.commit(new_state, message)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if cmd == "status":
        print("📊 Immutable State Manager")
        print("=" * 50)
        
        manager = StateManager()
        for name in ["metrics", "nexus", "constitution"]:
            state = manager.get_state(name)
            print(f"\n{name}:")
            print(f"  Version: {state._version}")
            print(f"  Hash: {state.get_hash()[:16]}...")
            print(f"  Keys: {list(state.get().keys())}")
    
    elif cmd == "snapshot":
        print("📸 Creating snapshot...")
        manager = StateManager()
        path = manager.snapshot_all()
        print(f"✅ Snapshot: {path}")
    
    elif cmd == "history":
        if len(sys.argv) < 3:
            print("Usage: immutable_state.py history <name>")
            sys.exit(1)
        
        name = sys.argv[2]
        state = ImmutableState(name)
        history = state.get_history()
        
        print(f"📜 History for {name}:")
        for i, archive in enumerate(history, 1):
            print(f"  {i}. {archive}")
    
    elif cmd == "restore":
        if len(sys.argv) < 4:
            print("Usage: immutable_state.py restore <name> <version>")
            sys.exit(1)
        
        name = sys.argv[2]
        version = int(sys.argv[3])
        state = ImmutableState(name)
        
        if state.restore(version):
            print(f"✅ Restored {name} to v{version}")
        else:
            print(f"❌ Failed to restore")
    
    else:
        print("Immutable State Manager")
        print("=" * 50)
        print()
        print("Commands:")
        print("  status              — Show all states")
        print("  snapshot            — Create snapshot of all states")
        print("  history <name>      — Show version history")
        print("  restore <name> <v>  — Restore to version")
        print()
        print("Usage: python3 immutable_state.py <command>")
