#!/usr/bin/env python3
"""
在 ChatAgentV4 中显式添加 _state 属性
"""

import os
import re

file_path = "agents/chat_agent/agent_v4.py"

# 备份
backup_path = file_path + ".backup2"
os.system(f"cp {file_path} {backup_path}")
print(f"✅ 已备份到: {backup_path}")

with open(file_path, 'r') as f:
    content = f.read()

# 在 __init__ 方法开头添加 _state 初始化
# 查找 class ChatAgentV4 的定义
pattern = r'(class ChatAgentV4\s*\([^)]*\):.*?def __init__\(self[^)]*\):)(.*?)(\n\s+def\s+\w+)'

def add_state_init(match):
    class_header = match.group(1)
    init_body = match.group(2)
    next_def = match.group(3)
    
    # 在 init_body 开头添加 _state 初始化
    state_init = '''
        # 🔧 显式初始化 _state 为字典（业务状态）
        self._state = {
            "total_interactions": 0,
            "session_count": 0,
            "last_active": datetime.now().isoformat()
        }
        self._stats = self._state
'''
    
    # 插入到 super 调用之后
    lines = init_body.split('\n')
    new_lines = []
    inserted = False
    
    for line in lines:
        new_lines.append(line)
        if not inserted and 'super()' in line and '(' in line:
            new_lines.append(state_init)
            inserted = True
    
    if not inserted:
        # 如果没找到 super，插入到开头
        new_lines.insert(0, state_init)
    
    new_init_body = '\n'.join(new_lines)
    
    return class_header + new_init_body + next_def

content = re.sub(pattern, add_state_init, content, flags=re.DOTALL)

# 如果上面的替换没成功，直接在整个文件中查找并替换
if 'self._state = {' not in content:
    # 更简单的替换：在 __init__ 方法中的 print 之前插入
    content = re.sub(
        r'(def __init__\(self[^)]*\):.*?)(\n\s+print\()',
        r'\1\n        # 🔧 显式初始化 _state 为字典\n        self._state = {}\n        self._state["total_interactions"] = 0\n        self._state["session_count"] = 0\n        self._state["last_active"] = datetime.now().isoformat()\n        self._stats = self._state\n\2',
        content,
        flags=re.DOTALL
    )

# 为所有方法添加 _state 访问保护
# 替换 self._state 访问为安全的 getter
content = re.sub(
    r'self\._state\.get\(',
    r'self._get_state_safe().get(',
    content
)

content = re.sub(
    r'self\._state\.update\(',
    r'self._get_state_safe().update(',
    content
)

# 添加 _get_state_safe 方法
if '_get_state_safe' not in content:
    # 在类中添加安全方法
    content = re.sub(
        r'(class ChatAgentV4\s*\([^)]*\):.*?)(def __init__)',
        r'\1    def _get_state_safe(self):\n        """安全获取状态字典"""\n        if not hasattr(self, "_state") or not isinstance(self._state, dict):\n            self._state = {\n                "total_interactions": 0,\n                "session_count": 0,\n                "last_active": datetime.now().isoformat()\n            }\n            self._stats = self._state\n        return self._state\n\n    \2',
        content,
        flags=re.DOTALL
    )

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 修复完成: agents/chat_agent/agent_v4.py")
print("   - 添加了 _state 显式初始化")
print("   - 添加了 _get_state_safe() 安全方法")
