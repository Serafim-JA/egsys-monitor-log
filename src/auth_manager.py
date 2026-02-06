import os
import hashlib
import json
from datetime import datetime

class AuthManager:
    def __init__(self, auth_file):
        self.auth_file = auth_file
        self.authorized_keys = self._load_authorized_keys()
    
    def _load_authorized_keys(self):
        if not os.path.exists(self.auth_file):
            default_keys = {
                "authorized_users": [
                    {
                        "name": "Lucas Serafim",
                        "email": "lucasserafim@egsyssuporte1-MS-7A15",
                        "key": "AAAAB3NzaC1yc2EAAAADAQABAAACAQC6/vBLRDkgqePjnfpxuQslwN4CaPJhtiXfS7QSxScgcaG0FpAyirCwV56tfeeRcS8RWmfYysln/5WzLmFNFdAk/4lHqouMrI6Sg1TbB+3WDrq8cROGmaJ6HoAn77YPLOzooPk8UHCGnFkj9q+pcK6FisX9S7CkG7y1ZrYRgpFbrLOOZwoJvveBFcpKjYbX8/Lco5rFnOOoT3F5vxfJdec5b9TNrIymrAIQdFuW9lTObYzsSH0XrDNw91l9xp2URV0ukT4iiUIwBYyWzJC2lVJSoqkvT/eDK6bnoKy2uDH6zdGh18HY59kKeRnW/qeZSpNUWl08C/VQrChqsLRpYqsNH0YL+W43kTVBy8ZX/scs+96sOf3scQ0bRl4egF5EKK6cZgfKlNSf51nbXf0sqymZqz728ptGT/XaqgdPxn6CdMsGdlvAD5njqNxujfOn3XUAKlsNRNg3bRvzvalZJ6MPCY3qjOrHmmA6WPDn47Mq1i7sLGntTrJHouOKL11YA6DhjxZL34wT54YmWjaRNwv8WnVBEc32Fb0+7kVpgUbb244DnK8VLxdA+X1K9Gwt+SFkcbgxpqizML/TWOppNoxrWjvAZ3iq2HEm3D07ZjYkW8fGUl5pAj1pJQdTq8yko//4KbGasnvHBVoMTNZO2Jr7dxReGF/MmUrzM56y4GuanQ==",
                        "role": "admin",
                        "created_at": datetime.now().isoformat(),
                        "last_access": None
                    }
                ]
            }
            os.makedirs(os.path.dirname(self.auth_file), exist_ok=True)
            with open(self.auth_file, 'w') as f:
                json.dump(default_keys, f, indent=2)
            os.chmod(self.auth_file, 0o600)
            return default_keys
        
        with open(self.auth_file, 'r') as f:
            return json.load(f)
    
    def _save_authorized_keys(self):
        with open(self.auth_file, 'w') as f:
            json.dump(self.authorized_keys, f, indent=2)
        os.chmod(self.auth_file, 0o600)
    
    def _get_current_user_key(self):
        ssh_dir = os.path.expanduser('~/.ssh')
        
        for key_file in ['id_rsa.pub', 'id_ed25519.pub', 'id_ecdsa.pub']:
            key_path = os.path.join(ssh_dir, key_file)
            if os.path.exists(key_path):
                with open(key_path, 'r') as f:
                    content = f.read().strip()
                    parts = content.split()
                    if len(parts) >= 2:
                        return parts[1]
        return None
    
    def authenticate(self):
        user_key = self._get_current_user_key()
        
        if not user_key:
            return False, "Nenhuma chave SSH pública encontrada em ~/.ssh/"
        
        for user in self.authorized_keys.get('authorized_users', []):
            if user['key'] == user_key:
                user['last_access'] = datetime.now().isoformat()
                self._save_authorized_keys()
                return True, user
        
        return False, "Chave SSH não autorizada"
    
    def add_user(self, name, email, key, role="user"):
        new_user = {
            "name": name,
            "email": email,
            "key": key,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_access": None
        }
        
        self.authorized_keys['authorized_users'].append(new_user)
        self._save_authorized_keys()
        return True
    
    def remove_user(self, key):
        users = self.authorized_keys.get('authorized_users', [])
        self.authorized_keys['authorized_users'] = [u for u in users if u['key'] != key]
        self._save_authorized_keys()
        return True
    
    def list_users(self):
        return self.authorized_keys.get('authorized_users', [])
    
    def get_access_log(self):
        log_file = self.auth_file.replace('authorized_keys.json', 'access_log.json')
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                return json.load(f)
        return []
    
    def log_access(self, user, action):
        log_file = self.auth_file.replace('authorized_keys.json', 'access_log.json')
        
        log_entry = {
            "user": user.get('name'),
            "email": user.get('email'),
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        logs = self.get_access_log()
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs[-1000:], f, indent=2)
        os.chmod(log_file, 0o600)
