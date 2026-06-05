#!/usr/bin/env python3
"""Agent 核心逻辑深度测试"""

import json
import sys
import time

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("🧠 Agent 核心逻辑验证")
print("=" * 60)

# 1. 测试 ChatAgent
print("\n1. 测试 ChatAgent...")
from agents.chat_agent.agent import ChatAgent

chat = ChatAgent("test_user_001")

test_cases = [
    ("你好", "问候"),
    ("我叫张三", "自我介绍"),
    ("今天天气怎么样", "天气查询"),
    ("1+2等于多少", "数学计算"),
    ("用粤语说你好", "方言翻译"),
    ("谢谢", "感谢"),
    ("再见", "告别"),
]

for msg, intent in test_cases:
    result = chat.process(msg)
    print(f"   📝 输入: {msg}")
    print(f"   🎯 意图: {intent}")
    print(f"   💬 响应: {result.get('response', '')[:60]}...")
    print(f"   ✅ 成功: {result.get('success', False)}")
    print()

# 2. 测试 CodeAgent
print("\n2. 测试 CodeAgent...")
try:
    from agents.code_agent.agent import CodeAgent

    code = CodeAgent("test_user_001")
    result = code.process("写一个计算斐波那契数列的函数")
    print(f"   💬 响应: {result.get('response', '')[:100]}...")
    print(f"   ✅ 成功: {result.get('success', False)}")
except Exception as e:
    print(f"   ⚠️ CodeAgent 测试: {e}")

# 3. 测试 Orchestrator (智能路由)
print("\n3. 测试 Orchestrator 智能路由...")
from agents.orchestrator.agent import orchestrator

orchestrator = orchestrator("test_user_001")

test_messages = [
    "帮我写代码",
    "今天天气怎么样",
    "翻译你好到英文",
    "计算 100 * 200",
]

for msg in test_messages:
    result = orchestrator.smart_route(msg)
    print(f"   📝 输入: {msg}")
    print(f"   🎯 路由到: {result}")
    print()
