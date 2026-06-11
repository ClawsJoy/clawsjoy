file_path = "agents/memory_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

if "memory_agent = " not in content:
    content += '\n\n# 全局实例\nmemory_agent = MemoryAgent()\n'

with open(file_path, 'w') as f:
    f.write(content)
print("✅ memory_agent 已修复")
