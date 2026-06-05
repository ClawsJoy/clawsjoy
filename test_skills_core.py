#!/usr/bin/env python3
"""技能系统内部逻辑深度测试"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("🔧 技能系统内部逻辑验证")
print("=" * 60)

# 1. 技能加载器测试
print("\n1. 技能加载器测试...")
from core.lib.skill_loader_v3 import skill_loader

# 获取所有技能
skills = skill_loader.list_skills()
print(f"   📦 已加载技能总数: {len(skills)}")

# 按类别分组
categories = skill_loader.get_categories()
print(f"   📂 技能类别: {list(categories.keys())[:10]}...")

# 2. 搜索技能
print("\n2. 技能搜索测试...")
search_terms = ["计算", "天气", "翻译", "视频", "图片"]

for term in search_terms:
    results = skill_loader.search_skills(term)
    print(f"   🔍 搜索 '{term}': 找到 {len(results)} 个技能")

# 3. 技能执行测试
print("\n3. 技能执行测试...")

# 测试计算器技能
try:
    calc_result = skill_loader.execute("calculator", {"a": 100, "b": 200, "op": "+"})
    print(f"   🧮 计算器: 100 + 200 = {calc_result}")
except Exception as e:
    print(f"   ⚠️ 计算器: {e}")

# 测试天气技能（需要网络）
try:
    weather_result = skill_loader.execute("weather", {"city": "北京"})
    print(f"   🌤️ 天气: {weather_result}")
except Exception as e:
    print(f"   ⚠️ 天气: {e}")

# 4. 技能元数据
print("\n4. 技能元数据示例...")
if skills:
    sample = skills[0]
    print(f"   📄 示例技能: {sample.get('name', 'unknown')}")
    print(f"     描述: {sample.get('description', 'N/A')[:50]}")
