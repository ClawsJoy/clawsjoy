#!/usr/bin/env python3
"""修复后的技能系统测试"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=== 技能系统修复测试 ===")

from core.lib.skill_loader_v3 import skill_loader

# 1. 获取技能（处理 dict 和 list 两种情况）
skills = skill_loader.list_skills()
print(f"\n1. 技能数据类型: {type(skills)}")

if isinstance(skills, dict):
    skill_names = list(skills.keys())
    print(f"   技能数量: {len(skill_names)}")
    print(f"   技能示例: {skill_names[:10]}")

    # 搜索包含关键词的技能
    for keyword in ["calc", "math", "weather", "translate", "video"]:
        matches = [name for name in skill_names if keyword in name.lower()]
        print(f"   搜索 '{keyword}': 找到 {len(matches)} 个技能")
        if matches:
            print(f"     示例: {matches[:3]}")
else:
    print(f"   技能数量: {len(skills)}")
    if skills:
        print(f"   示例: {skills[0]}")

# 2. 尝试执行技能
print("\n2. 技能执行测试...")
# 查找数学相关技能
math_skills = [
    name for name in skill_names if "calc" in name.lower() or "math" in name.lower()
]
if math_skills:
    skill_name = math_skills[0]
    print(f"   尝试执行: {skill_name}")
    try:
        result = skill_loader.execute(skill_name, {"a": 10, "b": 5})
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   执行失败: {e}")

print("\n✅ 测试完成")
