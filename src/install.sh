#!/bin/bash

# Cores
GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

echo "=========================================="
echo "   INSTALADOR DO MONITOR EGSYS"
echo "=========================================="

# 1. Dependências
echo "[*] Verificando dependências..."
if ! command -v git &> /dev/null; then
    echo "Instalando git..."
    sudo apt update && sudo apt install -y git
fi

if ! command -v sshpass &> /dev/null; then
    echo "Instalando sshpass..."
    sudo apt install -y sshpass
fi

# 2. Definição do diretório
INSTALL_DIR="$HOME/egsys-monitor"

# Se o script está rodando da pasta clonada, usamos ela
if [ -f "run_monitor.sh" ]; then
    CURRENT_DIR=$(pwd)
    echo "[*] Configurando instalação na pasta atual: $CURRENT_DIR"
    chmod +x "$CURRENT_DIR/run_monitor.sh"
    TARGET_SCRIPT="$CURRENT_DIR/run_monitor.sh"
else
    echo "${RED}[ERRO] Arquivo monitor.sh não encontrado.${NC}"
    echo "Rode este instalador dentro da pasta do projeto."
    exit 1
fi

# 3. Cria atalho (Alias)
BASHRC="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then BASHRC="$HOME/.zshrc"; fi

if ! grep -q "alias egsys=" "$BASHRC"; then
    echo "[*] Criando atalho 'egsys'..."
    echo "" >> "$BASHRC"
    echo "# Atalho egSYS Monitor" >> "$BASHRC"
    echo "alias egsys='$TARGET_SCRIPT'" >> "$BASHRC"
    echo "${GREEN}✔ Atalho criado com sucesso!${NC}"
else
    echo "[*] Atalho 'egsys' já existe."
fi

echo ""
echo "=========================================="
echo "   INSTALAÇÃO CONCLUÍDA!"
echo "=========================================="
echo "Para usar, feche este terminal e abra outro, ou digite:"
echo "source $BASHRC"
echo ""
echo "Depois, basta rodar o comando: egsys"
echo "=========================================="