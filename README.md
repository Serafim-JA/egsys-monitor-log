# egSYS Monitor - Sistema de Monitoramento de Logs

<div align="center">

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Sistema centralizado de monitoramento de logs para ambientes distribuídos**

[🚀 Instalação](#-instalação) • [📚 Documentação](#-documentação) • [✨ Features](#-features) • [🎯 Demo](#-demo) • [🤝 Contribuindo](#-contribuindo)

</div>

---

## 📋 Sumário

- [Sobre](#egsys-monitor---sistema-de-monitoramento-de-logs)
- [Features](#-features)
- [Instalação](#-instalação)
- [Uso Rápido](#-uso-rápido)
- [Documentação](#-documentação)
- [Requisitos](#-requisitos)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)
- [Autor](#-autor)

---

## ✨ Features

- 📊 **Dashboard Web Moderno** - Interface intuitiva com gráficos em tempo real
- 💻 **Monitor de Terminal Interativo** - Visualização de logs com navegação avançada
- 🔐 **Autenticação Integrada** - Sistema unificado de login com bcrypt
- 🔄 **Auto-Atualização** - Atualizações automáticas via GitHub
- 🛡️ **Segurança Avançada** - Criptografia, auditoria completa e verificação VPN
- 🌐 **Multi-Plataforma** - Linux, macOS e Windows (WSL)
- 📦 **Instalador Universal** - Executável standalone que detecta automaticamente o sistema
- 🔍 **Monitoramento em Tempo Real** - Suporte a múltiplos logs simultâneos
- 🎨 **Interface Colorida** - Saída com cores para melhor legibilidade
- ⚡ **Navegação Intuitiva** - Menus interativos com atalhos (b/voltar, h/início, 0/sair)

## 🚀 Instalação

### Instalação Automática (Recomendado)

Baixe o instalador executável mais recente do [GitHub Releases](https://github.com/Serafim-JA/egsys-monitor-log/releases) e execute:

```bash
# Para Linux
./egsys-monitor-installer

# Para Windows/Mac
# Execute o arquivo baixado
```

O instalador irá:
- ✅ Detectar automaticamente seu sistema operacional
- 📦 Instalar todas as dependências necessárias
- ⚙️ Configurar o ambiente
- 🚀 Criar atalhos e aliases

### Instalação Manual

```bash
# Clone o repositório
git clone https://github.com/Serafim-JA/egsys-monitor-log.git
cd egsys-monitor-log

# Instale as dependências
pip install -r requirements.txt

# Execute o instalador
python installer/egsys_installer.py
```

## 🎯 Uso Rápido

### Monitor de Logs
```bash
egsys-monitor
```

### Dashboard Web
```bash
# Inicie o dashboard
egsys-dashboard

# Acesse em: http://localhost:5000
```

### Comandos Disponíveis
- `egsys-monitor` - Inicia o monitor de terminal
- `egsys-dashboard` - Inicia o dashboard web
- `egsys-update` - Verifica e instala atualizações
- `egsys-install` - Reinstala o sistema

## 📚 Documentação

Para documentação completa, visite:

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Guia completo de instalação e configuração
- **[SECURITY.md](docs/SECURITY.md)** - Políticas de segurança
- **[UPDATE_UNINSTALL.md](docs/UPDATE_UNINSTALL.md)** - Atualização e desinstalação
- **[EXTERNAL_ACCESS.md](docs/EXTERNAL_ACCESS.md)** - Acesso remoto
- **[CLOUDFLARE_TUNNEL.md](docs/CLOUDFLARE_TUNNEL.md)** - Configuração Cloudflare

## 💻 Requisitos

- **Python**: 3.8 ou superior
- **Git**: Para atualizações automáticas
- **OpenSSH Client**: Para conexões remotas
- **Memória RAM**: 2GB mínimo (4GB recomendado)
- **Espaço em Disco**: 500MB para instalação completa

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga estes passos:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Desenvolvimento Local

```bash
# Clone e instale
git clone https://github.com/Serafim-JA/egsys-monitor-log.git
cd egsys-monitor-log
pip install -r requirements.txt

# Execute em modo desenvolvimento
python src/log_monitor.py
```

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ❤️ Autor

**Serafim**
- GitHub: [@Serafim-JA](https://github.com/Serafim-JA)

---

<div align="center">

**Desenvolvido com ❤️ para a comunidade egSYS**

⭐ Se este projeto te ajudou, dê uma estrela no GitHub!

</div>
