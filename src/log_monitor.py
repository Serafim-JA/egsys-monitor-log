import os
import json
import sys
import subprocess
import paramiko
from dotenv import load_dotenv
import select
import time
import signal

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.align import Align

# --- Configurações globais ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Caminho para config.json: sobe um nível (do src/) e entra na pasta config/
CONFIG_PATH = os.path.join(os.path.dirname(BASE_DIR), "config", "config.json")
# Caminho para .env: sobe um nível (do src/)
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")

load_dotenv(ENV_PATH)

console = Console()

stop_monitoring = False

def signal_handler(sig, frame):
    """
    Handler para o sinal de interrupção (Ctrl+C).
    Define a flag global 'stop_monitoring' para encerrar os loops.
    """
    global stop_monitoring
    console.print("\n[bold yellow]Sinal de interrupção (Ctrl+C) recebido. Encerrando monitoramento...[/bold yellow]")
    stop_monitoring = True


# Registra o handler de sinal para SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# --- Funções Auxiliares de Interface ---

def clear_screen():
    """Limpa a tela do terminal."""
    console.clear()

def display_menu(title, options_dict, current_choices):
    """
    Exibe um menu formatado com Rich, incluindo opções de navegação.
    Args:
        title (str): Título do menu.
        options_dict (dict or list): Dicionário de opções {chave: valor_display} ou lista de chaves.
        current_choices (list): Lista das escolhas anteriores (para contexto, não usado diretamente aqui).
    Returns:
        tuple: (escolha_do_usuario, items_do_menu)
    """
    clear_screen() # Limpa a tela para exibir um novo menu
    console.print("\n[bold deep_sky_blue1]=" * 35 + "[/bold deep_sky_blue1]")
    console.print(Panel(Text(title, justify="center", style="bold bright_magenta"), border_style="gold1"))
    console.print("[bold deep_sky_blue1]=" * 35 + "[/bold deep_sky_blue1]")

    items = list(options_dict.items()) if isinstance(options_dict, dict) else [(k, k) for k in options_dict]

    for i, (key, display_value) in enumerate(items, start=1):
        if "logs_" in display_value:
            display_value = display_value.replace("logs_", "").upper()
        elif "_" in display_value and not display_value.isupper():
            display_value = display_value.replace("_", " ").title()
        else:
            display_value = display_value.upper()
        console.print(f"[bright_green]{i}[/bright_green] - [bright_cyan]{display_value}[/bright_cyan]")

    console.print("[dim white]-" * 35 + "[/dim white]")
    console.print("[yellow]b[/yellow] - Voltar")
    console.print("[yellow]h[/yellow] - Voltar ao Menu Principal")
    console.print("[bold red]0[/bold red] - Sair")
    console.print("[bold deep_sky_blue1]=" * 35 + "[/bold deep_sky_blue1]")

    choice = console.input("[bold light_sky_blue3]Digite a opção desejada:[/bold light_sky_blue3] ").strip().lower()
    return choice, items

def get_user_choice(title, options_data, current_choices):
    """
    Gerencia a seleção do usuário em um menu, com tratamento para "Voltar", "Home" e "Sair".
    Args:
        title (str): Título do menu.
        options_data (dict or list): Dados das opções para exibir.
        current_choices (list): Lista de escolhas feitas até o momento.
    Returns:
        str: A chave da opção escolhida ou um comando de navegação ('b', 'h', '0').
    """
    while True:
        choice, items = display_menu(title, options_data, current_choices)

        if choice == '0':
            console.print("[bold yellow]SAINDO DO SISTEMA...[/bold yellow]")
            sys.exit()
        elif choice == 'b':
            return 'b'
        elif choice == 'h':
            return 'h'

        try:
            choice_int = int(choice)
            if 1 <= choice_int <= len(items):
                return items[choice_int - 1][0] # Retorna a chave original da opção
            else:
                console.print("[bold red]Opção inválida. Tente novamente.[/bold red]")
        except ValueError:
            console.print("[bold red]Opção inválida. Por favor, digite um número, 'b', 'h' ou '0'.[/bold red]")
        console.input("[yellow]Pressione Enter para continuar...[/yellow]")

# --- Função de Monitoramento de Logs ---

