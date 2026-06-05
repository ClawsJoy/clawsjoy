#!/usr/bin/env python3
"""修复后的技能系统测试"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("🔧 技能系统测试 (修复版)")
print("=" * 60)

from core.lib.skill_loader_v3 import skill_loader

# 1. 获取技能（正确处理 dict）
print("\n1. 技能加载测试...")
skills = skill_loader.list_skills()
print(f"   📦 技能类型: {type(skills)}")

if isinstance(skills, dict):
    skill_names = list(skills.keys())
    print(f"   📦 技能总数: {len(skill_names)}")
    print(f"   📂 技能分类: {skill_names[:10]}")

    # 查找特定技能
    for keyword in ["calc", "math", "weather", "translate", "video"]:
        matches = [name for name in skill_names if keyword in name.lower()]
        if matches:
            print(f"   🔍 '{keyword}' 相关技能: {matches[:5]}")

# 2. 获取技能详情
print("\n2. 技能详情测试...")
skill_name = "get_weather"
skill_info = skill_loader.get_skill(skill_name)
if skill_info:
    print(f"   📄 {skill_name}: {skill_info.get('description', 'N/A')[:50]}")
else:
    print(f"   ⚠️ 技能 '{skill_name}' 不存在")

# 3. 搜索技能
print("\n3. 技能搜索测试...")
search_terms = ["天气", "计算", "翻译"]
for term in search_terms:
    results = skill_loader.search_skills(term)
    print(f"   🔍 搜索 '{term}': 找到 {len(results)} 个技能")
    if results:
        print(f"      示例: {results[:3]}")

print("\n✅ 技能系统测试完成")
