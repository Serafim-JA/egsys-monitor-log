# egSYS Monitor - Sistema de Monitoramento Centralizado de Logs

**Autor:** Serafim  
**Versão:** 1.0.0  
**Licença:** MIT  
**Repositório:** https://github.com/Serafim-JA/egsys-monitor-log

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Problema e Solução](#problema-e-solução)
3. [Benefícios](#benefícios)
4. [Arquitetura](#arquitetura)
5. [Instalação](#instalação)
6. [Configuração](#configuração)
7. [Uso](#uso)
8. [Dashboard Web](#dashboard-web)
9. [Funcionalidades](#funcionalidades)
10. [Requisitos](#requisitos)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **egSYS Monitor** é uma solução completa de monitoramento centralizado de logs para ambientes distribuídos. Desenvolvido para facilitar a visualização e análise de logs de múltiplos servidores remotos através de uma interface unificada, eliminando a necessidade de acessar cada servidor individualmente.

### Conceito

Em ambientes corporativos com múltiplos servidores e serviços distribuídos, a análise de logs é uma tarefa crítica mas extremamente trabalhosa. O egSYS Monitor centraliza essa operação, permitindo que equipes de suporte e desenvolvimento monitorem logs em tempo real de qualquer lugar, através de uma interface moderna e intuitiva.

---

## 🔍 Problema e Solução

### Problema Identificado

**Cenário Atual:**
- Equipes precisam acessar múltiplos servidores via SSH individualmente
- Navegação manual entre diferentes arquivos de log
- Dificuldade em correlacionar eventos entre servidores
- Perda de tempo procurando erros específicos
- Falta de histórico e auditoria de acessos
- Ausência de controle centralizado de permissões

**Impactos:**
- ⏱️ Tempo médio de 15-30 minutos para diagnosticar problemas simples
- 🔒 Riscos de segurança com credenciais SSH dispersas
- 📊 Impossibilidade de análise agregada de logs
- 👥 Dificuldade em onboarding de novos membros da equipe

### Solução Proposta

O **egSYS Monitor** resolve esses problemas através de:

1. **Centralização:** Interface única para todos os servidores
2. **Automação:** Conexões SSH automatizadas e gerenciadas
3. **Visualização:** Logs em tempo real com cores e formatação
4. **Controle:** Dashboard web para gerenciamento de usuários e acessos
5. **Auditoria:** Registro completo de todas as operações
6. **Atualização:** Sistema auto-atualizável via GitHub

---

## ✨ Benefícios

### Para a Equipe de Suporte

- ⚡ **Redução de 80% no tempo de diagnóstico**
- 🎯 Acesso direto aos logs relevantes sem navegação manual
- 👁️ Visualização simultânea de múltiplos logs
- 📱 Acesso de qualquer dispositivo com navegador

### Para Gestores

- 📊 Métricas de acesso e uso do sistema
- 🔐 Controle centralizado de permissões
- 📝 Auditoria completa de acessos
- 💰 Redução de custos operacionais

### Para Desenvolvedores

- 🐛 Debug mais rápido em produção
- 🔄 Correlação de eventos entre serviços
- 📈 Análise de performance em tempo real
- 🛠️ Integração com ferramentas existentes

### Para a Organização

- 🔒 Maior segurança com credenciais centralizadas
- 📚 Documentação automática de infraestrutura
- 🚀 Onboarding acelerado de novos membros
- 🎓 Redução da curva de aprendizado

---

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────────┐
│                    egSYS Monitor                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Terminal   │  │  Dashboard   │  │  Auto-Update │ │
│  │   Monitor    │  │     Web      │  │    System    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                  │         │
│         └─────────────────┴──────────────────┘         │
│                           │                            │
│                  ┌────────▼────────┐                   │
│                  │  Auth Manager   │                   │
│                  └────────┬────────┘                   │
│                           │                            │
│                  ┌────────▼────────┐                   │
│                  │   SSH Manager   │                   │
│                  └────────┬────────┘                   │
└───────────────────────────┼─────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
   │ Server  │         │ Server  │        │ Server  │
   │    1    │         │    2    │        │    N    │
   └─────────┘         └─────────┘        └─────────┘
```

### Tecnologias Utilizadas

- **Backend:** Python 3.12+
- **Framework Web:** Flask + Gunicorn
- **SSH:** Paramiko
- **Interface Terminal:** Rich
- **Autenticação:** Flask-Login + bcrypt
- **Relatórios:** ReportLab (PDF)
- **Frontend:** HTML5 + CSS3 + JavaScript + Chart.js
- **Versionamento:** Git + GitHub

---

## 📦 Instalação

### Método 1: Instalação Automática (Recomendado)

```bash
curl -sSL https://raw.githubusercontent.com/Serafim-JA/egsys-monitor-log/main/install.sh | bash
```

**O que o instalador faz:**
1. Detecta automaticamente seu sistema operacional
2. Instala dependências necessárias (Python, pip, SSH, Git)
3. Clona o repositório do GitHub
4. Instala bibliotecas Python
5. Cria launcher global `egsys-monitor`
6. Configura arquivos iniciais

**Sistemas Suportados:**
- Ubuntu / Debian / Linux Mint / Pop!_OS
- Fedora / RHEL / CentOS
- Arch Linux / Manjaro
- openSUSE
- macOS (com Homebrew)

### Método 2: Instalação Manual

```bash
# 1. Clonar repositório
git clone https://github.com/Serafim-JA/egsys-monitor-log.git
cd egsys-monitor-log

# 2. Instalar dependências
pip3 install --user -r requirements.txt

# 3. Configurar ambiente
cp .env.example .env
nano .env

# 4. Executar
bash src/run_monitor.sh
```

---

## ⚙️ Configuração

### 1. Configurar Credenciais SSH (.env)

Edite o arquivo `~/.egsys-monitor/.env`:

```bash
# Servidor Paraná
USER_PR_MOB=usuario
HOST_PR_MOB=192.168.1.100
PASSWORD_PR_MOB='senha123'

# Servidor Santa Catarina
USER_SC_MOB=usuario
HOST_SC_MOB=192.168.1.101
PASSWORD_SC_MOB='senha456'
```

### 2. Configurar Estrutura de Logs (config.json)

Edite `~/.egsys-monitor/config/config.json`:

```json
{
  "Paraná": {
    "Mobile": {
      "Backend": {
        "Application": "tail -f /var/log/app.log",
        "Error": "tail -f /var/log/error.log"
      }
    }
  }
}
```

### 3. Criar Primeiro Usuário (Dashboard)

```bash
cd ~/.egsys-monitor
bash restart-dashboard.sh
```

Acesse: http://localhost:5000

**Credenciais padrão:**
- Usuário: `lucasserafim`
- Senha: `Rune89Lukas@#$`

⚠️ **Altere as credenciais após primeiro acesso!**

---

## 🚀 Uso

### Monitor de Logs (Terminal)

```bash
# Executar monitor
egsys-monitor

# Ou diretamente
cd ~/.egsys-monitor
bash src/run_monitor.sh
```

**Fluxo de uso:**
1. Sistema verifica atualizações automaticamente
2. Solicita login (use credenciais do dashboard)
3. Exibe menu de clientes
4. Selecione servidor → aplicação → serviço
5. Visualize logs em tempo real
6. Pressione `BACKSPACE` para voltar
7. Pressione `Ctrl+C` para sair

**Navegação:**
- `1-9`: Selecionar opção
- `b`: Voltar ao menu anterior
- `h`: Voltar ao menu principal
- `0`: Sair do sistema
- `BACKSPACE`: Parar visualização de logs

### Dashboard Web

```bash
# Iniciar dashboard
cd ~/.egsys-monitor
bash restart-dashboard.sh
```

**Acesso:**
- Local: http://localhost:5000
- Rede: http://[SEU_IP]:5000

**Funcionalidades:**
- Gerenciar usuários
- Adicionar/remover chaves SSH
- Visualizar logs de acesso
- Métricas do sistema
- Gráficos em tempo real

---

## 🎨 Dashboard Web

### Visão Geral

Interface moderna com design egSYS (azul #007acc) que oferece:

#### 1. Overview
- Total de usuários cadastrados
- Usuários ativos
- Acessos do dia
- Uso de CPU/Memória/Disco
- Gráfico de acessos por hora
- Distribuição por função

#### 2. Gerenciamento de Usuários

**Adicionar Usuário:**
- Nome completo
- Email
- Usuário SSH
- Função (Admin/User/Suporte)
- Host SSH
- Senha SSH
- Chave pública SSH (opcional)

**Ações:**
- Editar usuário
- Desativar/ativar
- Remover usuário

#### 3. Chaves SSH

- Visualizar chaves cadastradas
- Adicionar novas chaves
- Remover chaves
- Fingerprint de cada chave

#### 4. Logs de Acesso

- Histórico completo de acessos
- Filtros por data/usuário/ação
- Exportação de relatórios
- Limpeza de logs antigos

#### 5. Sistema

- Monitoramento de recursos
- Status dos serviços
- Configurações gerais

---

## 🎯 Funcionalidades

### Monitor de Logs (Terminal)

✅ **Navegação Hierárquica**
- Menu interativo com breadcrumbs
- Navegação intuitiva entre níveis
- Indicadores visuais de posição

✅ **Visualização de Logs**
- Múltiplos logs simultâneos
- Cores para melhor legibilidade
- Timestamps automáticos
- Separação visual entre logs

✅ **Controle de Fluxo**
- Interrupção com BACKSPACE
- Navegação com teclas
- Retorno rápido ao menu principal

✅ **Autenticação**
- Login integrado com dashboard
- Máximo de 3 tentativas
- Bloqueio automático
- Registro de tentativas

✅ **Auto-Atualização**
- Verificação automática no GitHub
- Atualização com um comando
- Preservação de configurações
- Rollback em caso de erro

### Dashboard Web

✅ **Gerenciamento Completo**
- CRUD de usuários
- Gerenciamento de chaves SSH
- Controle de permissões
- Auditoria de acessos

✅ **Visualização de Dados**
- Gráficos em tempo real
- Métricas do sistema
- Histórico de acessos
- Estatísticas de uso

✅ **Segurança**
- Autenticação com bcrypt
- Sessões seguras
- Logs de auditoria
- Controle de acesso por função

✅ **Integração**
- Sincronização com .env
- Atualização automática de configs
- API REST para integrações
- Webhooks (futuro)

---

## 📋 Requisitos

### Sistema Operacional

- Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- macOS 10.15+
- Windows (via WSL2)

### Software

- Python 3.8+
- pip3
- Git
- OpenSSH Client
- Navegador moderno (Chrome, Firefox, Edge)

### Rede

- Conexão com servidores remotos
- VPN (se necessário)
- Porta 5000 disponível (dashboard)

### Hardware Mínimo

- CPU: 2 cores
- RAM: 2GB
- Disco: 500MB

---

## 🔧 Troubleshooting

### Problema: Erro ao instalar dependências Python

**Solução:**
```bash
pip3 install --break-system-packages -r requirements.txt
# ou
pip3 install --user -r requirements.txt
```

### Problema: Não consegue conectar ao servidor SSH

**Verificar:**
1. Credenciais no .env estão corretas
2. VPN está conectada
3. Firewall permite conexão
4. Servidor está acessível

```bash
# Testar conexão manual
ssh usuario@host
```

### Problema: Dashboard não inicia

**Solução:**
```bash
# Verificar porta
lsof -i :5000

# Matar processo
kill $(lsof -t -i:5000)

# Reiniciar
bash restart-dashboard.sh
```

### Problema: Erro de autenticação

**Solução:**
1. Verificar se usuário existe no dashboard
2. Resetar senha via dashboard web
3. Verificar arquivo `config/authorized_keys.json`

### Problema: Sistema não atualiza

**Solução:**
```bash
cd ~/.egsys-monitor
python3 src/auto_update.py --force
```

---

## 📊 Casos de Uso

### 1. Suporte Técnico

**Cenário:** Cliente reporta erro no sistema

**Antes:**
1. Conectar VPN (2 min)
2. SSH no servidor (1 min)
3. Navegar até logs (2 min)
4. Encontrar erro (5-10 min)
**Total: 10-15 minutos**

**Com egSYS Monitor:**
1. Abrir terminal (10 seg)
2. Selecionar cliente/servidor (20 seg)
3. Visualizar log (imediato)
**Total: 30 segundos**

### 2. Desenvolvimento

**Cenário:** Debug de integração entre serviços

**Antes:**
- Múltiplas janelas SSH
- Correlação manual de timestamps
- Perda de contexto

**Com egSYS Monitor:**
- Visualização simultânea de múltiplos logs
- Timestamps sincronizados
- Contexto preservado

### 3. Auditoria

**Cenário:** Investigação de incidente

**Antes:**
- Logs dispersos
- Sem histórico de acessos
- Dificuldade em rastreabilidade

**Com egSYS Monitor:**
- Logs centralizados
- Histórico completo
- Relatórios em PDF

---

## 🔐 Segurança

### Boas Práticas

1. **Credenciais:**
   - Nunca commitar .env no Git
   - Usar senhas fortes
   - Rotacionar senhas periodicamente

2. **Acesso:**
   - Princípio do menor privilégio
   - Revisar logs regularmente
   - Desativar usuários inativos

3. **Rede:**
   - Usar VPN sempre que possível
   - Firewall configurado
   - Monitorar acessos suspeitos

4. **Sistema:**
   - Manter sistema atualizado
   - Backup de configurações
   - Logs de auditoria habilitados

---

## 🚀 Roadmap

### Versão 1.1 (Próxima)
- [ ] Filtros avançados de logs
- [ ] Exportação de logs em múltiplos formatos
- [ ] Notificações por email/Slack
- [ ] Suporte a Docker

### Versão 1.2
- [ ] Análise de logs com IA
- [ ] Alertas automáticos
- [ ] Dashboard mobile
- [ ] API REST completa

### Versão 2.0
- [ ] Suporte a Kubernetes
- [ ] Integração com Elasticsearch
- [ ] Machine Learning para detecção de anomalias
- [ ] Multi-tenancy

---

## 📞 Suporte

### Documentação
- GitHub: https://github.com/Serafim-JA/egsys-monitor-log
- Wiki: https://github.com/Serafim-JA/egsys-monitor-log/wiki

### Contato
- Issues: https://github.com/Serafim-JA/egsys-monitor-log/issues
- Email: serafim@egsys.com.br

### Contribuindo

Contribuições são bem-vindas! Por favor:
1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

## 📄 Licença

MIT License - Veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

Desenvolvido com ❤️ por **Serafim** para a comunidade egSYS.

**Tecnologias utilizadas:**
- Python Software Foundation
- Flask Team
- Paramiko Contributors
- Rich Library
- Chart.js Team

---

**© 2024 Serafim - egSYS Monitor**
