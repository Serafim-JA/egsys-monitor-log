#!/usr/bin/env python3
"""Sistema de Auto-Atualização via GitHub"""

import os
import sys
import json
import subprocess
from pathlib import Path
import requests

REPO_OWNER = "Serafim-JA"
REPO_NAME = "egsys-monitor-log"
GITHUB_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
PROJECT_ROOT = Path(__file__).parent.parent

def get_current_version():
    version_file = PROJECT_ROOT / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.0.0"

def get_latest_version():
    try:
        response = requests.get(f"{GITHUB_API}/releases/latest", timeout=5)
        if response.status_code == 200:
            return response.json()["tag_name"].lstrip("v")
        
        response = requests.get(f"{GITHUB_API}/commits/main", timeout=5)
        if response.status_code == 200:
            return response.json()["sha"][:7]
    except:
        pass
    return None

def check_updates():
    current = get_current_version()
    latest = get_latest_version()
    
    if not latest:
        return False, "Não foi possível verificar atualizações"
    
    if current != latest:
        return True, f"Nova versão disponível: {latest} (atual: {current})"
    
    return False, "Sistema atualizado"

def update_system():
    print("🔄 Atualizando sistema...")
    
    try:
        os.chdir(PROJECT_ROOT)
        
        subprocess.run(["git", "fetch", "origin"], check=True, capture_output=True)
        subprocess.run(["git", "reset", "--hard", "origin/main"], check=True, capture_output=True)
        
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--upgrade", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        latest = get_latest_version()
        if latest:
            (PROJECT_ROOT / "VERSION").write_text(latest)
        
        print("✅ Atualização concluída!")
        return True
    except Exception as e:
        print(f"❌ Erro na atualização: {e}")
        return False

def auto_update_check():
    has_update, message = check_updates()
    
    if has_update:
        print(f"\n⚠️  {message}")
        response = input("Deseja atualizar agora? (s/N): ").lower()
        
        if response == 's':
            if update_system():
                print("\n🔄 Reinicie o sistema para aplicar as atualizações.")
                sys.exit(0)
    else:
        print(f"✅ {message}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        update_system()
    else:
        auto_update_check()
