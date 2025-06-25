# egsys-monitor-log

## Objetivo desse script
Facilitar a visualização dos logs de serviços dos clientes via máquina local, sem precisar ter que ficar entrando na máquina e visualizar log por log para achar onde pode estar o erro. Este script permite navegar entre diferentes serviços e visualizar logs em tempo real.

## Informações sobre o script
É um script com interface de terminal que utiliza o Python para estabelecer conexões SSH (com a biblioteca `paramiko`) e executar comandos de visualização de logs (`tail -f`) nos servidores remotos. A configuração dos logs e das credenciais de acesso é feita através de arquivos JSON e de ambiente (`.env`).

### Funcionalidades:
* **Menu Interativo:** Navegação aprimorada entre clientes, servidores, aplicações e serviços de logs.
* **Opções de Navegação:** Inclui `b` (voltar à página anterior), `h` (voltar ao menu principal) e `0` (sair).
* **Visualização de Múltiplos Logs:** Permite selecionar vários logs para visualização simultânea, exibindo-os um abaixo do outro com separação e identificação.
* **Interrupção de Logs:** Pressione `Ctrl+C` durante a visualização dos logs para retornar ao menu de seleção de serviços.
* **Verificação de VPN:** O script verifica se uma conexão VPN está ativa antes de permitir o acesso aos servidores.
* **Cores na Saída:** Mensagens e logs são exibidos com cores para melhor legibilidade.
* **Autenticação Automatizada:** As credenciais SSH (host, usuário, senha) são lidas diretamente do arquivo `.env` para automação do login.

## Configuração e Instalação

1.  **Fazer o `git clone`:**
    ```bash
    git clone [https://github.com/seu-usuario/egsys-watcher-local-script.git](https://github.com/seu-usuario/egsys-watcher-local-script.git)
    cd egsys-watcher-local-script
    ```

2.  **Configurar o arquivo `.env`:**
    Crie um arquivo `.env` na raiz do projeto (`egsys-watcher-local-script/`).
    Você pode usar o `.env.example` como template:
    ```bash
    cp .env.example .env
    ```
    Abra o arquivo `.env` e preencha as variáveis de ambiente com as informações reais de host, usuário e **senha** para cada ambiente de cliente/servidor. Exemplo:
    ```
    HOST_PR_MOB=192.168.1.100
    USER_PR_MOB=usuario_ssh
    PASSWORD_PR_MOB=sua_senha_secreta
    ```
    **SEGURANÇA:** Certifique-se de que o arquivo `.env` tenha permissões restritivas (somente leitura para o proprietário):
    ```bash
    chmod 600 .env
    ```

3.  **Configurar o arquivo `config/config.json`:**
    Este arquivo define a estrutura dos seus logs. Verifique se os caminhos dos logs (`tail -f /caminho/do/log.log`) estão corretos para cada serviço.

4.  **Executar o Script de Instalação e Execução (`run_monitor.sh`):**
    Este script irá verificar e instalar as dependências necessárias (Python3, pip3, openssh-client, paramiko, python-dotenv) e, em seguida, iniciará o monitor de logs.
    ```bash
    cd src/ # Mova para o diretório src/
    chmod +x run_monitor.sh
    ./run_monitor.sh
    ```

5.  **Criar um alias (opcional, para facilitar o acesso):**
    Para facilitar a execução, você pode adicionar um alias ao seu arquivo de configuração do shell (ex: `~/.bashrc` ou `~/.zshrc`).
    Abra o arquivo (ex: `nano ~/.bashrc`) e adicione a seguinte linha no final (substitua `/caminho/para/seu/repositorio/` pelo caminho real):
    ```bash
    alias egsys-monitor-log="bash /caminho/para/seu/repositorio/src/run_monitor.sh"
    ```
    Salve e feche o arquivo. Para aplicar o alias imediatamente, execute:
    ```bash
    source ~/.bashrc
    # ou
    source ~/.zshrc
    ```
    Agora você pode simplesmente digitar `egsys-monitor-log` no terminal para iniciar o script.

## Requisitos de Sistema

* **Python 3.x**
* **pip** (gerenciador de pacotes Python)
* **OpenSSH Client** (geralmente já vem pré-instalado em sistemas Linux)
* **Conexão VPN ativa** (configurada e em funcionamento na sua máquina local, verificada pelo script)

## Possíveis Erros e Soluções
*(Mantenha esta seção com os erros que já discutimos e suas soluções, adaptando para a nova estrutura e funcionalidades.)*

---

### **Para o GitHub:**

1.  **Crie um novo repositório no GitHub.**
2.  **Siga as instruções do GitHub para fazer o `git init`, `git add`, `git commit` e `git push`** do seu projeto para o novo repositório, garantindo que o `.gitignore` esteja no lugar para não subir o `.env`.

Esta configuração centraliza todas as informações importantes e prepara seu projeto para ser facilmente compartilhado e utilizado por outros.
    Para facilitar a execução, você pode adicionar um alias ao seu arquivo de configuração do shell (ex: `~/.bashrc` ou `~/.zshrc`).
    Abra o arquivo com um editor de texto (ex: `nano ~/.bashrc`):
    ```bash
    nano ~/.bashrc
    ```
    Adicione a seguinte linha no final do arquivo (substitua `/caminho/para/seu/script/` pelo caminho real):
    ```bash
    alias logmon="/caminho/para/seu/script/run_monitor.sh"
    ```
    Salve e feche o arquivo. Para aplicar o alias imediatamente, execute:
    ```bash
    source ~/.bashrc
    # ou
    source ~/.zshrc
    ```
    Agora você pode simplesmente digitar `logmon` no terminal para iniciar o script.

## Requisitos de Sistema

* **Python 3.x**
* **pip** (gerenciador de pacotes Python)
* **OpenSSH Client** (geralmente já vem pré-instalado em sistemas Linux)
* **Conexão VPN ativa** (configurada e em funcionamento na sua máquina local)
