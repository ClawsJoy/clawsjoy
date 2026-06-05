#!/usr/bin/env python3
"""Auto Scanner - Auto Scanner 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""自动安全检测 - 精确版"""
import re
from pathlib import Path

# 真正危险的操作（精确匹配）
DANGEROUS_PATTERNS = {
    r"os\.system\s*\(": "critical",
    r"os\.popen\s*\(": "critical",
    r"subprocess\.run\s*\(": "high",
    r"subprocess\.Popen\s*\(": "high",
    r"eval\s*\(": "critical",
    r"exec\s*\(": "critical",
    r"__import__\s*\(": "high",
    r"pickle\.loads?\s*\(": "high",
    r"compile\s*\(": "high",
}


def scan_skill_code(code, skill_name):
    """扫描技能代码 - 精确匹配"""
    issues = []
    risk_level = "low"

    for pattern, level in DANGEROUS_PATTERNS.items():
        if re.search(pattern, code):
            issues.append({"pattern": pattern, "level": level})
            if level == "critical":
                risk_level = "critical"
            elif level == "high" and risk_level != "critical":
                risk_level = "high"

    is_safe = risk_level not in ["critical", "high"]

    if not is_safe:
        print(f"⚠️ 安全警告: {skill_name} 被阻止 ({risk_level})")
        from datetime import datetime

        Path("logs").mkdir(exist_ok=True)
        with open("logs/security.log", "a") as f:
            f.write(f"{datetime.now()} | BLOCKED | {skill_name} | {risk_level}\n")

    return is_safe
