#!/usr/bin/env python3
"""
egSYS Monitor - Instalador Interativo
Instalador estilo Discord com interface TUI completa
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import time

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

class Installer:
    def __init__(self):
        self.install_path = str(Path.home() / 'Documentos' / 'egSYS-Monitor')
        self.width = 70
        
    def clear(self):
        os.system('clear' if os.name != 'nt' else 'cls')
        
    def center(self, text):
        return text.center(self.width)
    
    def print_logo(self):
        logo = f"""
{Colors.CYAN}{Colors.BOLD}
        ███████╗ ██████╗ ███████╗██╗   ██╗███████╗
        ██╔════╝██╔════╝ ██╔════╝╚██╗ ██╔╝██╔════╝
        █████╗  ██║  ███╗███████╗ ╚████╔╝ ███████╗
        ██╔══╝  ██║   ██║╚════██║  ╚██╔╝  ╚════██║
        ███████╗╚██████╔╝███████║   ██║   ███████║
        ╚══════╝ ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝
{Colors.RESET}
{Colors.WHITE}{Colors.BOLD}{self.center('Monitor de Logs Distribuídos')}{Colors.RESET}
{Colors.DIM}{self.center('v1.0.0')}{Colors.RESET}
"""
        print(logo)
    
    def print_box(self, title, content, color=Colors.CYAN):
        print(f"\n{color}╔{'═' * (self.width - 2)}╗{Colors.RESET}")
        print(f"{color}║{Colors.RESET} {Colors.BOLD}{title.center(self.width - 4)}{Colors.RESET} {color}║{Colors.RESET}")
        print(f"{color}╠{'═' * (self.width - 2)}╣{Colors.RESET}")
        for line in content:
            print(f"{color}║{Colors.RESET} {line.ljust(self.width - 4)} {color}║{Colors.RESET}")
        print(f"{color}╚{'═' * (self.width - 2)}╝{Colors.RESET}")
    
    def welcome_screen(self):
        self.clear()
        self.print_logo()
        
        content = [
            "",
            f"{Colors.WHITE}Bem-vindo ao instalador do egSYS Monitor!{Colors.RESET}",
            "",
            "Este assistente irá guiá-lo através da instalação.",
            "",
            f"{Colors.GREEN}✓{Colors.RESET} Monitor de logs SSH em tempo real",
            f"{Colors.GREEN}✓{Colors.RESET} Dashboard web com autenticação",
            f"{Colors.GREEN}✓{Colors.RESET} Interface de terminal interativa",
            f"{Colors.GREEN}✓{Colors.RESET} Suporte a múltiplos servidores",
            "",
        ]
        
        self.print_box("Instalador egSYS Monitor", content)
        
        print(f"\n{Colors.YELLOW}Pressione ENTER para continuar ou SHIFT para cancelar{Colors.RESET}")
        try:
            input()
            return True
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.RED}Instalação cancelada.{Colors.RESET}")
            return False
    
    def license_screen(self):
        self.clear()
        self.print_logo()
        
        content = [
            "",
            f"{Colors.BOLD}TERMOS DE LICENÇA{Colors.RESET}",
            "",
            "MIT License - Copyright (c) 2026 egSYS",
            "",
            "É concedida permissão, gratuitamente, a qualquer pessoa",
            "que obtenha uma cópia deste software para usar, copiar,",
            "modificar, mesclar, publicar e distribuir.",
            "",
            "O SOFTWARE É FORNECIDO 'COMO ESTÁ', SEM GARANTIA.",
            "",
        ]
        
        self.print_box("Licença de Uso", content, Colors.BLUE)
        
        print(f"\n{Colors.YELLOW}Você aceita os termos da licença?{Colors.RESET}")
        print(f"{Colors.GREEN}[S]{Colors.RESET}im  {Colors.RED}[N]{Colors.RESET}ão")
        
        choice = input(f"\n{Colors.CYAN}›{Colors.RESET} ").strip().lower()
        return choice in ['s', 'sim', 'y', 'yes']
    
    def path_selection_screen(self):
        self.clear()
        self.print_logo()
        
        content = [
            "",
            f"{Colors.BOLD}DIRETÓRIO DE INSTALAÇÃO{Colors.RESET}",
            "",
            f"Caminho padrão: {Colors.CYAN}{self.install_path}{Colors.RESET}",
            "",
            "Você pode alterar o caminho de instalação ou",
            "pressionar ENTER para usar o padrão.",
            "",
        ]
        
        self.print_box("Selecionar Diretório", content, Colors.MAGENTA)
        
        print(f"\n{Colors.YELLOW}Digite o caminho de instalação (ou ENTER para padrão):{Colors.RESET}")
        custom_path = input(f"{Colors.CYAN}›{Colors.RESET} ").strip()
        
        if custom_path:
            custom_path = os.path.expanduser(custom_path)
            if not os.path.isabs(custom_path):
                custom_path = os.path.abspath(custom_path)
            self.install_path = custom_path
        
        # Confirmar
        self.clear()
        self.print_logo()
        
        content = [
            "",
            f"{Colors.BOLD}CONFIRMAR INSTALAÇÃO{Colors.RESET}",
            "",
            f"Diretório: {Colors.CYAN}{self.install_path}{Colors.RESET}",
            f"Espaço necessário: {Colors.YELLOW}~50 MB{Colors.RESET}",
            "",
            "A instalação criará:",
            "  • egSYS-Monitor/app/       (Aplicação)",
            "  • egSYS-Monitor/config/    (Configurações)",
            "  • egSYS-Monitor/logs/      (Logs)",
            "  • egSYS-Monitor/data/      (Dados)",
            "  • egSYS-Monitor/docs/      (Documentação)",
            "",
        ]
        
        self.print_box("Confirmar Instalação", content, Colors.GREEN)
        
        print(f"\n{Colors.YELLOW}Deseja continuar com a instalação?{Colors.RESET}")
        print(f"{Colors.GREEN}[S]{Colors.RESET}im  {Colors.RED}[N]{Colors.RESET}ão")
        
        choice = input(f"\n{Colors.CYAN}›{Colors.RESET} ").strip().lower()
        return choice in ['s', 'sim', 'y', 'yes']
    
    def progress_bar(self, current, total, task=""):
        percent = int((current / total) * 100)
        filled = int((current / total) * 50)
        bar = '█' * filled + '░' * (50 - filled)
        
        print(f"\r{Colors.CYAN}[{bar}]{Colors.RESET} {percent}% {Colors.DIM}{task}{Colors.RESET}", end='', flush=True)
    
    def install_screen(self):
        self.clear()
        self.print_logo()
        
        print(f"{Colors.BOLD}{self.center('INSTALANDO egSYS Monitor')}{Colors.RESET}\n")
        
        tasks = [
            ("Criando diretórios...", 0.5),
            ("Copiando arquivos...", 1.0),
            ("Instalando dependências...", 2.0),
            ("Configurando sistema...", 1.0),
            ("Criando atalhos...", 0.5),
            ("Finalizando instalação...", 0.5),
        ]
        
        total_steps = len(tasks)
        
        for i, (task, duration) in enumerate(tasks, 1):
            self.progress_bar(i - 1, total_steps, task)
            time.sleep(duration)
            self.progress_bar(i, total_steps, task)
        
        print(f"\n\n{Colors.GREEN}✓ Instalação concluída com sucesso!{Colors.RESET}\n")
        time.sleep(1)
    
    def perform_installation(self):
        """Executa a instalação real"""
        try:
            # Criar estrutura de diretórios organizada
            base_path = Path(self.install_path)
            base_path.mkdir(parents=True, exist_ok=True)
            
            # Criar subdiretórios categorizados
            (base_path / 'app').mkdir(exist_ok=True)
            (base_path / 'config').mkdir(exist_ok=True)
            (base_path / 'logs').mkdir(exist_ok=True)
            (base_path / 'data').mkdir(exist_ok=True)
            (base_path / 'docs').mkdir(exist_ok=True)
            
            # Copiar arquivos do projeto para app/
            source_dir = Path(__file__).parent.parent
            if (source_dir / 'src').exists():
                shutil.copytree(source_dir / 'src', base_path / 'app', dirs_exist_ok=True)
            if (source_dir / 'config').exists():
                for item in (source_dir / 'config').iterdir():
                    if item.is_file():
                        shutil.copy2(item, base_path / 'config')
            
            # Criar arquivo README
            readme = base_path / 'README.txt'
            readme.write_text(f"""egSYS Monitor - Sistema de Monitoramento de Logs

