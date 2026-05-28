#!/bin/bash
# Novahiz OS - Backup Script
# Creates encrypted backups of critical data

set -e

echo "💾 Novahiz OS Backup"
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""

# Configuration
NOVAHIZ_DIR="${HOME}/.opencode"
BACKUP_DIR="${HOME}/.opencode-backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/novahiz_backup_${DATE}.tar.gz"
CHECKSUM_FILE="${BACKUP_FILE}.sha256"
ENCRYPTED="${BACKUP_FILE}.gpg"

# Enable encryption (set to false to disable)
ENABLE_ENCRYPTION="${ENABLE_BACKUP_ENCRYPTION:-false}"
GPG_RECIPIENT="${BACKUP_GPG_RECIPIENT:-}"

# Critical directories to backup
CRITICAL_DIRS=(
    "memory/00_Core"
    "memory/01_Agents"
    "memory/02_Projects"
    "runtime/config.json"
    "docs/compliance"
    ".github/workflows"
)

# Create backup directory
mkdir -p "${BACKUP_DIR}"

echo "📁 Backup source: ${NOVAHIZ_DIR}"
echo "📦 Backup destination: ${BACKUP_FILE}"
echo ""

# Create tarball of critical files
echo "Creating backup archive..."
cd "${NOVAHIZ_DIR}"

# Build file list
FILES_TO_BACKUP=()
for dir in "${CRITICAL_DIRS[@]}"; do
    if [ -d "$dir" ] || [ -f "$dir" ]; then
        FILES_TO_BACKUP+=("$dir")
    fi
done

if [ ${#FILES_TO_BACKUP[@]} -eq 0 ]; then
    echo "❌ No critical files found to backup"
    exit 1
fi

echo "Files to backup:"
for f in "${FILES_TO_BACKUP[@]}"; do
    echo "  - $f"
done
echo ""

# Create compressed archive
echo "Creating backup archive..."
tar -czf "${BACKUP_FILE}" "${FILES_TO_BACKUP[@]}"

# Generate checksum
sha256sum "${BACKUP_FILE}" > "${CHECKSUM_FILE}"

# Get backup size
BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)

# Optional: Encrypt backup with GPG
if [ "$ENABLE_ENCRYPTION" = "true" ]; then
    if [ -n "$GPG_RECIPIENT" ]; then
        echo "🔐 Encrypting backup with GPG..."
        gpg --yes --batch --encrypt --recipient "$GPG_RECIPIENT" --output "$ENCRYPTED" "$BACKUP_FILE"
        
        # Remove unencrypted backup
        rm -f "$BACKUP_FILE"
        
        BACKUP_FILE="$ENCRYPTED"
        BACKUP_SIZE=$(du -h "$ENCRYPTED" | cut -f1)
        echo "✅ Backup encrypted"
    else
        echo "⚠️  Encryption enabled but GPG_RECIPIENT not set"
        echo "   Set: export BACKUP_GPG_RECIPIENT='your-gpg-key-id'"
        echo "   Continuing with unencrypted backup..."
    fi
fi

echo ""
echo "✅ Backup created successfully!"
echo ""
echo "📊 Details:"
echo "  File: ${BACKUP_FILE}"
echo "  Size: ${BACKUP_SIZE}"
echo "  Checksum: ${CHECKSUM_FILE}"
echo "  Encrypted: ${ENABLE_ENCRYPTION}"
echo ""

# Verify backup
echo "🔍 Verifying backup integrity..."
if sha256sum -c "${CHECKSUM_FILE}" > /dev/null 2>&1; then
    echo "✅ Checksum verified"
else
    echo "❌ Checksum verification failed!"
    exit 1
fi

# List archive contents
echo ""
echo "📋 Archive contents:"
tar -tzf "${BACKUP_FILE}" | head -20

# Cleanup old backups (keep last 7)
echo ""
echo "🧹 Cleaning old backups (keeping last 7)..."
cd "${BACKUP_DIR}"
ls -t novahiz_backup_*.tar.gz* 2>/dev/null | tail -n +8 | xargs -r rm --
ls -t novahiz_backup_*.sha256 2>/dev/null | tail -n +8 | xargs -r rm --
echo "✅ Old backups cleaned"

echo ""
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""
echo "✅ Backup complete!"
echo ""
echo "RESTORE COMMAND:"
if [[ "$BACKUP_FILE" == *.gpg ]]; then
    echo "  # Decrypt first:"
    echo "  gpg --decrypt ${BACKUP_FILE} > backup_decrypted.tar.gz"
    echo "  # Then extract:"
    echo "  tar -xzf backup_decrypted.tar.gz"
else
    echo "  cd ~/.opencode"
    echo "  tar -xzf ${BACKUP_FILE}"
fi
echo ""
