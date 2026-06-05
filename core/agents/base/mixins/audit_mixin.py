"""审计 Mixin - 所有 Agent 的审计规范"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class AuditMixin:
    """审计规范 - 每个 Agent 必须遵守"""

    def _audit(self, action: str, input_data: Dict, output_data: Dict, success: bool = True):
        """记录审计日志"""
        user_id = getattr(self, 'user_id', 'unknown')
        agent_name = getattr(self, 'name', 'unknown')
        
        audit_dir = Path(f"data/users/{user_id}/audit")
        audit_dir.mkdir(parents=True, exist_ok=True)
        
        audit_file = audit_dir / f"{datetime.now().strftime('%Y%m%d')}.json"
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "input": str(input_data)[:500],
            "output": str(output_data)[:500],
            "success": success
        }
        
        # 读取现有日志
        existing = []
        if audit_file.exists():
            try:
                with open(audit_file, 'r') as f:
                    existing = json.load(f)
            except:
                pass
        
        existing.append(entry)
        
        with open(audit_file, 'w') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        
        print(f"[审计] {agent_name} - {action[:50]}...")

    def audit_task_start(self, task: str):
        """记录任务开始"""
        self._audit("task_start", {"task": task}, {}, True)

    def audit_task_end(self, task: str, result: str, success: bool = True):
        """记录任务结束"""
        self._audit("task_end", {"task": task}, {"result": result[:200]}, success)
