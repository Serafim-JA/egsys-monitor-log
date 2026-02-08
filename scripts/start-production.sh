#!/bin/bash

echo "🚀 egSYS Monitor - Inicialização Produção"
echo "=========================================="
echo ""

# Adiciona usuário ao grupo docker
if ! groups | grep -q docker; then
    echo "📦 Configurando permissões Docker..."
    echo "280407" | sudo -S usermod -aG docker $USER
    echo "✓ Usuário adicionado ao grupo docker"
    echo ""
    echo "⚠️  IMPORTANTE: Execute 'newgrp docker' ou faça logout/login"
    echo "   Depois execute este script novamente"
    exit 0
fi

# Para processos Python existentes
echo "🛑 Parando processos existentes..."
pkill -9 -f "python.*complete_system" 2>/dev/null || true
sleep 2

# Inicia com Gunicorn
echo "🚀 Iniciando servidor de produção..."
cd "/home/lucasserafim/Área de Trabalho/egsys-monitor"

# Instala Gunicorn se necessário
pip3 install --break-system-packages gunicorn 2>/dev/null || pip3 install --user gunicorn

# Inicia com Gunicorn (4 workers, auto-restart)
nohup gunicorn --bind 0.0.0.0:5000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --daemon \
    --pid /tmp/egsys-monitor.pid \
    src.complete_system:app

sleep 3

# Verifica se está rodando
if [ -f /tmp/egsys-monitor.pid ] && kill -0 $(cat /tmp/egsys-monitor.pid) 2>/dev/null; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "✅ egSYS Monitor ONLINE 24/7!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📍 Acesso Local:"
    echo "   http://localhost:5000"
    echo ""
    echo "🌐 Acesso Rede Local:"
    echo "   http://${LOCAL_IP}:5000"
    echo ""
    echo "👤 Credenciais:"
    echo "   Usuário: lucasserafim"
    echo "   Senha: Rune89Lukas@#$"
    echo ""
    echo "🔧 Gerenciamento:"
    echo "   Parar:     kill \$(cat /tmp/egsys-monitor.pid)"
    echo "   Reiniciar: ./start-production.sh"
    echo "   Logs:      tail -f logs/access.log"
    echo ""
    echo "⚡ Servidor: Gunicorn (4 workers)"
    echo "🔄 Auto-restart: Ativo"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
else
    echo "❌ Erro ao iniciar servidor"
    echo "Verifique os logs em: logs/error.log"
    exit 1
fi
