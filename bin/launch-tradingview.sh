#!/bin/bash
# =============================================================================
# TradingView Launcher - NovaHiz OS
# Lance TradingView avec Chrome DevTools Protocol
# =============================================================================

NOVAHIZ_DIR="$HOME/.opencode"
PORT="${1:-9222}"
LOG_FILE="$NOVAHIZ_DIR/logs/tradingview-launch.log"

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}→ Lancement de TradingView avec CDP port $PORT...${NC}"

# Trouver TradingView
APP="/opt/TradingView/tradingview"
if [ ! -x "$APP" ]; then
    APP=$(which tradingview 2>/dev/null)
fi

if [ -z "$APP" ] || [ ! -x "$APP" ]; then
    echo -e "${RED}Erreur:${NC} TradingView non trouvé"
    echo "Installez-le depuis: https://tradingview.com/desktop/"
    exit 1
fi

echo "Found: $APP"

# Tuer les instances existantes (sans bloquer)
killall tradingview 2>/dev/null || true
sleep 1

# Lancer TradingView
export DISPLAY=:0
nohup "$APP" \
    --remote-debugging-port=$PORT \
    --disable-gpu \
    --disable-software-rasterizer \
    --no-sandbox \
    > "$LOG_FILE" 2>&1 &

TV_PID=$!
echo -e "${GREEN}✓ PID: $TV_PID${NC}"

# Attendre CDP
echo "Attente de CDP..."
for i in $(seq 1 20); do
    if curl -s "http://localhost:$PORT/json/version" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ CDP prêt sur http://localhost:$PORT${NC}"
        curl -s "http://localhost:$PORT/json/version" 2>/dev/null | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(f\"  Browser: {d.get('Browser','N/A')}\")
" 2>/dev/null || echo "  (info non disponible)"
        echo ""
        echo -e "${GREEN}TradingView est lancé avec succès!${NC}"
        echo "Maintenant dans OpenCode, tu peux utiliser les outils TradingView."
        exit 0
    fi
    sleep 1
    echo "  ... $i/20"
done

echo -e "${RED}✗ Timeout: CDP ne répond pas après 20s${NC}"
echo "Vérifie les logs: $LOG_FILE"
exit 1
