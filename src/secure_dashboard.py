#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
import json
import os
from pathlib import Path
from datetime import datetime
import secrets
import hashlib

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

PROJECT_ROOT = Path('/home/lucasserafim/Área de Trabalho/egsys-monitor')
CONFIG_DIR = PROJECT_ROOT / 'config'
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Security settings
ALLOWED_IPS_FILE = CONFIG_DIR / 'allowed_ips.json'
FAILED_ATTEMPTS_FILE = LOGS_DIR / 'failed_attempts.json'
MAX_FAILED_ATTEMPTS = 5

MASTER_USER = {
    'username': 'lucasserafim',
    'email': 'lucasserafim@egsyssuporte1',
    'password_hash': bcrypt.hashpw('Rune89Lukas@#$'.encode(), bcrypt.gensalt()).decode()
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username == MASTER_USER['username']:
        return User(username)
    return None

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0]
    return request.remote_addr

def is_ip_allowed(ip):
    if not ALLOWED_IPS_FILE.exists():
        return True
    try:
        data = json.loads(ALLOWED_IPS_FILE.read_text())
        if data.get('whitelist_enabled', False):
            return ip in data.get('allowed_ips', [])
    except:
        pass
    return True

def check_failed_attempts(ip):
    if not FAILED_ATTEMPTS_FILE.exists():
        return True
    try:
        data = json.loads(FAILED_ATTEMPTS_FILE.read_text())
        attempts = data.get(ip, {}).get('count', 0)
        return attempts < MAX_FAILED_ATTEMPTS
    except:
        return True

def log_failed_attempt(ip):
    data = {}
    if FAILED_ATTEMPTS_FILE.exists():
        data = json.loads(FAILED_ATTEMPTS_FILE.read_text())
    
    if ip not in data:
        data[ip] = {'count': 0, 'last_attempt': ''}
    
    data[ip]['count'] += 1
    data[ip]['last_attempt'] = datetime.now().isoformat()
    
    FAILED_ATTEMPTS_FILE.write_text(json.dumps(data, indent=2))

def reset_failed_attempts(ip):
    if FAILED_ATTEMPTS_FILE.exists():
        data = json.loads(FAILED_ATTEMPTS_FILE.read_text())
        if ip in data:
            del data[ip]
            FAILED_ATTEMPTS_FILE.write_text(json.dumps(data, indent=2))

@app.before_request
def security_check():
    if request.endpoint and request.endpoint != 'login':
        client_ip = get_client_ip()
        if not is_ip_allowed(client_ip):
            return jsonify({'error': 'IP não autorizado'}), 403

