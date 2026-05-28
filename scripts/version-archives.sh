#!/bin/bash
# Novahiz OS — Git Versioning for Memory/Archives
# Creates git repo for memory tracking with automated commits

set -e

NOVAHIZ_DIR="$HOME/.opencode"
MEMORY_DIR="$NOVAHIZ_DIR/memory"
ARCHIVES_DIR="$MEMORY_DIR/04_Archives"
GIT_DIR="$MEMORY_DIR/.git"

echo "📜 Novahiz OS — Memory Archives Git Versioning"
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""

# =============================================================================
# INITIALIZE GIT REPO
# =============================================================================
init_git_repo() {
    echo "📦 Initializing git repo for memory archives..."
    
    if [ -d "$GIT_DIR" ]; then
        echo "  ✓ Git repo already exists"
    else
        cd "$MEMORY_DIR"
        git init --quiet
        git config user.email "novahiz-os@local"
        git config user.name "Novahiz OS"
        echo "  ✓ Git repo initialized"
    fi
    
    # Create .gitignore for memory dir
    cat > "$MEMORY_DIR/.gitignore" << 'EOF'
# Active state files (backed up separately)
00_Core/*.tmp
00_Core/metrics.json.tmp
00_Core/nexus.json.tmp

# Logs
*.log

# OS files
.DS_Store
Thumbs.db
EOF
    
    echo "  ✓ .gitignore created"
}

# =============================================================================
# COMMIT CHANGES
# =============================================================================
commit_changes() {
    local message="${1:-Auto-commit memory archives}"
    
    cd "$MEMORY_DIR"
    
    # Check if there are changes
    if ! git diff --quiet || git ls-files --others --exclude-standard | grep -q .; then
        # Add all changes
        git add -A
        
        # Create commit
        timestamp=$(date +"%Y-%m-%d %H:%M:%S")
        git commit -m "[$timestamp] $message" --quiet
        
        echo "  ✓ Committed: $message"
    else
        echo "  - No changes to commit"
    fi
}

# =============================================================================
# CREATE VERSION TAG
# =============================================================================
create_tag() {
    local tag_name="${1:-$(date +%Y%m%d_%H%M%S)}"
    local message="${2:-Memory snapshot}"
    
    cd "$MEMORY_DIR"
    
    git tag -a "$tag_name" -m "$message"
    echo "  ✓ Created tag: $tag_name"
}

# =============================================================================
# SHOW HISTORY
# =============================================================================
show_history() {
    cd "$MEMORY_DIR"
    
    echo "📜 Git History (last 20 commits):"
    echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""
    git log --oneline -20
    
    echo ""
    echo "📌 Tags:"
    git tag -l
}

# =============================================================================
# EXPORT SNAPSHOT
# =============================================================================
export_snapshot() {
    local output_dir="${1:-$NOVAHIZ_DIR/backups/memory_snapshots}"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local snapshot_dir="$output_dir/snapshot_$timestamp"
    
    mkdir -p "$snapshot_dir"
    
    # Copy entire memory directory
    cp -r "$MEMORY_DIR"/* "$snapshot_dir/"
    
    # Create manifest
    cat > "$snapshot_dir/MANIFEST.json" << EOF
{
    "timestamp": "$(date -Iseconds)",
    "git_commit": "$(cd $MEMORY_DIR && git rev-parse HEAD 2>/dev/null || echo 'N/A')",
    "git_tag": "$(cd $MEMORY_DIR && git describe --tags 2>/dev/null || echo 'N/A')",
    "files_count": $(find "$snapshot_dir" -type f | wc -l),
    "total_size_kb": $(du -sk "$snapshot_dir" | cut -f1)
}
EOF
    
    echo "✅ Snapshot exported: $snapshot_dir"
}

# =============================================================================
# RESTORE FROM SNAPSHOT
# =============================================================================
restore_snapshot() {
    local snapshot_dir="$1"
    
    if [ -z "$snapshot_dir" ] || [ ! -d "$snapshot_dir" ]; then
        echo "❌ Invalid snapshot directory"
        echo "Usage: $0 restore <snapshot_dir>"
        exit 1
    fi
    
    echo "⚠️  Restoring from: $snapshot_dir"
    echo "  This will overwrite current memory files!"
    echo -n "  Type 'RESTORE' to confirm: "
    read confirm
    
    if [ "$confirm" = "RESTORE" ]; then
        # Backup current
        backup_dir="$NOVAHIZ_DIR/backups/pre_restore_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        cp -r "$MEMORY_DIR"/* "$backup_dir/"
        echo "  ✓ Current state backed up to: $backup_dir"
        
        # Restore
        cp -r "$snapshot_dir"/* "$MEMORY_DIR/"
        echo "  ✓ Restored from snapshot"
    else
        echo "  Cancelled"
    fi
}

# =============================================================================
# SETUP AUTO-COMMIT (CRON)
# =============================================================================
setup_autocommit() {
    echo "⏰ Setting up auto-commit cron job..."
    
    CRON_JOB="0 * * * * cd $MEMORY_DIR && git add -A && git commit -m '[Auto] Hourly snapshot' --quiet 2>/dev/null || true"
    
    (crontab -l 2>/dev/null | grep -v "Novahiz auto-commit"; echo "$CRON_JOB") | crontab -
    
    echo "  ✓ Auto-commit scheduled (hourly)"
    echo "  View: crontab -l"
}

# =============================================================================
# MAIN
# =============================================================================
case "${1:-status}" in
    init)
        init_git_repo
        commit_changes "Initial commit"
        ;;
    commit)
        commit_changes "${2:-Manual commit}"
        ;;
    tag)
        create_tag "$2" "$3"
        ;;
    history)
        show_history
        ;;
    export)
        export_snapshot "$2"
        ;;
    restore)
        restore_snapshot "$2"
        ;;
    autocommit)
        setup_autocommit
        ;;
    status)
        echo "📊 Memory Archives Git Status"
        echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""
        
        if [ -d "$GIT_DIR" ]; then
            cd "$MEMORY_DIR"
            echo "Git Repo: ✓ Initialized"
            echo ""
            echo "Recent Commits:"
            git log --oneline -5
            echo ""
            echo "Tags:"
            git tag -l | tail -5
            echo ""
            echo "Working Tree:"
            git status --short
        else
            echo "Git Repo: ✗ Not initialized"
            echo ""
            echo "Run: $0 init"
        fi
        ;;
    *)
        echo "Memory Archives Git Versioning"
        echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""
        echo "Commands:"
        echo "  init              — Initialize git repo"
        echo "  commit [msg]      — Commit changes"
        echo "  tag [name] [msg]  — Create version tag"
        echo "  history           — Show commit history"
        echo "  export [dir]      — Export snapshot"
        echo "  restore <dir>     — Restore from snapshot"
        echo "  autocommit        — Setup hourly auto-commit"
        echo "  status            — Show current status"
        echo ""
        echo "Usage: $0 <command>"
        ;;
esac
