#!/bin/bash

cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        egSYS Monitor - Build Executável Standalone          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🎯 GERAR EXECUTÁVEL .exec

Execute os comandos abaixo:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ Instalar PyInstaller (requer sudo):

   sudo apt update
   sudo apt install -y python3-pyinstaller

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣ Compilar executável:

   cd ~/Área\ de\ Trabalho/egsys-monitor/installer
   pyinstaller egsys_installer.spec --clean

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣ Testar executável:

   ./dist/egsys-monitor-installer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 RESULTADO:

   Executável: dist/egsys-monitor-installer
   Tamanho: ~50 MB
   Standalone: Não precisa de Python instalado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 DISTRIBUIR:

   O arquivo dist/egsys-monitor-installer pode ser copiado
   para qualquer máquina Linux e executado diretamente!

   chmod +x egsys-monitor-installer
   ./egsys-monitor-installer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
