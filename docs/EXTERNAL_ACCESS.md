# egSYS Monitor - Guia de Acesso Externo

## ✅ Dashboard Configurado

O dashboard está configurado para aceitar conexões de qualquer IP (`0.0.0.0:5000`).

## 🌐 Formas de Acesso

### 1. Acesso Local (mesma máquina)
```
http://localhost:5000
http://127.0.0.1:5000
```

### 2. Acesso na Rede Local (LAN)
```
http://192.168.2.55:5000
```
Outros dispositivos na mesma rede Wi-Fi/Ethernet podem acessar usando o IP acima.

### 3. Acesso via Internet (Requer Configuração)

#### Opção A: Ngrok (Mais Fácil - Túnel Temporário)
```bash
# Instalar ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Criar conta gratuita em https://ngrok.com e pegar token
ngrok config add-authtoken SEU_TOKEN_AQUI

# Criar túnel
ngrok http 5000
```
Você receberá uma URL pública tipo: `https://abc123.ngrok.io`

#### Opção B: Cloudflare Tunnel (Gratuito e Permanente)
```bash
# Instalar cloudflared
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Autenticar (abre navegador)
cloudflared tunnel login

# Criar túnel
cloudflared tunnel create egsys-monitor

# Configurar
cat > ~/.cloudflared/config.yml << EOF
tunnel: egsys-monitor
credentials-file: /home/lucasserafim/.cloudflared/TUNNEL_ID.json

ingress:
  - hostname: egsys-monitor.seu-dominio.com
    service: http://localhost:5000
  - service: http_status:404
EOF

# Iniciar túnel
cloudflared tunnel run egsys-monitor
```

#### Opção C: Port Forwarding no Roteador (Permanente)
1. Acesse o painel do seu roteador (geralmente `192.168.1.1` ou `192.168.0.1`)
2. Procure por "Port Forwarding" ou "Redirecionamento de Portas"
3. Adicione regra:
   - Porta Externa: `5000`
   - IP Interno: `192.168.2.55`
   - Porta Interna: `5000`
   - Protocolo: `TCP`
4. Acesse via IP público: `http://SEU_IP_PUBLICO:5000`
   - Descubra seu IP público em: https://meuip.com.br

#### Opção D: VPS/Cloud (Produção)
Deploy em servidor cloud (AWS, DigitalOcean, etc):
```bash
# No servidor remoto
git clone https://github.com/Serafim-JA/egsys-monitor-log.git
cd egsys-monitor-log
bash install.sh

# Configurar Nginx como proxy reverso
sudo apt install nginx
sudo nano /etc/nginx/sites-available/egsys-monitor

# Adicionar:
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

sudo ln -s /etc/nginx/sites-available/egsys-monitor /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Adicionar SSL (HTTPS)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

## 🔒 Segurança

### Firewall (Recomendado para Produção)
```bash
# Permitir apenas IPs específicos
sudo ufw allow from 192.168.2.0/24 to any port 5000

# Ou permitir todos (menos seguro)
sudo ufw allow 5000/tcp
```

### Autenticação
O dashboard já possui autenticação integrada:
- **Usuário:** lucasserafim
- **Senha:** Rune89Lukas@#$

### HTTPS
Para produção, sempre use HTTPS (Cloudflare Tunnel ou Certbot).

## 📊 Monitoramento

### Ver logs em tempo real
```bash
tail -f ~/.egsys-monitor/logs/access.log
tail -f ~/.egsys-monitor/logs/error.log
```

### Verificar status
```bash
ps aux | grep gunicorn
lsof -i :5000
```

### Reiniciar
```bash
bash ~/.egsys-monitor/restart-dashboard.sh
```

## 🎯 Recomendação

**Para uso pessoal/desenvolvimento:** Acesso via rede local (192.168.2.55:5000)

**Para compartilhar temporariamente:** Ngrok

**Para produção:** VPS com Nginx + SSL
