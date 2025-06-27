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
CONFIG_PATH = os.path.join(os.path.dirname(BASE_DIR), "config", "config.json")
ENV_PATH = os.path.join(os.path.dirname(BASE_DIR), ".env")

load_dotenv(ENV_PATH)

console = Console()

stop_monitoring = False

def signal_handler(sig, frame):
    global stop_monitoring
    console.print("\n[bold yellow]Sinal de interrupção (Ctrl+C) recebido. Encerrando monitoramento...[/bold yellow]")
    stop_monitoring = True

signal.signal(signal.SIGINT, signal_handler)

# --- Funções Auxiliares ---

def clear_screen():
    console.clear()

def display_menu(title, options_dict, current_choices):
    clear_screen()
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
                return items[choice_int - 1][0]
            else:
                console.print("[bold red]Opção inválida. Tente novamente.[/bold red]")
        except ValueError:
            console.print("[bold red]Opção inválida. Por favor, digite um número, 'b', 'h' ou '0'.[/bold red]")
        console.input("[yellow]Pressione Enter para continuar...[/yellow]")

def monitor_logs_normal(ssh_client, log_commands):
    global stop_monitoring

    active_channels = []
    log_buffers = {cmd['name']: [] for cmd in log_commands}
    max_display_lines = max(10, console.height - 8) 

    live_panel_text_content = Text("[bold magenta]Aguardando a primeira linha de log...[/bold magenta]\n[dim white]Verifique se os serviços estão ativos e gerando logs.[/dim white]", justify="center", style="dim")
    
    live_log_panel = Panel(
        Align.center(live_panel_text_content, vertical="middle"),
        title="[bold green_yellow]Monitoramento de Logs Ativos[/bold green_yellow]",
        border_style="green_yellow",
        height=console.height - 2
    )

    with Live(live_log_panel, screen=True, refresh_per_second=8) as live:
        try:
            # Abrindo canais SSH e enviando comandos
            for cmd_info in log_commands:
                log_name = cmd_info['name']
                command = cmd_info['command']
                
                console.log(f"[bold magenta]Configurando monitoramento para [italic]{log_name.upper().replace('_', ' ')}[/italic] com comando: [dim white]{command}[/dim white][/bold magenta]")
                
                try:
                    chan = ssh_client.get_transport().open_session()
                    chan.exec_command(command)
                    active_channels.append({
                        'name': log_name,
                        'channel': chan,
                        'stdout': chan.makefile('rb', -1),
                        'stderr': chan.makefile_stderr('rb', -1)
                    })
                    console.log(f"[green]Canal SSH para {log_name.upper()} aberto com sucesso.[/green]")
                    
                    # Atualiza o painel para mostrar que está conectando aos logs
                    live_panel_text_content.plain = f"[bold magenta]Conectando a {log_name.upper().replace('_', ' ')}...[/bold magenta]\n[white]Aguardando dados...[/white]" # Corrigido para [white]
                    live_log_panel.renderable = Align.center(live_panel_text_content, vertical="middle") 
                    live.update(live_log_panel)

                except paramiko.SSHException as e:
                    console.log(f"[bold red]ERRO: Falha ao abrir canal SSH para {log_name.upper()}: {e}[/bold red]")
                    live_panel_text_content.plain = f"[bold red]ERRO ao conectar a {log_name.upper()}![/bold red]\n[white]{e}[/white]\n[bold yellow]Verifique o caminho do log ou permissões.[/bold yellow]" # Corrigido para [white]
                    live_log_panel.renderable = Align.center(live_panel_text_content, vertical="middle")
                    live.update(live_log_panel)
                    time.sleep(2)
                    continue
                except Exception as e:
                    console.log(f"[bold red]ERRO DESCONHECIDO ao abrir canal para {log_name.upper()}: {e}[/bold red]")
                    live_panel_text_content.plain = f"[bold red]ERRO DESCONHECIDO ao conectar a {log_name.upper()}![/bold red]\n[white]{e}[/white]" # Corrigido para [white]
                    live_log_panel.renderable = Align.center(live_panel_text_content, vertical="middle")
                    live.update(live_log_panel)
                    time.sleep(2)
                    continue
                
            if not active_channels:
                console.log("[bold red]Nenhum canal de log ativo após as tentativas de conexão. Retornando.[/bold red]")
                live_panel_text_content.plain = "[bold red]Nenhum log disponível ou erro na conexão.[/bold red]\n[white]Verifique o .env e config.json, e as permissões dos logs no servidor.[/white]" # Corrigido para [white]
                live_log_panel.renderable = Align.center(live_panel_text_content, vertical="middle")
                live.update(live_log_panel)
                time.sleep(3)
                return

            readable_fds = [chan_info['channel'] for chan_info in active_channels]
            stop_monitoring = False # Reinicia a flag antes de entrar no loop principal

            logs_received = False

            # Loop principal de monitoramento
            while not stop_monitoring:
                if not active_channels:
                    break

                rlist, _, _ = select.select(readable_fds, [], [], 0.05) 

                if not rlist:
                    channels_to_remove = []
                    for channel_info in active_channels:
                        if channel_info['channel'].exit_status_ready():
                            exit_status = channel_info['channel'].recv_exit_status()
                            console.log(f"[bold yellow]--- LOG DE {channel_info['name'].upper().replace('_', ' ')} ENCERRADO REMOTAMENTE. Status: {exit_status} ---[/bold yellow]")
                            channels_to_remove.append(channel_info)
                    
                    for channel_info in channels_to_remove:
                        active_channels.remove(channel_info)
                        readable_fds = [c for c in readable_fds if c != channel_info['channel']]
                        if channel_info['name'] in log_buffers:
                            del log_buffers[channel_info['name']]
                    
                    if not active_channels and not stop_monitoring:
                        final_message = "[bold magenta]Todos os logs encerrados ou comandos remotos finalizados.[/bold magenta]"
                        if not logs_received:
                            final_message += "\n[bold red]Nenhuma linha de log recebida.[/bold red]"
                        live_panel_text_content.plain = f"{final_message}\n[white]Pressione Ctrl+C para voltar ao menu.[/white]" # Corrigido para [white]
                        live_log_panel.renderable = Align.center(live_panel_text_content, vertical="middle")
                        live.update(live_log_panel)
                        time.sleep(3) 
                        break 
                    
                    time.sleep(0.1)
                    continue 

                # Processa os canais que estão prontos para leitura
                for channel_obj in rlist:
                    current_chan_info = next((item for item in active_channels if item['channel'] == channel_obj), None)
                    if current_chan_info:
                        line = current_chan_info['stdout'].readline().decode('utf-8', errors='ignore').strip()
                        
                        if line:
                            logs_received = True
                            log_buffers[current_chan_info['name']].append(Text.from_markup(
                                # Corrigido: Cor do texto do log para [white]
                                f"[bright_white on #005f87][[b blue]{current_chan_info['name'].upper().replace('_', ' ')}[/b blue]][/bright_white on #005f87] [white]{line}[/white]"
                            ))
                            # Limita o buffer para não sobrecarregar a tela
                            if len(log_buffers[current_chan_info['name']]) > max_display_lines:
                                log_buffers[current_chan_info['name']].pop(0)

                            # Constrói o conteúdo total dos logs para o painel
                            combined_logs_content_rich = Text() 
                            
                            # Garante a ordem consistente dos logs
                            for name_info in log_commands: 
                                name_key = name_info['name']
                                if name_key in log_buffers and log_buffers[name_key]:
                                    for buffered_line in log_buffers[name_key]:
                                        combined_logs_content_rich.append(buffered_line)
                                        combined_logs_content_rich.append("\n") 
                                    
                                    # Adiciona separador entre logs se houver mais de um log ativo
                                    if len(log_commands) > 1 and len(active_channels) > 1 and name_info != log_commands[-1]:
                                        # Corrigido: Cor do separador para [bold yellow]
                                        combined_logs_content_rich.append(Text(f"[bold yellow]--- FIM {name_key.upper().replace('_', ' ')} ---[/bold yellow]", justify="center"))
                                        combined_logs_content_rich.append("\n")

                            # Adiciona um marcador de tempo para indicar atividade recente
                            if combined_logs_content_rich.plain: 
                                combined_logs_content_rich.append(Text(f"\n[dim gray]{time.strftime('%H:%M:%S')} - Atualizado[/dim gray]", justify="right"))
                                
                                # CORRIGIDO: Passar o objeto Text diretamente para o Panel
                                live_log_panel.renderable = Panel(
                                    combined_logs_content_rich, 
                                    title="[bold green_yellow]Monitoramento de Logs Ativos[/bold green_yellow]",
                                    border_style="green_yellow",
                                    height=console.height - 2
                                )
                                live.update(live_log_panel)

                        elif current_chan_info['channel'].exit_status_ready():
                            pass
                            
        except Exception as e:
            console.print(f"[bold red]ERRO CRÍTICO DURANTE O MONITORAMENTO: {e}[/bold red]")
            live_panel_text_content.plain = f"[bold red]UM ERRO CRÍTICO OCORREU![/bold red]\n[white]{e}[/white]\n[bold yellow]Verifique as mensagens de log abaixo para detalhes.[/bold yellow]" # Corrigido para [white]
            live_log_panel.renderable = Align.center(live_panel_text_content, vertical="middle")
            live.update(live_log_panel)
            time.sleep(3)
        finally:
            for channel_info in active_channels:
                try:
                    if not channel_info['stdout'].closed:
                        channel_info['stdout'].close()
                    if not channel_info['stderr'].closed:
                        channel_info['stderr'].close()
                    if not channel_info['channel'].closed:
                        channel_info['channel'].close()
                except Exception as e:
                    console.log(f"[dim red]Erro ao fechar canal SSH para {channel_info.get('name', 'desconhecido')}: {e}[/dim red]")
            
    console.print("[bold yellow]Voltando ao menu de seleção de serviço...[/bold yellow]")
    console.input("[yellow]Pressione Enter para continuar...[/yellow]")


