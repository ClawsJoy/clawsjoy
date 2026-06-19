import re

file_path = "core/lib/decision_evaluator.py"

with open(file_path, 'r') as f:
    content = f.read()

# 替换 get_absolute 为 get_path 或直接使用 Path
# 方案1: 使用 get_path
content = content.replace(
    'path_manager.get_absolute("data.decision_history")',
    'Path("data/decision_history.json")'
)

# 或者方案2: 如果 path_manager 有 get_path 方法
# content = content.replace(
#     'path_manager.get_absolute("data.decision_history")',
#     'path_manager.get_path("data.decision_history")'
# )

# 添加必要的导入
if 'from pathlib import Path' not in content:
    content = content.replace(
        'from pathlib import Path',
        'from pathlib import Path'
    )

with open(file_path, 'w') as f:
    f.write(content)

print("✅ decision_evaluator.py 已修复")
