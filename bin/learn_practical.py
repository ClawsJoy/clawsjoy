#!/usr/bin/env python3
import re
import json
from pathlib import Path

knowledge = {
    "learned_fixes": [],
    "learned_commands": [],
    "competency": {"service_recovery": 0, "error_diagnosis": 0}
}

# 从日志学习
log_file = Path("/mnt/d/clawsjoy/logs/auto_ops.log")
if log_file.exists():
    with open(log_file) as f:
        content = f.read()
    
    fixes = re.findall(r'✅ (.*?)(?:\n|$)', content)
    for fix in fixes[:10]:
        if fix not in knowledge["learned_fixes"]:
            knowledge["learned_fixes"].append(fix)
            print(f"📚 学到: {fix[:50]}")

# 能力评估
knowledge["competency"]["service_recovery"] = min(100, len(knowledge["learned_fixes"]) * 10)
knowledge["competency"]["error_diagnosis"] = 50

# 保存
with open('/mnt/d/clawsjoy/data/practical_knowledge.json', 'w') as f:
    json.dump(knowledge, f, indent=2)

print(f"\n📊 学习完成: {len(knowledge['learned_fixes'])} 个修复方法")
print(f"🔧 服务恢复能力: {knowledge['competency']['service_recovery']}%")
