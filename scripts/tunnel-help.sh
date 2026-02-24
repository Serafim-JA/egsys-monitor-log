#!/bin/bash

cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              egSYS Monitor - Túnel Cloudflare                ║
║                  Configuração Permanente                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 INSTALAÇÃO EM 3 PASSOS:

┌──────────────────────────────────────────────────────────────┐
│ 1. Executar Setup                                            │
└──────────────────────────────────────────────────────────────┘

   bash ~/Área\ de\ Trabalho/egsys-monitor/scripts/setup-cloudflare.sh

   ⚠️  Isso abrirá seu navegador para login no Cloudflare
   ⚠️  Crie uma conta gratuita se não tiver


┌──────────────────────────────────────────────────────────────┐
│ 2. Aguardar Configuração                                     │
└──────────────────────────────────────────────────────────────┘

   O script irá:
   ✓ Autenticar com Cloudflare
   ✓ Criar túnel "egSYS-Monitor"
   ✓ Configurar serviço systemd
   ✓ Iniciar túnel automaticamente


┌──────────────────────────────────────────────────────────────┐
│ 3. Acessar Dashboard                                         │
└──────────────────────────────────────────────────────────────┘

   URL gerada automaticamente:
   https://egsys-monitor.trycloudflare.com

   Credenciais:
   Usuário: lucasserafim
   Senha: Rune89Lukas@#$


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 COMANDOS ÚTEIS:

   source ~/.bashrc                  # Carregar aliases

   egsys-tunnel-setup               # Configurar túnel
   egsys-tunnel-status              # Ver status
   egsys-tunnel-restart             # Reiniciar
   egsys-tunnel-logs                # Ver logs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ VANTAGENS:

   ✅ Permanente - Não expira
   ✅ Automático - Inicia com o sistema
   ✅ Seguro - HTTPS automático
   ✅ Gratuito - Sem custos
   ✅ Confiável - Reconecta automaticamente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DOCUMENTAÇÃO COMPLETA:

   ~/Área de Trabalho/egsys-monitor/docs/CLOUDFLARE_TUNNEL.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 PRONTO PARA COMEÇAR?

   Execute agora:
   bash ~/Área\ de\ Trabalho/egsys-monitor/scripts/setup-cloudflare.sh

EOF
