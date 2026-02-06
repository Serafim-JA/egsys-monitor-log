#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def show_header():
    console.print(Panel(
        "[bold cyan]egSYS Monitor - Servidor de Atualizações[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

def get_current_version():
    version_file = os.path.join(BASE_DIR, "VERSION")
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            return f.read().strip()
    return "1.0.0"

def set_version(version):
    version_file = os.path.join(BASE_DIR, "VERSION")
    with open(version_file, 'w') as f:
        f.write(version)
    console.print(f"[green]✓[/green] Versão atualizada para {version}")

def add_changelog_entry(version, changes):
    changelog_file = os.path.join(BASE_DIR, "CHANGELOG.json")
    
    if os.path.exists(changelog_file):
        with open(changelog_file, 'r') as f:
            changelog = json.load(f)
    else:
        changelog = []
    
    entry = {
        "version": version,
        "date": datetime.now().isoformat(),
        "changes": changes
    }
    
    changelog.insert(0, entry)
    
    with open(changelog_file, 'w') as f:
        json.dump(changelog, f, indent=2)
    
    console.print(f"[green]✓[/green] Changelog atualizado")

def list_clients():
    clients_file = os.path.join(BASE_DIR, "clients.json")
    
    if not os.path.exists(clients_file):
        console.print("[yellow]Nenhum cliente registrado[/yellow]")
        return
    
    with open(clients_file, 'r') as f:
        clients = json.load(f)
    
    table = Table(title="Clientes Conectados")
    table.add_column("Hostname", style="cyan")
    table.add_column("Versão", style="yellow")
    table.add_column("Último Acesso", style="dim")
    
    for client in clients:
        table.add_row(
            client.get('hostname', 'N/A'),
            client.get('version', 'N/A'),
            client.get('last_seen', 'N/A')
        )
    
    console.print(table)

def start_server(port=8080):
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:
        console.print(f"[yellow]Servidor já está rodando na porta {port}[/yellow]")
        console.print(f"[cyan]Dashboard: http://localhost:{port}/dashboard[/cyan]")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        show_menu()
        return
    
    console.print(f"[cyan]Iniciando servidor na porta {port}...[/cyan]")
    subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "update_server.py")],
                     stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    console.print(f"[green]✓[/green] Servidor iniciado em background")
    console.print(f"[cyan]Dashboard: http://localhost:{port}/dashboard[/cyan]")
    console.input("\n[dim]Pressione Enter para continuar...[/dim]")
    show_menu()

def publish_update():
    console.print("[bold cyan]Publicar Nova Atualização[/bold cyan]\n")
    
    current = get_current_version()
    console.print(f"Versão atual: [yellow]{current}[/yellow]\n")
    
    new_version = console.input("Nova versão: ").strip()
    
    if not new_version:
        console.print("[red]Versão inválida[/red]")
        return
    
    console.print("\nDigite as mudanças (uma por linha, linha vazia para finalizar):")
    changes = []
    while True:
        change = console.input("  • ").strip()
        if not change:
            break
        changes.append(change)
    
    if not changes:
        console.print("[red]Nenhuma mudança especificada[/red]")
        return
    
    set_version(new_version)
    add_changelog_entry(new_version, changes)
    
    console.print(f"\n[green]✓[/green] Atualização {new_version} publicada!")
    console.print("[dim]Os clientes receberão a atualização na próxima verificação[/dim]")

def show_menu():
    show_header()
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_running = sock.connect_ex(('localhost', 8080)) == 0
    sock.close()
    
    if server_running:
        console.print("[green]✓ Servidor Online[/green] - http://localhost:8080/dashboard\n")
    else:
        console.print("[red]✗ Servidor Offline[/red]\n")
    
    console.print("[bold]Opções:[/bold]\n")
    console.print("  [cyan]1[/cyan] - Iniciar servidor de atualizações")
    console.print("  [cyan]2[/cyan] - Publicar nova atualização")
    console.print("  [cyan]3[/cyan] - Ver clientes conectados")
    console.print("  [cyan]4[/cyan] - Ver versão atual")
    console.print("  [cyan]5[/cyan] - Abrir dashboard no navegador")
    console.print("  [red]0[/red] - Sair\n")
    
    choice = console.input("[cyan]›[/cyan] ").strip()
    
    if choice == '1':
        start_server()
    elif choice == '2':
        publish_update()
    elif choice == '3':
        list_clients()
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        show_menu()
    elif choice == '4':
        console.print(f"\nVersão atual: [yellow]{get_current_version()}[/yellow]")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        show_menu()
    elif choice == '5':
        import webbrowser
        webbrowser.open('http://localhost:8080/dashboard')
        console.print("[green]✓[/green] Dashboard aberto no navegador")
        console.input("\n[dim]Pressione Enter para continuar...[/dim]")
        show_menu()
    elif choice == '0':
        console.print("[yellow]Encerrando...[/yellow]")
        sys.exit()
    else:
        console.print("[red]Opção inválida[/red]")
        show_menu()

if __name__ == "__main__":
    show_menu()
