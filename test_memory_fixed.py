#!/usr/bin/env python3
"""修复后的记忆系统测试"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("🧠 记忆系统测试 (修复版)")
print("=" * 60)

# 1. SmartMemoryManager 测试
print("\n1. SmartMemoryManager 测试...")
from core.butler.memory_manager import SmartMemoryManager

memory = SmartMemoryManager("test_user_fixed")
print(f"   ✅ SmartMemoryManager 加载成功")

# 使用正确的方法
memory.remember_fact("用户喜欢 Python 编程", importance=5)
print("   ✅ remember_fact() 成功")

memory.remember_preference("theme", "dark")
memory.remember_preference("language", "zh-CN")
print("   ✅ remember_preference() 成功")

memory.add_conversation("你好", "你好！有什么可以帮助您的吗？")
memory.add_conversation("今天天气怎么样", "今天天气晴朗，温度25度")
print("   ✅ add_conversation() 成功")

# 检索
pref = memory.recall_preference("theme")
print(f"   📝 偏好 theme: {pref}")

context = memory.recall_context("Python", limit=3)
print(f"   📝 上下文: {context}")

stats = memory.get_stats()
print(f"   📊 统计: {stats}")

# 2. 跨会话记忆测试
print("\n2. 跨会话记忆测试...")
from core.lib.cross_session_memory import CrossSessionMemory

session = CrossSessionMemory("test_user_cross")
session.remember("name", "张三")
session.remember("age", 25)
session.record_interaction("你好", "你好！")
print("   ✅ 跨会话记忆存储成功")

user_info = session.recall()
print(f"   📝 用户信息: {user_info}")

# 3. 向量记忆测试
print("\n3. 向量记忆测试...")
from core.lib.memory_vector import vector_memory

# 正确格式：metadata 需要是字符串或简单类型
vector_memory.add("这是一个测试文档", category="test", metadata={"source": "test"})
print("   ✅ 向量记忆添加成功")

results = vector_memory.search("测试", n=2)
print(f"   📊 向量搜索: 找到 {len(results)} 条结果")

stats = vector_memory.get_stats()
print(f"   📊 向量统计: {stats}")

print("\n✅ 记忆系统测试完成")
