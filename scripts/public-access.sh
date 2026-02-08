#!/bin/bash

echo "🌍 egSYS Monitor - Acesso Público Global"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if dashboard is running
if ! pgrep -f dashboard_server > /dev/null; then
    echo -e "${YELLOW}Iniciando dashboard...${NC}"
    cd "/home/lucasserafim/Área de Trabalho/egsys-monitor"
    nohup python3 src/dashboard_server.py > /tmp/egsys_dashboard.log 2>&1 &
    sleep 5
fi

# Check if ngrok exists
if [ ! -f "/tmp/ngrok" ]; then
    echo -e "${YELLOW}Baixando ngrok...${NC}"
    cd /tmp
    wget -q https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar xzf ngrok-v3-stable-linux-amd64.tgz
    chmod +x ngrok
fi

# Kill existing ngrok
pkill -9 ngrok 2>/dev/null

# Start ngrok tunnel
echo -e "${BLUE}Criando túnel público...${NC}"
cd /tmp
nohup ./ngrok http 5000 --log=stdout > /tmp/ngrok.log 2>&1 &

sleep 5

# Get public URL
echo -e "${YELLOW}Obtendo URL pública...${NC}"
sleep 3

PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)

if [ -z "$PUBLIC_URL" ]; then
    echo -e "${RED}❌ Erro ao criar túnel público${NC}"
    echo "Logs do ngrok:"
    cat /tmp/ngrok.log
    exit 1
fi

LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}✅ egSYS Monitor acessível globalmente!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🌍 ACESSO PÚBLICO (de qualquer lugar):${NC}"
echo "   ${PUBLIC_URL}"
echo ""
echo -e "${BLUE}📱 Acesse de:${NC}"
echo "   • Celular (4G/5G/WiFi)"
echo "   • Tablet"
echo "   • Qualquer computador"
echo "   • Qualquer rede"
echo ""
echo -e "${GREEN}📍 Acesso Local:${NC}"
echo "   http://localhost:5000"
echo ""
echo -e "${GREEN}🏠 Acesso Rede Local:${NC}"
echo "   http://${LOCAL_IP}:5000"
echo ""
echo -e "${YELLOW}🔐 Credenciais:${NC}"
echo "   Fornecidas pelo administrador"
echo ""
echo -e "${BLUE}📊 Painel ngrok:${NC}"
echo "   http://localhost:4040"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "   • URL pública válida enquanto o script estiver rodando"
echo "   • Mantenha este terminal aberto"
echo "   • Para parar: Ctrl+C"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save URL to file
echo "$PUBLIC_URL" > /tmp/egsys_public_url.txt
echo -e "${GREEN}URL salva em: /tmp/egsys_public_url.txt${NC}"
echo ""

# Keep script running
echo -e "${BLUE}Pressione Ctrl+C para parar o túnel${NC}"
tail -f /tmp/ngrok.log
