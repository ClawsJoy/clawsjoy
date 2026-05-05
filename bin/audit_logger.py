#!/usr/bin/env python3
"""ClawsJoy 审计日志模块"""

import json
import os
from datetime import datetime
from pathlib import Path

AUDIT_LOG = Path("/mnt/d/clawsjoy/logs/audit.log")


def log_audit(tenant_id: str, action: str, detail: str):
    """记录审计日志"""
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "tenant": tenant_id,
        "action": action,
        "detail": detail,
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def query_audit(tenant_id: str = None, limit: int = 100):
    """查询审计日志"""
    if not AUDIT_LOG.exists():
        return []
    entries = []
    with open(AUDIT_LOG, "r") as f:
        for line in f:
            entry = json.loads(line)
            if tenant_id is None or entry.get("tenant") == tenant_id:
                entries.append(entry)
    return entries[-limit:]


if __name__ == "__main__":
    # 测试
    log_audit("tenant_1", "test", "audit working")
    print("最近日志:", query_audit(limit=3))
