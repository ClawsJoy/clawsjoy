"""安全 Mixin - 所有 Agent 的安全规范（通过 Hook 实现）"""

import re
from typing import Dict, List, Tuple
from datetime import datetime


class SecurityMixin:
    """安全规范 - 横切关注点"""

    # 危险关键词
    DANGEROUS_PATTERNS = [
        r'(rm\s+-rf|del\s+/|format\s+[c-z]:)',
        r'(drop\s+table|truncate\s+table|delete\s+from)',
        r'(eval\(|exec\(|__import__\(|compile\()',
        r'(sudo|chmod\s+777|chown)',
        r'(wget|curl).*\|.*sh',
    ]

    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        r'(password|passwd|pwd|secret|token|key)\s*[=:]\s*[\'"]?[^\'"]+',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # email
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # phone
    ]

    def security_check_input(self, user_input: str) -> Tuple[bool, str]:
        """输入安全检查"""
        # 检查危险模式
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False, f"检测到危险操作: {pattern}"
        
        return True, "安全"

    def security_mask_sensitive(self, text: str) -> str:
        """脱敏处理"""
        result = text
        for pattern in self.SENSITIVE_PATTERNS:
            result = re.sub(pattern, '***已脱敏***', result)
        return result

    def security_check_output(self, output: str) -> Tuple[bool, str]:
        """输出安全检查"""
        # 检查是否泄露敏感信息
        for pattern in self.SENSITIVE_PATTERNS:
            if re.search(pattern, output, re.IGNORECASE):
                return False, "检测到敏感信息泄露"
        
        return True, "安全"

    def security_rate_limit(self, user_id: str, action: str) -> bool:
        """频率限制"""
        from pathlib import Path
        import json
        from datetime import datetime
        
        rate_file = Path(f"data/users/{user_id}/rate_limit.json")
        now = datetime.now()
        minute_key = now.strftime("%Y%m%d%H%M")
        
        # 读取现有记录
        records = {}
        if rate_file.exists():
            try:
                with open(rate_file, 'r') as f:
                    records = json.load(f)
            except:
                pass
        
        # 检查频率（每分钟最多10次）
        if minute_key in records:
            if records[minute_key] >= 10:
                return False
        
        records[minute_key] = records.get(minute_key, 0) + 1
        with open(rate_file, 'w') as f:
            json.dump(records, f)
        
        return True
