# egSYS Monitor - Aplicativo Desktop

## 🖥️ Visão Geral

Aplicativo desktop standalone do egSYS Monitor com interface gráfica completa, funcionando como Discord, Slack ou qualquer aplicativo moderno.

## ✨ Características

### Interface Gráfica Completa
- 🔐 **Tela de Login** - Autenticação visual com validação
- 📊 **Monitor de Logs** - Visualização em tempo real
- ⚙️ **Configurações** - Gerenciamento de servidores
- 👥 **Usuários** - CRUD completo (apenas admin)
- ℹ️ **Sobre** - Informações do sistema

### Funcionalidades
- ✅ Login com credenciais do dashboard
- ✅ Seleção visual de cliente/servidor/aplicação/log
- ✅ Conexão SSH automática
- ✅ Visualização de logs em tempo real
- ✅ Gerenciamento de configurações
- ✅ Gerenciamento de usuários (admin)
- ✅ Interface moderna e responsiva
- ✅ Tema escuro profissional

## 📦 Instalação

### Método 1: Executável Pronto (Recomendado)

```bash
# Baixar executável
wget https://github.com/Serafim-JA/egsys-monitor-log/releases/latest/download/egSYS-Monitor

# Tornar executável
chmod +x egSYS-Monitor

# Executar
./egSYS-Monitor
```

### Método 2: Construir do Código Fonte

```bash
# Clonar repositório
git clone https://github.com/Serafim-JA/egsys-monitor-log.git
cd egsys-monitor-log

# Construir executável
bash scripts/build-desktop.sh

# Executar
./dist/egSYS-Monitor
```

### Método 3: Executar Diretamente (Desenvolvimento)

```bash
# Instalar dependências
pip3 install --user PyQt5 paramiko python-dotenv bcrypt

# Executar
python3 src/desktop_app.py
```

## 🚀 Uso

### 1. Login
- Abra o aplicativo
- Digite seu usuário e senha (mesmas do dashboard web)
- Clique em "Entrar"

### 2. Monitor de Logs
- Selecione Cliente, Servidor, Aplicação e Log
- Clique em "🔌 Conectar"
- Visualize logs em tempo real
- Clique em "⏹️ Parar" para desconectar

### 3. Configurações
- Adicione novos servidores
- Edite configurações existentes
- Remova servidores não utilizados

### 4. Usuários (Admin)
- Visualize todos os usuários
- Adicione novos usuários
- Edite permissões
- Remova usuários

## 🎨 Interface

### Tela de Login
```
┌─────────────────────────────────┐
│       egSYS Monitor             │
│  Sistema de Monitoramento       │
│                                 │
│  👤 Usuário: [_____________]    │
│  🔑 Senha:   [_____________]    │
│                                 │
│         [ Entrar ]              │
└─────────────────────────────────┘
```

### Tela Principal
```
┌────────────────────────────────────────────────┐
│ egSYS Monitor          👤 Nome (role)  [Sair] │
├────────────────────────────────────────────────┤
│ [📊 Monitor] [⚙️ Config] [👥 Users] [ℹ️ Sobre] │
├────────────────────────────────────────────────┤
│ Cliente: [▼] Server: [▼] App: [▼] Log: [▼]   │
│ [🔌 Conectar] [⏹️ Parar]                       │
├────────────────────────────────────────────────┤
│                                                │
│  [12:34:56] Conectando ao servidor...         │
│  [12:34:57] ✅ Conectado                       │
│  [12:34:58] INFO: Sistema iniciado            │
│  [12:34:59] DEBUG: Processando requisição     │
│                                                │
├────────────────────────────────────────────────┤
│ Status: Conectado ✅                           │
└────────────────────────────────────────────────┘
```

## 🔧 Requisitos

### Sistema
- Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- macOS 10.15+
- Windows 10+ (via WSL ou nativo)

### Software
- Python 3.8+
- PyQt5
- Paramiko
- bcrypt
- python-dotenv

### Hardware
- CPU: 2 cores
- RAM: 2GB
- Disco: 100MB

## 📝 Configuração

### Primeira Execução

1. O aplicativo procura configurações em `~/.egsys-monitor/`
2. Se não encontrar, solicita configuração inicial
3. Conecta-se ao servidor de configuração (se disponível)
4. Ou permite configuração manual

### Arquivos de Configuração

```
~/.egsys-monitor/
├── config/
│   ├── config.json              # Estrutura de logs
│   └── authorized_keys.json     # Usuários
├── logs/
│   └── app.log                  # Logs do aplicativo
└── .env                         # Credenciais SSH
```

## 🎯 Atalhos de Teclado

- `Ctrl+L` - Focar no campo de login
- `Ctrl+Q` - Sair do aplicativo
- `Ctrl+R` - Reconectar ao log
- `Ctrl+S` - Parar monitoramento
- `Ctrl+,` - Abrir configurações
- `F5` - Atualizar lista de logs

## 🔐 Segurança

- ✅ Senhas nunca são armazenadas em texto plano
- ✅ Hash bcrypt para autenticação
- ✅ Conexões SSH criptografadas
- ✅ Logs de acesso completos
- ✅ Timeout automático de sessão

## 🐛 Troubleshooting

### Aplicativo não inicia
```bash
# Verificar dependências
pip3 list | grep -E "PyQt5|paramiko|bcrypt"

# Reinstalar
pip3 install --user --force-reinstall PyQt5
```

### Erro de conexão SSH
- Verificar VPN está ativa
- Verificar credenciais no .env
- Verificar firewall

### Interface não aparece
```bash
# Verificar display
echo $DISPLAY

# Executar com debug
python3 src/desktop_app.py --debug
```

## 📦 Distribuição

### Criar Executável Standalone

```bash
# Gerar executável
bash scripts/build-desktop.sh

# Resultado em:
dist/egSYS-Monitor
```

### Distribuir para Usuários

1. Copie o executável `dist/egSYS-Monitor`
2. Envie para usuários
3. Usuários apenas executam: `./egSYS-Monitor`
4. Não precisa instalar Python ou dependências!

## 🚀 Roadmap

### Versão 1.1
- [ ] Notificações desktop
- [ ] Múltiplas abas de logs
- [ ] Filtros avançados
- [ ] Exportar logs

### Versão 1.2
- [ ] Gráficos de métricas
- [ ] Alertas customizados
- [ ] Temas personalizáveis
- [ ] Suporte a plugins

### Versão 2.0
- [ ] Modo offline
- [ ] Sincronização em nuvem
- [ ] Mobile app
- [ ] Integração com Slack/Teams

## 📞 Suporte

- GitHub Issues: https://github.com/Serafim-JA/egsys-monitor-log/issues
- Email: serafim@egsys.com.br
- Documentação: https://github.com/Serafim-JA/egsys-monitor-log/wiki

## 📄 Licença

MIT License - Veja [LICENSE](../LICENSE)

---

**Desenvolvido com ❤️ por Serafim para a comunidade egSYS**
