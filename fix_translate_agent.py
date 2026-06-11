file_path = "agents/translate_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 添加全局实例
if "translate_agent = " not in content:
    content += '\n\n# 全局实例\ntranslate_agent = TranslateAgent()\n'

with open(file_path, 'w') as f:
    f.write(content)
print("✅ translate_agent 已修复")