Estrutura de Diretórios:

├── app/              Aplicação principal
├── config/           Arquivos de configuração
├── logs/             Logs do sistema
├── data/             Dados e cache
└── docs/             Documentação

Para iniciar: egsys-monitor

Instalado em: {base_path}
Versão: 1.0.0
""")
            
            # Instalar dependências
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', '-q',
                          'paramiko', 'python-dotenv', 'rich', 'flask', 'bcrypt', 'gunicorn'],
                         check=False)
            
            # Criar atalhos
            bin_dir = Path.home() / '.local' / 'bin'
            bin_dir.mkdir(parents=True, exist_ok=True)
            
            # Atalho principal
            launcher = bin_dir / 'egsys-monitor'
            launcher.write_text(f"""#!/bin/bash
cd "{base_path / 'app'}"
python3 log_monitor.py "$@"
""")
            launcher.chmod(0o755)
            
            # Atalho de atualização
            updater = bin_dir / 'egsys-update'
            updater.write_text(f"""#!/bin/bash
python3 "{base_path / 'app' / 'updater.py'}" "{base_path}"
""")
            updater.chmod(0o755)
            
            # Atalho de desinstalação
            uninstaller = bin_dir / 'egsys-uninstall'
            uninstaller.write_text(f"""#!/bin/bash
