#!/usr/bin/env python3
"""敏感数据过滤器 - Agent 安全边界核心组件"""

import re
import json
from pathlib import Path

class SecretFilter:
    """识别、隔离、脱敏用户输入中的敏感数据"""
    
    PATTERNS = {
        "client_secret": [
            r'client_secret["\s:]+["\']?([a-zA-Z0-9_\-]{10,})["\']?',
            r'"client_secret":\s*"([^"]+)"',
        ],
        "api_key": [
            r'api_key["\s:]+["\']?([a-zA-Z0-9_\-]{10,})["\']?',
            r'API_KEY\s*=\s*["\']([a-zA-Z0-9_\-]+)["\']',
        ],
        "access_token": [
            r'access_token["\s:]+["\']?(ya29\.[a-zA-Z0-9_\-\.]+)["\']?',
            r'Bearer\s+([a-zA-Z0-9_\-\.]+)',
        ],
        "webhook": [
            r'https?://[^\s]+webhook[^\s]*',
            r'dingtalk\.com[^\s]*',
            r'feishu\.cn[^\s]*',
            r'qyapi\.weixin\.qq\.com[^\s]*',
        ],
    }
    
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
        self.secrets_vault = Path(f"/mnt/d/clawsjoy/tenants/{tenant_id}/secrets.json")
        self.secrets_vault.parent.mkdir(parents=True, exist_ok=True)
        self._load_vault()
    
    def _load_vault(self):
        if self.secrets_vault.exists():
            with open(self.secrets_vault) as f:
                self.vault = json.load(f)
        else:
            self.vault = {"secrets": {}}
    
    def _save_vault(self):
        with open(self.secrets_vault, 'w') as f:
            json.dump(self.vault, f, indent=2)
    
    def extract_and_sanitize(self, text):
        extracted = {}
        sanitized = text
        
        for key_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                matches = re.findall(pattern, sanitized, re.IGNORECASE | re.DOTALL)
                if matches:
                    extracted[key_type] = matches
                    for match in matches:
                        placeholder = f"[{key_type.upper()}_REDACTED]"
                        sanitized = sanitized.replace(match, placeholder)
        
        if extracted:
            for key_type, values in extracted.items():
                if key_type not in self.vault["secrets"]:
                    self.vault["secrets"][key_type] = []
                for v in values:
                    if v not in self.vault["secrets"][key_type]:
                        self.vault["secrets"][key_type].append(v)
            self._save_vault()
        
        return sanitized, extracted
    
    def get_secret(self, key_type):
        return self.vault["secrets"].get(key_type, [])
    
    def has_secret(self, key_type):
        return key_type in self.vault["secrets"] and len(self.vault["secrets"][key_type]) > 0

if __name__ == "__main__":
    sf = SecretFilter("tenant_1")
    test = 'client_secret="abc123", webhook: https://oapi.dingtalk.com/robot/send?token=xyz'
    sanitized, extracted = sf.extract_and_sanitize(test)
    print(f"脱敏: {sanitized}")
    print(f"提取: {extracted}")
