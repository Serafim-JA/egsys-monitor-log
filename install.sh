#!/bin/bash
# egSYS Monitor - Instalador Universal
# Detecta automaticamente o sistema operacional e instala dependências

set -e

REPO_URL="https://github.com/Serafim-JA/egsys-monitor-log.git"
INSTALL_DIR="$HOME/.egsys-monitor"
VERSION_FILE="$INSTALL_DIR/VERSION"

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        OS="rhel"
    elif [ "$(uname)" = "Darwin" ]; then
        OS="macos"
    else
        OS="unknown"
    fi
    echo "$OS"
}

install_dependencies() {
    local os=$(detect_os)
    echo "🔍 Sistema detectado: $os"
    
    case "$os" in
        ubuntu|debian|linuxmint|pop)
            sudo apt update
            sudo apt install -y git python3 python3-pip openssh-client curl
            ;;
        fedora|rhel|centos)
            sudo dnf install -y git python3 python3-pip openssh-clients curl || \
            sudo yum install -y git python3 python3-pip openssh-clients curl
            ;;
        arch|manjaro)
            sudo pacman -Sy --noconfirm git python python-pip openssh curl
            ;;
        opensuse*)
            sudo zypper install -y git python3 python3-pip openssh curl
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                echo "❌ Homebrew não encontrado. Instale: https://brew.sh"
                exit 1
            fi
            brew install git python openssh curl
            ;;
        *)
            echo "❌ Sistema não suportado: $os"
            exit 1
            ;;
    esac
}

install_python_deps() {
    echo "📦 Instalando dependências Python..."
    pip3 install --user --upgrade pip
    pip3 install --user paramiko python-dotenv rich reportlab flask flask-login bcrypt psutil gunicorn requests
}

clone_or_update() {
    if [ -d "$INSTALL_DIR/.git" ]; then
        echo "🔄 Atualizando repositório..."
        cd "$INSTALL_DIR"
        git fetch origin
        git reset --hard origin/main
    else
        echo "📥 Clonando repositório..."
        rm -rf "$INSTALL_DIR"
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
}

setup_config() {
    if [ ! -f "$INSTALL_DIR/.env" ]; then
        echo "⚙️  Criando arquivo .env..."
        cat > "$INSTALL_DIR/.env" << 'EOF'
# Configurações SSH - Adicione suas credenciais aqui
# Exemplo:
# USER_SERVIDOR1=usuario
# HOST_SERVIDOR1=192.168.1.100
# PASSWORD_SERVIDOR1='senha123'
EOF
        echo "⚠️  Configure o arquivo: $INSTALL_DIR/.env"
    fi
    
    mkdir -p "$INSTALL_DIR/logs" "$INSTALL_DIR/config"
    
    if [ ! -f "$INSTALL_DIR/config/authorized_keys.json" ]; then
        echo '{"users":[]}' > "$INSTALL_DIR/config/authorized_keys.json"
    fi
}

create_launcher() {
    local launcher="$HOME/.local/bin/egsys-monitor"
    mkdir -p "$HOME/.local/bin"
    
    cat > "$launcher" << 'EOF'
#!/bin/bash
INSTALL_DIR="$HOME/.egsys-monitor"
cd "$INSTALL_DIR" && bash "$INSTALL_DIR/src/run_monitor.sh"
EOF
    
    chmod +x "$launcher"
    
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        echo "⚠️  Execute: source ~/.bashrc"
    fi
}

echo "╔════════════════════════════════════════╗"
echo "║   egSYS Monitor - Instalador v1.0     ║"
echo "╚════════════════════════════════════════╝"
echo ""

install_dependencies
install_python_deps
clone_or_update
setup_config
create_launcher

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Configure: $INSTALL_DIR/.env"
echo "   2. Execute: egsys-monitor"
echo "   3. Dashboard: bash $INSTALL_DIR/restart-dashboard.sh"
echo ""