def monitor_logs_normal(ssh_client, log_commands):
    """
    Executa os comandos 'tail -f' remotamente e exibe os logs no terminal,
    permitindo rolagem nativa.
    Args:
        ssh_client (paramiko.SSHClient): Cliente SSH conectado.
        log_commands (list): Lista de dicionários {'name': log_name, 'command': command}.
    """
    global stop_monitoring

    active_channels_info = [] # Canais SSH que estão ativamente monitorando logs
    
    # Este painel será impresso APENAS UMA VEZ no início do monitoramento
    console.print(Panel(
        Text("Monitoramento de Logs Ativos", justify="center", style="bold green_yellow"),
        border_style="green_yellow",
        expand=True # Garante que o painel ocupe a largura total
    ))
    console.print("[bold magenta]Pressione Ctrl+C a qualquer momento para voltar ao menu.[/bold magenta]\n")
    console.print("=" * console.width, style="dim white") # Separador horizontal
    
    try:
        # 1. Abrir canais SSH e enviar comandos 'tail -f'
        for cmd_info in log_commands:
            log_name = cmd_info['name']
            command = cmd_info['command']
            
            console.log(f"[bold magenta]Configurando monitoramento para [italic]{log_name.upper().replace('_', ' ')}[/italic] com comando: [dim white]{command}[/dim white][/bold magenta]")
            
            try:
                chan = ssh_client.get_transport().open_session()
                chan.get_pty() # Aloca um PTY para a sessão antes de executar o comando
                chan.exec_command(command)
                
                active_channels_info.append({
                    'name': log_name,
                    'channel': chan,
                    'stdout_file': chan.makefile('rb', -1), # File-like object para leitura de stdout
                    'stderr_file': chan.makefile_stderr('rb', -1) # File-like object para leitura de stderr
                })
                console.log(f"[green]Canal SSH para {log_name.upper()} aberto com sucesso.[/green]")

            except paramiko.SSHException as e:
                console.log(f"[bold red]ERRO: Falha ao abrir canal SSH para {log_name.upper()}: {e}[/bold red]")
                console.print(f"[bold red]VERIFIQUE: Caminho do log no config.json ou permissões SSH no servidor.[/bold red]")
                time.sleep(2) # Pausa para o usuário ler a mensagem de erro
                continue # Tenta configurar o próximo log, se houver
            except Exception as e: 
                console.log(f"[bold red]ERRO DESCONHECIDO ao abrir canal para {log_name.upper()}: {e}[/bold red]")
                console.print(f"[bold red]VERIFIQUE: Detalhes do erro acima.[/bold red]")
                time.sleep(2)
                continue
            
        # Se nenhum canal pôde ser ativado, informa e retorna
        if not active_channels_info: 
            console.print("[bold red]Nenhum canal de log ativo após as tentativas de conexão. Retornando.[/bold red]")
            console.print("[dim white]Verifique o .env e config.json, e as permissões dos logs no servidor.[/dim white]")
            time.sleep(3)
            return

        # NOVO/CORRIGIDO: Lista de paramiko.Channel objects to monitor with select.select
        channels_for_select = [info['channel'] for info in active_channels_info]
        
        stop_monitoring = False # Reseta a flag para o novo ciclo de monitoramento
        logs_received = False # Flag para saber se alguma linha de log foi recebida

        # 2. Loop principal para ler e exibir logs
        while not stop_monitoring:
            if not channels_for_select: # Exit loop if all channels are closed
                console.log("[dim yellow]Todos os canais de log foram fechados. Encerrando monitoramento.[/dim yellow]")
                break

            # select.select espera por dados em qualquer canal por um curto período
            rlist, _, _ = select.select(channels_for_select, [], [], 0.01) # Small timeout for responsiveness

            if not rlist: # If no channels are ready for reading at this moment
                channels_to_remove_from_select = []
                for chan_obj in channels_for_select: # Iterate over current selectable channels
                    chan_info = next((info for info in active_channels_info if info['channel'] == chan_obj), None)
                    if not chan_info: continue

                    # Check stderr for any remaining output before checking exit status
                    stderr_output = ""
                    if chan_obj.recv_stderr_ready():
                        stderr_output = chan_info['stderr_file'].read().decode('utf-8', errors='ignore').strip()
                        if stderr_output:
                            console.print(f"[bold red]--- ERRO REMOTO EM {chan_info['name'].upper().replace('_', ' ')} (stderr): {stderr_output} ---[/bold red]")
                            logs_received = True

                    # Check if the channel has exited
                    if chan_obj.exit_status_ready():
                        exit_status = chan_obj.recv_exit_status()
                        console.log(f"[bold yellow]--- LOG DE {chan_info['name'].upper().replace('_', ' ')} ENCERRADO REMOTELY. Status: {exit_status} ---[/bold yellow]")
                        channels_to_remove_from_select.append(chan_obj) # Mark for removal
                
                for chan_obj_to_remove in channels_to_remove_from_select:
                    channels_for_select.remove(chan_obj_to_remove) # Remove from select list
                    # Also remove from active_channels_info to clean up and close files
                    chan_info_to_remove = next((info for info in active_channels_info if info['channel'] == chan_obj_to_remove), None)
                    if chan_info_to_remove:
                        chan_info_to_remove['stdout_file'].close()
                        chan_info_to_remove['stderr_file'].close()
                        active_channels_info.remove(chan_info_to_remove)
                
                # If all logs are closed and we are not manually stopping
                if not channels_for_select and not stop_monitoring:
                    final_message = "[bold magenta]Todos os logs encerrados ou comandos remotos finalizados.[/bold magenta]"
                    if not logs_received: # If no log has arrived before closing
                        final_message += "\n[bold red]Nenhuma linha de log recebida.[/bold red]"
                    console.print(f"\n{final_message}\n[dim white]Pressione Enter para voltar ao menu.[/dim white]\n")
                    time.sleep(1)
                    break 
                
                time.sleep(0.01) # Small sleep for responsiveness
                continue 

            # Process channels that are ready for reading (have new lines)
            current_batch_content = Text() # Agrupa todas as linhas lidas neste ciclo de select para um único Panel
            batch_has_content = False

            for channel_obj in rlist: # Iterate over the channel objects that are ready
                chan_info = next((info for info in active_channels_info if info['channel'] == channel_obj), None)
                if not chan_info: continue

                # Read from stdout
                lines_to_process = []
                while chan_info['channel'].recv_ready(): # Check if stdout has data
                    line = chan_info['stdout_file'].readline().decode('utf-8', errors='ignore')
                    if not line: break
                    lines_to_process.append({'type': 'stdout', 'content': line.strip()})
                
                # Read from stderr
                while chan_info['channel'].recv_stderr_ready(): # Check if stderr has data
                    line = chan_info['stderr_file'].readline().decode('utf-8', errors='ignore')
                    if not line: break
                    lines_to_process.append({'type': 'stderr', 'content': line.strip()})

                if lines_to_process:
                    logs_received = True
                    batch_has_content = True
                    
                    for item in lines_to_process:
                        line_content = item['content']
                        stream_type = item['type']

                        if not line_content: continue # Ignore empty lines after stripping

                        if stream_type == 'stdout':
                            current_batch_content.append(Text.from_markup(
                                f"[bold bright_white on deep_sky_blue4][[b bright_blue]{chan_info['name'].upper().replace('_', ' ')}[/b bright_blue]][/bold bright_white on deep_sky_blue4] [white]{line_content}[/white]"
                            ))
                        else: # stderr
                            current_batch_content.append(Text.from_markup(
                                f"[bold red on gray23][[b red]{chan_info['name'].upper().replace('_', ' ')} ERR[/b red]][/bold red on gray23] [bright_red]{line_content}[/bright_red]"
                            ))
                        current_batch_content.append("\n") # Newline after each log line

                    # Add separator after a block of logs, if there are multiple active channels
                    # and this is not the last channel in the select.select result for this batch
                    # This separator is now controlled to appear only if it's not the final channel in the batch
                    if len(log_commands) > 1 and chan_info != active_channels_info[-1] and len(rlist) > 1: # CORRIGIDO: Usar active_channels_info
                        current_batch_content.append(Text(f"[bold bright_yellow]--- FIM {chan_info['name'].upper().replace('_', ' ')} ---[/bold bright_yellow]", justify="center"))
                        current_batch_content.append("\n")

            # Imprime o Panel completo com todas as novas linhas lidas neste ciclo
            if batch_has_content:
                current_batch_content.append(Text(f"\n[dim gray]{time.strftime('%H:%M:%S')} - Atualizado[/dim gray]", justify="right"))
                console.print(Panel(
                    current_batch_content,
                    title="[bold green_yellow]Monitoramento de Logs Ativos[/bold green_yellow]",
                    border_style="green_yellow",
                    expand=True # Panel expands to full terminal width
                ))
                console.print("-" * console.width, style="dim white") # Visual separator between each printed Panel

    except Exception as e: # Catch any unexpected errors during monitoring
        console.print(f"[bold red]ERRO CRÍTICO DURANTE O MONITORAMENTO: {e}[/bold red]")
        console.print(f"[bold red]UM ERRO CRÍTICO OCORREU![/bold red]\n[white]{e}[/white]\n[bold yellow]Verifique as mensagens de log acima para detalhes.[/bold yellow]")
        time.sleep(3)
    finally:
        # Ensure all open SSH channels are closed.
        for chan_info in active_channels_info: # Iterate over the original list of channel infos
            try:
                if not chan_info['stdout_file'].closed:
                    chan_info['stdout_file'].close()
                if not chan_info['stderr_file'].closed:
                    chan_info['stderr_file'].close()
                if not chan_info['channel'].closed:
                    chan_info['channel'].close()
            except Exception as e:
                console.log(f"[dim red]Erro ao fechar canal SSH para {chan_info.get('name', 'desconhecido')}: {e}[/dim red]")
            
    console.print("[bold yellow]Voltando ao menu de seleção de serviço...[/bold yellow]")
    console.input("[yellow]Pressione Enter para continuar...[/yellow]")


