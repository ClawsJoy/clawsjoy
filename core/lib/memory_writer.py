"""记忆写入器 - 兼容层，重定向到 memory_vector"""

# 兼容旧代码导入
from core.lib.memory_vector import vector_memory as memory
from core.lib.memory_vector import VectorMemory

__all__ = ['memory', 'VectorMemory']
