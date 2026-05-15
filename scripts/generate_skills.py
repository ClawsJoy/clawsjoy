"""批量生成基础技能"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

import requests
import json
import re
from pathlib import Path

def generate_skill(name, description, category, code_template):
    """生成技能文件"""
    skill_content = f'''"""
{description}
"""
class {name.capitalize()}Skill:
    name = "{name}"
    description = "{description}"
    version = "1.0.0"
    category = "{category}"
    
    def execute(self, params):
        {code_template}
        return {{"success": True, "result": result}}

skill = {name.capitalize()}Skill()
'''
    skill_path = Path(f"skills/{category}/{name}.py")
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(skill_content, encoding='utf-8')
    print(f"  ✅ 生成技能: {category}/{name}.py")

# 基础数学技能（已有 add, multiply, divide，补充）
math_skills = [
    ("power", "幂运算", "a = params.get('a', 0); b = params.get('b', 1); result = a ** b"),
    ("mod", "取模运算", "a = params.get('a', 0); b = params.get('b', 1); result = a % b"),
    ("sqrt", "平方根", "import math; a = params.get('a', 0); result = math.sqrt(a)"),
    ("abs", "绝对值", "a = params.get('a', 0); result = abs(a)"),
]

# 字符串处理技能
string_skills = [
    ("to_upper", "转大写", "text = params.get('text', ''); result = text.upper()"),
    ("to_lower", "转小写", "text = params.get('text', ''); result = text.lower()"),
    ("reverse", "字符串反转", "text = params.get('text', ''); result = text[::-1]"),
    ("trim", "去除空格", "text = params.get('text', ''); result = text.strip()"),
]

# 列表处理技能
list_skills = [
    ("list_sort", "列表排序", "lst = params.get('list', []); result = sorted(lst)"),
    ("list_reverse", "列表反转", "lst = params.get('list', []); result = list(reversed(lst))"),
    ("list_unique", "列表去重", "lst = params.get('list', []); result = list(set(lst))"),
]

# 生成所有技能
print("生成数学技能...")
for name, desc, code in math_skills:
    generate_skill(name, desc, "math", code)

print("生成字符串技能...")
for name, desc, code in string_skills:
    generate_skill(name, desc, "text", code)

print("生成列表技能...")
for name, desc, code in list_skills:
    generate_skill(name, desc, "tools", code)

print("\n✅ 基础技能批量生成完成")
