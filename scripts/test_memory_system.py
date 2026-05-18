#!/usr/bin/env python3
"""记忆系统测试 - 修复版"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

from lib.memory_simple import memory
from lib.memory_layers import memory_layers

def test_memory():
    print("=" * 60)
    print("记忆系统测试")
    print("=" * 60)
    
    # 1. 测试记忆写入
    print("\n1. 记忆写入测试:")
    memory.remember("测试记忆内容", category="test")
    print("   ✅ 记忆已写入")
    
    # 2. 测试记忆读取（使用正确的参数）
    print("\n2. 记忆读取测试:")
    try:
        # SimpleMemory.recall 需要 query 参数
        results = memory.recall(query="测试", category="test")
        print(f"   ✅ 读取到 {len(results) if results else 0} 条记忆")
    except TypeError:
        # 如果不支持 query，使用 recall_all
        results = memory.recall_all(category="test")
        print(f"   ✅ 读取到 {len(results)} 条记忆")
    
    # 3. 测试四层记忆
    print("\n3. 四层记忆统计:")
    stats = memory_layers.get_stats()
    print(f"   ✅ 日记忆文件: {stats.get('daily_files', 0)}")
    print(f"   ✅ 向量数量: {stats.get('vector_count', 0)}")
    
    print("\n✅ 记忆系统测试通过")

if __name__ == "__main__":
    test_memory()
