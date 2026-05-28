#!/bin/bash
# Novahiz OS - Setup Cron Jobs for Backup & Maintenance

echo "⏰ Novahiz OS Cron Setup"
echo "=" | awk '{for(i=1;i<=50;i++) printf $0}' ; echo ""

# Get absolute paths
NOVAHIZ_DIR="$HOME/.opencode"
BACKUP_SCRIPT="${NOVAHIZ_DIR}/scripts/backup.sh"
LOG_CENTRALIZE="${NOVAHIZ_DIR}/scripts/centralize-logs.py"
SECRET_SCAN="${NOVAHIZ_DIR}/scripts/scan-secrets.sh"

# Check if scripts exist
for script in "$BACKUP_SCRIPT" "$LOG_CENTRALIZE" "$SECRET_SCAN"; do
    if [ ! -f "$script" ]; then
        echo "❌ Script not found: $script"
        exit 1
    fi
done

echo "Scripts validated:"
echo "  ✓ Backup: $BACKUP_SCRIPT"
echo "  ✓ Logs: $LOG_CENTRALIZE"
echo "  ✓ Secrets: $SECRET_SCAN"
echo ""

# Create cron entries
CRON_JOBS="
# Novahiz OS Automated Tasks
# Daily backup at 2 AM
0 2 * * * $BACKUP_SCRIPT >> $HOME/.opencode/logs/backup.log 2>&1

# Log centralization every 6 hours
0 */6 * * * /usr/bin/python3 $LOG_CENTRALIZE >> $HOME/.opencode/logs/log-centralize.log 2>&1

# Secret scan weekly (Sunday 3 AM)
0 3 * * 0 $SECRET_SCAN >> $HOME/.opencode/logs/secret-scan.log 2>&1
"

# Install crontab
echo "$CRON_JOBS" | crontab - 2>/dev/null || {
    echo "⚠️  Could not install crontab (may need manual setup)"
    echo ""
    echo "Manual installation:"
    echo "  crontab -e"
    echo "  # Add the jobs above"
    exit 0
}

echo "✅ Cron jobs installed!"
echo ""
echo "Schedule:"
echo "  🕐 Daily 2:00 AM  - Backup"
echo "  🕐 Every 6 hours - Log centralization"
echo "  🕐 Sunday 3:00 AM - Secret scan"
echo ""
echo "View cron jobs:"
echo "  crontab -l"
echo ""
echo "Logs:"
echo "  ~/.opencode/logs/backup.log"
echo "  ~/.opencode/logs/log-centralize.log"
echo "  ~/.opencode/logs/secret-scan.log"
echo ""
