file_path = "agents/calculator_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

if "calculator_agent = " not in content:
    content += '\n\n# 全局实例\ncalculator_agent = CalculatorAgent()\n'

with open(file_path, 'w') as f:
    f.write(content)
print("✅ calculator_agent 已修复")
