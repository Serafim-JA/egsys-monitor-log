import os
import json
import sys
import subprocess
import paramiko
from dotenv import load_dotenv
# from getpass import getpass # Mantido comentado se não for mais usado
import select
import time
import signal

# --- Configurações globais ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Carrega variáveis de ambiente do .env
load_dotenv(ENV_PATH)

# Variável global para controlar interrupção (usada no modo normal)
stop_monitoring = False

# Handler de sinal para Ctrl+C (usado no modo normal)
def signal_handler(sig, frame):
    global stop_monitoring
    print("\n" + Color.WARNING + "Sinal de interrupção (Ctrl+C) recebido. Encerrando monitoramento..." + Color.END)
    stop_monitoring = True

# --- NOVO: Classe para Gerenciamento de Cores ---
class Color:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m' # Usado para nomes de logs
    OKCYAN = '\033[96m' # Usado para linhas de log
    OKGREEN = '\033[92m' # Usado para mensagens de sucesso
    WARNING = '\033[93m' # Usado para mensagens de aviso/saída
    FAIL = '\033[91m' # Usado para mensagens de erro
    END = '\033[0m' # Reseta a cor para o padrão do terminal
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Registrar o handler de sinal ao iniciar o script
signal.signal(signal.SIGINT, signal_handler)

# --- Funções Auxiliares ---

def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu(title, options_dict, current_choices):
    """
    Exibe um menu genérico com opções e permite seleção, incluindo "Voltar" e "Home".
    options_dict: Dicionário {chave: valor_display} ou lista de chaves.
    current_choices: Lista de escolhas feitas até o momento para contexto.
    """
    clear_screen()
    print("\n" + "=" * 35)
    print(Color.HEADER + f" {title}" + Color.END) # Aplicação de cor
    print("=" * 35)

    items = list(options_dict.items()) if isinstance(options_dict, dict) else [(k, k) for k in options_dict]

    for i, (key, display_value) in enumerate(items, start=1):
        if "logs_" in display_value:
            display_value = display_value.replace("logs_", "").upper()
        elif "_" in display_value and not display_value.isupper():
            display_value = display_value.replace("_", " ").title()
        else:
            display_value = display_value.upper()
        print(f"{i} - {display_value}")

    print("-" * 35)
    print("b - Voltar")
    print("h - Voltar ao Menu Principal")
    print("0 - Sair")
    print("=" * 35)

    choice = input("Digite a opção desejada: ").strip().lower()
    return choice, items

def get_user_choice(title, options_data, current_choices):
    """
    Gerencia a seleção do usuário em um menu, com tratamento para "Voltar" e "Home".
    Retorna a opção escolhida ou um comando de navegação ('b', 'h', '0').
    """
    while True:
        choice, items = display_menu(title, options_data, current_choices)

        if choice == '0':
            print(Color.WARNING + "SAINDO DO SISTEMA..." + Color.END) # Aplicação de cor
            sys.exit()
        elif choice == 'b':
            return 'b'
        elif choice == 'h':
            return 'h'

        try:
            choice_int = int(choice)
            if 1 <= choice_int <= len(items):
                return items[choice_int - 1][0]
            else:
                print(Color.FAIL + "Opção inválida. Tente novamente." + Color.END) # Aplicação de cor
        except ValueError:
            print(Color.FAIL + "Opção inválida. Por favor, digite um número, 'b', 'h' ou '0'." + Color.END) # Aplicação de cor
        input("Pressione Enter para continuar...")

