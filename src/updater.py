#!/usr/bin/env python3
"""
egSYS Monitor - Sistema de Auto-Atualização
Verifica e aplica atualizações do GitHub automaticamente
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import urllib.request
import urllib.error

class AutoUpdater:
    def __init__(self, install_path):
        self.install_path = Path(install_path)
        self.version_file = self.install_path / 'VERSION'
        self.github_repo = 'Serafim-JA/egsys-monitor-log'
        self.github_api = f'https://api.github.com/repos/{self.github_repo}/releases/latest'
        
    def get_current_version(self):
        """Obtém versão atual instalada"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return '0.0.0'
    
    def get_latest_version(self):
        """Obtém última versão do GitHub"""
        try:
            with urllib.request.urlopen(self.github_api, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data['tag_name'].lstrip('v')
        except (urllib.error.URLError, KeyError, json.JSONDecodeError):
            return None
    
    def check_for_updates(self):
        """Verifica se há atualizações disponíveis"""
        current = self.get_current_version()
        latest = self.get_latest_version()
        
        if latest and latest != current:
            return True, current, latest
        return False, current, current
    
    def perform_update(self):
        """Executa atualização via git pull"""
        try:
            # Verificar se é repositório git
            git_dir = self.install_path / '.git'
            if not git_dir.exists():
                return False, "Não é um repositório git"
            
            # Fazer backup de configurações
            config_backup = self.install_path / 'config.backup'
            if (self.install_path / 'config').exists():
                subprocess.run(['cp', '-r', 
                              str(self.install_path / 'config'),
                              str(config_backup)], check=True)
            
            # Git pull
            result = subprocess.run(['git', 'pull'], 
                                  cwd=str(self.install_path),
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, result.stderr
            
            # Restaurar configurações
            if config_backup.exists():
                subprocess.run(['cp', '-r', str(config_backup / '*'),
                              str(self.install_path / 'config')], 
                             shell=True, check=False)
                subprocess.run(['rm', '-rf', str(config_backup)], check=True)
            
            # Atualizar VERSION
            latest = self.get_latest_version()
            if latest:
                self.version_file.write_text(latest)
            
            return True, "Atualização concluída"
            
        except Exception as e:
            return False, str(e)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        updater = AutoUpdater(sys.argv[1])
        has_update, current, latest = updater.check_for_updates()
        
        if has_update:
            print(f"Nova versão disponível: {latest} (atual: {current})")
            print("Atualizando...")
            success, message = updater.perform_update()
            print(message)
            sys.exit(0 if success else 1)
        else:
            print(f"Versão atual ({current}) está atualizada")
