#!/usr/bin/env python3
"""
在 lifecycle_mixin 的循环中添加 _state 保护
"""

import os
import re

file_path = "core/agents/base/mixins/lifecycle_mixin.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 loop 函数的 except 块之前添加 _state 保护
loop_pattern = r'(def loop\(\):.*?)(\n\s+except Exception as e:)'

def add_state_protection(match):
    before = match.group(1)
    except_line = match.group(2)
    
    # 在 except 之前添加 _state 保护
    protection = '''
                    # 🔧 确保 _state 是字典（防御性编程）
                    if hasattr(self, "_state") and not isinstance(self._state, dict):
                        self._state = {}
                    if hasattr(self, "_state") and "total_interactions" not in self._state:
                        self._state["total_interactions"] = 0
                    if hasattr(self, "_stats") and not isinstance(self._stats, dict):
                        self._stats = {}
                    if hasattr(self, "_stats") and "total_interactions" not in self._stats:
                        self._stats["total_interactions"] = 0
'''
    
    return before + protection + '\n' + except_line

content = re.sub(loop_pattern, add_state_protection, content, flags=re.DOTALL)

# 在 _do_routine 中添加保护
routine_pattern = r'(def _do_routine\(self\):.*?)(\n\s+self\.log)'
if re.search(routine_pattern, content, re.DOTALL):
    content = re.sub(
        routine_pattern,
        r'\1\n        # 🔧 确保状态是字典\n        if not hasattr(self, "_state") or not isinstance(self._state, dict):\n            self._state = {}\n        if "total_interactions" not in self._state:\n            self._state["total_interactions"] = 0\n\2',
        content,
        flags=re.DOTALL
    )

# 在 _go_to_dream 中添加保护
dream_pattern = r'(def _go_to_dream\(self\):.*?)(\n\s+self\._lifecycle_state)'
if re.search(dream_pattern, content, re.DOTALL):
    content = re.sub(
        dream_pattern,
        r'\1\n        # 🔧 确保状态是字典\n        if not hasattr(self, "_state") or not isinstance(self._state, dict):\n            self._state = {}\n        if "total_interactions" not in self._state:\n            self._state["total_interactions"] = 0\n\2',
        content,
        flags=re.DOTALL
    )

with open(file_path, 'w') as f:
    f.write(content)

print("✅ lifecycle_mixin 循环已添加 _state 保护")
