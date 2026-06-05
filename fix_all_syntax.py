#!/usr/bin/env python3
"""修复所有被破坏的语法"""

import os
import re

files_to_fix = [
    "core/agents/builtin/task_fixed.py",
    "core/butler/llm_client.py",
    "core/lib/llm_chat.py",
    "core/embedding/embedding_complete.py",
    "core/embedding/embedding_full.py",
    "core/embedding/embedding_legacy.py",
    "core/embedding/embedding_v2.py",
    "core/embedding/local_embedding.py",
    "core/enhancement/llm_enhancer.py",
    "core/lib/config_unified_manager.py",
    "core/llm/llm_enhanced.py",
    "core/llm/async_llm.py",
    "core/storage/chroma_ollama.py",
    "core/storage/chroma_store_optimized.py",
    "core/v5/workflow.py",
]


def fix_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, "r") as f:
        content = f.read()

    # 修复错误的 f-string
    pattern = r'"f"http://\{\{unified_config\.get\("services\.gateway\.host", "localhost"\)\}\}:11434"'
    replacement = '"http://localhost:11434"'

    if pattern in content:
        content = content.replace(pattern, replacement)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"✅ 修复: {filepath}")
    else:
        # 另一种模式
        pattern2 = r'f"http://\{\{unified_config\.get\("services\.gateway\.host", "localhost"\)\}\}:11434"'
        if pattern2 in content:
            content = content.replace(pattern2, replacement)
            with open(filepath, "w") as f:
                f.write(content)
            print(f"✅ 修复: {filepath}")


for f in files_to_fix:
    fix_file(f)

print("修复完成")
