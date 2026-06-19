import re

file_path = "agents/code_agent/agent_v4.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 _execute_business 开头添加记忆提取逻辑
old_start = '''    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心逻辑 - 调用积木"""
        t = user_input.lower()'''

new_start = '''    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """核心逻辑 - 调用积木"""
        # ========== 0. 加载用户记忆 ==========
        user_memory_text = ""
        if context and context.get("memories"):
            try:
                memories = context.get("memories", [])
                if memories:
                    memory_lines = []
                    for mem in memories[:5]:
                        if isinstance(mem, dict):
                            content_text = mem.get("content", mem.get("user_input", ""))
                            if content_text:
                                memory_lines.append(f"- {content_text}")
                        else:
                            memory_lines.append(f"- {mem}")
                    if memory_lines:
                        user_memory_text = "\\n用户历史记忆:\\n" + "\\n".join(memory_lines)
            except Exception as e:
                print(f"[CodeAgent] 记忆提取失败: {e}")
        
        t = user_input.lower()'''

content = content.replace(old_start, new_start)

# 在调用 LLM 时，将记忆注入到 prompt
# 查找 _call_llm 调用，在 prompt 前添加记忆
call_llm_pattern = r'(result = self\._call_llm\()([^)]+)\)'

def add_memory_to_prompt(match):
    prefix = match.group(1)
    prompt_content = match.group(2)
    # 在 prompt 中注入记忆
    return f'''            # 注入用户记忆
            enhanced_prompt = prompt
            if user_memory_text:
                enhanced_prompt = f"{{user_memory_text}}\\n\\n用户当前问题：{{prompt}}"
            result = self._call_llm(enhanced_prompt)'''

# 由于代码结构复杂，使用更简单的方法：在 _call_llm 之前添加
# 找到 _call_llm 调用的位置
content = content.replace(
    'result = self._call_llm(prompt)',
    '            # 注入用户记忆\n            enhanced_prompt = prompt\n            if user_memory_text:\n                enhanced_prompt = f"{user_memory_text}\\n\\n用户当前问题：{prompt}"\n            result = self._call_llm(enhanced_prompt)'
)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ code_agent 已修复 - 支持用户记忆注入")
