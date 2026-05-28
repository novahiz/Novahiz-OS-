# Novahiz OS — Disaster Recovery Runbook

## 🚨 Emergency Contacts

- **System Owner:** Novahiz OS Team
- **Backup Location:** `~/.opencode-backups/`
- **Last Backup:** Run `ls -lt ~/.opencode-backups/ | head -1`

---

## 📋 Recovery Scenarios

### Scenario 1: Corrupted Memory Files

**Symptoms:**
- Agents not loading
- Metrics not tracking
- Configuration lost

**Recovery:**
```bash
# Stop all daemons
pkill -f novahiz-runtime
pkill -f opencode-bridge

# Restore from backup
cd ~/.opencode
tar -xzf ~/.opencode-backups/novahiz_backup_LATEST.tar.gz

# Restart daemons
./mcp/supervisor.sh start
```

---

### Scenario 2: Complete System Failure

**Symptoms:**
- Novahiz directory deleted
- All configurations lost

**Recovery:**
```bash
# Clone fresh repo
cd ~
git clone https://github.com/your-org/novahiz-os.git .opencode
cd .opencode

# Restore data from backup
tar -xzf ~/.opencode-backups/novahiz_backup_LATEST.tar.gz

# Reinstall dependencies
pip install -r requirements.txt 2>/dev/null || true
npm install 2>/dev/null || true

# Setup
./setup-cicd.sh
```

---

### Scenario 3: API Keys Lost

**Symptoms:**
- All LLM calls failing
- Authentication errors

**Recovery:**
```bash
# Restore config
cp ~/.opencode-backups/config.json.backup ~/.opencode/runtime/config.json

# Or reconfigure
export OPENROUTER_API_KEY="your-new-key"
python3 ~/.opencode/scripts/novahiz-config.py
```

---

## 🔄 Backup Schedule

| Frequency | Command | Cron Entry |
|-----------|---------|------------|
| Daily | `./scripts/backup.sh` | `0 2 * * * /home/novahiz/.opencode/scripts/backup.sh` |
| Weekly | Offsite copy | `0 3 * * 0 rsync -av ~/.opencode-backups/ remote:/backups/` |

---

## ✅ Pre-Recovery Checklist

- [ ] Identify failure scope (partial vs complete)
- [ ] Locate latest valid backup
- [ ] Verify backup checksum: `sha256sum -c backup.tar.gz.sha256`
- [ ] Stop all running daemons
- [ ] Document incident start time

---

## 📞 Post-Recovery Validation

```bash
# 1. Check runtime status
python3 ~/.opencode/runtime/novahiz-runtime.py status

# 2. Verify premium budget
cat ~/.opencode/memory/00_Core/metrics.json | jq .premiumBudget

# 3. Test agent execution
nv exec test-agent "Hello, this is a recovery test"

# 4. Check logs
tail -f ~/.opencode/logs/novahiz-runtime.log
```

---

## 🔐 Security Notes

- Backups are NOT encrypted by default
- For production: Add `gpg --encrypt` to backup script
- Store offsite backups in secure location
- Rotate API keys after recovery if compromise suspected

---

## 📧 Incident Reporting Template

```
INCIDENT REPORT
===============
Date/Time: 
Detected By: 
Severity: P0/P1/P2
Impact: 
Root Cause: 
Resolution: 
Recovery Time: 
Lessons Learned: 
```

---

*Last Updated: 2026-05-27*  
*Version: 1.0*
