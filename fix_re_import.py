import re

file_path = "agents/writer_agent/agent_v4.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 _handle_character 方法开头添加 import re（如果还没有）
old_func = '''    def _handle_character(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """④ 角色工坊（深度角色设计）"""
        # 提取角色名
        name_match = re.search(r'角色\s*([^\s，,。.]+)', user_input)'''

new_func = '''    def _handle_character(self, user_input: str, semantic: Any, emotion: Dict, soul: Dict) -> str:
        """④ 角色工坊（深度角色设计）"""
        import re
        # 提取角色名
        name_match = re.search(r'角色\s*([^\s，,。.]+)', user_input)'''

content = content.replace(old_func, new_func)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 已添加 import re")
