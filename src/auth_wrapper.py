import os
import sys
import socket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from auth_manager import AuthManager
from update_manager import UpdateManager
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def show_auth_screen():
    console.clear()
    
    header = Text()
    header.append("eg", style="bold white")
    header.append("SYS", style="bold cyan")
    header.append(" Monitor", style="bold white")
    
    console.print()
    console.print(Panel(
        header,
        title="[bold cyan]Sistema de Autenticação[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()

def main():
    show_auth_screen()
    
    auth_file = os.path.join(os.path.dirname(BASE_DIR), "config", "authorized_keys.json")
    auth_manager = AuthManager(auth_file)
    
    console.print("[cyan]Verificando autenticação...[/cyan]\n")
    
    authenticated, result = auth_manager.authenticate()
    
    if not authenticated:
        console.print(Panel(
            f"[bold red]✗ Acesso Negado[/bold red]\n\n{result}",
            border_style="red",
            padding=(1, 2)
        ))
        console.print("\n[dim]Contate o administrador para autorizar sua chave SSH.[/dim]")
        sys.exit(1)
    
    user = result
    console.print(Panel(
        f"[bold green]✓ Autenticado com Sucesso[/bold green]\n\n"
        f"Usuário: [cyan]{user['name']}[/cyan]\n"
        f"Email: [dim]{user['email']}[/dim]\n"
        f"Função: [yellow]{user['role'].upper()}[/yellow]",
        border_style="green",
        padding=(1, 2)
    ))
    
    auth_manager.log_access(user, "login")
    
    console.print("\n[cyan]Verificando atualizações...[/cyan]")
    
    update_manager = UpdateManager(os.path.dirname(BASE_DIR))
    has_update, version, changelog = update_manager.check_for_updates()
    
    if has_update:
        console.print(Panel(
            f"[bold yellow]Nova versão disponível: {version}[/bold yellow]\n\n" +
            "\n".join([f"• {change}" for change in changelog[:5]]),
            title="[bold]Atualização Disponível[/bold]",
            border_style="yellow",
            padding=(1, 2)
        ))
        
        if update_manager.config.get('auto_update'):
            console.print("\n[cyan]Baixando atualização...[/cyan]")
            success, update_file = update_manager.download_update(version)
            
            if success:
                console.print("[green]✓[/green] Download concluído")
                console.print("[cyan]Aplicando atualização...[/cyan]")
                
                if update_manager.apply_update(update_file):
                    console.print("[green]✓[/green] Atualização aplicada com sucesso!")
                    console.print("[yellow]Reinicie o sistema para usar a nova versão[/yellow]")
                else:
                    console.print("[red]✗[/red] Falha ao aplicar atualização")
            else:
                console.print("[red]✗[/red] Falha no download")
    else:
        console.print("[green]✓[/green] Sistema atualizado (v{version})")
    
    import requests
    try:
        hostname = socket.gethostname()
        requests.post(
            f"{update_manager.config['update_server']}/api/register",
            json={
                'hostname': hostname,
                'version': update_manager.get_current_version(),
                'user': user['name']
            },
            timeout=2
        )
    except:
        pass
    
    console.print("\n[dim]Iniciando monitor...[/dim]\n")
    
    import time
    time.sleep(1)
    
    from log_monitor import main_menu
    main_menu()

if __name__ == "__main__":
    main()
