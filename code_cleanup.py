#!/usr/bin/env python3
"""代码清理优化脚本"""

import os
import re
from pathlib import Path

print("=" * 60)
print("🧹 代码清理优化")
print("=" * 60)

# 1. 清理未使用的导入
print("\n1. 检查未使用的导入...")
unused_count = 0
for py_file in Path(".").rglob("*.py"):
    if "__pycache__" in str(py_file) or "tools" in str(py_file):
        continue
    try:
        content = py_file.read_text()
        # 简单检查常见的未使用模式
        if "import " in content and "unused" in content.lower():
            unused_count += 1
    except Exception as e:
        pass
print(f"   可能包含未使用导入的文件: {unused_count}")

# 2. 检查 TODO 和 FIXME
print("\n2. 检查 TODO/FIXME...")
todo_count = 0
for py_file in Path(".").rglob("*.py"):
    if "__pycache__" in str(py_file) or "tools" in str(py_file):
        continue
    try:
        content = py_file.read_text()
        todos = re.findall(r"#\s*(TODO|FIXME|HACK|XXX):", content, re.IGNORECASE)
        if todos:
            todo_count += len(todos)
            if todo_count <= 10:
                print(f"   {py_file.name}: {todos}")
    except Exception as e:
        pass
print(f"   总计 TODO/FIXME: {todo_count}")

# 3. 检查硬编码字符串
print("\n3. 检查硬编码字符串...")
hardcoded = []
for py_file in Path("core").rglob("*.py"):
    if "__pycache__" in str(py_file):
        continue
    try:
        content = py_file.read_text()
        # 检查硬编码的 URL/端口
        urls = re.findall(r'https?://[^\s"\']+', content)
        ports = re.findall(r"port\s*=\s*(\d{4,5})", content, re.IGNORECASE)
        if urls or ports:
            hardcoded.append((py_file.name, len(urls), len(ports)))
    except Exception as e:
        pass
print(f"   可能包含硬编码的文件: {len(hardcoded)}")
for name, urls, ports in hardcoded[:5]:
    print(f"      {name}: {urls} URLs, {ports} 端口")

print("\n✅ 代码清理检查完成")
