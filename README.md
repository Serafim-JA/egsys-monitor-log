Markdown

# 🖥️ egSYS Monitor - Log Viewer (CLI)

Ferramenta de linha de comando (CLI) desenvolvida para a equipe de suporte **egSYS**. O objetivo é simplificar, agilizar e auditar o monitoramento de logs em tempo real (Java, System, Apache, etc.) em múltiplos servidores via SSH.

---

## 🚀 Novidades da Versão 7.0 (Bash Edition)
- **Zero Dependências Pesadas:** Reescrevemos o código de Python para **Bash Puro**. Mais rápido e compatível com qualquer Linux.
- **Parada Segura:** Não usamos mais `CTRL+C` para parar o log. Agora basta pressionar **[ENTER]**.
- **Ping Check:** O script testa se o servidor responde (Ping) antes de tentar conectar o SSH, evitando travamentos.
- **Auto Update:** O sistema possui um botão para buscar atualizações diretamente do GitHub.
- **Auditoria:** Todo acesso gera um registro local em `audit_egsys.log`.

---

## 📦 Como Instalar

Siga os passos abaixo no terminal do seu Linux (Ubuntu, Mint, Debian, WSL, etc).

### 1. Clonar o repositório
Baixe os arquivos para sua máquina:
```bash
cd /opt
sudo git clone [https://github.com/Serafim-JA/egsys-monitor-log.git](https://github.com/Serafim-JA/egsys-monitor-log.git) egsys-monitor
sudo chown -R $USER:$USER egsys-monitor
cd egsys-monitor
2. Executar o Instalador
O script de instalação configura as permissões, instala o sshpass (necessário para login automático) e cria o atalho no sistema.

Bash

chmod +x install.sh
./install.sh
3. Finalizar
Reinicie o terminal ou atualize as configurações com:

Bash

source ~/.bashrc
🛠️ Como Usar
Após a instalação, você pode rodar o programa de qualquer lugar do terminal digitando apenas:

Bash

egsys
Navegação
Login: Digite seu nome de usuário (para registro de auditoria).

Menu Principal: Escolha o Estado/Grupo de servidores.

Servidores: Selecione o servidor desejado (ex: Mobile, Web, AIT).

Logs: Escolha qual arquivo de log deseja assistir (ex: Socket, Consumidor, Gerador).

🛑 Como parar o log?
Diferente do padrão Linux, não use CTRL+C. O script roda o log em modo protegido. Para sair do log e voltar ao menu:

PRESSIONE A TECLA [ENTER]

🔄 Atualizações
Sempre que houver mudanças nos IPs ou novos logs adicionados ao código, você não precisa baixar tudo de novo.

Abra o egsys.

No menu principal, digite U (Update).

O script irá baixar a versão mais recente do Git e reiniciar automaticamente.

📂 Estrutura de Arquivos
monitor.sh: O script principal (Core do sistema).

install.sh: Script de configuração inicial e criação de atalhos.

audit_egsys.log: Arquivo gerado automaticamente contendo o histórico de acessos.

Nota: Certifique-se de estar conectado à VPN necessária para acessar os IPs privados dos servidores listados.
