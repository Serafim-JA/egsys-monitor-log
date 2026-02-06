#!/bin/bash

echo "🚀 egSYS Monitor - Início Rápido"
echo "================================="
echo ""

# Para processos existentes
pkill -9 -f "python.*complete_system" 2>/dev/null
pkill -9 -f gunicorn 2>/dev/null
sleep 2

# Instala Gunicorn
pip3 install --break-system-packages gunicorn 2>/dev/null || pip3 install --user gunicorn 2>/dev/null

# Inicia servidor
cd "/home/lucasserafim/Área de Trabalho/egsys-monitor"
nohup gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 --timeout 120 --access-logfile logs/access.log --error-logfile logs/error.log --pid /tmp/egsys.pid src.complete_system:app > /tmp/gunicorn_start.log 2>&1 &

sleep 5

if [ -f /tmp/egsys.pid ] && kill -0 $(cat /tmp/egsys.pid) 2>/dev/null; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    echo "✅ SISTEMA ONLINE!"
    echo ""
    echo "📍 http://localhost:5000"
    echo "🌐 http://${LOCAL_IP}:5000"
    echo ""
    echo "👤 lucasserafim"
    echo "🔑 Rune89Lukas@#$"
    echo ""
    echo "⚡ Gunicorn rodando (PID: $(cat /tmp/egsys.pid))"
else
    echo "❌ Erro ao iniciar"
    cat /tmp/gunicorn_start.log
fi
