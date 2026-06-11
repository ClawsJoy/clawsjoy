file_path = "agents/code_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

if "code_agent = " not in content:
    content += '\n\n# 全局实例\ncode_agent = CodeAgent()\n'

with open(file_path, 'w') as f:
    f.write(content)
print("✅ code_agent 已修复")
