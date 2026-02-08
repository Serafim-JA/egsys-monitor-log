# Estrutura do Projeto egSYS Monitor

```
egsys-monitor/
├── config/                      # Configurações do sistema
│   ├── config.json             # Estrutura de logs e servidores
│   ├── authorized_keys.json    # Usuários autorizados
│   ├── access_log.json         # Log de acessos
│   └── update_config.json      # Configurações de atualização
│
├── logs/                        # Logs do sistema
│   ├── access.log              # Log de acessos
│   ├── dashboard.log           # Log do dashboard
│   └── error.log               # Log de erros
│
├── src/                         # Código fonte principal
│   ├── log_monitor.py          # Monitor de logs (terminal)
│   ├── login.py                # Sistema de autenticação
│   ├── auth_wrapper.py         # Wrapper de autenticação
│   ├── auth_manager.py         # Gerenciador de autenticação
│   ├── log_auditor.py          # Auditor de logs
│   ├── auto_update.py          # Sistema de auto-atualização
│   ├── update_manager.py       # Gerenciador de updates
│   └── run_monitor.sh          # Script de execução
│
├── web/                         # Aplicação web
│   └── dashboard/              # Dashboard web
│       ├── app.py              # Aplicação Flask principal
│       ├── templates/          # Templates HTML
│       │   ├── dashboard.html  # Dashboard principal
│       │   └── login.html      # Página de login
│       └── static/             # Arquivos estáticos
│           ├── css/            # Estilos CSS
│           ├── js/             # Scripts JavaScript
│           └── images/         # Imagens
│
├── scripts/                     # Scripts de automação
│   ├── install.sh              # Instalador universal
│   ├── deploy.sh               # Script de deploy
│   ├── restart-dashboard.sh    # Reiniciar dashboard
│   ├── quick-start.sh          # Início rápido
│   ├── start.sh                # Iniciar sistema
│   ├── start-production.sh     # Iniciar em produção
│   ├── global-access.sh        # Acesso global
│   └── public-access.sh        # Acesso público
│
├── tools/                       # Ferramentas auxiliares
│   ├── update_admin.py         # Administrador de updates
│   └── update_server.py        # Servidor de updates
│
├── docs/                        # Documentação
│   ├── DOCUMENTATION.md        # Documentação completa
│   └── SECURITY.md             # Diretrizes de segurança
│
├── backup/                      # Backups e arquivos antigos
│   └── old_html/               # HTMLs antigos
│
├── .env                         # Variáveis de ambiente (não versionado)
├── .gitignore                  # Arquivos ignorados pelo Git
├── .dockerignore               # Arquivos ignorados pelo Docker
├── Dockerfile                  # Configuração Docker
├── docker-compose.yml          # Orquestração Docker
├── requirements.txt            # Dependências Python
├── VERSION                     # Versão do sistema
├── CHANGELOG.json              # Histórico de mudanças
├── README.md                   # Documentação principal
├── egsys-monitor               # Launcher principal
└── log_monitor.spec            # Especificação PyInstaller
```

## Descrição dos Diretórios

### `/config`
Armazena todas as configurações do sistema, incluindo estrutura de logs, usuários autorizados e configurações de atualização.

### `/logs`
Contém todos os logs gerados pelo sistema, incluindo acessos, erros e logs do dashboard.

### `/src`
Código fonte principal do sistema, incluindo monitor de logs, autenticação e gerenciamento de updates.

### `/web/dashboard`
Aplicação web Flask com dashboard moderno, templates HTML e arquivos estáticos.

### `/scripts`
Scripts de automação para instalação, deploy, inicialização e gerenciamento do sistema.

### `/tools`
Ferramentas auxiliares para administração e gerenciamento de updates.

### `/docs`
Documentação completa do projeto, incluindo guias de uso e diretrizes de segurança.

### `/backup`
Backups e arquivos antigos mantidos para referência.

## Arquivos Principais

- **egsys-monitor**: Launcher principal que integra login e monitor
- **requirements.txt**: Lista de dependências Python
- **README.md**: Documentação principal do projeto
- **VERSION**: Versão atual do sistema
- **.env**: Credenciais SSH (não versionado)
- **Dockerfile**: Configuração para containerização
- **docker-compose.yml**: Orquestração de containers

## Convenções

- Arquivos de configuração em JSON
- Scripts em Bash (.sh)
- Código Python em /src
- Templates HTML em /web/dashboard/templates
- Documentação em Markdown (.md)
- Logs em /logs com extensão .log
