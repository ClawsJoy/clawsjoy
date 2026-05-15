#!/usr/bin/env python3
"""将旧格式技能转换为标准格式"""

import os
import re
from pathlib import Path

def convert_skill(filepath):
    filepath = Path(filepath)
    with open(filepath, 'r') as f:
        content = f.read()
    
    skill_name = filepath.stem
    
    # 检查是否已有 skill 实例
    if 'skill = ' in content:
        print(f"✅ {skill_name} 已是标准格式")
        return
    
    # 提取 execute 函数
    execute_match = re.search(r'def execute\([^)]*\):.*?(?=\n\S|\Z)', content, re.DOTALL)
    if not execute_match:
        print(f"⚠️ {skill_name}: 没有找到 execute 函数")
        return
    
    execute_code = execute_match.group(0)
    
    # 生成标准格式
    class_name = ''.join(word.capitalize() for word in skill_name.split('_'))
    standard = f'''from skills.skill_interface import BaseSkill

class {class_name}Skill(BaseSkill):
    name = "{skill_name}"
    description = "{skill_name} 技能"
    version = "1.0.0"
    category = "general"
    
    def execute(self, params):
{chr(10).join(['        ' + line for line in execute_code.split(chr(10))])}

skill = {class_name}Skill()
'''
    
    # 备份原文件
    backup = filepath.with_suffix('.py.bak')
    filepath.rename(backup)
    
    # 写入新文件
    with open(filepath, 'w') as f:
        f.write(standard)
    
    print(f"✅ 转换: {skill_name}")

if __name__ == '__main__':
    skills_dir = Path('skills')
    for py_file in skills_dir.glob('*.py'):
        if py_file.stem in ['skill_interface', '__init__', 'weather']:
            continue
        if py_file.stem.startswith('_'):
            continue
        convert_skill(py_file)
