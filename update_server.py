#!/usr/bin/env python3
import os
import json
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import tarfile
import shutil

class UpdateServer(BaseHTTPRequestHandler):
    VERSION = "1.0.0"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPDATES_DIR = os.path.join(BASE_DIR, "updates")
    
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.send_dashboard()
        elif self.path == '/api/version':
            self.send_version_info()
        elif self.path.startswith('/api/download/'):
            version = self.path.split('/')[-1]
            self.send_update_package(version)
        elif self.path == '/api/changelog':
            self.send_changelog()
        elif self.path == '/api/clients':
            self.send_client_list()
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/api/register':
            self.register_client()
        elif self.path == '/api/publish':
            self.publish_update()
        else:
            self.send_error(404)
    
    def send_dashboard(self):
        dashboard_file = os.path.join(self.BASE_DIR, "dashboard.html")
        
        if os.path.exists(dashboard_file):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            with open(dashboard_file, 'r') as f:
                self.wfile.write(f.read().encode())
        else:
            self.send_error(404)
    
    def send_version_info(self):
        version_file = os.path.join(self.BASE_DIR, "VERSION")
        
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                version = f.read().strip()
        else:
            version = self.VERSION
        
        changelog_file = os.path.join(self.BASE_DIR, "CHANGELOG.json")
        changelog = []
        
        if os.path.exists(changelog_file):
            with open(changelog_file, 'r') as f:
                changelog = json.load(f)
        
        response = {
            'version': version,
            'release_date': datetime.now().isoformat(),
            'changelog': changelog,
            'download_url': f'/api/download/{version}'
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def send_update_package(self, version):
        package_file = os.path.join(self.UPDATES_DIR, f"egsys-monitor-{version}.tar.gz")
        
        if not os.path.exists(package_file):
            self.create_update_package(version)
        
        if os.path.exists(package_file):
            self.send_response(200)
            self.send_header('Content-type', 'application/gzip')
            self.send_header('Content-Disposition', f'attachment; filename="update-{version}.tar.gz"')
            self.end_headers()
            
            with open(package_file, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)
    
    def create_update_package(self, version):
        os.makedirs(self.UPDATES_DIR, exist_ok=True)
        
        package_file = os.path.join(self.UPDATES_DIR, f"egsys-monitor-{version}.tar.gz")
        
        with tarfile.open(package_file, 'w:gz') as tar:
            tar.add(os.path.join(self.BASE_DIR, "src"), arcname="src")
            tar.add(os.path.join(self.BASE_DIR, "config"), arcname="config")
            
            if os.path.exists(os.path.join(self.BASE_DIR, "VERSION")):
                tar.add(os.path.join(self.BASE_DIR, "VERSION"), arcname="VERSION")
    
    def send_changelog(self):
        changelog_file = os.path.join(self.BASE_DIR, "CHANGELOG.json")
        
        if os.path.exists(changelog_file):
            with open(changelog_file, 'r') as f:
                changelog = json.load(f)
        else:
            changelog = []
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(changelog).encode())
    
    def register_client(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        client_info = json.loads(post_data.decode())
        
        clients_file = os.path.join(self.BASE_DIR, "clients.json")
        
        if os.path.exists(clients_file):
            with open(clients_file, 'r') as f:
                clients = json.load(f)
        else:
            clients = []
        
        client_info['last_seen'] = datetime.now().isoformat()
        
        existing = False
        for i, client in enumerate(clients):
            if client.get('hostname') == client_info.get('hostname'):
                clients[i] = client_info
                existing = True
                break
        
        if not existing:
            clients.append(client_info)
        
        with open(clients_file, 'w') as f:
            json.dump(clients, f, indent=2)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'registered'}).encode())
    
    def send_client_list(self):
        clients_file = os.path.join(self.BASE_DIR, "clients.json")
        
        if os.path.exists(clients_file):
            with open(clients_file, 'r') as f:
                clients = json.load(f)
        else:
            clients = []
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(clients).encode())

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, UpdateServer)
    print(f"Servidor de atualizações rodando na porta {port}")
    print(f"Acesse: http://localhost:{port}/api/version")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
