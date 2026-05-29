from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""记忆写入器 - 统一导入入口"""

import importlib.util
from pathlib import Path

def _get_memory_writer():
    """获取 memory_writer 模块"""
    lib_dir = Path(__file__).parent
    
    # 查找 memory_writer 文件
    for f in lib_dir.glob("memory_writer_v*.py"):
        if f.name.startswith("memory_writer_v"):
            spec = importlib.util.spec_from_file_location("memory_writer_module", f)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    
    raise ImportError("未找到 memory_writer 模块")

_module = _get_memory_writer()
memory_writer = _module.memory_writer

__all__ = ['memory_writer']
