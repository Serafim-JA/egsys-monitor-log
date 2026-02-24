# egSYS Monitor - Cloudflare Tunnel

## 🚀 Instalação Rápida

```bash
bash ~/Área\ de\ Trabalho/egsys-monitor/scripts/setup-cloudflare.sh
```

O script irá:
1. ✅ Autenticar com Cloudflare (abre navegador)
2. ✅ Criar túnel nomeado "egSYS-Monitor"
3. ✅ Configurar serviço systemd (inicia automaticamente)
4. ✅ Gerar URL pública permanente

## 🌐 Acesso

### URL Temporária (trycloudflare.com)
```
https://egsys-monitor.trycloudflare.com
```

### URL Personalizada (Requer domínio próprio)
1. Acesse: https://dash.cloudflare.com
2. Vá em: **Zero Trust** > **Access** > **Tunnels**
3. Selecione túnel "egSYS-Monitor"
4. Configure: `monitor.seu-dominio.com` → `http://localhost:5000`

## 🔧 Gerenciamento

### Ver Status
```bash
sudo systemctl status egsys-tunnel
```

### Reiniciar
```bash
sudo systemctl restart egsys-tunnel
```

### Parar
```bash
sudo systemctl stop egsys-tunnel
```

### Iniciar
```bash
sudo systemctl start egsys-tunnel
```

### Ver Logs
```bash
# Logs em tempo real
tail -f ~/.egsys-monitor/logs/tunnel.log

# Últimas 50 linhas
tail -50 ~/.egsys-monitor/logs/tunnel.log
```

### Desabilitar Inicialização Automática
```bash
sudo systemctl disable egsys-tunnel
```

### Habilitar Inicialização Automática
```bash
sudo systemctl enable egsys-tunnel
```

## 🔐 Segurança

### Credenciais de Acesso
```
Usuário: lucasserafim
Senha: Rune89Lukas@#$
```

### Proteção Adicional (Opcional)

#### 1. Cloudflare Access (Autenticação Extra)
```bash
# No dashboard Cloudflare:
# Zero Trust > Access > Applications > Add an application
# Configurar autenticação por email, Google, etc.
```

#### 2. IP Whitelist
```bash
# Permitir apenas IPs específicos no Cloudflare
# Zero Trust > Gateway > Firewall Policies
```

## 📊 Monitoramento

### Métricas do Túnel
```bash
# Acessar métricas locais
curl http://127.0.0.1:20241/metrics
```

### Dashboard Cloudflare
```
https://dash.cloudflare.com
Zero Trust > Analytics
```

## 🆘 Troubleshooting

### Túnel não inicia
```bash
# Ver logs de erro
sudo journalctl -u egsys-tunnel -n 50

# Verificar configuração
cloudflared tunnel info egSYS-Monitor

# Testar manualmente
cloudflared tunnel --config ~/.cloudflared/config.yml run egSYS-Monitor
```

### URL não funciona
```bash
# Verificar se túnel está rodando
ps aux | grep cloudflared

# Verificar se dashboard está rodando
ps aux | grep gunicorn

# Reiniciar ambos
sudo systemctl restart egsys-tunnel
bash ~/.egsys-monitor/restart-dashboard.sh
```

### Recriar túnel
```bash
# Parar serviço
sudo systemctl stop egsys-tunnel

# Deletar túnel antigo
cloudflared tunnel delete egSYS-Monitor

# Executar setup novamente
bash ~/Área\ de\ Trabalho/egsys-monitor/scripts/setup-cloudflare.sh
```

## 🎯 Vantagens

✅ **Permanente** - Túnel nomeado não expira  
✅ **Automático** - Inicia com o sistema (systemd)  
✅ **Seguro** - HTTPS automático, sem expor portas  
✅ **Gratuito** - Sem custos para uso pessoal  
✅ **Confiável** - Reconecta automaticamente se cair  

## 📝 Notas

- **trycloudflare.com**: URL temporária, pode mudar se recriar túnel
- **Domínio próprio**: Requer conta Cloudflare e domínio registrado
- **Systemd**: Túnel inicia automaticamente ao ligar o computador
- **Logs**: Salvos em `~/.egsys-monitor/logs/tunnel.log`
