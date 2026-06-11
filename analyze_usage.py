#!/usr/bin/env python3
"""分析实际被使用的模块"""

import re
import sys
from collections import defaultdict
from pathlib import Path

print("=" * 60)
print("模块使用分析报告")
print("=" * 60)

# 收集所有 Python 文件中被导入的模块
used_modules = set()
module_locations = defaultdict(list)

# 遍历所有 Python 文件
for py_file in Path(".").rglob("*.py"):
    if "tools" in str(py_file) or "__pycache__" in str(py_file):
        continue
    try:
        content = py_file.read_text()
        # 查找 import 语句
        imports = re.findall(
            r"^(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)", content, re.MULTILINE
        )
        for imp in imports:
            # 提取模块名
            module_name = imp.split(".")[0]
            used_modules.add(module_name)
            module_locations[module_name].append(str(py_file))
    except Exception as e:
        pass

# 检查 core/lib 下的模块使用情况
print("\n📊 core/lib 模块使用情况:")
lib_dir = Path("core/lib")
used_count = 0
unused_count = 0
unused_files = []

for py_file in lib_dir.glob("*.py"):
    module_name = py_file.stem
    if module_name in used_modules or module_name in [
        "__init__",
        "config",
        "unified_config",
    ]:
        used_count += 1
        print(f"   ✅ {module_name}.py - 被使用")
    else:
        # 检查是否被 agent_gateway 直接导入
        with open("agent_gateway_enhanced.py") as f:
            gateway_content = f.read()
            if module_name in gateway_content:
                print(f"   ✅ {module_name}.py - 在网关中使用")
                used_count += 1
            else:
                unused_count += 1
                unused_files.append(module_name)

print(f"\n📈 统计:")
print(f"   使用的模块: {used_count}")
print(f"   未使用的模块: {unused_count}")

if unused_files:
    print(f"\n⚠️ 可能未使用的模块 (前30个):")
    for f in unused_files[:30]:
        print(f"   - {f}.py")

print(f"\n💡 建议:")
print(f"   1. 先备份这些未使用的模块")
print(f"   2. 运行完整功能测试")
print(f"   3. 确认无影响后再删除")
