import os
import json
import sys
import paramiko
from dotenv import load_dotenv
import select
import time
import signal
import termios
import tty
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.live import Live
from rich.layout import Layout

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(os.path.dirname(BASE_DIR), "config", "config.json")
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

console = Console()
stop_monitoring = False

def signal_handler(sig, frame):
    global stop_monitoring
    stop_monitoring = True

signal.signal(signal.SIGINT, signal_handler)

def clear_screen():
    console.clear()

def show_header():
    header = Text()
    header.append("eg", style="bold white")
    header.append("SYS", style="bold cyan")
    header.append(" Monitor", style="bold white")
    
    console.print()
    console.print(Panel(
        Align.center(header),
        border_style="cyan",
        padding=(0, 2)
    ))
    console.print()

def display_menu(title, options_dict, current_choices):
    clear_screen()
    show_header()
    
    breadcrumb = " › ".join([c.upper() for c in current_choices]) if current_choices else "INÍCIO"
    console.print(f"[dim cyan]{breadcrumb}[/dim cyan]\n")
    
    console.print(Panel(
        Text(title, justify="center", style="bold white"),
        border_style="cyan",
        padding=(0, 2)
    ))
    console.print()

    items = list(options_dict.items()) if isinstance(options_dict, dict) else [(k, k) for k in options_dict]

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Opção", style="cyan", width=8)
    table.add_column("Descrição", style="white")

    for i, (key, display_value) in enumerate(items, start=1):
        if "logs_" in str(display_value):
            display_value = str(display_value).replace("logs_", "").upper()
        elif "_" in str(display_value) and not str(display_value).isupper():
            display_value = str(display_value).replace("_", " ").title()
        else:
            display_value = str(display_value).upper()
        
        table.add_row(f"[bold cyan]{i}[/bold cyan]", display_value)

    console.print(table)
    console.print()
    console.print("[dim]─[/dim]" * console.width)
    console.print("[yellow]b[/yellow] Voltar  [yellow]h[/yellow] Início  [red]0[/red] Sair")
    console.print("[dim]─[/dim]" * console.width)
    console.print()

    choice = console.input("[cyan]›[/cyan] ").strip().lower()
    return choice, items

def get_user_choice(title, options_data, current_choices):
    while True:
        choice, menu_items_list = display_menu(title, options_data, current_choices)

        if choice == '0':
            console.print("\n[yellow]Encerrando...[/yellow]")
            sys.exit()
        elif choice == 'b':
            return 'b'
        elif choice == 'h':
            return 'h'

        is_log_service_selection = "serviços de log" in title.lower()

        if is_log_service_selection:
            parts = [p.strip() for p in choice.split(',')]
            if all(p.isdigit() for p in parts):
                return choice
            console.print("[red]✗[/red] Entrada inválida\n")
        else:
            try:
                choice_int = int(choice)
                if 1 <= choice_int <= len(menu_items_list):
                    return menu_items_list[choice_int - 1][0]
                console.print("[red]✗[/red] Opção fora do intervalo\n")
            except ValueError:
                console.print("[red]✗[/red] Digite um número válido\n")
        
        time.sleep(1)

