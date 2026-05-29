from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""加密钩子 - 用户数据加密/解密"""

import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from pathlib import Path
from typing import Dict, Any

class EncryptionHook:
    """用户数据加密钩子"""
    
    def __init__(self):
        self.key_file = Path(f"{get_data_root()}/keys/master.key")
        self._load_or_create_key()
    
    def _load_or_create_key(self):
        """加载或创建主密钥"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
        self.cipher = Fernet(self.key)
    
    def encrypt_user_data(self, context: Dict) -> Dict:
        """加密用户敏感数据"""
        data = context.get('data', {})
        sensitive_fields = ['preferences', 'habits', 'todos', 'patterns']
        
        for field in sensitive_fields:
            if field in data and data[field]:
                # 序列化并加密
                json_str = json.dumps(data[field], ensure_ascii=False)
                encrypted = self.cipher.encrypt(json_str.encode())
                data[f"{field}_encrypted"] = base64.b64encode(encrypted).decode()
                # 可选：保留非敏感部分或删除原字段
                # del data[field]
        
        context['data'] = data
        return context
    
    def decrypt_user_data(self, context: Dict) -> Dict:
        """解密用户敏感数据"""
        data = context.get('data', {})
        sensitive_fields = ['preferences', 'habits', 'todos', 'patterns']
        
        for field in sensitive_fields:
            encrypted_field = f"{field}_encrypted"
            if encrypted_field in data and data[encrypted_field]:
                try:
                    encrypted = base64.b64decode(data[encrypted_field])
                    decrypted = self.cipher.decrypt(encrypted)
                    data[field] = json.loads(decrypted.decode())
                except Exception as e:
                    print(f"⚠️ 解密失败 {field}: {e}")
        
        context['data'] = data
        return context


encryption_hook = EncryptionHook()
