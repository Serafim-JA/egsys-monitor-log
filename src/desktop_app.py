#!/usr/bin/env python3
"""
egSYS Monitor - Aplicativo Desktop
Interface gráfica completa para monitoramento de logs
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import threading
import queue

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    print("Instalando PyQt5...")
    os.system("pip3 install --user PyQt5")
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *

import paramiko
import bcrypt
from dotenv import load_dotenv

# Configurações
PROJECT_ROOT = Path.home() / '.egsys-monitor'
CONFIG_DIR = PROJECT_ROOT / 'config'
LOGS_DIR = PROJECT_ROOT / 'logs'

class LoginWindow(QDialog):
    """Janela de Login"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("egSYS Monitor - Login")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #0a1929);
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLineEdit {
                background: rgba(0, 122, 204, 0.1);
                border: 1px solid #007acc;
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #007acc, stop:1 #00a8ff);
                border: none;
                border-radius: 8px;
                padding: 12px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00a8ff;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo
        logo = QLabel("egSYS Monitor")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 28px; font-weight: bold; color: #00a8ff;")
        layout.addWidget(logo)
        
        subtitle = QLabel("Sistema de Monitoramento Centralizado")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #888;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Usuário
        self.username = QLineEdit()
        self.username.setPlaceholderText("👤 Usuário")
        layout.addWidget(self.username)
        
        # Senha
        self.password = QLineEdit()
        self.password.setPlaceholderText("🔑 Senha")
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)
        
        # Botão Login
        btn_login = QPushButton("Entrar")
        btn_login.clicked.connect(self.login)
        layout.addWidget(btn_login)
        
        # Erro
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ef4444; font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)
        
        self.setLayout(layout)
        
    def login(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        
        if not username or not password:
            self.error_label.setText("❌ Preencha todos os campos")
            return
        
        # Verificar credenciais
        auth_file = CONFIG_DIR / 'authorized_keys.json'
        if not auth_file.exists():
            self.error_label.setText("❌ Arquivo de usuários não encontrado")
            return
        
        users = json.loads(auth_file.read_text())['users']
        
        for user in users:
            if user.get('username') == username or user.get('email') == username:
                if user.get('password_hash'):
                    if bcrypt.checkpw(password.encode(), user['password_hash'].encode()):
                        self.user_data = user
                        self.accept()
                        return
        
        self.error_label.setText("❌ Credenciais inválidas")

class MainWindow(QMainWindow):
    """Janela Principal do Aplicativo"""
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setWindowTitle(f"egSYS Monitor - {user_data['name']}")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background: #0a0a0a;
            }
            QWidget {
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #007acc;
                background: #0f0f0f;
            }
            QTabBar::tab {
                background: #1a1a1a;
                color: white;
                padding: 10px 20px;
                border: 1px solid #007acc;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: #007acc;
            }
            QPushButton {
                background: #007acc;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
            }
            QPushButton:hover {
                background: #00a8ff;
            }
            QTextEdit, QListWidget {
                background: #1a1a1a;
                border: 1px solid #007acc;
                border-radius: 8px;
                padding: 10px;
                color: white;
            }
            QComboBox {
                background: #1a1a1a;
                border: 1px solid #007acc;
                border-radius: 6px;
                padding: 8px;
                color: white;
            }
        """)
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        # Widget central
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        central.setLayout(layout)
        
        # Barra superior
        top_bar = QHBoxLayout()
        
        logo = QLabel("egSYS Monitor")
        logo.setStyleSheet("font-size: 20px; font-weight: bold; color: #00a8ff;")
        top_bar.addWidget(logo)
        
        top_bar.addStretch()
        
        user_label = QLabel(f"👤 {self.user_data['name']} ({self.user_data['role']})")
        user_label.setStyleSheet("font-size: 14px; color: #888;")
        top_bar.addWidget(user_label)
        
        btn_logout = QPushButton("Sair")
        btn_logout.clicked.connect(self.close)
        top_bar.addWidget(btn_logout)
        
        layout.addLayout(top_bar)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab Monitor
        tabs.addTab(self.create_monitor_tab(), "📊 Monitor de Logs")
        
        # Tab Configurações
        tabs.addTab(self.create_config_tab(), "⚙️ Configurações")
        
        # Tab Usuários (apenas admin)
        if self.user_data['role'] == 'admin':
            tabs.addTab(self.create_users_tab(), "👥 Usuários")
        
        # Tab Sobre
        tabs.addTab(self.create_about_tab(), "ℹ️ Sobre")
        
        layout.addWidget(tabs)
        
    def create_monitor_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Seleção de servidor
        select_layout = QHBoxLayout()
        
        select_layout.addWidget(QLabel("Cliente:"))
        self.combo_client = QComboBox()
        select_layout.addWidget(self.combo_client)
        
        select_layout.addWidget(QLabel("Servidor:"))
        self.combo_server = QComboBox()
        select_layout.addWidget(self.combo_server)
        
        select_layout.addWidget(QLabel("Aplicação:"))
        self.combo_app = QComboBox()
        select_layout.addWidget(self.combo_app)
        
        select_layout.addWidget(QLabel("Log:"))
        self.combo_log = QComboBox()
        select_layout.addWidget(self.combo_log)
        
        btn_connect = QPushButton("🔌 Conectar")
        btn_connect.clicked.connect(self.connect_log)
        select_layout.addWidget(btn_connect)
        
        btn_stop = QPushButton("⏹️ Parar")
        btn_stop.clicked.connect(self.stop_log)
        select_layout.addWidget(btn_stop)
        
        layout.addLayout(select_layout)
        
        # Área de logs
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("font-family: 'Courier New'; font-size: 12px;")
        layout.addWidget(self.log_display)
        
        # Status
        self.status_label = QLabel("Status: Desconectado")
        self.status_label.setStyleSheet("color: #888; padding: 10px;")
        layout.addWidget(self.status_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_config_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Configurações do Sistema"))
        
        # Lista de servidores
        group = QGroupBox("Servidores Configurados")
        group_layout = QVBoxLayout()
        
        self.servers_list = QListWidget()
        group_layout.addWidget(self.servers_list)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Adicionar Servidor")
        btn_edit = QPushButton("✏️ Editar")
        btn_remove = QPushButton("🗑️ Remover")
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_remove)
        group_layout.addLayout(btn_layout)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        widget.setLayout(layout)
        return widget
    
    def create_users_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Gerenciamento de Usuários"))
        
        self.users_list = QListWidget()
        layout.addWidget(self.users_list)
        
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("➕ Novo Usuário")
        btn_edit = QPushButton("✏️ Editar")
        btn_remove = QPushButton("🗑️ Remover")
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_edit)
        btn_layout.addWidget(btn_remove)
        layout.addLayout(btn_layout)
        
        self.load_users()
        
        widget.setLayout(layout)
        return widget
    
    def create_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        logo = QLabel("egSYS Monitor")
        logo.setStyleSheet("font-size: 32px; font-weight: bold; color: #00a8ff;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        version = QLabel("Versão 1.0.0")
        version.setStyleSheet("font-size: 16px; color: #888;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        layout.addSpacing(20)
        
        desc = QLabel("Sistema de Monitoramento Centralizado de Logs")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        author = QLabel("Desenvolvido por: Serafim")
        author.setStyleSheet("color: #888;")
        author.setAlignment(Qt.AlignCenter)
        layout.addWidget(author)
        
        github = QLabel('<a href="https://github.com/Serafim-JA/egsys-monitor-log" style="color: #00a8ff;">GitHub</a>')
        github.setOpenExternalLinks(True)
        github.setAlignment(Qt.AlignCenter)
        layout.addWidget(github)
        
        widget.setLayout(layout)
        return widget
    
    def load_config(self):
        config_file = CONFIG_DIR / 'config.json'
        if config_file.exists():
            self.config = json.loads(config_file.read_text())
            self.combo_client.addItems(self.config.keys())
            self.combo_client.currentTextChanged.connect(self.update_servers)
            self.update_servers()
    
    def update_servers(self):
        self.combo_server.clear()
        client = self.combo_client.currentText()
        if client and client in self.config:
            self.combo_server.addItems(self.config[client].keys())
            self.combo_server.currentTextChanged.connect(self.update_apps)
            self.update_apps()
    
    def update_apps(self):
        self.combo_app.clear()
        client = self.combo_client.currentText()
        server = self.combo_server.currentText()
        if client and server and client in self.config and server in self.config[client]:
            self.combo_app.addItems(self.config[client][server].keys())
            self.combo_app.currentTextChanged.connect(self.update_logs)
            self.update_logs()
    
    def update_logs(self):
        self.combo_log.clear()
        client = self.combo_client.currentText()
        server = self.combo_server.currentText()
        app = self.combo_app.currentText()
        if all([client, server, app]) and client in self.config:
            if server in self.config[client] and app in self.config[client][server]:
                self.combo_log.addItems(self.config[client][server][app].keys())
    
    def connect_log(self):
        self.log_display.clear()
        self.status_label.setText("Status: Conectando...")
        self.log_display.append(f"[{datetime.now().strftime('%H:%M:%S')}] Conectando ao servidor...")
        # TODO: Implementar conexão SSH real
        self.status_label.setText("Status: Conectado ✅")
    
    def stop_log(self):
        self.status_label.setText("Status: Desconectado")
        self.log_display.append(f"[{datetime.now().strftime('%H:%M:%S')}] Conexão encerrada")
    
    def load_users(self):
        auth_file = CONFIG_DIR / 'authorized_keys.json'
        if auth_file.exists():
            users = json.loads(auth_file.read_text())['users']
            for user in users:
                self.users_list.addItem(f"{user['name']} ({user['email']}) - {user['role']}")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("egSYS Monitor")
    app.setOrganizationName("egSYS")
    
    # Login
    login = LoginWindow()
    if login.exec_() == QDialog.Accepted:
        # Janela principal
        window = MainWindow(login.user_data)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
