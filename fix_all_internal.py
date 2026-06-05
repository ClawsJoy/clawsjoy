#!/usr/bin/env python3
"""内部核心功能修复脚本"""

import os
import re
import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("🔧 ClawsJoy v5 内部功能修复")
print("=" * 60)

# 1. 修复技能加载器方法
print("\n1. 检查技能加载器...")
from core.lib.skill_loader_v3 import skill_loader

# 查看正确的方法名
print(f"   list_skills 返回类型: {type(skill_loader.list_skills())}")
skills = skill_loader.list_skills()
if isinstance(skills, dict):
    print(f"   技能是字典，键: {list(skills.keys())[:5]}")
    # 获取技能列表
    skill_names = list(skills.keys())
    print(f"   技能名称示例: {skill_names[:10]}")
elif isinstance(skills, list):
    print(f"   技能是列表，长度: {len(skills)}")
    if skills:
        print(
            f"   示例: {skills[0] if isinstance(skills[0], str) else skills[0].get('name', 'unknown')}"
        )

# 2. 检查 SmartMemoryManager 方法
print("\n2. 检查 SmartMemoryManager...")
from core.butler.memory_manager import SmartMemoryManager

memory = SmartMemoryManager("test")
methods = [
    m for m in dir(memory) if not m.startswith("_") and callable(getattr(memory, m))
]
print(f"   可用方法: {methods[:15]}")

# 3. 检查 Agent 注册表
print("\n3. 检查 Agent 注册表...")
from core.lib.agent_registry import agent_registry

registry_methods = [m for m in dir(agent_registry) if not m.startswith("_")]
print(f"   AgentRegistry 方法: {registry_methods[:15]}")
stats = agent_registry.get_stats()
print(f"   统计: {stats}")

# 4. 检查 Orchestrator 类名
print("\n4. 检查 Orchestrator...")
import agents.orchestrator.agent as orch

orch_classes = [c for c in dir(orch) if c[0].isupper()]
print(f"   Orchestrator 模块中的类: {orch_classes}")

# 5. 检查 Agent 总线
print("\n5. 检查 Agent 总线...")
try:
    from core.lib.agent_bus import AgentBus

    print(f"   AgentBus 类存在")
    bus_methods = [m for m in dir(AgentBus) if not m.startswith("_")]
    print(f"   方法: {bus_methods[:10]}")
except ImportError as e:
    print(f"   AgentBus 导入失败: {e}")

print("\n✅ 诊断完成")
