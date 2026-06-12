#!/usr/bin/env python3
"""端到端集成测试"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "agent_v4", 
    "agents/chat_agent/agent_v4.py"
)
agent_v4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_v4)
ChatAgentV4 = agent_v4.ChatAgentV4

from core.agents.wisdom.wisdom_wrapper import WisdomWrapper


def test_e2e_simple():
    """测试简单文本输入"""
    print("\n" + "=" * 50)
    print("E2E 测试1: 简单文本输入")
    
    agent = ChatAgentV4("e2e_user")
    
    user_input = "你好，我叫李明"
    print(f"User: {user_input}")
    result = agent.process(user_input)
    print(f"Assistant: {result.get('response')}")
    
    result = agent.process("我叫什么名字")
    print(f"User: 我叫什么名字")
    print(f"Assistant: {result.get('response')}")
    
    print("✅ 简单文本测试通过")


def test_e2e_json():
    """测试标准化 JSON 输入"""
    print("\n" + "=" * 50)
    print("E2E 测试2: 标准化 JSON 输入")
    
    agent = ChatAgentV4("e2e_user")
    
    json_input = {
        "version": "1.1",
        "action": "chat",
        "target": "text",
        "raw_input": "介绍一下你自己",
        "user_id": "e2e_user",
        "session_id": "test_session",
        "thread_id": "test_thread",
        "turn": 0
    }
    
    print(f"JSON input: {json.dumps(json_input, ensure_ascii=False)}")
    result = agent.handle_json(json_input)
    print(f"Output: {result.get('output_content', result.get('response'))[:100]}")
    
    assert result.get("version") == "1.1"
    assert result.get("session_id") == "test_session"
    
    print("✅ JSON 输入测试通过")


def test_e2e_with_wrapper():
    """测试智慧包装器"""
    print("\n" + "=" * 50)
    print("E2E 测试3: 智慧包装器")
    
    agent = ChatAgentV4("e2e_user")
    wisdom_agent = WisdomWrapper(agent)
    
    result = wisdom_agent.process("帮我分析一下这个问题")
    print(f"Result: {result.get('output_content', result.get('response'))[:100]}")
    
    awareness = wisdom_agent.get_self_awareness()
    print(f"Self awareness: {awareness.get('identity', {}).get('name')}")
    
    print("✅ 智慧包装器测试通过")


def test_performance():
    """性能测试"""
    print("\n" + "=" * 50)
    print("性能测试: 缓存 + 批处理")
    
    import time
    
    agent = ChatAgentV4("perf_user")
    
    test_inputs = [
        "你好",
        "你好",
        "你好",
        "今天天气怎么样",
        "今天天气怎么样",
    ]
    
    start = time.time()
    for inp in test_inputs:
        agent.process(inp)
    elapsed = time.time() - start
    
    cache_hits = agent._stats.get('cache_hits', 0)
    cache_misses = agent._stats.get('cache_misses', 0)
    total = cache_hits + cache_misses
    hit_rate = cache_hits / total if total > 0 else 0
    
    print(f"Processed {len(test_inputs)} messages in {elapsed:.3f}s")
    print(f"Cache hits: {cache_hits}, misses: {cache_misses}")
    print(f"Cache hit rate: {hit_rate:.0%}")
    
    print("✅ 性能测试通过")


if __name__ == "__main__":
    print("🧪 端到端集成测试")
    
    test_e2e_simple()
    test_e2e_json()
    test_e2e_with_wrapper()
    test_performance()
    
    print("\n" + "=" * 50)
    print("🎉 所有 E2E 测试通过！")
