#!/usr/bin/env python3
"""分析重复和重叠代码"""

import os
from pathlib import Path

print("=" * 60)
print("重复代码分析报告")
print("=" * 60)

# 1. 查找功能重叠的模块
overlap_groups = {
    "缓存模块": ["response_cache.py", "cache.py", "request_cache"],
    "配置模块": [
        "config.py",
        "unified_config.py",
        "config_helper.py",
        "config_manager.py",
    ],
    "管理器": [
        "agent_manager.py",
        "skill_manager.py",
        "task_manager.py",
        "unified_manager.py",
    ],
    "工具类": ["utils.py", "helpers.py", "common.py"],
}

print("\n📊 1. 功能重叠模块:")
for group, modules in overlap_groups.items():
    existing = []
    for m in modules:
        if Path(f"core/lib/{m}").exists() or Path(f"core/lib/{m}.py").exists():
            existing.append(m)
    if len(existing) > 1:
        print(f"   {group}: {existing}")

# 2. 查找大文件
print("\n📁 2. 大文件 (>500行):")
for py_file in Path(".").rglob("*.py"):
    if "tools" in str(py_file) or "__pycache__" in str(py_file):
        continue
    try:
        lines = len(py_file.read_text().splitlines())
        if lines > 500:
            print(f"   {py_file}: {lines} 行")
    except Exception as e:
        pass

# 3. 查找可能未使用的导入
print("\n📦 3. 可能未使用的模块:")
# 检查哪些模块被主网关导入
with open("agent_gateway_enhanced.py") as f:
    main_content = f.read()
    for py_file in Path("core/lib").glob("*.py"):
        module_name = py_file.stem
        if module_name not in main_content and module_name not in [
            "__init__",
            "config",
        ]:
            print(f"   core/lib/{module_name}.py - 可能未使用")
