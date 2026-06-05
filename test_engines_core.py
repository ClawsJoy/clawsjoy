#!/usr/bin/env python3
"""引擎系统内部逻辑深度测试"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("🔧 引擎系统内部逻辑验证")
print("=" * 60)

# 1. 测试语义引擎
print("\n1. 语义理解引擎测试...")
try:
    from engine.semantic import semantic_engine

    result = semantic_engine.understand("今天天气怎么样")
    print(f"   📝 输入: 今天天气怎么样")
    print(f"   🎯 意图: {result.get('intent', 'unknown')}")
    print(f"   📊 置信度: {result.get('confidence', 0)}")
except Exception as e:
    print(f"   ⚠️ 语义引擎: {e}")

# 2. 测试知识引擎
print("\n2. 知识引擎测试...")
try:
    from engine.knowledge import knowledge_engine

    result = knowledge_engine.search("ClawsJoy", limit=3)
    print(f"   📚 知识搜索: 找到 {len(result) if result else 0} 条结果")
except Exception as e:
    print(f"   ⚠️ 知识引擎: {e}")

# 3. 测试学习引擎
print("\n3. 学习引擎测试...")
try:
    from engine.learning import learning_engine

    # 反馈学习
    result = learning_engine.learn_from_feedback(
        query="天气", action="weather_query", success=True, user_id="test"
    )
    print(f"   🧠 学习反馈: {result}")
except Exception as e:
    print(f"   ⚠️ 学习引擎: {e}")

# 4. 测试规划引擎
print("\n4. 规划引擎测试...")
try:
    from engine.planning.core import planning_engine

    result = planning_engine.plan("写一篇关于AI的文章")
    print(f"   📋 规划步骤: {result.get('steps', [])[:3]}")
except Exception as e:
    print(f"   ⚠️ 规划引擎: {e}")

# 5. 测试所有引擎状态
print("\n5. 引擎状态汇总...")
try:
    from engine.manager import engine_manager

    status = engine_manager.get_status()
    print(f"   📊 引擎总数: {status.get('total', 0)}")
    print(f"   ✅ 活跃引擎: {status.get('active', 0)}")
except Exception as e:
    print(f"   ⚠️ 引擎状态: {e}")
