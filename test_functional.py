#!/usr/bin/env python3
"""ClawsJoy v5 功能性测试"""

import json
import sys

import requests

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

BASE_URL = "http://127.0.0.1:5002"


def test_health():
    print("1. 健康检查...")
    r = requests.get(f"{BASE_URL}/health")
    print(f"   ✅ {r.json()}")


def test_metrics():
    print("\n2. 监控指标...")
    r = requests.get(f"{BASE_URL}/metrics")
    print(
        f"   ✅ CPU: {r.json().get('cpu_percent')}%, Memory: {r.json().get('memory_percent')}%"
    )


def test_chat():
    print("\n3. Chat Agent 测试...")
    # 测试内部直接调用
    from agents.chat_agent.agent import ChatAgent

    agent = ChatAgent("test_user")
    result = agent.process("你好")
    print(f"   ✅ {result['response'][:50]}...")


def test_memory_api():
    print("\n4. 记忆 API 测试...")
    # 测试记忆存储
    r = requests.post(
        f"{BASE_URL}/api/v5/memory/remember",
        json={"user_id": "test", "key": "name", "value": "ClawsJoy"},
    )
    if r.status_code == 200:
        print(f"   ✅ 记忆存储成功")
    else:
        print(f"   ⚠️ 记忆 API 返回 {r.status_code}")

    # 测试记忆检索
    r = requests.post(
        f"{BASE_URL}/api/v5/memory/recall", json={"user_id": "test", "key": "name"}
    )
    if r.status_code == 200:
        print(f"   ✅ 记忆检索: {r.json()}")


def test_enhanced_chat():
    print("\n5. 增强聊天 API...")
    r = requests.post(
        f"{BASE_URL}/api/v5/enhanced/chat", json={"user_id": "test", "message": "你好"}
    )
    if r.status_code == 200:
        print(f"   ✅ {r.json()}")
    else:
        print(f"   ⚠️ 返回 {r.status_code}")


def test_skills():
    print("\n6. 技能系统测试...")
    from core.lib.skill_loader_v3 import skill_loader

    # 查找正确的方法
    methods = [m for m in dir(skill_loader) if not m.startswith("_")]
    print(f"   可用方法: {methods[:10]}...")

    # 尝试获取技能列表
    if hasattr(skill_loader, "get_skills"):
        skills = skill_loader.get_skills()
        print(f"   ✅ 已加载 {len(skills)} 个技能")
    elif hasattr(skill_loader, "skills"):
        print(f"   ✅ 已加载 {len(skill_loader.skills)} 个技能")
    else:
        print(f"   ⚠️ 技能列表方法未知")


if __name__ == "__main__":
    test_health()
    test_metrics()
    test_chat()
    test_memory_api()
    test_enhanced_chat()
    test_skills()
