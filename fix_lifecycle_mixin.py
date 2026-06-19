#!/usr/bin/env python3
"""
修复 lifecycle_mixin.py 中的 _state 冲突
将 _state 改为 _lifecycle_state 避免与业务状态冲突
"""

import os
import re

file_path = "core/agents/base/mixins/lifecycle_mixin.py"

if not os.path.exists(file_path):
    print(f"❌ 文件不存在: {file_path}")
    exit(1)

# 备份
backup_path = file_path + ".backup"
os.system(f"cp {file_path} {backup_path}")
print(f"✅ 已备份到: {backup_path}")

with open(file_path, 'r') as f:
    content = f.read()

# 将所有 self._state 替换为 self._lifecycle_state
# 注意：需要区分是状态变量还是其他用法
content = re.sub(r'self\._state\s*=', r'self._lifecycle_state =', content)
content = re.sub(r'self\._state\s*==', r'self._lifecycle_state ==', content)
content = re.sub(r'"state": self\._state', r'"state": self._lifecycle_state', content)

# 添加初始化
content = re.sub(
    r'(class LifecycleMixin:)',
    r'\1\n    def __init__(self, *args, **kwargs):\n        super().__init__(*args, **kwargs)\n        self._lifecycle_state = "sleeping"\n        self._state = {}  # 业务状态字典',
    content
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 修复完成: core/agents/base/mixins/lifecycle_mixin.py")
print("📝 将 _state 重命名为 _lifecycle_state，避免冲突")
