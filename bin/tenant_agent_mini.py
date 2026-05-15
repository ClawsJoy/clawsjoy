#!/usr/bin/env python3
"""最小 TenantAgent - 只做关键词统计"""

import json
from pathlib import Path

class TenantAgent:
    def __init__(self, tenant_id="tenant_1"):
        self.tenant_id = tenant_id
    
    def process(self, user_input):
        # 关键词统计
        if "统计" in user_input or "关键词" in user_input:
            kw_file = Path("/mnt/d/clawsjoy/data/keywords.json")
            pending_file = Path("/mnt/d/clawsjoy/data/keyword_pending.json")
            
            total = 0
            if kw_file.exists():
                with open(kw_file) as f:
                    data = json.load(f)
                for cat, info in data.get("categories", {}).items():
                    total += len(info.get("keywords", []))
            
            pending = 0
            if pending_file.exists():
                with open(pending_file) as f:
                    pdata = json.load(f)
                pending = len(pdata.get("candidates", {}))
            
            return {"type": "result", "message": f"📊 关键词库: {total} 个, 待学习: {pending} 个"}
        
        return {"type": "text", "message": f"收到: {user_input}"}
