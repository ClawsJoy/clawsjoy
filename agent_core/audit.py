"""操作审计 - 记录所有关键操作"""

import json
from pathlib import Path
from datetime import datetime
from functools import wraps

class AuditLog:
    def __init__(self):
        self.log_file = Path("logs/audit.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, user_id: str, action: str, resource: str, result: str, detail: dict = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "result": result,
            "detail": detail or {}
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def get_recent(self, limit=100):
        if not self.log_file.exists():
            return []
        with open(self.log_file, 'r') as f:
            lines = f.readlines()[-limit:]
            return [json.loads(line) for line in lines]

audit = AuditLog()
