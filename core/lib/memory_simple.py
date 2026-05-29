"""简单内存存储 - 兼容性模块"""

from typing import Dict, Any, Optional


class SimpleMemory:
    """简单的内存存储"""

    def __init__(self):
        self._data: Dict[str, Any] = {}

    def set(self, key: str, value: Any):
        """存储值"""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取值"""
        return self._data.get(key, default)

    def delete(self, key: str):
        """删除值"""
        if key in self._data:
            del self._data[key]

    def exists(self, key: str) -> bool:
        """检查是否存在"""
        return key in self._data

    def clear(self):
        """清空所有数据"""
        self._data.clear()


# 全局单例
memory = SimpleMemory()
