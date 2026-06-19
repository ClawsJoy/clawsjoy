import re

file_path = "core/agents/business/business_agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 找到并删除旧的 memory property（在 __init__ 之后的那个）
# 旧的在 __init__ 之后，包含 _memory = None
pattern = r'    @property\s+def memory\(self\):.*?return self\._memory'

# 查找匹配
match = re.search(pattern, content, re.DOTALL)
if match:
    print(f"找到旧的 memory 属性: {match.group()[:100]}...")
    content = content.replace(match.group(), '')
    print("✅ 已删除旧的 memory 属性")
else:
    print("⚠️ 未找到旧的 memory 属性")

# 同时删除 __init__ 中的 self._memory = None
content = content.replace('        self._memory = None\n', '')

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 修复完成")