def monitor_logs_normal(ssh_client, log_commands):
    """
    Executa os comandos remotamente e exibe os logs, um abaixo do outro.
    Controlado por stop_monitoring global para Ctrl+C.
    """
    global stop_monitoring

    active_channels = []
    try:
        clear_screen()
        print(Color.OKGREEN + "Iniciando monitoramento de logs. Pressione Ctrl+C para voltar." + Color.END) # Aplicação de cor
        print("=" * 50)

        for cmd_info in log_commands:
            log_name = cmd_info['name']
            command = cmd_info['command']
            print("\n" + Color.OKBLUE + "=== LOG DE " + log_name.upper().replace('_', ' ') + " ===" + Color.END) # Aplicação de cor
            print(f"Comando: {command}")
            
            chan = ssh_client.get_transport().open_session()
            chan.exec_command(command)
            active_channels.append({
                'name': log_name,
                'channel': chan,
                'stdout': chan.makefile('rb', -1),
                'stderr': chan.makefile_stderr('rb', -1)
            })
            
        readable_fds = [chan_info['channel'] for chan_info in active_channels]

        stop_monitoring = False # Reinicia a flag antes de entrar no loop

        while not stop_monitoring:
            if not active_channels:
                break

            rlist, _, _ = select.select(readable_fds, [], [], 0.1)

            for channel_obj in rlist:
                current_chan_info = next((item for item in active_channels if item['channel'] == channel_obj), None)
                if current_chan_info:
                    line = current_chan_info['stdout'].readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(Color.OKCYAN + "[" + current_chan_info['name'].upper().replace('_', ' ') + "] " + line + Color.END) # Aplicação de cor
                    elif current_chan_info['channel'].exit_status_ready():
                        print("\n" + Color.WARNING + "--- LOG DE " + current_chan_info['name'].upper().replace('_', ' ') + " ENCERRADO ---" + Color.END + "\n") # Aplicação de cor
                        active_channels = [c for c in active_channels if c['channel'] != channel_obj]
                        readable_fds = [c['channel'] for c in active_channels]

    except Exception as e:
        print(Color.FAIL + f"Erro durante o monitoramento: {e}" + Color.END) # Aplicação de cor
    finally:
        for channel_info in active_channels:
            try:
                if not channel_info['stdout'].closed:
                    channel_info['stdout'].close()
                if not channel_info['stderr'].closed:
                    channel_info['stderr'].close()
                if not channel_info['channel'].closed:
                    channel_info['channel'].close()
            except Exception:
                pass 
        print(Color.WARNING + "Voltando ao menu de seleção de serviço..." + Color.END) # Aplicação de cor
        input("Pressione Enter para continuar...")


