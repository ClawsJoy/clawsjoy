import re

file_path = "core/agents/business/business_agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 _get_shared_memory 方法后面添加 memory 属性
pattern = r'(@classmethod\s+def _get_shared_memory\(cls\):.*?return cls\._shared_memory)'

def add_memory_property(match):
    base = match.group(1)
    property_code = '''

    @property
    def memory(self):
        """返回共享的记忆实例（所有 Agent 共享）"""
        return self._get_shared_memory()'''
    
    return base + property_code

content = re.sub(pattern, add_memory_property, content, flags=re.DOTALL)

# 如果上面的替换没找到，直接在 class 末尾添加
if 'def memory(self)' not in content:
    # 在最后一个方法后面添加
    content = content.replace(
        '        return cls._shared_memory',
        '        return cls._shared_memory\n\n    @property\n    def memory(self):\n        """返回共享的记忆实例（所有 Agent 共享）"""\n        return self._get_shared_memory()'
    )

with open(file_path, 'w') as f:
    f.write(content)

print("✅ memory 属性已添加")
