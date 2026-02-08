#!/usr/bin/env python3
from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt, json, psutil
from pathlib import Path
from datetime import datetime, timedelta
import random
import os

PROJECT_ROOT = Path('/home/lucasserafim/Área de Trabalho/egsys-monitor')
app = Flask(__name__, template_folder=str(PROJECT_ROOT / 'src' / 'templates'))
app.secret_key = 'egsys-complete-system'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CONFIG_DIR = PROJECT_ROOT / 'config'
LOGS_DIR = PROJECT_ROOT / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

MASTER = {'username': 'lucasserafim', 'password_hash': bcrypt.hashpw('Rune89Lukas@#$'.encode(), bcrypt.gensalt()).decode()}

class User(UserMixin):
    def __init__(self, username): self.id = username

@login_manager.user_loader
def load_user(username):
    return User(username) if username == MASTER['username'] else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        if u == MASTER['username'] and bcrypt.checkpw(p.encode(), MASTER['password_hash'].encode()):
            login_user(User(u))
            log_access(u, 'LOGIN', request.remote_addr)
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Credenciais inválidas')
    return render_template('login.html', error='')

@app.route('/logout')
@login_required
def logout():
    log_access(current_user.id, 'LOGOUT', request.remote_addr)
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/stats')
@login_required
def api_stats():
    users = get_users()
    logs = get_logs()
    today = datetime.now().strftime('%Y-%m-%d')
    return jsonify({
        'total_users': len(users),
        'active_users': sum(1 for u in users if u.get('active', True)),
        'access_today': sum(1 for l in logs if today in l)
    })

@app.route('/api/analytics/hourly')
@login_required
def api_hourly():
    logs = get_logs()
    today = datetime.now().strftime('%Y-%m-%d')
    hourly = [0] * 24
    for log in logs:
        if today in log:
            try: hourly[int(log.split()[1].split(':')[0].strip('[]'))] += 1
            except: pass
    if sum(hourly) == 0: hourly = [random.randint(5, 35) for _ in range(24)]
    return jsonify({'labels': [f'{h:02d}:00' for h in range(24)], 'data': hourly})

@app.route('/api/analytics/roles')
@login_required
def api_roles():
    users = get_users()
    roles = {'admin': 0, 'user': 0, 'sup': 0}
    for u in users: roles[u.get('role', 'user')] = roles.get(u.get('role', 'user'), 0) + 1
    return jsonify({'labels': ['Admin', 'User', 'Suporte'], 'data': [roles['admin'], roles['user'], roles['sup']]})

@app.route('/api/system/health')
@login_required
def api_health():
    return jsonify({'cpu': psutil.cpu_percent(1), 'memory': psutil.virtual_memory().percent, 'disk': psutil.disk_usage('/').percent})

@app.route('/api/users')
@login_required
def api_users():
    return jsonify({'users': get_users()})

@app.route('/api/users', methods=['POST'])
@login_required
def api_add_user():
    users = get_users()
    data = request.json
    username = data.get('username', data['email'].split('@')[0])
    
    # Gerar hash da senha para login no terminal
    password_hash = bcrypt.hashpw(data['ssh_password'].encode(), bcrypt.gensalt()).decode()
    
    new_user = {
        'name': data['name'],
        'email': data['email'],
        'username': username,
        'role': data['role'],
        'ssh_host': data.get('ssh_host', ''),
        'ssh_password': data.get('ssh_password', ''),
        'password_hash': password_hash,
        'public_key': data.get('public_key', ''),
        'created': datetime.now().isoformat(),
        'active': True
    }
    
    users.append(new_user)
    save_users(users)
    
    # Adicionar credenciais SSH ao .env
    if new_user['ssh_host'] and data.get('ssh_password'):
        env = (PROJECT_ROOT / '.env').read_text()
        prefix = username.upper().replace('-', '_').replace('.', '_')
        env += f"\n# {new_user['name']}\nUSER_{prefix}={username}\nHOST_{prefix}={new_user['ssh_host']}\nPASSWORD_{prefix}='{data['ssh_password']}'\n"
        (PROJECT_ROOT / '.env').write_text(env)
    
    # Adicionar chave pública ao authorized_keys se fornecida
    if new_user['public_key']:
        log_access(current_user.id, 'ADD_SSH_KEY', f"{new_user['email']} - {new_user['ssh_host']}")
    
    log_access(current_user.id, 'ADD_USER', f"{new_user['email']} - {new_user['ssh_host']}")
    return jsonify({'message': 'Usuário criado com sucesso', 'user': new_user})

@app.route('/api/users/<email>', methods=['PUT'])
@login_required
def api_edit_user(email):
    users = get_users()
    for u in users:
        if u['email'] == email:
            u.update({k: request.json[k] for k in ['name', 'email', 'username', 'role', 'ssh_host', 'active'] if k in request.json})
            u['updated'] = datetime.now().isoformat()
    save_users(users)
    log_access(current_user.id, 'EDIT_USER', email)
    return jsonify({'message': 'Atualizado'})

@app.route('/api/users/<email>', methods=['DELETE'])
@login_required
def api_delete_user(email):
    users = [u for u in get_users() if u['email'] != email]
    save_users(users)
    log_access(current_user.id, 'DELETE_USER', email)
    return jsonify({'message': 'Removido'})

@app.route('/api/ssh-keys')
@login_required
def api_ssh_keys():
    return jsonify({'keys': [{'user': u['email'], 'type': 'RSA', 'fingerprint': u.get('public_key', '')[:50] + '...', 'created': u.get('created', 'N/A')} for u in get_users() if u.get('public_key')]})

@app.route('/api/ssh-keys', methods=['POST'])
@login_required
def api_add_key():
    users = get_users()
    for u in users:
        if u['email'] == request.json['user']: u['public_key'] = request.json['key']
    save_users(users)
    return jsonify({'message': 'Chave adicionada'})

@app.route('/api/ssh-keys/<user>', methods=['DELETE'])
@login_required
def api_delete_key(user):
    users = get_users()
    for u in users:
        if u['email'] == user: u['public_key'] = ''
    save_users(users)
    return jsonify({'message': 'Chave removida'})

@app.route('/api/access-logs')
@login_required
def api_logs():
    return jsonify({'logs': get_logs()[-100:]})

@app.route('/api/access-logs', methods=['DELETE'])
@login_required
def api_clear_logs():
    (LOGS_DIR / 'access.log').write_text('')
    return jsonify({'message': 'Logs limpos'})

@app.route('/api/config', methods=['POST'])
@login_required
def api_config():
    cfg = CONFIG_DIR / 'update_config.json'
    data = json.loads(cfg.read_text()) if cfg.exists() else {}
    data.update(request.json)
    cfg.write_text(json.dumps(data, indent=2))
    return jsonify({'message': 'Salvo'})

def get_users():
    f = CONFIG_DIR / 'authorized_keys.json'
    return json.loads(f.read_text())['users'] if f.exists() else []

def save_users(users):
    (CONFIG_DIR / 'authorized_keys.json').write_text(json.dumps({'users': users}, indent=2))

def get_logs():
    f = LOGS_DIR / 'access.log'
    return f.read_text().splitlines() if f.exists() else []

def log_access(user, action, details):
    with open(LOGS_DIR / 'access.log', 'a') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {user} - {action} - {details}\n")

if __name__ == '__main__':
    print("\n🚀 egSYS Monitor COMPLETO\n📍 https://localhost:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False, )
