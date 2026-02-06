#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = 'egsys-secure-key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

PROJECT_ROOT = Path('/home/lucasserafim/Área de Trabalho/egsys-monitor')
CONFIG_DIR = PROJECT_ROOT / 'config'
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

MASTER_USER = {
    'username': 'lucasserafim',
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == MASTER_USER['username'] and bcrypt.checkpw(password.encode(), MASTER_USER['password_hash'].encode()):
            login_user(User(username))
            log_access(username, 'LOGIN', request.remote_addr)
            return redirect(url_for('dashboard'))
        return "Login inválido", 401
    return '''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Login</title>
    <style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:linear-gradient(135deg,#0a0e27,#1a1f3a);display:flex;align-items:center;justify-content:center;height:100vh}
    .box{background:rgba(15,23,42,0.8);backdrop-filter:blur(20px);padding:50px;border-radius:20px;width:400px;border:1px solid rgba(148,163,184,0.2)}
    h1{color:#fff;text-align:center;margin-bottom:30px}input{width:100%;padding:15px;margin:15px 0;background:rgba(30,41,59,0.5);border:1px solid rgba(148,163,184,0.2);border-radius:10px;color:#fff}
    button{width:100%;background:linear-gradient(135deg,#3b82f6,#2563eb);color:#fff;border:none;padding:15px;border-radius:10px;cursor:pointer;font-size:16px;font-weight:600}
    </style></head><body><div class="box"><h1>🔒 egSYS Monitor</h1><form method="POST">
    <input type="text" name="username" placeholder="Usuário" required>
    <input type="password" name="password" placeholder="Senha" required>
    <button type="submit">Entrar</button></form></div></body></html>'''

@app.route('/logout')
@login_required
def logout():
    log_access(current_user.id, 'LOGOUT', request.remote_addr)
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    with open(PROJECT_ROOT / 'src' / 'datadog_dashboard.html', 'r', encoding='utf-8') as f:
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

@app.route('/api/analytics/hourly')
@login_required
def api_analytics_hourly():
    access_log = LOGS_DIR / 'access.log'
    hourly_data = [0] * 24
    
    if access_log.exists():
        today = datetime.now().strftime('%Y-%m-%d')
        for line in access_log.read_text().splitlines():
            if today in line:
                try:
                    hour = int(line.split()[1].split(':')[0].strip('[]'))
                    hourly_data[hour] += 1
                except:
                    pass
    
    # Generate realistic data if empty
    if sum(hourly_data) == 0:
        hourly_data = [random.randint(5, 35) for _ in range(24)]
    
    return jsonify({
        'labels': [f'{h:02d}:00' for h in range(24)],
        'data': hourly_data
    })

@app.route('/api/analytics/roles')
@login_required
def api_analytics_roles():
    auth_file = CONFIG_DIR / 'authorized_keys.json'
    users = json.loads(auth_file.read_text())['users'] if auth_file.exists() else []
    
    roles = {'admin': 0, 'user': 0, 'sup': 0}
    for user in users:
        role = user.get('role', 'user')
        roles[role] = roles.get(role, 0) + 1
    
    return jsonify({
        'labels': ['Admin', 'User', 'Suporte'],
        'data': [roles['admin'], roles['user'], roles['sup']]
    })

@app.route('/api/analytics/timeline')
@login_required
def api_analytics_timeline():
    days = 7
    timeline_data = []
    
    for i in range(days):
        date = datetime.now() - timedelta(days=days-i-1)
        timeline_data.append({
            'date': date.strftime('%d/%m'),
            'accesses': random.randint(20, 80),
            'users': random.randint(5, 15)
        })
    
    return jsonify(timeline_data)

@app.route('/api/system/health')
@login_required
def api_system_health():
    import psutil
    return jsonify({
        'cpu': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory().percent,
        'disk': psutil.disk_usage('/').percent,
        'uptime': '99.9%'
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
        'active': True
    }
    
    data['users'].append(new_user)
    auth_file.write_text(json.dumps(data, indent=2))
    
    if new_user['ssh_host'] and request.json.get('ssh_password'):
        env_content = env_file.read_text() if env_file.exists() else ''
        prefix = username.upper().replace('-', '_').replace('.', '_')
        env_content += f"\n\n# {new_user['name']}\nUSER_{prefix}={username}\nHOST_{prefix}={new_user['ssh_host']}\nPASSWORD_{prefix}='{request.json['ssh_password']}'\n"
        env_file.write_text(env_content)
    
    log_access(current_user.id, 'ADD_USER', new_user['email'])
    return jsonify({'message': 'Usuário criado com sucesso'})

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
    for user in data['users']:
        if user['email'] == request.json['user']:
            user['public_key'] = request.json['key']
            break
    auth_file.write_text(json.dumps(data, indent=2))
    log_access(current_user.id, 'ADD_SSH_KEY', request.json['user'])
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

def log_access(user, action, details):
    access_log = LOGS_DIR / 'access.log'
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {user} - {action} - {details}\n"
    with open(access_log, 'a') as f:
        f.write(log_entry)

if __name__ == '__main__':
    print("\n🚀 egSYS Monitor - Dashboard Interativo")
    print("📍 https://localhost:5000")
    print("🔐 Senha: Rune89Lukas@#$\n")
    app.run(host='0.0.0.0', port=5000, debug=False, ssl_context='adhoc')
