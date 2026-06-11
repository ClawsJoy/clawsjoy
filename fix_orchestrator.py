file_path = "agents/orchestrator/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

if "orchestrator = " not in content:
    content += '\n\n# 全局实例\norchestrator = OrchestratorAgent()\n'

with open(file_path, 'w') as f:
    f.write(content)
print("✅ orchestrator 已修复")
