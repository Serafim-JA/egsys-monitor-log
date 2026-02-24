#!/bin/bash

# egSYS Monitor - Cloudflare Tunnel Setup
# Configura túnel permanente com nome personalizado

set -e

echo "🌐 egSYS Monitor - Configuração Cloudflare Tunnel"
echo ""

TUNNEL_NAME="egSYS-Monitor"
CONFIG_DIR="$HOME/.cloudflared"
INSTALL_DIR="$HOME/.egsys-monitor"

# Criar diretório de configuração
mkdir -p "$CONFIG_DIR"
mkdir -p "$INSTALL_DIR/logs"

echo "📝 Passo 1: Autenticação Cloudflare"
echo "   Isso abrirá seu navegador para login..."
echo ""
read -p "Pressione ENTER para continuar..."

cloudflared tunnel login

if [ ! -f "$CONFIG_DIR/cert.pem" ]; then
    echo "❌ Autenticação falhou. Tente novamente."
    exit 1
fi

echo ""
echo "✅ Autenticação concluída!"
echo ""

# Verificar se túnel já existe
if cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
    echo "⚠️  Túnel '$TUNNEL_NAME' já existe"
    read -p "Deseja deletar e recriar? (s/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
        cloudflared tunnel delete "$TUNNEL_ID" 2>/dev/null || true
        echo "🗑️  Túnel antigo removido"
    else
        echo "Usando túnel existente..."
    fi
fi

echo ""
echo "📝 Passo 2: Criando túnel '$TUNNEL_NAME'..."
cloudflared tunnel create "$TUNNEL_NAME"

# Obter ID do túnel
TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
CREDENTIALS_FILE="$CONFIG_DIR/${TUNNEL_ID}.json"

if [ ! -f "$CREDENTIALS_FILE" ]; then
    echo "❌ Erro ao criar túnel"
    exit 1
fi

echo "✅ Túnel criado: $TUNNEL_ID"
echo ""

# Criar arquivo de configuração
echo "📝 Passo 3: Configurando túnel..."
cat > "$CONFIG_DIR/config.yml" << EOF
tunnel: $TUNNEL_ID
credentials-file: $CREDENTIALS_FILE

ingress:
  - hostname: egsys-monitor.trycloudflare.com
    service: http://localhost:5000
  - service: http_status:404
EOF

echo "✅ Configuração criada"
echo ""

# Criar script de inicialização
cat > "$INSTALL_DIR/start-tunnel.sh" << 'SCRIPT'
#!/bin/bash
cloudflared tunnel --config ~/.cloudflared/config.yml run egSYS-Monitor
SCRIPT

chmod +x "$INSTALL_DIR/start-tunnel.sh"

# Criar serviço systemd
echo "📝 Passo 4: Criando serviço systemd..."
sudo tee /etc/systemd/system/egsys-tunnel.service > /dev/null << EOF
[Unit]
Description=egSYS Monitor - Cloudflare Tunnel
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/bin/cloudflared tunnel --config $CONFIG_DIR/config.yml run $TUNNEL_NAME
Restart=always
RestartSec=5
StandardOutput=append:$INSTALL_DIR/logs/tunnel.log
StandardError=append:$INSTALL_DIR/logs/tunnel-error.log

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable egsys-tunnel.service
sudo systemctl start egsys-tunnel.service

echo "✅ Serviço criado e iniciado"
echo ""

# Aguardar inicialização
echo "⏳ Aguardando túnel inicializar..."
sleep 5

# Obter URL do túnel
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo ""
echo "🌐 URL Pública (Temporária):"
echo "   https://egsys-monitor.trycloudflare.com"
echo ""
echo "📝 Para URL personalizada permanente:"
echo "   1. Acesse: https://dash.cloudflare.com"
echo "   2. Vá em: Zero Trust > Access > Tunnels"
echo "   3. Configure domínio personalizado"
echo ""
echo "🔐 Credenciais:"
echo "   Usuário: lucasserafim"
echo "   Senha: Rune89Lukas@#$"
echo ""
echo "📊 Comandos úteis:"
echo "   sudo systemctl status egsys-tunnel    # Ver status"
echo "   sudo systemctl restart egsys-tunnel   # Reiniciar"
echo "   sudo systemctl stop egsys-tunnel      # Parar"
echo "   tail -f ~/.egsys-monitor/logs/tunnel.log  # Ver logs"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
