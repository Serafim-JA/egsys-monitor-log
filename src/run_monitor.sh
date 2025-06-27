#!/bin/bash

# --- Função para verificar e instalar dependências ---
install_dependencies() {
    # Suprime a saída padrão e de erro da instalação e verificação
    # Apenas mensagens de erro crítico serão impressas diretamente.
    echo "Verificando e instalando dependências (em segundo plano)..."

    # Verificar se python3 e pip3 estão instalados
    if ! command -v python3 &> /dev/null; then
        echo "Python 3 não encontrado. Tentando instalar..."
        if command -v apt &> /dev/null; then
            sudo apt update &> /dev/null
            sudo apt install -y python3 python3-pip openssh-client &> /dev/null
        elif command -v yum &> /dev/null; then
            sudo yum check-update &> /dev/null
            sudo yum install -y python3 python3-pip openssh-client &> /dev/null
        elif command -v dnf &> /dev/null; then
            sudo dnf check-update &> /dev/null
            sudo dnf install -y python3 python3-pip openssh-client &> /dev/null
        elif command -v pacman &> /dev/null; then
            sudo pacman -Sy --noconfirm python python-pip openssh &> /dev/null
        else
            echo "Gerenciador de pacotes não suportado. Por favor, instale python3, python3-pip e openssh-client manualmente." >&2
            return 1 # Retorna erro
        fi
        if [ $? -ne 0 ]; then
            echo "Erro ao instalar Python 3. Verifique as permissões ou a conexão." >&2
            return 1
        fi
    fi

    # Instalar módulos Python via pip
    pip_install_cmd="pip3 install paramiko python-dotenv rich"
    
    # Suprime a saída, apenas erros serão visíveis
    $pip_install_cmd &> /dev/null
    if [ $? -ne 0 ]; then
        echo "Erro ao instalar módulos Python. Tente executar 'sudo $pip_install_cmd'." >&2
        return 1
    fi
    echo "Dependências verificadas."
    return 0 # Retorna sucesso
}

# --- Função para verificar a conexão VPN ---
check_vpn_connection() {
    echo "Verificando conexão VPN..."
    # Suprime a saída do grep se a VPN for detectada
    if ip link show | grep -q "tun"; then
        echo "Interface VPN (tun) detectada. Assumindo VPN conectada."
        return 0
    fi

    echo "VPN não conectada. Por favor, conecte-se à VPN antes de continuar." >&2
    return 1
}

# --- Execução Principal ---

# Limpa a tela para um início limpo
clear

# Mensagem de início do sistema
echo -e "\n\033[1;36m=========================================\033[0m"
echo -e "\033[1;36m|          INICIANDO SISTEMA          |\033[0m"
echo -e "\033[1;36m=========================================\033[0m"
echo "" # Linha em branco

# Executa as verificações e instalações
if ! install_dependencies; then
    echo -e "\n\033[1;31mFALHA: Erro na instalação de dependências. Encerrando.\033[0m"
    exit 1
fi

if ! check_vpn_connection; then
    echo -e "\n\033[1;31mFALHA: Verificação de VPN. Encerrando.\033[0m"
    exit 1
fi

# Limpa a tela novamente antes de iniciar o script Python para uma interface limpa
clear

# Inicia o script Python
echo -e "\n\033[1;32mIniciando o monitor de logs...\033[0m"
# Garante que o script python seja chamado com o caminho correto
python3 "$(dirname "$0")/log_monitor.py"