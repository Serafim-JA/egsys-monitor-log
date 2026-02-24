#!/bin/bash

# egSYS Monitor - Desktop App Launcher
# Instala dependências e executa aplicativo desktop

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 egSYS Monitor - Desktop App"
echo ""

# Verificar se PyQt5 está instalado
if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "📦 Instalando PyQt5..."
    
    # Tentar instalar via apt (recomendado para ambientes gerenciados)
    if command -v apt &> /dev/null; then
        echo "   Usando apt (requer sudo)..."
        sudo apt update -qq
        sudo apt install -y python3-pyqt5 python3-pyqt5.qtsvg
    else
        echo "   Usando pip com --break-system-packages..."
        pip3 install --break-system-packages PyQt5
    fi
    
    echo "✓ PyQt5 instalado"
    echo ""
fi

# Executar aplicativo
echo "🖥️  Iniciando aplicativo desktop..."
cd "$PROJECT_DIR"
python3 src/desktop_app.py

exit 0
