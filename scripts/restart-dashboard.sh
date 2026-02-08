#!/bin/bash

# Parar todos os processos
echo "🛑 Parando processos antigos..."
lsof -ti:5000 | xargs kill -9 2>/dev/null
pkill -9 -f "gunicorn.*complete_system" 2>/dev/null
pkill -9 -f "python.*complete_system" 2>/dev/null
sleep 2

# Limpar cache
echo "🧹 Limpando cache..."
rm -rf "/home/lucasserafim/Área de Trabalho/egsys-monitor/src/__pycache__"
rm -f "/home/lucasserafim/Área de Trabalho/egsys-monitor/src/"*.pyc

# Iniciar servidor
echo "🚀 Iniciando servidor..."
cd "/home/lucasserafim/Área de Trabalho/egsys-monitor"
gunicorn -w 4 --threads 2 -b 0.0.0.0:5000 --chdir src complete_system:app --daemon --pid /tmp/egsys.pid --preload

sleep 4

# Verificar
if ps aux | grep -q "[g]unicorn.*complete_system"; then
    echo "✅ Servidor iniciado com sucesso!"
    echo "🌐 Acesse: http://localhost:5000"
    echo "📊 PID: $(cat /tmp/egsys.pid 2>/dev/null)"
else
    echo "❌ Erro ao iniciar servidor"
    exit 1
fi
