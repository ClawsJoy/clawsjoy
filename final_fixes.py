#!/usr/bin/env python3
"""最终修复脚本"""

import os
import re
import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("🔧 应用最终修复...")
print("=" * 60)

# 1. 修复 CrossSessionMemory 中的变量名
print("\n1. 修复 CrossSessionMemory...")
file_path = "core/lib/cross_session_memory.py"
if os.path.exists(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    # 修复 funified_config -> unified_config
    if "funified_config" in content:
        content = content.replace("funified_config", "unified_config")
        with open(file_path, "w") as f:
            f.write(content)
        print("   ✅ 已修复 funified_config -> unified_config")
    else:
        print("   ✅ 无需修复")
else:
    print(f"   ⚠️ 文件不存在: {file_path}")

# 2. 查看 AgentBus.publish 的正确签名
print("\n2. 检查 AgentBus.publish 签名...")
try:
    import inspect

    from core.lib.agent_bus import AgentBus

    sig = inspect.signature(AgentBus.publish)
    print(f"   📋 publish 签名: {sig}")
except Exception as e:
    print(f"   ⚠️ 无法检查: {e}")

# 3. 修复技能搜索中文支持
print("\n3. 检查技能搜索...")
from core.lib.skill_loader_v3 import skill_loader

# 测试中文搜索
skills = skill_loader.list_skills()
skill_names = list(skills.keys()) if isinstance(skills, dict) else skills

# 查找包含中文的技能
chinese_skills = [s for s in skill_names if any("\u4e00" <= c <= "\u9fff" for c in s)]
print(f"   📝 包含中文的技能: {chinese_skills[:10]}")

# 测试中文字段搜索
if hasattr(skill_loader, "search_skills_by_chinese"):
    print("   ✅ 支持中文搜索")
else:
    print("   ⚠️ 中文搜索需要通过技能描述匹配")

print("\n✅ 修复完成")