def ssh_connect(hostname, username, password, log_commands_list):
    """
    Conecta a um servidor via SSH e inicia o monitoramento de logs no modo normal.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        console.print(f"Conectando a [bold cyan]{hostname}[/bold cyan] com o usuário [bold cyan]{username}[/bold cyan]...")
        
        with console.status("[bold green]Estabelecendo conexão SSH...[/bold green]", spinner="dots"):
            ssh.connect(hostname, username=username, password=password, timeout=20) 
        
        console.print("[bold green]Conexão SSH bem-sucedida![/bold green]")
        monitor_logs_normal(ssh, log_commands_list)
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

        if not path_chosen:
            title = "Seleção de Cliente"
            options = list(current_level_data.keys())
            chosen_client = get_user_choice(title, options, path_chosen)
            if chosen_client in ['b', 'h', '0']:
                if chosen_client == 'b' or chosen_client == 'h':
                    console.print("[bold yellow]Voltando ao menu principal...[/bold yellow]")
                    continue
                else:
                    sys.exit()
            navigation_stack.append(chosen_client)
            path_chosen.append(chosen_client)
            current_level_data = current_level_data[chosen_client]

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

            ssh_connect(host, user, password, selected_log_commands)
                
            continue

# --- Execução ---
if __name__ == "__main__":
    main_menu()