#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/config/config.json"
ENV_FILE="$PROJECT_ROOT/.env"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"

install_dependencies() {
    echo "Verificando dependências..."

    if ! command -v python3 &> /dev/null; then
        echo "Python 3 não encontrado. Instalando..."
        if command -v apt &> /dev/null; then
            sudo apt update && sudo apt install -y python3 python3-pip openssh-client
        elif command -v yum &> /dev/null; then
            sudo yum check-update && sudo yum install -y python3 python3-pip openssh-clients
        elif command -v dnf &> /dev/null; then
            sudo dnf check-update && sudo dnf install -y python3 python3-pip openssh-clients
        elif command -v pacman &> /dev/null; then
            sudo pacman -Sy --noconfirm python python-pip openssh
        else
            echo "ERRO: Gerenciador de pacotes não suportado." >&2
            echo "Instale manualmente: python3, python3-pip, openssh-client" >&2
            return 1
        fi
    fi

    if ! command -v pip3 &> /dev/null; then
        echo "ERRO: pip3 não encontrado após instalação do Python." >&2
        return 1
    fi

    echo "Verificando módulos Python..."
    python3 -c "import paramiko, dotenv, rich, reportlab" 2>/dev/null && {
        echo "Módulos Python já instalados."
        return 0
    }

    echo "Instalando módulos Python..."
    pip3 install --break-system-packages paramiko python-dotenv rich reportlab 2>/dev/null || \
    pip3 install --user paramiko python-dotenv rich reportlab 2>/dev/null || {
        echo "ERRO: Falha ao instalar dependências Python." >&2
        echo "Execute manualmente: pip3 install --break-system-packages paramiko python-dotenv rich reportlab" >&2
        return 1
    }

    echo "Dependências instaladas com sucesso."
    return 0
}

check_vpn_connection() {
    echo "Verificando conexão VPN..."
    
    if ip link show 2>/dev/null | grep -qE "tun[0-9]+|tap[0-9]+"; then
        echo "Interface VPN detectada."
        return 0
    fi
    
    if ip addr show 2>/dev/null | grep -qE "10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.|192\.168\."; then
        echo "Rede privada detectada. Assumindo VPN conectada."
        return 0
    fi

    echo "AVISO: VPN não detectada. Continuando mesmo assim..." >&2
    read -p "Pressione Enter para continuar ou Ctrl+C para cancelar..."
    return 0
}

validate_ssh_auth() {
    echo "Verificando autenticação SSH..."
    
    if [ ! -d "$HOME/.ssh" ]; then
        echo "ERRO: Diretório .ssh não encontrado." >&2
        echo "Execute: ssh-keygen -t rsa -b 4096" >&2
        return 1
    fi
    
    SSH_KEY_FOUND=false
    for key_file in "$HOME/.ssh/id_rsa.pub" "$HOME/.ssh/id_ed25519.pub" "$HOME/.ssh/id_ecdsa.pub"; do
        if [ -f "$key_file" ]; then
            SSH_KEY_FOUND=true
            break
        fi
    done
    
    if [ "$SSH_KEY_FOUND" = false ]; then
        echo "ERRO: Nenhuma chave SSH pública encontrada." >&2
        echo "Execute: ssh-keygen -t rsa -b 4096" >&2
        return 1
    fi
    
    echo "Chave SSH encontrada."
    return 0
}

validate_files() {
    echo "Validando arquivos de configuração..."

    if [ ! -f "$CONFIG_FILE" ]; then
        echo "ERRO: Arquivo config.json não encontrado em: $CONFIG_FILE" >&2
        return 1
    fi

    if ! python3 -c "import json; json.load(open('$CONFIG_FILE'))" 2>/dev/null; then
        echo "ERRO: config.json contém JSON inválido." >&2
        return 1
    fi

    if [ ! -f "$ENV_FILE" ]; then
        echo "AVISO: Arquivo .env não encontrado em: $ENV_FILE" >&2
        echo "Crie o arquivo .env com as credenciais SSH." >&2
        return 1
    fi

    if [ ! -r "$ENV_FILE" ]; then
        echo "ERRO: Sem permissão de leitura para .env" >&2
        return 1
    fi

    echo "Arquivos validados com sucesso."
    return 0
}

clear

echo -e "\n\033[1;36m=========================================\033[0m"
echo -e "\033[1;36m|          INICIANDO SISTEMA          |\033[0m"
echo -e "\033[1;36m=========================================\033[0m\n"

if ! install_dependencies; then
    echo -e "\n\033[1;31mFALHA: Erro na instalação de dependências.\033[0m"
    exit 1
fi

if ! validate_files; then
    echo -e "\n\033[1;31mFALHA: Validação de arquivos.\033[0m"
    exit 1
fi

if ! validate_ssh_auth; then
    echo -e "\n\033[1;31mFALHA: Autenticação SSH.\033[0m"
    exit 1
fi

if ! check_vpn_connection; then
    echo -e "\n\033[1;33mAVISO: Verificação de VPN falhou.\033[0m"
fi

clear

echo -e "\n\033[1;32mIniciando o monitor de logs...\033[0m\n"

cd "$SCRIPT_DIR" || exit 1

if ! python3 "$SCRIPT_DIR/auth_wrapper.py"; then
    echo -e "\n\033[1;31mERRO: O monitor de logs encerrou com erro.\033[0m"
    exit 1
fi
