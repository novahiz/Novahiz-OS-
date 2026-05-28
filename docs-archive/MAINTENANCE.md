# 🔧 Novahiz OS — Maintenance Guide

## Daily Tasks

### Morning Check
```bash
# Health check
nv health

# Check overnight executions
nv metrics today

# Review errors
grep "ERROR" ~/.opencode/logs/*.log | tail -20
```

### Evening Check
```bash
# Verify daemons running
ps aux | grep novahiz | grep -v grep | wc -l

# Check disk space
df -h ~/.opencode

# Quick restart if needed
novahiz-stop.sh && novahiz-autostart.sh
```

---

## Weekly Tasks

### Monday
```bash
# Full test suite
cd ~/.opencode/tests
python3 test_novahiz.py
./run-integration-tests.sh
```

### Wednesday
```bash
# Log rotation
logrotate -f ~/.opencode/logs/logrotate.conf

# Clean old executions
find ~/.opencode/executions -name "*.json" -mtime +7 -delete
```

### Friday
```bash
# Review metrics
nv metrics week

# Backup metrics
cp ~/.opencode/metrics/usage.json ~/.opencode/metrics/usage-$(date +%Y%m%d).json

# Check for updates
git fetch origin 2>/dev/null && git log HEAD..origin/main --oneline
```

---

## Monthly Tasks

### First Week
```bash
# Security audit
grep -r "sk-or-v1\|sk-TnPvEk" ~/.opencode --include="*.py" --include="*.sh" --include="*.json" 2>/dev/null
# Should return nothing (keys only in .env)

# Review .bashrc for secrets
grep -i "api_key\|secret" ~/.bashrc
# Should return nothing

# Check file permissions
stat -c "%a %n" ~/.novahiz/.env
# Should be 600
```

### Mid Month
```bash
# Performance review
ps aux | grep novahiz | awk '{print "CPU: " $3 "% MEM: " $4 "% - " $11}'

# Memory check
ps aux | grep novahiz | awk '{sum+=$6} END {print "Total memory: " sum/1024 " MB"}'

# Log analysis
wc -l ~/.opencode/logs/*.log
```

### End of Month
```bash
# Full backup
tar -czf ~/backups/novahiz-$(date +%Y%m).tar.gz \
    ~/.opencode/runtime \
    ~/.opencode/mcp \
    ~/.opencode/metrics \
    ~/.opencode/tests \
    --exclude="logs/*" \
    --exclude="executions/*"

# Documentation review
# Ensure README.md is up to date

# Plan next month improvements
```

---

## Quarterly Tasks

### Q1, Q2, Q3, Q4

```bash
# Dependency audit
pip list --outdated
npm outdated 2>/dev/null

# Security scan
# Review API key rotation schedule

# Performance benchmark
# Compare metrics with previous quarter

# Documentation audit
# Update any outdated sections

# Test coverage review
# Aim for 80%+ coverage
```

---

## Incident Response

### Service Down
```bash
# 1. Check status
nv health

# 2. Check logs
tail -100 ~/.opencode/logs/autostart.log

# 3. Restart services
novahiz-stop.sh
sleep 2
novahiz-autostart.sh

# 4. Verify
nv health

# 5. If still failing, check system
journalctl -u novahiz-runtime --since "10 minutes ago"
```

### High Memory Usage
```bash
# 1. Check memory
ps aux | grep novahiz | awk '{print $6/1024 " MB - " $11}'

# 2. Identify culprit
# Look for processes > 100MB

# 3. Restart specific daemon
pkill -f opencode-bridge.py
sleep 2
python3 ~/.opencode/mcp/opencode-bridge.py daemon 2 &

# 4. Monitor
watch -n 5 'ps aux | grep novahiz | awk "{print \$6/1024}"'
```

### API Errors
```bash
# 1. Check API key
echo $OPENROUTER_API_KEY | cut -c1-20

# 2. Test API directly
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models | head -5

# 3. Check rate limits
grep "rate limit\|429" ~/.opencode/logs/*.log

# 4. If key expired, update .env
nano ~/.novahiz/.env
novahiz-stop.sh && novahiz-autostart.sh
```

---

## Performance Tuning

### Adjust Concurrency
```bash
# Edit config
nano ~/.opencode/runtime/config.json

# Change:
"max_concurrent": 5  # Increase for high load, decrease for low memory
```

### Adjust Timeout
```bash
# In .env:
NOVAHIZ_TIMEOUT=120  # Increase for complex tasks
```

### Adjust Poll Interval
```bash
# In opencode-bridge.py daemon call:
python3 opencode-bridge.py daemon 5  # 5 seconds instead of 2
```

---

## Backup Strategy

### Daily (Automated)
```bash
# Add to crontab:
0 2 * * * cp ~/.opencode/metrics/usage.json ~/.opencode/backups/metrics-$(date +\%Y\%m\%d).json
```

### Weekly (Manual)
```bash
# Backup configs
tar -czf ~/backups/novahiz-config-$(date +%Y%m%d).tar.gz \
    ~/.novahiz/.env \
    ~/.opencode/runtime/config.json \
    ~/.config/opencode/opencode.jsonc
```

### Monthly (Full)
```bash
# Full backup with exclusions
tar -czf ~/backups/novahiz-full-$(date +%Y%m).tar.gz \
    ~/.opencode \
    ~/.novahiz \
    --exclude="logs/*" \
    --exclude="executions/*" \
    --exclude="pids/*" \
    --exclude="__pycache__/*"
```

---

[Novahiz OS v6.0 — Maintenance Guide]
