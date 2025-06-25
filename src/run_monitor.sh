#!/bin/bash

# --- Função para verificar e instalar dependências ---
install_dependencies() {
    echo "Verificando e instalando dependências..."

    # Verificar se python3 e pip3 estão instalados
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 não encontrado. Instalando..."
        # Detectar o gerenciador de pacotes e instalar python3
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3 python3-pip openssh-client
        elif command -v yum &> /dev/null; then
            sudo yum check-update
            sudo yum install -y python3 python3-pip openssh-client
        elif command -v dnf &> /dev/null; then
            sudo dnf check-update
            sudo dnf install -y python3 python3-pip openssh-client
        elif command -v pacman &> /dev/null; then
            sudo pacman -Sy --noconfirm python python-pip openssh
        else
            echo "Gerenciador de pacotes não suportado. Por favor, instale python3, python3-pip e openssh-client manualmente."
            exit 1
        fi
    fi

    # Verificar se paramiko e python-dotenv estão instalados
    if ! python3 -c "import paramiko" &> /dev/null; then
        echo "Módulo paramiko não encontrado. Instalando..."
        pip3 install paramiko
        if [ $? -ne 0 ]; then
            echo "Erro ao instalar paramiko. Tente executar 'sudo pip3 install paramiko'."
            exit 1
        fi
    fi

    if ! python3 -c "import dotenv" &> /dev/null; then
        echo "Módulo python-dotenv não encontrado. Instalando..."
        pip3 install python-dotenv
        if [ $? -ne 0 ]; then
            echo "Erro ao instalar python-dotenv. Tente executar 'sudo pip3 install python-dotenv'."
            exit 1
        fi
    fi
    echo "Dependências verificadas."
}

# --- Função para verificar a conexão VPN ---
check_vpn_connection() {
    echo "Verificando conexão VPN..."
    # Adapte esta parte para a sua VPN específica.
    # Exemplo genérico: Verifica se existe algum "tun" device (comum em VPNs)
    if ip link show | grep -q "tun"; then
        echo "Interface VPN (tun) detectada. Assumindo VPN conectada."
        return 0
    fi

    echo "VPN não conectada. Por favor, conecte-se à VPN antes de continuar."
    return 1
}

# --- Execução Principal ---

# 1. Instalar dependências (se necessário)
install_dependencies

# 2. Verificar conexão VPN (sem pedir senha aqui)
if ! check_vpn_connection; then
    exit 1
fi

# 3. Executar o script Python
echo "Iniciando o monitor de logs..."
python3 "$(dirname "$0")/log_monitor.py"