def ssh_connect(hostname, username, password, log_commands_list):
    """
    Establishes an SSH connection and starts log monitoring.
    Args:
        hostname (str): Hostname or IP of the SSH server.
        username (str): SSH user.
        password (str): SSH password (read from .env).
        log_commands_list (list): List of logs to monitor.
    """
    ssh = paramiko.SSHClient()
    # Automatically add unknown host keys, be cautious in production environments.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        console.print(f"Conectando a [bold cyan]{hostname}[/bold cyan] com o usuário [bold cyan]{username}[/bold cyan]...")
        
        # Display a spinner while trying to connect
        with console.status("[bold green]Estabelecendo conexão SSH...[/bold green]", spinner="dots"):
            ssh.connect(hostname, username=username, password=password, timeout=20) 
        
        console.print("[bold green]Conexão SSH bem-sucedida![/bold green]")
        monitor_logs_normal(ssh, log_commands_list) # Call the log monitoring function
    except paramiko.AuthenticationException:
        console.print("[bold red]Erro de autenticação: Verifique usuário e senha no arquivo .env.[/bold red]")
        console.input("[yellow]Pressione Enter para continuar...[/yellow]")
    except paramiko.SSHException as e:
        console.print(f"[bold red]Erro SSH: {e}[/bold red]")
        console.input("[yellow]Pressione Enter para continuar...[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Erro ao conectar: {e}[/bold red]")
        console.input("[yellow]Pressione Enter para continuar...[/yellow]")
    finally:
        if ssh.get_transport() and ssh.get_transport().is_active():
            ssh.close()
            console.print("[dim white]Conexão SSH principal encerrada.[/dim white]")

