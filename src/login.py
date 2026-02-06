#!/usr/bin/env python3
"""Sistema de Autenticação Integrado com Dashboard"""

import json
import bcrypt
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / 'config'
LOGS_DIR = PROJECT_ROOT / 'logs'

def load_users():
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    if auth_file.exists():
        data = json.loads(auth_file.read_text())
        return data.get('users', [])
    return []

def verify_credentials(username, password):
    users = load_users()
    
    for user in users:
        if user.get('username') == username or user.get('email') == username:
            if user.get('password_hash'):
                if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
                    return True, user
            elif user.get('ssh_password') == password:
                return True, user
    
    return False, None

def log_access(username, action, details=""):
    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / 'access.log'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(log_file, 'a') as f:
        f.write(f"[{timestamp}] {username} - {action} - {details}\n")

def authenticate():
    print("\n╔════════════════════════════════════════╗")
    print("║     egSYS Monitor - Autenticação      ║")
    print("╚════════════════════════════════════════╝\n")
    
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        username = input("👤 Usuário: ").strip()
        password = input("🔑 Senha: ").strip()
        
        valid, user = verify_credentials(username, password)
        
        if valid:
            print(f"\n✅ Autenticado como: {user['name']} ({user['role']})")
            log_access(username, 'LOGIN_CLI', 'Terminal')
            
            with open(PROJECT_ROOT / '.current_user', 'w') as f:
                json.dump(user, f)
            
            return True
        
        attempts += 1
        remaining = max_attempts - attempts
        
        if remaining > 0:
            print(f"\n❌ Credenciais inválidas. Tentativas restantes: {remaining}\n")
            log_access(username, 'LOGIN_FAILED', 'Terminal')
        else:
            print("\n❌ Número máximo de tentativas excedido.")
            log_access(username, 'LOGIN_BLOCKED', 'Terminal')
    
    return False

def get_current_user():
    user_file = PROJECT_ROOT / '.current_user'
    if user_file.exists():
        return json.loads(user_file.read_text())
    return None

if __name__ == "__main__":
    if not authenticate():
        sys.exit(1)
