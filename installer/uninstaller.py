#!/usr/bin/env python3
"""
egSYS Monitor - Desinstalador
Remove completamente o aplicativo do sistema
"""

import os
import sys
import shutil
from pathlib import Path

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class Uninstaller:
    def __init__(self):
        self.install_locations = [
            Path.home() / 'egSYS-Monitor',
            Path.home() / '.egsys-monitor',
            Path.home() / 'Documentos' / 'egSYS-Monitor'
        ]
        self.found_installation = None
        
    def find_installation(self):
        """Localiza instalação existente"""
        for location in self.install_locations:
            if location.exists():
                self.found_installation = location
                return True
        return False
    
    def confirm_uninstall(self):
        """Solicita confirmação do usuário"""
        print(f"\n{Colors.YELLOW}╔{'═' * 68}╗{Colors.RESET}")
        print(f"{Colors.YELLOW}║{Colors.RESET} {Colors.BOLD}{'DESINSTALAR egSYS Monitor'.center(66)}{Colors.RESET} {Colors.YELLOW}║{Colors.RESET}")
        print(f"{Colors.YELLOW}╚{'═' * 68}╝{Colors.RESET}\n")
        
        print(f"Instalação encontrada em:")
        print(f"{Colors.CYAN}{self.found_installation}{Colors.RESET}\n")
        
        print(f"{Colors.RED}ATENÇÃO: Esta ação não pode ser desfeita!{Colors.RESET}\n")
        print("Os seguintes itens serão removidos:")
        print(f"  • Aplicação e código fonte")
        print(f"  • Configurações")
        print(f"  • Logs")
        print(f"  • Atalhos do sistema")
        print(f"  • Serviços systemd\n")
        
        response = input(f"{Colors.YELLOW}Deseja continuar? Digite 'DESINSTALAR' para confirmar: {Colors.RESET}")
        return response == 'DESINSTALAR'
    
    def remove_files(self):
        """Remove arquivos da instalação"""
        try:
            print(f"\n{Colors.CYAN}Removendo arquivos...{Colors.RESET}")
            shutil.rmtree(self.found_installation)
            print(f"{Colors.GREEN}✓{Colors.RESET} Arquivos removidos")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Erro ao remover arquivos: {e}{Colors.RESET}")
            return False
    
    def remove_shortcuts(self):
        """Remove atalhos do sistema"""
        try:
            print(f"{Colors.CYAN}Removendo atalhos...{Colors.RESET}")
            
            bin_dir = Path.home() / '.local' / 'bin'
            shortcuts = ['egsys-monitor', 'egsys-update', 'egsys-uninstall']
            
            for shortcut in shortcuts:
                shortcut_path = bin_dir / shortcut
                if shortcut_path.exists():
                    shortcut_path.unlink()
            
            print(f"{Colors.GREEN}✓{Colors.RESET} Atalhos removidos")
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Erro ao remover atalhos: {e}{Colors.RESET}")
            return False
    
    def remove_services(self):
        """Remove serviços systemd"""
        try:
            print(f"{Colors.CYAN}Removendo serviços systemd...{Colors.RESET}")
            
            services = ['egsys-dashboard.service', 'egsys-tunnel.service']
            
            for service in services:
                service_path = Path(f'/etc/systemd/system/{service}')
                if service_path.exists():
                    os.system(f'sudo systemctl stop {service}')
                    os.system(f'sudo systemctl disable {service}')
                    os.system(f'sudo rm {service_path}')
            
            os.system('sudo systemctl daemon-reload')
            print(f"{Colors.GREEN}✓{Colors.RESET} Serviços removidos")
            return True
        except Exception as e:
            print(f"{Colors.YELLOW}⚠{Colors.RESET} Erro ao remover serviços: {e}")
            return True  # Não é crítico
    
    def clean_bashrc(self):
        """Remove entradas do .bashrc"""
        try:
            print(f"{Colors.CYAN}Limpando configurações do shell...{Colors.RESET}")
            
            bashrc = Path.home() / '.bashrc'
            if bashrc.exists():
                content = bashrc.read_text()
                lines = content.split('\n')
                
                # Remover linhas relacionadas ao egSYS
                cleaned_lines = [line for line in lines 
                               if 'egsys' not in line.lower() and 'egSYS' not in line]
                
                bashrc.write_text('\n'.join(cleaned_lines))
            
            print(f"{Colors.GREEN}✓{Colors.RESET} Configurações limpas")
            return True
        except Exception as e:
            print(f"{Colors.YELLOW}⚠{Colors.RESET} Erro ao limpar bashrc: {e}")
            return True
    
    def run(self):
        """Executa desinstalação"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}egSYS Monitor - Desinstalador{Colors.RESET}\n")
        
        if not self.find_installation():
            print(f"{Colors.YELLOW}Nenhuma instalação encontrada.{Colors.RESET}")
            return
        
        if not self.confirm_uninstall():
            print(f"\n{Colors.YELLOW}Desinstalação cancelada.{Colors.RESET}")
            return
        
        print(f"\n{Colors.BOLD}Desinstalando egSYS Monitor...{Colors.RESET}\n")
        
        success = True
        success &= self.remove_services()
        success &= self.remove_files()
        success &= self.remove_shortcuts()
        success &= self.clean_bashrc()
        
        if success:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Desinstalação concluída com sucesso!{Colors.RESET}\n")
            print(f"egSYS Monitor foi completamente removido do sistema.\n")
        else:
            print(f"\n{Colors.YELLOW}Desinstalação concluída com avisos.{Colors.RESET}")
            print(f"Alguns itens podem não ter sido removidos completamente.\n")

if __name__ == '__main__':
    uninstaller = Uninstaller()
    uninstaller.run()
