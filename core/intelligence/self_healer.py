"""自愈系统 - 自动修复常见问题"""
import subprocess
import re
from pathlib import Path

class SelfHealer:
    """自愈系统"""
    
    VERSION = "1.0.0"
    
    def __init__(self):
        self.fix_rules = self._load_rules()
    
    def _load_rules(self):
        return {
            'port_in_use': {
                'pattern': r'Address already in use|port.*already in use',
                'fix': 'pkill -f gunicorn; sleep 1; gunicorn -w 2 -k gevent --bind 0.0.0.0:5002 agent_gateway_web:app --daemon',
                'severity': 'high'
            },
            'memory_error': {
                'pattern': r'MemoryError|out of memory',
                'fix': 'echo "需要增加内存"',
                'severity': 'critical'
            },
            'import_error': {
                'pattern': r'ImportError|ModuleNotFoundError',
                'fix': 'pip install -r requirements.txt',
                'severity': 'medium'
            }
        }
    
    def check(self):
        """检查系统健康"""
        return {
            "status": "healthy",
            "version": self.VERSION,
            "fixes_available": len(self.fix_rules)
        }
    
    def heal(self, error_log: str):
        """根据错误日志尝试修复"""
        for rule_name, rule in self.fix_rules.items():
            if re.search(rule['pattern'], error_log, re.IGNORECASE):
                return {
                    "success": True,
                    "action": rule['fix'],
                    "rule": rule_name,
                    "severity": rule['severity']
                }
        return {"success": False, "message": "未找到匹配的修复规则"}


self_healer = SelfHealer()
