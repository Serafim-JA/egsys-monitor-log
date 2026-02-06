#!/bin/bash

echo "🚀 egSYS Monitor - Quick Deploy"
echo "================================"
echo ""

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Stop existing processes
echo "Parando processos existentes..."
pkill -9 -f dashboard_server 2>/dev/null || true
pkill -9 -f "flask.*5000" 2>/dev/null || true
sleep 2

# Start dashboard
echo "Iniciando dashboard..."
cd "/home/lucasserafim/Área de Trabalho/egsys-monitor"
nohup python3 src/dashboard_server.py > /tmp/egsys_dashboard.log 2>&1 &
DASH_PID=$!

sleep 5

# Check if running
if ps -p $DASH_PID > /dev/null; then
    echo ""
    echo "✅ egSYS Monitor iniciado com sucesso!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📍 Acesso Local:"
    echo "   http://localhost:5000"
    echo ""
    echo "🌐 Acesso Remoto (mesma rede):"
    echo "   http://${LOCAL_IP}:5000"
    echo ""
    echo "📱 De qualquer dispositivo:"
    echo "   1. Conecte na mesma rede WiFi"
    echo "   2. Acesse: http://${LOCAL_IP}:5000"
    echo ""
    echo "🔐 Credenciais fornecidas pelo administrador"
    echo ""
    echo "📋 Logs: tail -f /tmp/egsys_dashboard.log"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "PID: $DASH_PID"
else
    echo "❌ Erro ao iniciar"
    cat /tmp/egsys_dashboard.log
    exit 1
fi
