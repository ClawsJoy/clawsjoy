"""用户专属安全网关 - 1对1服务，数据完全隔离"""

import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Tuple

class UserSecurityGate:
    """
    用户专属安全网关
    - 每个用户独立保险库
    - 数据完全隔离
    - 1对1亲密服务
    """
    
    PATTERNS = {
        "api_key": [r'api_key["\s:]+["\']?([a-zA-Z0-9_\-]{10,})["\']?', r'API_KEY\s*=\s*["\']([a-zA-Z0-9_\-]+)["\']'],
        "password": [r'密码[是为]?\s*["\']?([^"\'\s，,]{4,})["\']?', r'pwd\s*=\s*["\']([^"\']+)["\']'],
        "email": [r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'],
        "token": [r'token["\s:]+["\']?([a-zA-Z0-9_\-\.]{20,})["\']?'],
        "phone": [r'1[3-9]\d{9}'],
        "id_card": [r'[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]'],
    }
    
    def __init__(self, user_id: str, base_path: str = "data/security_vault"):
        self.user_id = user_id
        self.vault_path = Path(base_path) / user_id
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self._vault = self._load_vault()
    
    def _load_vault(self) -> Dict:
        vault_file = self.vault_path / "secrets.json"
        if vault_file.exists():
            with open(vault_file, 'r') as f:
                return json.load(f)
        return {"user_id": self.user_id, "secrets": {}, "created_at": datetime.now().isoformat(), "stats": {"total": 0}}
    
    def _save_vault(self):
        vault_file = self.vault_path / "secrets.json"
        self._vault['stats']['total'] = len(self._vault['secrets'])
        self._vault['stats']['updated_at'] = datetime.now().isoformat()
        with open(vault_file, 'w') as f:
            json.dump(self._vault, f, indent=2)
    
    def _generate_placeholder(self, secret_type: str, value: str) -> str:
        short_hash = hashlib.md5(f"{self.user_id}{value}".encode()).hexdigest()[:8]
        return f"🔐[{secret_type.upper()}_{short_hash}]"
    
    def protect(self, text: str) -> Tuple[str, List[Dict]]:
        """保护用户输入 - 脱敏并保管"""
        sanitized = text
        extracted = []
        
        for stype, patterns in self.PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, sanitized, re.IGNORECASE)
                for match in matches:
                    value = match if isinstance(match, str) else match[-1]
                    if len(str(value)) < 4:
                        continue
                    
                    secret_id = hashlib.md5(f"{self.user_id}{stype}{value}".encode()).hexdigest()[:16]
                    placeholder = self._generate_placeholder(stype, value)
                    
                    if secret_id not in self._vault['secrets']:
                        self._vault['secrets'][secret_id] = {
                            'id': secret_id, 'type': stype, 'value': value,
                            'placeholder': placeholder, 'created_at': datetime.now().isoformat(),
                            'use_count': 0
                        }
                        extracted.append({'type': stype, 'placeholder': placeholder, 'value_preview': value[:8] + '...'})
                    
                    self._vault['secrets'][secret_id]['use_count'] += 1
                    sanitized = sanitized.replace(value, placeholder)
        
        if extracted:
            self._save_vault()
            print(f"🔒 [{self.user_id}] 已保护 {len(extracted)} 条敏感信息")
        
        return sanitized, extracted
    
    def reveal(self, text: str) -> str:
        """恢复输出 - 脱敏显示（不暴露完整值）"""
        restored = text
        for secret_id, record in self._vault['secrets'].items():
            if record['placeholder'] in restored:
                value = record['value']
                if len(value) > 12:
                    masked = value[:4] + "●●●●" + value[-4:]
                elif len(value) > 6:
                    masked = value[:3] + "●●●●" + value[-3:]
                else:
                    masked = "●●●●"
                restored = restored.replace(record['placeholder'], f"[{record['type']}:{masked}]")
        return restored
    
    def get_my_secrets(self) -> List[Dict]:
        """查看我保管的所有信息"""
        return [
            {'type': s['type'], 'created_at': s['created_at'], 'use_count': s['use_count']}
            for s in self._vault['secrets'].values()
        ]
    
    def get_stats(self) -> Dict:
        return {
            'user_id': self.user_id,
            'total_secrets': len(self._vault['secrets']),
            'vault_path': str(self.vault_path),
            'created_at': self._vault.get('created_at'),
            'last_updated': self._vault.get('stats', {}).get('updated_at')
        }
    
    def chat(self, message: str) -> str:
        """专属对话 - 自动保护敏感信息"""
        # 1. 保护用户输入
        safe_msg, protected = self.protect(message)
        
        # 2. 调用 LLM
        import requests
        resp = requests.post("http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": safe_msg, "stream": False}, timeout=60)
        raw_response = resp.json().get('response', '')
        
        # 3. 恢复并脱敏
        safe_response = self.reveal(raw_response)
        
        return safe_response, protected


class SecurityManager:
    """安全管家管理器 - 管理所有用户的安全网关"""
    
    _instance = None
    _gates: Dict[str, UserSecurityGate] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_gate(self, user_id: str) -> UserSecurityGate:
        """获取用户专属安全网关（1对1服务）"""
        if user_id not in self._gates:
            self._gates[user_id] = UserSecurityGate(user_id)
            print(f"🛡️ 为用户 [{user_id}] 创建专属安全管家")
        return self._gates[user_id]
    
    def get_all_stats(self) -> Dict:
        return {uid: gate.get_stats() for uid, gate in self._gates.items()}

security_manager = SecurityManager()
