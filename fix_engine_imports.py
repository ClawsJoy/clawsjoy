#!/usr/bin/env python3
"""修复引擎导入路径"""

import os
import re

# 需要修复的文件
files_to_fix = [
    "test_engines_core.py",
]

for file_path in files_to_fix:
    if not os.path.exists(file_path):
        continue

    with open(file_path, "r") as f:
        content = f.read()

    # 修复导入语句
    content = re.sub(
        r"from engine\.semantic\.semantic_engine import",
        "from engine.semantic import",
        content,
    )
    content = re.sub(
        r"from engine\.knowledge\.knowledge_engine import",
        "from engine.knowledge import",
        content,
    )
    content = re.sub(
        r"from engine\.learning\.core import learning_engine",
        "from engine.learning import learning_engine",
        content,
    )

    with open(file_path, "w") as f:
        f.write(content)

    print(f"✅ 修复: {file_path}")

print("修复完成")
