#!/usr/bin/env python3
"""修复技能导入路径问题"""

import sys
from pathlib import Path

# 需要修复的技能文件
skills_to_fix = [
    "skills/ai_image_gen.py",
    "skills/check_video_status.py",
    "skills/file_service_skill.py",
    "skills/improve_executor.py",
    "skills/scheduler.py",
    "skills/video_description.py",
    "skills/video_public.py",
]

def add_path_to_skill(skill_path):
    """在技能文件中添加正确的路径"""
    if not Path(skill_path).exists():
        print(f"   ⚠️ 文件不存在: {skill_path}")
        return False
    
    content = Path(skill_path).read_text(encoding='utf-8', errors='ignore')
    
    # 添加路径设置
    path_setup = '''import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

'''
    
    # 检查是否已有路径设置
    if 'sys.path.insert' not in content:
        # 在文件开头添加
        content = path_setup + content
        Path(skill_path).write_text(content, encoding='utf-8')
        print(f"   ✅ 已修复: {skill_path}")
        return True
    
    print(f"   ⏭️ 已包含路径: {skill_path}")
    return False

if __name__ == "__main__":
    print("修复技能导入路径")
    print("-" * 40)
    
    for skill_path in skills_to_fix:
        add_path_to_skill(skill_path)
    
    print("-" * 40)
    print("✅ 技能修复完成")
