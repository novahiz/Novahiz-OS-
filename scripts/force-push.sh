#!/bin/bash
# Force push with maximum retries and timeouts

cd /home/novahiz/.opencode

echo "🚀 Novahiz OS — GitHub Force Push"
echo "=================================="
echo ""

# Config Git pour gros push
git config http.postBuffer 524288000
git config http.lowSpeedLimit 0
git config http.lowSpeedTime 999999
git config pack.compression 6

# Nettoyer
git gc --quiet

# Push avec curl retry
echo "📤 Pushing to GitHub..."
echo "   This may take several minutes..."
echo ""

export GIT_HTTP_LOW_SPEED_LIMIT=0
export GIT_HTTP_LOW_SPEED_TIME=999999

# Utiliser curl avec retry
curl_retry () {
    local n=1
    local max=5
    local delay=15
    while true; do
        echo "Attempt $n/$max..."
        git push -u origin main --force 2>&1 | tee /tmp/push-log.txt
        
        if grep -q "done\|Everything up-to-date" /tmp/push-log.txt && ! grep -q "error\|fatal" /tmp/push-log.txt; then
            echo ""
            echo "✅ PUSH SUCCESSFUL!"
            return 0
        fi
        
        if [ $n -ge $max ]; then
            echo ""
            echo "❌ PUSH FAILED after $max attempts"
            echo ""
            echo "Last error:"
            tail -5 /tmp/push-log.txt
            return 1
        fi
        
        echo "⏳ Waiting ${delay}s before retry..."
        sleep $delay
        n=$((n+1))
        delay=$((delay*2))
    done
}

curl_retry
