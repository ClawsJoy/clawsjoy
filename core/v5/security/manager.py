"""安全模块 - 权限管理、输入验证"""

import re
from typing import Dict, List, Optional
from datetime import datetime


class SecurityManager:
    """安全管理器"""
    
    def __init__(self):
        self.api_keys: Dict[str, Dict] = {}
        self.rate_limits: Dict[str, List[float]] = {}
    
    def validate_input(self, text: str) -> bool:
        """验证输入安全性"""
        if not text or len(text) > 10000:
            return False
        # 防止注入
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'--',
            r';.*DROP',
            r';.*DELETE'
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        return True
    
    def sanitize_output(self, text: str) -> str:
        """清理输出"""
        # 转义 HTML
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
    
    def check_rate_limit(self, user_id: str, limit: int = 60, window: int = 60) -> bool:
        """检查频率限制"""
        import time
        current = time.time()
        if user_id not in self.rate_limits:
            self.rate_limits[user_id] = []
        
        # 清理过期记录
        self.rate_limits[user_id] = [t for t in self.rate_limits[user_id] if current - t < window]
        
        if len(self.rate_limits[user_id]) >= limit:
            return False
        
        self.rate_limits[user_id].append(current)
        return True
    
    def generate_api_key(self, user_id: str) -> str:
        """生成 API Key"""
        import secrets
        api_key = f"ck_{secrets.token_hex(16)}"
        self.api_keys[api_key] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_used": None
        }
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[str]:
        """验证 API Key"""
        if api_key in self.api_keys:
            self.api_keys[api_key]["last_used"] = datetime.now().isoformat()
            return self.api_keys[api_key]["user_id"]
        return None


security = SecurityManager()