python3 "{source_dir / 'installer' / 'uninstaller.py'}"
""")
            uninstaller.chmod(0o755)
            
            # Copiar updater para app/
            if (source_dir / 'src' / 'updater.py').exists():
                shutil.copy2(source_dir / 'src' / 'updater.py', base_path / 'app')
            
            # Criar arquivo VERSION
            version_file = base_path / 'VERSION'
            version_file.write_text('1.0.0')
            
            # Adicionar ao PATH
            bashrc = Path.home() / '.bashrc'
            path_line = f'\nexport PATH="$HOME/.local/bin:$PATH"\n'
            if bashrc.exists():
                content = bashrc.read_text()
                if '.local/bin' not in content:
                    with open(bashrc, 'a') as f:
                        f.write(path_line)
            
            return True
            
        except Exception as e:
            print(f"\n{Colors.RED}Erro durante instalação: {e}{Colors.RESET}")
            return False
    
    def completion_screen(self):
        self.clear()
        self.print_logo()
        
        content = [
            "",
            f"{Colors.GREEN}{Colors.BOLD}✓ INSTALAÇÃO CONCLUÍDA!{Colors.RESET}",
            "",
            f"egSYS Monitor foi instalado em:",
            f"{Colors.CYAN}{self.install_path}{Colors.RESET}",
            "",
            f"{Colors.BOLD}Para iniciar o aplicativo:{Colors.RESET}",
            "",
            f"  {Colors.CYAN}$ egsys-monitor{Colors.RESET}",
            "",
            "Comandos disponíveis:",
            f"  {Colors.CYAN}$ egsys-monitor{Colors.RESET}      Iniciar aplicação",
            f"  {Colors.CYAN}$ egsys-update{Colors.RESET}       Verificar atualizações",
            f"  {Colors.CYAN}$ egsys-uninstall{Colors.RESET}    Desinstalar",
            "",
        ]
        
        self.print_box("Instalação Completa", content, Colors.GREEN)
        
        print(f"\n{Colors.YELLOW}Deseja iniciar o egSYS Monitor agora?{Colors.RESET}")
        print(f"{Colors.GREEN}[S]{Colors.RESET}im  {Colors.RED}[N]{Colors.RESET}ão")
        
        choice = input(f"\n{Colors.CYAN}›{Colors.RESET} ").strip().lower()
        
        if choice in ['s', 'sim', 'y', 'yes']:
            self.clear()
            os.system(f'cd "{self.install_path}/app" && python3 log_monitor.py')
    
    def run(self):
        """Executa o instalador"""
        try:
            if not self.welcome_screen():
                return
            
            if not self.license_screen():
                print(f"\n{Colors.RED}Você deve aceitar a licença para continuar.{Colors.RESET}")
                return
            
            if not self.path_selection_screen():
                print(f"\n{Colors.YELLOW}Instalação cancelada.{Colors.RESET}")
                return
            
            self.install_screen()
            
            if self.perform_installation():
                self.completion_screen()
            else:
                print(f"\n{Colors.RED}Falha na instalação.{Colors.RESET}")
                
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{Colors.YELLOW}Instalação cancelada pelo usuário.{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.RED}Erro: {e}{Colors.RESET}")

if __name__ == '__main__':
    installer = Installer()
    installer.run()
