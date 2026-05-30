from core.lib.config_helper import get_data_root, get_llm_endpoint, get_llm_model, get_embedding_model, get_gateway_port, get_timeout
from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""统一安全钩子 - 加密、脱敏、验证"""

import re
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet


class SecurityHooks:
    """统一安全钩子"""
    
    def __init__(self):
        self.key_file = Path(f"{get_data_root()}/keys/user_master.key")
        self._init_key()
    
    def _init_key(self):
        """初始化主密钥"""
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.key)
        self.cipher = Fernet(self.key)
    
    # ========== 数据脱敏 ==========
    def redact_sensitive(self, context: Dict) -> Dict:
        """脱敏敏感数据"""
        data = context.get('data', {})

        # 脱敏模式
        patterns = [
            (r'(api[_-]?key|apikey|token|secret)[=:]\s*\S+', r'\1=***'),
            (r'(password|passwd|pwd)[=:]\s*\S+', r'\1=***'),
            (r'(bearer|authorization)[=:]\s*\S+', r'\1=***'),
        ]

        for pattern, replacement in patterns:
            if isinstance(data, dict):
                for key in list(data.keys()):
                    if re.search(r'api|key|token|secret|password', key, re.I):
                        data[key] = '***'
            elif isinstance(data, str):
                data = re.sub(pattern, replacement, data, flags=re.I)

        context['data'] = data
        return context
    
    # ========== 加密/解密 ==========
    def encrypt_sensitive(self, context: Dict) -> Dict:
        """加密敏感数据"""
        data = context.get('data', {})
        sensitive_fields = context.get('sensitive_fields', 
            ['preferences', 'habits', 'todos', 'patterns', 'credentials'])

        for field in sensitive_fields:
            if field in data and data[field]:
                try:
                    json_str = json.dumps(data[field], ensure_ascii=False, default=str)
                    encrypted = self.cipher.encrypt(json_str.encode())
                    data[f"{field}_encrypted"] = base64.b64encode(encrypted).decode()
                    # 可选：删除原字段
                    # del data[field]
                except Exception as e:
                    print(f"⚠️ 加密失败 {field}: {e}")

        context['data'] = data
        return context
    
    def decrypt_sensitive(self, context: Dict) -> Dict:
        """解密敏感数据"""
        data = context.get('data', {})
        encrypted_fields = [k for k in data.keys() if k.endswith('_encrypted')]

        for enc_field in encrypted_fields:
            original_field = enc_field.replace('_encrypted', '')
            try:
                encrypted = base64.b64decode(data[enc_field])
                decrypted = self.cipher.decrypt(encrypted)
                data[original_field] = json.loads(decrypted.decode())
            except Exception as e:
                print(f"⚠️ 解密失败 {enc_field}: {e}")

        context['data'] = data
        return context
    
    # ========== 数据验证 ==========
    def validate_data(self, context: Dict) -> Dict:
        """验证数据完整性"""
        data = context.get('data', {})
        errors = []

        # 基本验证规则
        if isinstance(data, dict):
            # 检查必要字段
            if 'user_id' not in data and 'user_id' in context:
                data['user_id'] = context['user_id']

            # 检查数据大小
            data_size = len(json.dumps(data, default=str))
            if data_size > 10 * 1024 * 1024:  # 10MB
                errors.append("数据过大")

        context['data'] = data
        context['validation_errors'] = errors
        return context
    
    # ========== 准备/清理 ==========
    def prepare_encryption(self, context: Dict) -> Dict:
        """准备加密（预处理）"""
        context['sensitive_fields'] = ['preferences', 'habits', 'todos', 'patterns']
        return context
    
    def cleanup_after_decrypt(self, context: Dict) -> Dict:
        """解密后清理"""
        # 移除临时加密字段
        data = context.get('data', {})
        temp_fields = [k for k in data.keys() if k.startswith('_temp_')]
        for field in temp_fields:
            del data[field]
        context['data'] = data
        return context


# 全局实例
security_hooks = SecurityHooks()

# 导出函数（供钩子管理器调用）
redact_sensitive = security_hooks.redact_sensitive
encrypt_sensitive = security_hooks.encrypt_sensitive
decrypt_sensitive = security_hooks.decrypt_sensitive
validate_data = security_hooks.validate_data
prepare_encryption = security_hooks.prepare_encryption
cleanup_after_decrypt = security_hooks.cleanup_after_decrypt
