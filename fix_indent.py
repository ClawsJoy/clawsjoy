import re

file_path = "core/agents/wisdom/wisdom_factory.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# 删除 _register_comic_agents 方法及其内容
new_lines = []
skip = False
for line in lines:
    if line.strip().startswith('def _register_comic_agents'):
        skip = True
        continue
    if skip and line.strip() and not line.startswith('    '):
        skip = False
    if not skip:
        new_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(new_lines)

print("✅ 已删除 _register_comic_agents 方法（comic_writer_agent 已在 v4_agents 中）")