# --- Main Menu Function ---

def main_menu():
    """
    Main function that manages navigation between log selection menus.
    Loads initial configuration and manages the navigation stack.
    """
    # Load log configuration from the JSON file
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    navigation_stack = [] # Stack to manage navigation (back, home)

    while True:
        current_level_data = config
        path_chosen = []

        # Reconstruct navigation path if returning from a submenu
        if navigation_stack:
            path_chosen = list(navigation_stack)
            for choice in path_chosen:
                current_level_data = current_level_data[choice]

        # Level 0: Client Selection
        if not path_chosen:
            title = "Seleção de Cliente"
            options = list(current_level_data.keys())
            chosen_client = get_user_choice(title, options, path_chosen)
            if chosen_client in ['b', 'h', '0']: # Handle navigation/exit commands
                if chosen_client == 'b' or chosen_client == 'h':
                    console.print("[bold yellow]Voltando ao menu principal...[/bold yellow]")
                    continue # Restart the main menu loop
                else:
                    sys.exit() # Exit the script
            navigation_stack.append(chosen_client) # Add client to stack
            path_chosen.append(chosen_client)
            current_level_data = current_level_data[chosen_client]

        # Level 1: Server Selection (e.g., mob, web)
        if len(path_chosen) == 1:
            title = f"Servidores do Cliente: {path_chosen[0].upper()}"
            options = list(current_level_data.keys())
            chosen_server = get_user_choice(title, options, path_chosen)
            if chosen_server in ['b', 'h', '0']: # Handle navigation/exit commands
                if chosen_server == 'b':
                    navigation_stack.pop() # Remove the last item from the stack to go back
                    continue
                elif chosen_server == 'h':
                    navigation_stack.clear() # Clear the stack to go to Home
                    continue
                else:
                    sys.exit()
            navigation_stack.append(chosen_server)
            path_chosen.append(chosen_server)
            current_level_data = current_level_data[chosen_server]

        # Level 2: Application Selection (e.g., logs_mobile, logs_ait)
        if len(path_chosen) == 2:
            title = f"Aplicações em {path_chosen[1].upper()} do Cliente: {path_chosen[0].upper()}"
            options = list(current_level_data.keys())
            chosen_app = get_user_choice(title, options, path_chosen)
            if chosen_app in ['b', 'h', '0']: # Handle navigation/exit commands
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

        # Level 3: Log Service Selection (e.g., socket, generator)
        if len(path_chosen) == 3:
            title = f"Serviços de Log da Aplicação '{chosen_app.replace('logs_', '').upper()}'"
            log_services = list(current_level_data.keys())
            
            clear_screen()
            console.print("\n[bold deep_sky_blue1]=" * 35 + "[/bold deep_sky_blue1]")
            console.print(Panel(Text(title, justify="center", style="bold bright_magenta"), border_style="gold1"))
            console.print("[bold deep_sky_blue1]=" * 35 + "[/bold deep_sky_blue1]")
            for i, service_name in enumerate(log_services, start=1):
                display_name = service_name.replace("_", " ").upper()
                console.print(f"[bright_green]{i}[/bright_green] - [bright_cyan]{display_name}[/bright_cyan]")
            console.print("[dim white]-" * 35 + "[/dim white]")
            console.print("[yellow]b[/yellow] - Voltar")
            console.print("[yellow]h[/yellow] - Voltar ao Menu Principal")
            console.print("[bold red]0[/bold red] - Sair")
            console.print("[bold deep_sky_blue1]=" * 35 + "[/bold deep_sky_blue1]")
            console.print("Para múltiplos logs, digite os números separados por vírgula ([italic white]ex: 1,3,5[/italic white])")
            
            chosen_services_raw = console.input("[bold light_sky_blue3]Digite a(s) opção(ões) desejada(s):[/bold light_sky_blue3] ").strip().lower()

            if chosen_services_raw == '0':
                console.print("[bold yellow]SAINDO DO SISTEMA...[/bold yellow]")
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
                        console.print(f"[bold red]Opção de serviço inválida: {idx}. Tente novamente.[/bold red]")
                        selected_log_commands = []
                        break
                
                if not selected_log_commands:
                    console.input("[yellow]Pressione Enter para continuar...[/yellow]")
                    continue

            except ValueError:
                console.print("[bold red]Opção inválida. Por favor, digite um número, 'b', 'h' ou '0' ou números separados por vírgula.[/bold red]")
                console.input("[yellow]Pressione Enter para continuar...[/yellow]")
                continue

            client = path_chosen[0]
            server = path_chosen[1]

            host = os.getenv(f"HOST_{client.upper()}_{server.upper()}")
            user = os.getenv(f"USER_{client.upper()}_{server.upper()}")
            password = os.getenv(f"PASSWORD_{client.upper()}_{server.upper()}")


            if not host or not user or not password:
                console.print(f"[bold red]Erro: Variáveis de ambiente HOST_{client.upper()}_{server.upper()}, USER_{client.upper()}_{server.upper()} ou PASSWORD_{client.upper()}_{server.upper()} não encontradas no .env.[/bold red]")
                console.input("[yellow]Pressione Enter para continuar...[/yellow]")
                continue

            # Calls the SSH connection and monitoring function (always in normal mode now)
            ssh_connect(host, user, password, selected_log_commands)
                
            continue

# --- Main Script Execution ---
if __name__ == "__main__":
    main_menu()