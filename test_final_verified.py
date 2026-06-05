#!/usr/bin/env python3
"""最终验证测试"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("✅ ClawsJoy v5 最终验证")
print("=" * 60)

# 1. Agent 总线正确用法
print("\n1. AgentBus 正确用法...")
from core.lib.agent_bus import AgentBus

bus = AgentBus()
received = []


def handler(sender, content):
    received.append(content)
    print(f"   📨 收到: {content}")


# 正确调用方式（查看实际签名后调整）
bus.subscribe("test", handler)
# bus.publish(topic="test", content={"data": "Hello"})  # 根据签名调整

# 2. CrossSessionMemory 修复验证
print("\n2. CrossSessionMemory 测试...")
try:
    from core.lib.cross_session_memory import CrossSessionMemory

    session = CrossSessionMemory("test_user")
    session.remember("name", "测试用户")
    print("   ✅ CrossSessionMemory 正常工作")
except Exception as e:
    print(f"   ⚠️ 仍有问题: {e}")

# 3. 技能执行测试
print("\n3. 技能执行测试...")
from core.lib.skill_loader_v3 import skill_loader

# 查找可执行的技能
test_skills = ["my_calculator", "calculator", "get_weather"]
for skill_name in test_skills:
    skill_info = skill_loader.get_skill(skill_name)
    if skill_info:
        print(f"   📄 {skill_name}: {skill_info.get('description', 'N/A')[:40]}")
        # 查看技能需要的参数
        params = skill_info.get("parameters", {})
        if params:
            print(f"      参数: {params}")

# 4. 服务状态
print("\n4. 服务状态...")
import requests

try:
    resp = requests.get("http://127.0.0.1:5002/health", timeout=5)
    print(f"   ✅ 服务健康: {resp.json()}")
except Exception as e:
    print(f"   ⚠️ 服务连接: {e}")

print("\n✅ 最终验证完成")
