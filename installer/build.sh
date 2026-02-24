#!/bin/bash

# egSYS Monitor - Build Script
# Gera executável standalone usando PyInstaller

set -e

echo "🔨 egSYS Monitor - Build Executável"
echo ""

# Instalar PyInstaller via apt
echo "📦 Instalando PyInstaller..."
if ! command -v pyinstaller &> /dev/null; then
    sudo apt update -qq
    sudo apt install -y python3-pyinstaller
fi

# Criar spec file customizado
cat > egsys_installer.spec << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['egsys_installer.py'],
    pathex=[],
    binaries=[],
    datas=[('../src', 'src'), ('../config', 'config')],
    hiddenimports=['paramiko', 'dotenv', 'rich', 'flask', 'bcrypt'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='egsys-monitor-installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

# Build
echo ""
echo "🔨 Compilando executável..."
cd "$(dirname "$0")"
pyinstaller egsys_installer.spec --clean

# Verificar
if [ -f "dist/egsys-monitor-installer" ]; then
    echo ""
    echo "✅ Executável criado com sucesso!"
    echo ""
    echo "📍 Localização: $(pwd)/dist/egsys-monitor-installer"
    echo "📦 Tamanho: $(du -h dist/egsys-monitor-installer | cut -f1)"
    echo ""
    echo "🚀 Para testar:"
    echo "   ./dist/egsys-monitor-installer"
    echo ""
else
    echo "❌ Erro ao criar executável"
    exit 1
fi