def monitor_logs_normal(ssh_client, log_commands):
    global stop_monitoring

    active_channels_info = []
    
    clear_screen()
    show_header()
    
    console.print(Panel(
        "[bold white]Monitoramento Ativo[/bold white]",
        border_style="green",
        padding=(0, 2)
    ))
    console.print("\n[dim]Pressione [yellow]BACKSPACE[/yellow] para voltar[/dim]\n")
    
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
    except:
        pass
    
    total_lines = 0
    warning_lines = 0
    error_lines = 0
    start_time = time.time()
    last_stats_print_time = time.time()

    try:
        for cmd_info in log_commands:
            log_name = cmd_info['name']
            command = cmd_info['command']
            
            console.print(f"[cyan]•[/cyan] Conectando ao log [bold]{log_name.upper().replace('_', ' ')}[/bold]")
            
            try:
                chan = ssh_client.get_transport().open_session()
                chan.get_pty()
                chan.exec_command(command)
                
                active_channels_info.append({
                    'name': log_name,
                    'channel': chan,
                    'stdout_file': chan.makefile('rb', -1),
                    'stderr_file': chan.makefile_stderr('rb', -1)
                })
                console.print(f"[green]✓[/green] {log_name.upper()} conectado")
            except Exception as e:
                console.print(f"[red]✗[/red] Falha em {log_name.upper()}: {e}")
                time.sleep(1)
                continue
            
        if not active_channels_info:
            console.print("\n[red]Nenhum canal ativo[/red]")
            time.sleep(2)
            return

        console.print(f"\n[dim]{'─' * console.width}[/dim]\n")
        
        channels_for_select = [info['channel'] for info in active_channels_info]
        stop_monitoring = False
        logs_received = False

        while not stop_monitoring:
            if time.time() - last_stats_print_time >= 60:
                elapsed = int(time.time() - start_time)
                console.print(f"\n[dim]Stats: {total_lines} linhas | {warning_lines} warnings | {error_lines} erros | {elapsed}s[/dim]")
                last_stats_print_time = time.time()

            if not channels_for_select:
                break

            stdin_list = [sys.stdin] if sys.stdin.isatty() else []
            try:
                rlist, _, _ = select.select(channels_for_select + stdin_list, [], [], 0.1)
            except (KeyboardInterrupt, select.error):
                stop_monitoring = True
                break
            
            if sys.stdin in rlist:
                try:
                    key = sys.stdin.read(1)
                    if key in ['\x7f', '\x08']:
                        stop_monitoring = True
                        console.print("\n[yellow]Encerrando monitoramento...[/yellow]")
                        break
                except:
                    pass
                rlist.remove(sys.stdin)

            if not rlist:
                channels_to_remove = []
                for chan_obj in channels_for_select:
                    chan_info = next((info for info in active_channels_info if info['channel'] == chan_obj), None)
                    if not chan_info:
                        continue

                    if chan_obj.exit_status_ready():
                        channels_to_remove.append(chan_obj)
                
                for chan_obj in channels_to_remove:
                    channels_for_select.remove(chan_obj)
                    chan_info = next((info for info in active_channels_info if info['channel'] == chan_obj), None)
                    if chan_info:
                        try:
                            chan_info['stdout_file'].close()
                            chan_info['stderr_file'].close()
                        except:
                            pass
                        active_channels_info.remove(chan_info)
                
                if not channels_for_select and not stop_monitoring:
                    break
                
                continue

            for channel_obj in rlist:
                chan_info = next((info for info in active_channels_info if info['channel'] == channel_obj), None)
                if not chan_info:
                    continue

                while chan_info['channel'].recv_ready():
                    try:
                        line = chan_info['stdout_file'].readline().decode('utf-8', errors='ignore').strip()
                        if not line:
                            break
                        
                        logs_received = True
                        total_lines += 1
                        
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        log_name = chan_info['name'].upper().replace('_', ' ')
                        
                        if "error" in line.lower():
                            error_lines += 1
                            console.print(f"[dim]{timestamp}[/dim] [red]●[/red] [bold cyan]{log_name}[/bold cyan] [red]{line}[/red]")
                        elif "warning" in line.lower():
                            warning_lines += 1
                            console.print(f"[dim]{timestamp}[/dim] [yellow]●[/yellow] [bold cyan]{log_name}[/bold cyan] [yellow]{line}[/yellow]")
                        else:
                            console.print(f"[dim]{timestamp}[/dim] [green]●[/green] [bold cyan]{log_name}[/bold cyan] {line}")
                    except:
                        break

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrompido[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Erro: {e}[/red]")
    finally:
        stop_monitoring = True
        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        except:
            pass
        
        elapsed = int(time.time() - start_time)
        console.print(f"\n[dim]{'─' * console.width}[/dim]\n")
        
        stats_table = Table(show_header=False, box=None, padding=(0, 2))
        stats_table.add_column("Métrica", style="dim")
        stats_table.add_column("Valor", style="bold")
        stats_table.add_row("Total de linhas", f"[green]{total_lines}[/green]")
        stats_table.add_row("Warnings", f"[yellow]{warning_lines}[/yellow]")
        stats_table.add_row("Erros", f"[red]{error_lines}[/red]")
        stats_table.add_row("Duração", f"[cyan]{elapsed}s[/cyan]")
        
        console.print(Panel(stats_table, title="[bold]Resumo da Sessão[/bold]", border_style="cyan"))
        console.print()

        for chan_info in active_channels_info:
            try:
                chan = chan_info['channel']
                if not chan.closed:
                    try:
                        chan.send('\x03')
                        time.sleep(0.05)
                    except:
                        pass
                chan_info['stdout_file'].close()
                chan_info['stderr_file'].close()
                chan.close()
            except:
                pass
    
    time.sleep(2)

def ssh_connect(hostname, username, password, log_commands_list):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        console.print(f"\n[cyan]Conectando a {hostname}...[/cyan]")
        
        with console.status("[cyan]Estabelecendo conexão SSH...[/cyan]", spinner="dots"):
            ssh.connect(hostname, username=username, password=password, timeout=20)
        
        console.print("[green]✓[/green] Conectado\n")
        time.sleep(0.5)
        
        monitor_logs_normal(ssh, log_commands_list)
    except paramiko.AuthenticationException:
        console.print("[red]✗[/red] Falha na autenticação")
        time.sleep(2)
    except Exception as e:
        console.print(f"[red]✗[/red] Erro: {e}")
        time.sleep(2)
    finally:
        if ssh.get_transport() and ssh.get_transport().is_active():
            ssh.close()

def main_menu():
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]Erro: config.json não encontrado[/red]")
        sys.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]Erro: config.json inválido[/red]")
        sys.exit(1)

    navigation_stack = []

    while True:
        current_level_data = config
        path_chosen = []

        if navigation_stack:
            path_chosen = list(navigation_stack)
            for choice in path_chosen:
                current_level_data = current_level_data[choice]

        if not path_chosen:
            title = "Selecione o Cliente"
            options = list(current_level_data.keys())
            chosen_client = get_user_choice(title, options, path_chosen)
            if chosen_client in ['b', 'h', '0']:
                if chosen_client == 'b' or chosen_client == 'h':
                    navigation_stack.clear()
                    continue
                else:
                    sys.exit()
            navigation_stack.append(chosen_client)
            continue

        if len(path_chosen) == 1:
            title = f"Selecione o Servidor"
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
            continue

        if len(path_chosen) == 2:
            title = f"Selecione a Aplicação"
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
            continue

        if len(path_chosen) == 3:
            title = "Selecione os Serviços de Log"
            log_services = list(current_level_data.keys())
            
            chosen_service_input = get_user_choice(title, log_services, path_chosen)
            
            if chosen_service_input == 'b':
                navigation_stack.pop()
                continue
            elif chosen_service_input == 'h':
                navigation_stack.clear()
                continue
            elif chosen_service_input == '0':
                sys.exit()
            
            selected_log_commands = []
            try:
                service_choices_str = [s.strip() for s in chosen_service_input.split(',')]
                service_indices = []
                
                for s_choice in service_choices_str:
                    try:
                        idx = int(s_choice)
                        if 1 <= idx <= len(log_services):
                            service_indices.append(idx)
                        else:
                            console.print(f"[red]✗[/red] Opção {idx} inválida")
                            selected_log_commands = []
                            break
                    except ValueError:
                        console.print(f"[red]✗[/red] Entrada inválida: {s_choice}")
                        selected_log_commands = []
                        break

                if not service_indices:
                    time.sleep(1)
                    continue

                for idx in service_indices:
                    service_key = log_services[idx - 1]
                    command_str = current_level_data[service_key]
                    selected_log_commands.append({
                        'name': service_key,
                        'command': command_str
                    })
                
                if not selected_log_commands:
                    time.sleep(1)
                    continue

            except Exception as e:
                console.print(f"[red]Erro: {e}[/red]")
                time.sleep(1)
                continue

            client = path_chosen[0]
            server = path_chosen[1]

            host = os.getenv(f"HOST_{client.upper()}_{server.upper()}")
            user = os.getenv(f"USER_{client.upper()}_{server.upper()}")
            password = os.getenv(f"PASSWORD_{client.upper()}_{server.upper()}")

            if not host or not user or not password:
                console.print(f"[red]✗[/red] Credenciais não encontradas no .env")
                time.sleep(2)
                continue

            # Verificar se socket foi selecionado e oferecer filtro por idGuarnicao ou IMEI
            socket_selected = any(cmd['name'] == 'socket' for cmd in selected_log_commands)
            if socket_selected:
                console.print("\n[bold cyan]Opção para SOCKET:[/bold cyan]")
                console.print("1. Monitoramento normal")
                console.print("2. Pesquisar por idGuarnicao específico")
                console.print("3. Pesquisar por IMEI específico")
                choice = input("Escolha (1, 2 ou 3): ").strip()
                
                if choice == '2':
                    id_guarnicao = input("Digite o idGuarnicao: ").strip()
                    if id_guarnicao:
                        # Modificar o comando do socket para incluir grep
                        for cmd in selected_log_commands:
                            if cmd['name'] == 'socket':
                                cmd['command'] += f" | grep 'idGuarnicao={id_guarnicao}'"
                                console.print(f"[green]✓[/green] Filtro aplicado: idGuarnicao={id_guarnicao}")
                                break
                    else:
                        console.print("[yellow]Nenhum idGuarnicao informado, usando monitoramento normal[/yellow]")
                
                elif choice == '3':
                    imei = input("Digite o IMEI: ").strip()
                    if imei:
                        # Modificar o comando do socket para incluir grep
                        for cmd in selected_log_commands:
                            if cmd['name'] == 'socket':
                                cmd['command'] += f" | grep '{imei}'"
                                console.print(f"[green]✓[/green] Filtro aplicado: IMEI={imei}")
                                break
                    else:
                        console.print("[yellow]Nenhum IMEI informado, usando monitoramento normal[/yellow]")

            ssh_connect(host, user, password, selected_log_commands)
            continue

if __name__ == "__main__":
    main_menu()
