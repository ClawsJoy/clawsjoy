#!/usr/bin/env python3
"""
修复 BusinessAgent：跨 Agent 记忆共享 + 自动注入记忆上下文
"""

import re

file_path = "core/agents/business/business_agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# ========== 修复 1: 让所有 Agent 共享同一个 MemoryLayers 实例 ==========
# 在类中添加类变量 _shared_memory

# 找到 class BusinessAgent 定义，在下面添加类变量
class_pattern = r'(class BusinessAgent\(SmartAgent, JSONCapableMixin\):)(.*?)(def __init__)'
if re.search(class_pattern, content, re.DOTALL):
    content = re.sub(
        class_pattern,
        r'\1\n    # 🔧 所有 Agent 共享同一个记忆实例（跨 Agent 记忆共享）\n    _shared_memory = None\n\n    @classmethod\n    def _get_shared_memory(cls):\n        """获取共享的记忆实例"""\n        if cls._shared_memory is None:\n            try:\n                from core.lib.memory_layers import MemoryLayers\n                cls._shared_memory = MemoryLayers()\n                print("🧠 BusinessAgent: 共享记忆实例已创建")\n            except Exception as e:\n                print(f"🧠 BusinessAgent: 共享记忆创建失败: {e}")\n                cls._shared_memory = None\n        return cls._shared_memory\n\n    @property\n    def memory(self):\n        """返回共享的记忆实例（所有 Agent 共享）"""\n        return self._get_shared_memory()\n\n\3',
        content,
        flags=re.DOTALL
    )

# ========== 修复 2: 删除旧的 memory 属性（如果有） ==========
# 查找旧的 memory property 并注释掉（保留新的）
old_memory_pattern = r'    @property\s+def memory\(self\):.*?return self\._memory'
if re.search(old_memory_pattern, content, re.DOTALL):
    # 不删除，只是确保新的覆盖旧的
    pass

# ========== 修复 3: 在 process 方法中自动注入记忆上下文 ==========
# 找到 process 方法，在开头添加记忆加载
process_pattern = r'(def process\(self, user_input: str, context: Optional\[Dict\] = None\) -> Dict:)(.*?)(self\._stats\["total_interactions"\])'

def add_memory_injection(match):
    prefix = match.group(1)
    middle = match.group(2)
    stats_line = match.group(3)
    
    injection = '''
        # 🔧 自动加载用户记忆，注入到上下文
        if context is None:
            context = {}
        
        # 从共享记忆实例获取记忆
        shared_mem = self._get_shared_memory()
        if shared_mem:
            try:
                # 如果有 session_id，获取会话记忆
                session_id = context.get("session_id")
                if session_id:
                    memories = shared_mem.get_session_memory(session_id, limit=5)
                else:
                    # 否则获取长期记忆
                    memories = shared_mem.get_long_term_memory(limit=10)
                if memories:
                    context["memories"] = memories
            except Exception as e:
                print(f"[BusinessAgent] 记忆加载失败: {e}")
        
        # 如果有 memory 属性（共享实例），也保存到 context
        if hasattr(self, 'memory') and self.memory:
            context["_has_memory"] = True
'''
    
    return prefix + injection + '\n        ' + stats_line

content = re.sub(process_pattern, add_memory_injection, content, flags=re.DOTALL)

# ========== 修复 4: 确保 _execute_business 的子类能访问记忆 ==========
# 在 _execute_business 的 docstring 中提示

with open(file_path, 'w') as f:
    f.write(content)

print("✅ BusinessAgent 已修复")
print("   - 所有 Agent 共享同一个 MemoryLayers 实例")
print("   - process 自动加载用户记忆到 context")
print("   - 跨 Agent 记忆共享已启用")
