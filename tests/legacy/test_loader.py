import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')

print("=== 测试加载器 ===")
from lib.skill_loader_v3 import skill_loader
print(f"加载器技能数: {len(skill_loader.list_skills())}")
print(f"script_generator: {'script_generator' in skill_loader.list_skills()}")

# 检查 skills/text 目录
from pathlib import Path
text_dir = Path("skills/text")
if text_dir.exists():
    print(f"skills/text 存在，文件: {list(text_dir.glob('*.py'))}")
else:
    print("skills/text 不存在")
