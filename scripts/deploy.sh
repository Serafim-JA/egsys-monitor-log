#!/bin/bash

set -e

echo "🚀 egSYS Monitor - Deployment Script"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker não encontrado. Instalando...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker instalado${NC}"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose não encontrado. Instalando...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose instalado${NC}"
fi

echo ""
echo -e "${BLUE}Configurando acesso remoto...${NC}"

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')

# Stop existing containers
echo -e "${YELLOW}Parando containers existentes...${NC}"
docker-compose down 2>/dev/null || true

# Kill processes on port 5000
echo -e "${YELLOW}Liberando porta 5000...${NC}"
sudo fuser -k 5000/tcp 2>/dev/null || true
sleep 2

# Build and start containers
echo -e "${BLUE}Construindo imagem Docker...${NC}"
docker-compose build

echo -e "${BLUE}Iniciando containers...${NC}"
docker-compose up -d

# Wait for container to be healthy
echo -e "${YELLOW}Aguardando container inicializar...${NC}"
sleep 10

# Check if container is running
if docker ps | grep -q egsys-monitor; then
    echo ""
    echo -e "${GREEN}✅ egSYS Monitor iniciado com sucesso!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}📍 Acesso Local:${NC}"
    echo "   http://localhost:5000"
    echo "   http://127.0.0.1:5000"
    echo ""
    echo -e "${GREEN}🌐 Acesso Remoto (mesma rede):${NC}"
    echo "   http://${LOCAL_IP}:5000"
    echo ""
    echo -e "${BLUE}📱 Acesso de qualquer dispositivo:${NC}"
    echo "   1. Conecte o dispositivo na mesma rede WiFi"
    echo "   2. Acesse: http://${LOCAL_IP}:5000"
    echo ""
    echo -e "${YELLOW}🔐 Credenciais:${NC}"
    echo "   Fornecidas pelo administrador"
    echo ""
    echo -e "${BLUE}🐳 Comandos Docker úteis:${NC}"
    echo "   docker-compose logs -f          # Ver logs"
    echo "   docker-compose restart          # Reiniciar"
    echo "   docker-compose down             # Parar"
    echo "   docker-compose up -d            # Iniciar"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Configure firewall
    echo -e "${YELLOW}Configurando firewall...${NC}"
    if command -v ufw &> /dev/null; then
        sudo ufw allow 5000/tcp 2>/dev/null || true
        echo -e "${GREEN}✓ Firewall configurado (UFW)${NC}"
    elif command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --permanent --add-port=5000/tcp 2>/dev/null || true
        sudo firewall-cmd --reload 2>/dev/null || true
        echo -e "${GREEN}✓ Firewall configurado (firewalld)${NC}"
    fi
    
else
    echo -e "${RED}❌ Erro ao iniciar container${NC}"
    echo "Logs:"
    docker-compose logs
    exit 1
fi
