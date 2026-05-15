#!/usr/bin/env python3
"""将旧格式技能转换为标准 BaseSkill 格式"""

import re
from pathlib import Path

def convert_to_standard(filepath):
    """将只有 execute 函数的文件转换为标准格式"""
    content = filepath.read_text()
    
    # 提取 execute 函数体
    exec_match = re.search(r'def execute\([^)]*\):.*?(?=\n\S|\Z)', content, re.DOTALL)
    if not exec_match:
        return False
    
    exec_code = exec_match.group(0)
    skill_name = filepath.stem
    
    # 生成标准格式
    class_name = ''.join(word.capitalize() for word in skill_name.split('_'))
    
    standard = f'''from skills.skill_interface import BaseSkill

class {class_name}Skill(BaseSkill):
    name = "{skill_name}"
    description = "{skill_name} 技能"
    version = "1.0.0"
    category = "general"
    
    def execute(self, params):
{chr(10).join(['        ' + line for line in exec_code.split(chr(10))])}

skill = {class_name}Skill()
'''
    
    # 备份并写入
    backup = filepath.with_suffix('.py.old')
    filepath.rename(backup)
    filepath.write_text(standard)
    return True

def main():
    skills_dir = Path('skills')
    converted = []
    skipped = []
    
    for py_file in skills_dir.glob('*.py'):
        if py_file.stem in ['skill_interface', '__init__', '_template']:
            continue
        
        content = py_file.read_text()
        
        # 已经是标准格式
        if 'skill = ' in content and 'class' in content:
            continue
        
        # 尝试转换
        if convert_to_standard(py_file):
            converted.append(py_file.name)
            print(f"✅ 转换: {py_file.name}")
        else:
            skipped.append(py_file.name)
            print(f"⚠️ 跳过: {py_file.name}")
    
    print(f"\n转换完成: {len(converted)} 个, 跳过: {len(skipped)} 个")

if __name__ == '__main__':
    main()