@app.route('/login', methods=['GET', 'POST'])
def login():
    client_ip = get_client_ip()
    
    if not check_failed_attempts(client_ip):
        return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Bloqueado</title>
        <style>body{{font-family:Inter,sans-serif;background:linear-gradient(135deg,#0a0e27 0%,#1a1f3a 100%);display:flex;align-items:center;justify-content:center;height:100vh;color:#fff}}
        .box{{background:rgba(239,68,68,0.2);backdrop-filter:blur(20px);padding:50px;border-radius:20px;width:400px;border:2px solid #ef4444;text-align:center}}
        h1{{color:#ef4444;margin-bottom:20px}}</style></head><body>
        <div class="box"><h1>🚫 Acesso Bloqueado</h1><p>Muitas tentativas de login falhadas.</p><p>IP: {client_ip}</p><p>Contate o administrador.</p></div></body></html>''', 403
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == MASTER_USER['username']:
            if bcrypt.checkpw(password.encode(), MASTER_USER['password_hash'].encode()):
                user = User(username)
                login_user(user)
                reset_failed_attempts(client_ip)
                log_access(username, 'LOGIN', f'IP: {client_ip}')
                return redirect(url_for('dashboard'))
        
        log_failed_attempt(client_ip)
        log_access(username or 'unknown', 'FAILED_LOGIN', f'IP: {client_ip}')
        return "Login inválido", 401
    
    return '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Login Seguro</title>
    <style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:linear-gradient(135deg,#0a0e27 0%,#1a1f3a 100%);display:flex;align-items:center;justify-content:center;height:100vh}
    .box{background:rgba(15,23,42,0.8);backdrop-filter:blur(20px);padding:50px;border-radius:20px;width:400px;border:1px solid rgba(148,163,184,0.2);box-shadow:0 25px 50px rgba(0,0,0,0.5)}
    h1{color:#fff;text-align:center;margin-bottom:30px;font-size:28px}.security-badge{background:rgba(16,185,129,0.2);color:#10b981;padding:8px 16px;border-radius:8px;text-align:center;margin-bottom:20px;font-size:12px}
    input{width:100%;padding:15px;margin:15px 0;background:rgba(30,41,59,0.5);border:1px solid rgba(148,163,184,0.2);border-radius:10px;color:#fff;font-size:14px}
    input:focus{outline:none;border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,0.1)}
    button{width:100%;background:linear-gradient(135deg,#3b82f6 0%,#2563eb 100%);color:#fff;border:none;padding:15px;border-radius:10px;cursor:pointer;font-size:16px;font-weight:600;margin-top:10px}
    button:hover{transform:translateY(-2px);box-shadow:0 10px 30px rgba(59,130,246,0.3)}</style></head><body>
    <div class="box"><h1>🔒 egSYS Monitor</h1><div class="security-badge">🛡️ Conexão Segura</div><form method="POST">
    <input type="text" name="username" placeholder="Usuário" required autocomplete="username">
    <input type="password" name="password" placeholder="Senha" required autocomplete="current-password">
    <button type="submit">Entrar com Segurança</button></form></div></body></html>'''

@app.route('/logout')
@login_required
def logout():
    log_access(current_user.id, 'LOGOUT', f'IP: {get_client_ip()}')
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    dashboard_path = PROJECT_ROOT / 'src' / 'datadog_dashboard.html'
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/stats')
@login_required
def api_stats():
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    users = json.loads(auth_file.read_text())['users'] if auth_file.exists() else []
    
    access_log = LOGS_DIR / 'access.log'
    access_today = 0
    if access_log.exists():
        today = datetime.now().strftime('%Y-%m-%d')
        access_today = sum(1 for line in access_log.read_text().splitlines() if today in line)
    
    return jsonify({
        'total_users': len(users),
        'active_users': sum(1 for u in users if u.get('active', True)),
        'access_today': access_today
    })

@app.route('/api/users')
@login_required
def api_users():
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    data = json.loads(auth_file.read_text()) if auth_file.exists() else {'users': []}
    return jsonify({'users': data['users']})

@app.route('/api/users', methods=['POST'])
@login_required
def api_add_user():
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    env_file = PROJECT_ROOT / '.env'
    data = json.loads(auth_file.read_text()) if auth_file.exists() else {'users': []}
    
    username = request.json.get('username', request.json['email'].split('@')[0])
    new_user = {
        'name': request.json['name'],
        'email': request.json['email'],
        'username': username,
        'role': request.json['role'],
        'ssh_host': request.json.get('ssh_host', ''),
        'ssh_port': '22',
        'created': datetime.now().isoformat(),
        'active': True,
        'password': bcrypt.hashpw('egsys123'.encode(), bcrypt.gensalt()).decode()
    }
    
    data['users'].append(new_user)
    auth_file.write_text(json.dumps(data, indent=2))
    
    if new_user['ssh_host'] and request.json.get('ssh_password'):
        env_content = env_file.read_text() if env_file.exists() else ''
        prefix = username.upper().replace('-', '_').replace('.', '_')
        env_content += f"\n\n# {new_user['name']}\n"
        env_content += f"USER_{prefix}={username}\n"
        env_content += f"HOST_{prefix}={new_user['ssh_host']}\n"
        env_content += f"PASSWORD_{prefix}='{request.json['ssh_password']}'\n"
        env_file.write_text(env_content)
    
    log_access(current_user.id, 'ADD_USER', new_user['email'])
    return jsonify({'message': 'Usuário criado'})

@app.route('/api/users/<email>', methods=['PUT'])
@login_required
def api_edit_user(email):
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    data = json.loads(auth_file.read_text())
    
    for user in data['users']:
        if user['email'] == email:
            user['name'] = request.json.get('name', user['name'])
            user['email'] = request.json.get('email', user['email'])
            user['username'] = request.json.get('username', user.get('username', ''))
            user['role'] = request.json.get('role', user['role'])
            user['ssh_host'] = request.json.get('ssh_host', user.get('ssh_host', ''))
            user['active'] = request.json.get('active', user['active'])
            user['updated'] = datetime.now().isoformat()
            break
    
    auth_file.write_text(json.dumps(data, indent=2))
    log_access(current_user.id, 'EDIT_USER', email)
    return jsonify({'message': 'Usuário atualizado'})

@app.route('/api/users/<email>', methods=['DELETE'])
@login_required
def api_delete_user(email):
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    data = json.loads(auth_file.read_text())
    data['users'] = [u for u in data['users'] if u['email'] != email]
    auth_file.write_text(json.dumps(data, indent=2))
    log_access(current_user.id, 'DELETE_USER', email)
    return jsonify({'message': 'Usuário removido'})

@app.route('/api/ssh-keys')
@login_required
def api_ssh_keys():
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    data = json.loads(auth_file.read_text()) if auth_file.exists() else {'users': []}
    keys = []
    for user in data['users']:
        if user.get('public_key'):
            keys.append({
                'user': user['email'],
                'type': 'RSA',
                'fingerprint': user['public_key'][:50] + '...',
                'created': user.get('created', 'N/A')
            })
    return jsonify({'keys': keys})

@app.route('/api/ssh-keys', methods=['POST'])
@login_required
def api_add_ssh_key():
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    data = json.loads(auth_file.read_text())
    user_email = request.json['user']
    key_content = request.json['key']
    for user in data['users']:
        if user['email'] == user_email:
            user['public_key'] = key_content
            break
    auth_file.write_text(json.dumps(data, indent=2))
    log_access(current_user.id, 'ADD_SSH_KEY', user_email)
    return jsonify({'message': 'Chave SSH adicionada'})

@app.route('/api/ssh-keys/<user>', methods=['DELETE'])
@login_required
def api_delete_ssh_key(user):
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    data = json.loads(auth_file.read_text())
    for u in data['users']:
        if u['email'] == user:
            u['public_key'] = ''
            break
    auth_file.write_text(json.dumps(data, indent=2))
    log_access(current_user.id, 'DELETE_SSH_KEY', user)
    return jsonify({'message': 'Chave SSH removida'})

@app.route('/api/access-logs')
@login_required
def api_access_logs():
    access_log = LOGS_DIR / 'access.log'
    logs = []
    if access_log.exists():
        logs = access_log.read_text().splitlines()[-100:]
    return jsonify({'logs': logs})

@app.route('/api/access-logs', methods=['DELETE'])
@login_required
def api_clear_logs():
    access_log = LOGS_DIR / 'access.log'
    if access_log.exists():
        access_log.write_text('')
    log_access(current_user.id, 'CLEAR_LOGS', 'All logs cleared')
    return jsonify({'message': 'Logs limpos'})

@app.route('/api/config', methods=['POST'])
@login_required
def api_save_config():
    config_file = CONFIG_DIR / 'update_config.json'
    data = json.loads(config_file.read_text()) if config_file.exists() else {}
    data['server_url'] = request.json['server_url']
    data['auto_update'] = request.json['auto_update']
    config_file.write_text(json.dumps(data, indent=2))
    log_access(current_user.id, 'UPDATE_CONFIG', 'Configuration updated')
    return jsonify({'message': 'Configurações salvas'})

@app.route('/api/security/whitelist', methods=['GET', 'POST'])
@login_required
def api_whitelist():
    if request.method == 'POST':
        data = request.json
        ALLOWED_IPS_FILE.write_text(json.dumps(data, indent=2))
        log_access(current_user.id, 'UPDATE_WHITELIST', f"IPs: {len(data.get('allowed_ips', []))}")
        return jsonify({'message': 'Whitelist atualizada'})
    
    if ALLOWED_IPS_FILE.exists():
        return jsonify(json.loads(ALLOWED_IPS_FILE.read_text()))
    return jsonify({'whitelist_enabled': False, 'allowed_ips': []})

def log_access(user, action, details):
    access_log = LOGS_DIR / 'access.log'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {user} - {action} - {details}\n"
    with open(access_log, 'a') as f:
        f.write(log_entry)

if __name__ == '__main__':
    print("\n🔒 egSYS Monitor - Servidor Seguro")
    print(f"📍 Acesse: http://localhost:5000")
    print(f"🛡️  Segurança: Ativada")
    print(f"🔐 Senha atualizada\n")
    app.run(host='0.0.0.0', port=5000, debug=False, ssl_context='adhoc')
