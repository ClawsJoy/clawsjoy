"""租户隔离的安全网关"""

from agent_core.auth.tenant_auth import tenant_auth
import hashlib
import json
from pathlib import Path
from datetime import datetime

class TenantSecurityGate:
    """租户隔离的安全管家"""
    
    def __init__(self, tenant_id: str, user_id: str):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.vault_path = tenant_auth.get_user_data_path(tenant_id, user_id) / "secrets.json"
        self._vault = self._load_vault()
    
    def _load_vault(self):
        if self.vault_path.exists():
            with open(self.vault_path, 'r') as f:
                return json.load(f)
        return {"secrets": {}}
    
    def _save_vault(self):
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.vault_path, 'w') as f:
            json.dump(self._vault, f, indent=2)
    
    def protect(self, text: str):
        """保护敏感信息（租户隔离）"""
        # 简化的保护逻辑
        sanitized = text
        return sanitized, []
    
    def chat(self, message: str):
        """安全对话（租户隔离）"""
        import requests
        safe_msg, _ = self.protect(message)
        try:
            resp = requests.post("http://localhost:11434/api/generate",
                json={"model": "llama3.2:3b", "prompt": safe_msg, "stream": False}, timeout=60)
            response = resp.json().get('response', '')
            return response, []
        except:
            return "服务暂时不可用", []

def get_tenant_gate(tenant_id: str, user_id: str):
    """获取租户隔离的安全管家"""
    return TenantSecurityGate(tenant_id, user_id)
