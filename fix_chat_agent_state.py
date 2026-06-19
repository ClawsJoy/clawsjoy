#!/usr/bin/env python3
"""
修复 chat_agent 状态字典问题
"""

import re
import os

file_path = "agents/chat_agent/agent_v4.py"

if not os.path.exists(file_path):
    print(f"❌ 文件不存在: {file_path}")
    exit(1)

with open(file_path, 'r') as f:
    content = f.read()

# 查找并修复 __init__ 中的 _state 初始化
# 确保 _state 是字典而不是字符串

# 添加保护性检查：在访问 _state.keys() 之前检查类型
fix_code = '''
    def _get_state_safe(self):
        """安全获取状态字典"""
        if not isinstance(self._state, dict):
            self._state = {}
        return self._state
    
    def _ensure_state_dict(self):
        """确保状态是字典"""
        if not isinstance(self._state, dict):
            self._state = {}
'''

# 在类中插入修复方法
# 查找 class ChatAgentV4 或类似的类定义
class_pattern = r'(class\s+ChatAgentV4\s*[^:]*:.*?)(\n\s+def\s+__init__)'
if re.search(class_pattern, content, re.DOTALL):
    # 在 __init__ 之前插入保护方法
    content = re.sub(
        class_pattern,
        r'\1\n    def _get_state_safe(self):\n        """安全获取状态字典"""\n        if not isinstance(self._state, dict):\n            self._state = {}\n        return self._state\n\n    def _ensure_state_dict(self):\n        """确保状态是字典"""\n        if not isinstance(self._state, dict):\n            self._state = {}\n\2',
        content,
        flags=re.DOTALL
    )

# 在所有使用 _state.keys() 的地方添加保护
content = re.sub(
    r'self\._state\.keys\(\)',
    r'self._get_state_safe().keys()',
    content
)

# 在所有使用 _state.get() 的地方添加保护
content = re.sub(
    r'self\._state\.get\(',
    r'self._get_state_safe().get(',
    content
)

# 在所有使用 _state.update() 的地方添加保护
content = re.sub(
    r'self\._state\.update\(',
    r'self._ensure_state_dict(); self._state.update(',
    content
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 修复完成: agents/chat_agent/agent_v4.py")
