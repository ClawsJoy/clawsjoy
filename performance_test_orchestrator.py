#!/usr/bin/env python3
"""Orchestrator 性能对比测试"""

import sys
import time

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

print("=" * 60)
print("Orchestrator 性能对比测试")
print("=" * 60)

# 测试消息
test_messages = [
    "今天天气怎么样",
    "1+2等于多少",
    "用粤语说你好",
    "写一个Python函数",
    "你好，我叫张三",
    "分析一下这个数据",
]

# 测试原版
print("\n1. 测试原版 Orchestrator...")
try:
    from core.agents.builtin.orchestrator import OrchestratorV6

    original = OrchestratorV6("test_user")

    times = []
    for msg in test_messages:
        start = time.time()
        result = original.smart_route(msg)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"   {msg[:20]:20} → {result:15} ({elapsed:.1f}ms)")

    print(f"\n   平均延迟: {sum(times)/len(times):.1f}ms")
    print(f"   统计: {original.get_route_stats()}")
except Exception as e:
    print(f"   原版测试失败: {e}")

# 测试优化版
print("\n2. 测试优化版 Orchestrator...")
try:
    from core.agents.builtin.orchestrator_optimized import OptimizedOrchestratorV6

    optimized = OptimizedOrchestratorV6("test_user")

    # 先关闭并行模式测试串行
    optimized.parallel_mode = False
    print("\n   串行模式:")
    times = []
    for msg in test_messages:
        start = time.time()
        result = optimized.smart_route(msg)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"   {msg[:20]:20} → {result:15} ({elapsed:.1f}ms)")
    print(f"\n   平均延迟: {sum(times)/len(times):.1f}ms")

    # 开启并行模式
    optimized.parallel_mode = True
    print("\n   并行模式:")
    times = []
    for msg in test_messages:
        start = time.time()
        result = optimized.smart_route(msg)
        elapsed = (time.time() - start) * 1000
        times.append(elapsed)
        print(f"   {msg[:20]:20} → {result:15} ({elapsed:.1f}ms)")

    print(f"\n   平均延迟: {sum(times)/len(times):.1f}ms")
    print(f"   统计: {optimized.get_route_stats()}")

    # 测试缓存效果
    print("\n3. 缓存效果测试...")
    cache_test_msg = "今天天气怎么样"
    for i in range(3):
        start = time.time()
        result = optimized.smart_route(cache_test_msg)
        elapsed = (time.time() - start) * 1000
        print(f"   第{i+1}次: {result} ({elapsed:.1f}ms)")
    print(f"   缓存命中: {optimized.get_route_stats()['cache_hits']}")

except Exception as e:
    print(f"   优化版测试失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
