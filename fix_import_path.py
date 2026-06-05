import re

file_path = "agent_gateway_enhanced.py"

with open(file_path, "r") as f:
    content = f.read()

# 修复导入路径：core.agents.builtin.xxx -> agents.xxx.agent
old_import = r'__import__\(f"core\.agents\.builtin\.\{target_agent\}", fromlist=\[target_agent\]\)'
new_import = '__import__(f"agents.{target_agent}.agent", fromlist=[target_agent])'

content = re.sub(old_import, new_import, content)

# 修复类名获取方式
# 因为 agents 目录下的类名可能不同，需要动态获取
# 找到 agent_class = getattr(module, class_name) 这行
# 改为使用标准类名

with open(file_path, "w") as f:
    f.write(content)

print("✅ 已修复导入路径")
