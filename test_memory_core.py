#!/usr/bin/env python3
"""记忆系统内部逻辑深度测试"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("🧠 记忆系统内部逻辑验证")
print("=" * 60)

# 1. 测试记忆管理器
print("\n1. 记忆管理器测试...")

# 查找正确的记忆模块
try:
    from core.butler.memory_manager import SmartMemoryManager

    memory = SmartMemoryManager("test_user")
    print("   ✅ SmartMemoryManager 加载成功")

    # 存储记忆
    memory.add("用户偏好", "喜欢简洁风格")
    memory.add("用户姓名", "张三")
    print("   ✅ 记忆存储成功")

    # 检索记忆
    recalled = memory.recall()
    print(f"   📝 记忆内容: {recalled}")

except ImportError as e:
    print(f"   ⚠️ 导入错误: {e}")

    # 备选方案
    try:
        from core.butler.memory_manager import memory_manager

        print("   ✅ memory_manager 加载成功")
    except Exception as e2:
        print(f"   ⚠️ 备选也失败: {e2}")

# 2. 测试跨会话记忆
print("\n2. 跨会话记忆测试...")
try:
    from core.lib.cross_session_memory import CrossSessionMemory

    session_mem = CrossSessionMemory("test_user_002")
    session_mem.remember("name", "李四")
    session_mem.remember("preference", "喜欢技术")

    user_info = session_mem.recall()
    print(f"   📝 用户信息: {user_info}")

except Exception as e:
    print(f"   ⚠️ 跨会话记忆: {e}")

# 3. 测试向量记忆
print("\n3. 向量记忆测试...")
try:
    from core.lib.memory_vector import vector_memory

    vector_memory.add("这是一个测试文档", {"source": "test"})
    results = vector_memory.search("测试", n=2)
    print(f"   📊 向量搜索: 找到 {len(results)} 条结果")
except Exception as e:
    print(f"   ⚠️ 向量记忆: {e}")
