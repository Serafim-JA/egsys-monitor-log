#!/bin/bash
# Script para criar executável do egSYS Monitor

echo "🔨 Criando executável do egSYS Monitor..."
echo ""

# Instalar dependências
echo "📦 Instalando dependências..."
pip3 install --user PyQt5 pyinstaller paramiko python-dotenv bcrypt

# Criar executável
echo ""
echo "🏗️  Gerando executável..."
cd "$(dirname "$0")/.."

pyinstaller --name="egSYS-Monitor" \
    --windowed \
    --onefile \
    --icon=docs/icon.png \
    --add-data="config:config" \
    --hidden-import=PyQt5 \
    --hidden-import=paramiko \
    --hidden-import=bcrypt \
    src/desktop_app.py

echo ""
echo "✅ Executável criado!"
echo ""
echo "📍 Localização:"
echo "   dist/egSYS-Monitor"
echo ""
echo "💡 Para executar:"
echo "   ./dist/egSYS-Monitor"
echo ""
echo "📦 Para distribuir:"
echo "   Copie o arquivo dist/egSYS-Monitor para qualquer máquina"