def ssh_connect(hostname, username, password, log_commands_list):
    """
    Conecta a um servidor via SSH e inicia o monitoramento de logs no modo normal.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(f"Conectando a {Color.OKCYAN}{hostname}{Color.END} com o usuário {Color.OKCYAN}{username}{Color.END}...") # Aplicação de cor
        ssh.connect(hostname, username=username, password=password, timeout=10)
        print(Color.OKGREEN + "Conexão SSH bem-sucedida!" + Color.END) # Aplicação de cor
        monitor_logs_normal(ssh, log_commands_list) # Sempre chama o modo normal
    except paramiko.AuthenticationException:
        print(Color.FAIL + "Erro de autenticação: Verifique usuário e senha no arquivo .env." + Color.END) # Aplicação de cor
    except paramiko.SSHException as e:
        print(Color.FAIL + f"Erro SSH: {e}" + Color.END) # Aplicação de cor
    except Exception as e:
        print(Color.FAIL + f"Erro ao conectar: {e}" + Color.END) # Aplicação de cor
    finally:
        if ssh.get_transport() and ssh.get_transport().is_active():
            ssh.close()
            print("Conexão SSH principal encerrada.")

# --- Menu Principal e Navegação ---

def main_menu():
    """Função principal que gerencia a navegação entre os menus."""
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    navigation_stack = []

    while True:
        current_level_data = config
        path_chosen = []

        if navigation_stack:
            path_chosen = list(navigation_stack)
            for choice in path_chosen:
                current_level_data = current_level_data[choice]

        # Nível 0: Clientes
        if not path_chosen:
            title = "Seleção de Cliente"
            options = list(current_level_data.keys())
            chosen_client = get_user_choice(title, options, path_chosen)
            if chosen_client in ['b', 'h', '0']:
                if chosen_client == 'b' or chosen_client == 'h':
                    print(Color.WARNING + "Voltando ao menu principal..." + Color.END) # Aplicação de cor
                    continue
                else:
                    sys.exit()
            navigation_stack.append(chosen_client)
            path_chosen.append(chosen_client)
            current_level_data = current_level_data[chosen_client]

        # Nível 1: Servidores (mob, web, etc.)
        if len(path_chosen) == 1:
            title = f"Servidores do Cliente: {path_chosen[0].upper()}"
            options = list(current_level_data.keys())
            chosen_server = get_user_choice(title, options, path_chosen)
            if chosen_server in ['b', 'h', '0']:
                if chosen_server == 'b':
                    navigation_stack.pop()
                    continue
                elif chosen_server == 'h':
                    navigation_stack.clear()
                    continue
                else:
                    sys.exit()
            navigation_stack.append(chosen_server)
            path_chosen.append(chosen_server)
            current_level_data = current_level_data[chosen_server]

        # Nível 2: Aplicações (logs_mobile, logs_ait, etc.)
        if len(path_chosen) == 2:
            title = f"Aplicações em {path_chosen[1].upper()} do Cliente: {path_chosen[0].upper()}"
            options = list(current_level_data.keys())
            chosen_app = get_user_choice(title, options, path_chosen)
            if chosen_app in ['b', 'h', '0']:
                if chosen_app == 'b':
                    navigation_stack.pop()
                    continue
                elif chosen_app == 'h':
                    navigation_stack.clear()
                    continue
                else:
                    sys.exit()
            navigation_stack.append(chosen_app)
            path_chosen.append(chosen_app)
            current_level_data = current_level_data[chosen_app]

        # Nível 3: Serviços de Log (socket, consumidor, etc.)
        if len(path_chosen) == 3:
            title = f"Serviços de Log da Aplicação '{chosen_app.replace('logs_', '').upper()}'"
            log_services = list(current_level_data.keys())
            
            clear_screen()
            print("\n" + "=" * 35)
            print(Color.HEADER + f" {title}" + Color.END) # Aplicação de cor
            print("=" * 35)
            for i, service_name in enumerate(log_services, start=1):
                display_name = service_name.replace("_", " ").upper()
                print(f"{i} - {display_name}")
            print("-" * 35)
            print("b - Voltar")
            print("h - Voltar ao Menu Principal")
            print("0 - Sair")
            print("=" * 35)
            print("Para múltiplos logs, digite os números separados por vírgula (ex: 1,3,5)")
            
            chosen_services_raw = input("Digite a(s) opção(ões) desejada(s): ").strip().lower()

            if chosen_services_raw == '0':
                print(Color.WARNING + "SAINDO DO SISTEMA..." + Color.END) # Aplicação de cor
                sys.exit()
            elif chosen_services_raw == 'b':
                navigation_stack.pop()
                continue
            elif chosen_services_raw == 'h':
                navigation_stack.clear()
                continue
            
            selected_log_commands = []
            try:
                service_indices = [int(s.strip()) for s in chosen_services_raw.split(',')]
                
                for idx in service_indices:
                    if 1 <= idx <= len(log_services):
                        service_key = log_services[idx - 1]
                        command_str = current_level_data[service_key]
                        selected_log_commands.append({
                            'name': service_key,
                            'command': command_str
                        })
                    else:
                        print(Color.FAIL + f"Opção de serviço inválida: {idx}. Tente novamente." + Color.END) # Aplicação de cor
                        selected_log_commands = []
                        break
                
                if not selected_log_commands:
                    input("Pressione Enter para continuar...")
                    continue

            except ValueError:
                print(Color.FAIL + "Opção inválida. Por favor, digite um número, 'b', 'h' ou '0' ou números separados por vírgula." + Color.END) # Aplicação de cor
                input("Pressione Enter para continuar...")
                continue

            client = path_chosen[0]
            server = path_chosen[1]

            host = os.getenv(f"HOST_{client.upper()}_{server.upper()}")
            user = os.getenv(f"USER_{client.upper()}_{server.upper()}")
            password = os.getenv(f"PASSWORD_{client.upper()}_{server.upper()}")


            if not host or not user or not password:
                print(Color.FAIL + f"Erro: Variáveis de ambiente HOST_{client.upper()}_{server.upper()}, USER_{client.upper()}_{server.upper()} ou PASSWORD_{client.upper()}_{server.upper()} não encontradas no .env." + Color.END) # Aplicação de cor
                input("Pressione Enter para continuar...")
                continue

            ssh_connect(host, user, password, selected_log_commands)
                
            continue

# --- Execução ---
if __name__ == "__main__":
    main_menu()