#!/bin/bash

# egSYS Monitor - Instalação Completa com Systemd
# Dashboard e Túnel rodando como serviços do sistema

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║        egSYS Monitor - Instalação de Serviços Systemd       ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

INSTALL_DIR="$HOME/.egsys-monitor"
USER=$(whoami)

# 1. Criar serviço do Dashboard
echo "📝 1/3: Criando serviço do Dashboard..."

sudo tee /etc/systemd/system/egsys-dashboard.service > /dev/null << EOF
[Unit]
Description=egSYS Monitor - Dashboard Web
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR/src
ExecStart=/usr/bin/gunicorn -w 2 -b 0.0.0.0:5000 complete_system:app
Restart=always
RestartSec=5
StandardOutput=append:$INSTALL_DIR/logs/dashboard.log
StandardError=append:$INSTALL_DIR/logs/dashboard-error.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Serviço do Dashboard criado"

# 2. Criar serviço do Túnel Cloudflare
echo ""
echo "📝 2/3: Criando serviço do Túnel Cloudflare..."

sudo tee /etc/systemd/system/egsys-tunnel.service > /dev/null << EOF
[Unit]
Description=egSYS Monitor - Cloudflare Tunnel
After=network.target egsys-dashboard.service
Requires=egsys-dashboard.service

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/cloudflared tunnel --url http://localhost:5000
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/tunnel.log
StandardError=append:$INSTALL_DIR/logs/tunnel-error.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Serviço do Túnel criado"

# 3. Habilitar e iniciar serviços
echo ""
echo "📝 3/3: Habilitando e iniciando serviços..."

sudo systemctl daemon-reload
sudo systemctl enable egsys-dashboard.service
sudo systemctl enable egsys-tunnel.service
sudo systemctl start egsys-dashboard.service
sleep 3
sudo systemctl start egsys-tunnel.service

echo "✅ Serviços habilitados e iniciados"

# 4. Aguardar túnel gerar URL
echo ""
echo "⏳ Aguardando túnel gerar URL pública..."
sleep 10

# 5. Extrair URL
TUNNEL_URL=$(grep -oP 'https://[a-z0-9-]+\.trycloudflare\.com' $INSTALL_DIR/logs/tunnel.log 2>/dev/null | tail -1)

# 6. Mostrar resultado
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo ""
echo "🎉 egSYS Monitor está rodando como serviço do sistema!"
echo ""

if [ -n "$TUNNEL_URL" ]; then
    echo "🌐 URL Pública:"
    echo "   $TUNNEL_URL"
    echo ""
    echo "$TUNNEL_URL" > $INSTALL_DIR/tunnel-url.txt
else
    echo "⏳ URL ainda sendo gerada. Execute para ver:"
    echo "   egsys-url"
    echo ""
fi

echo "🔐 Credenciais:"
echo "   Usuário: lucasserafim"
echo "   Senha: Rune89Lukas@#$"
echo ""
echo "📊 Status dos Serviços:"
sudo systemctl status egsys-dashboard.service --no-pager -l | head -3
sudo systemctl status egsys-tunnel.service --no-pager -l | head -3
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 COMANDOS ÚTEIS:"
echo ""
echo "   egsys-status      # Ver status dos serviços"
echo "   egsys-restart     # Reiniciar serviços"
echo "   egsys-stop        # Parar serviços"
echo "   egsys-start       # Iniciar serviços"
echo "   egsys-logs        # Ver logs do dashboard"
echo "   egsys-tunnel-logs # Ver logs do túnel"
echo "   egsys-url         # Ver URL pública"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 VANTAGENS:"
echo ""
echo "   ✅ Roda automaticamente ao ligar o computador"
echo "   ✅ Não precisa de terminal aberto"
echo "   ✅ Reinicia automaticamente se cair"
echo "   ✅ Logs salvos automaticamente"
echo "   ✅ Gerenciado pelo systemd (sistema operacional)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
