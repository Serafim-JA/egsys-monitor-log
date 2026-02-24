#!/bin/bash

# Adicionar alias para túnel Cloudflare

BASHRC="$HOME/.bashrc"

# Verificar se alias já existe
if grep -q "alias egsys-tunnel-setup" "$BASHRC" 2>/dev/null; then
    echo "✅ Alias já configurado"
else
    echo "" >> "$BASHRC"
    echo "# egSYS Monitor - Cloudflare Tunnel" >> "$BASHRC"
    echo "alias egsys-tunnel-setup='bash ~/Área\ de\ Trabalho/egsys-monitor/scripts/setup-cloudflare.sh'" >> "$BASHRC"
    echo "alias egsys-tunnel-status='sudo systemctl status egsys-tunnel'" >> "$BASHRC"
    echo "alias egsys-tunnel-restart='sudo systemctl restart egsys-tunnel'" >> "$BASHRC"
    echo "alias egsys-tunnel-logs='tail -f ~/.egsys-monitor/logs/tunnel.log'" >> "$BASHRC"
    
    echo "✅ Aliases adicionados ao ~/.bashrc"
    echo ""
    echo "Execute: source ~/.bashrc"
    echo ""
    echo "Comandos disponíveis:"
    echo "  egsys-tunnel-setup    - Configurar túnel"
    echo "  egsys-tunnel-status   - Ver status"
    echo "  egsys-tunnel-restart  - Reiniciar"
    echo "  egsys-tunnel-logs     - Ver logs"
fi
