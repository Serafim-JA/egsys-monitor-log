import os
import json
import hashlib
import requests
from datetime import datetime
import subprocess

class UpdateManager:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.config_file = os.path.join(base_dir, "config", "update_config.json")
        self.version_file = os.path.join(base_dir, "VERSION")
        self.config = self._load_config()
    
    def _load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        
        default_config = {
            "update_server": "http://192.168.1.100:8080",
            "check_interval": 3600,
            "auto_update": True,
            "current_version": "1.0.0",
            "last_check": None,
            "update_channel": "stable"
        }
        
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        return default_config
    
    def get_current_version(self):
        if os.path.exists(self.version_file):
            with open(self.version_file, 'r') as f:
                return f.read().strip()
        return self.config.get('current_version', '1.0.0')
    
    def check_for_updates(self):
        try:
            response = requests.get(
                f"{self.config['update_server']}/api/version",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                server_version = data.get('version')
                current_version = self.get_current_version()
                
                self.config['last_check'] = datetime.now().isoformat()
                self._save_config()
                
                if self._compare_versions(server_version, current_version) > 0:
                    return True, server_version, data.get('changelog', [])
                
                return False, current_version, []
        except:
            return False, self.get_current_version(), []
    
    def download_update(self, version):
        try:
            response = requests.get(
                f"{self.config['update_server']}/api/download/{version}",
                timeout=30
            )
            
            if response.status_code == 200:
                update_file = os.path.join(self.base_dir, f"update_{version}.tar.gz")
                with open(update_file, 'wb') as f:
                    f.write(response.content)
                return True, update_file
        except:
            pass
        
        return False, None
    
    def apply_update(self, update_file):
        try:
            backup_dir = os.path.join(self.base_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(backup_dir, exist_ok=True)
            
            subprocess.run(['tar', '-xzf', update_file, '-C', self.base_dir], check=True)
            
            os.remove(update_file)
            
            return True
        except:
            return False
    
    def _compare_versions(self, v1, v2):
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            p1 = v1_parts[i] if i < len(v1_parts) else 0
            p2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        
        return 0
    
    def _save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
