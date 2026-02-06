#!/bin/bash

echo "🌍 egSYS Monitor - Acesso Global via Cloudflare"
echo "================================================"
echo ""

# Download cloudflared
if [ ! -f "/tmp/cloudflared" ]; then
    echo "📦 Baixando Cloudflare Tunnel..."
    wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -O /tmp/cloudflared
    chmod +x /tmp/cloudflared
fi

# Check dashboard
if ! pgrep -f dashboard_server > /dev/null; then
    echo "🚀 Iniciando dashboard..."
    cd "/home/lucasserafim/Área de Trabalho/egsys-monitor"
    nohup python3 src/dashboard_server.py > /tmp/egsys_dashboard.log 2>&1 &
    sleep 5
fi

# Kill existing tunnel
pkill -9 cloudflared 2>/dev/null
sleep 2

# Start tunnel
echo "🔗 Criando túnel público..."
/tmp/cloudflared tunnel --url http://localhost:5000 > /tmp/cloudflare.log 2>&1 &

sleep 8

# Extract URL
PUBLIC_URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflare.log | head -1)

if [ -z "$PUBLIC_URL" ]; then
    echo "⏳ Aguardando túnel..."
    sleep 5
    PUBLIC_URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' /tmp/cloudflare.log | head -1)
fi

if [ -z "$PUBLIC_URL" ]; then
    echo "❌ Erro ao criar túnel"
    cat /tmp/cloudflare.log
    exit 1
fi

LOCAL_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "✅ egSYS Monitor ONLINE GLOBALMENTE!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌍 ACESSO PÚBLICO (Internet):"
echo "   ${PUBLIC_URL}"
echo ""
echo "📱 Acesse de qualquer lugar:"
echo "   • Celular (4G/5G)"
echo "   • WiFi público"
echo "   • Outra cidade/país"
echo "   • Qualquer dispositivo"
echo ""
echo "🏠 Acesso Local:"
echo "   http://localhost:5000"
echo "   http://${LOCAL_IP}:5000"
echo ""
echo "🔐 Login: Credenciais do administrador"
echo ""
echo "⚠️  Mantenha este terminal aberto"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save URL
echo "$PUBLIC_URL" > /tmp/egsys_public_url.txt
echo "URL salva em: /tmp/egsys_public_url.txt"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

# Keep running
tail -f /tmp/cloudflare.log
