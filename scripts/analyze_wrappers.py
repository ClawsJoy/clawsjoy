"""分析技能文件，识别包装器类型"""
import ast
import re
from pathlib import Path

def analyze_skill(filepath):
    """分析单个技能文件"""
    content = filepath.read_text()
    
    # 特征检测
    is_wrapper = False
    wrapper_type = None
    calls = []
    
    # 检测是否只调用其他技能
    if 'from skills.' in content or 'import skills.' in content:
        imports = re.findall(r'from skills\.(\w+) import', content)
        if imports:
            is_wrapper = True
            wrapper_type = 'skill_caller'
            calls = imports
    
    # 检测是否只是 HTTP 请求转发
    if 'requests.post' in content or 'requests.get' in content:
        if 'skill.execute' not in content:  # 不是复杂技能
            is_wrapper = True
            wrapper_type = 'api_proxy'
            # 提取调用的 URL
            urls = re.findall(r'["\'](http[s]?://[^"\']+)["\']', content)
            calls = urls
    
    # 检测是否只是简单函数包装
    if content.count('\n') < 30 and 'def execute' in content:
        if 'import' not in content or len(re.findall(r'^import|^from', content, re.M)) <= 2:
            is_wrapper = True
            wrapper_type = 'simple_wrapper'
    
    return {
        'name': filepath.stem,
        'is_wrapper': is_wrapper,
        'type': wrapper_type,
        'calls': calls[:3],
        'lines': len(content.split('\n'))
    }

skills_dir = Path('skills')
wrappers = []
real_skills = []

for py_file in skills_dir.glob('*.py'):
    if py_file.stem in ['__init__', 'skill_interface']:
        continue
    analysis = analyze_skill(py_file)
    if analysis['is_wrapper']:
        wrappers.append(analysis)
    else:
        real_skills.append(analysis)

print("=" * 60)
print(f"真实技能: {len(real_skills)} 个")
print(f"包装器技能: {len(wrappers)} 个")
print("=" * 60)

print("\n--- 包装器技能列表 ---")
for w in wrappers:
    print(f"  {w['name']} ({w['type']}) -> 调用: {w['calls']}")

print("\n--- 真实技能列表 ---")
for r in real_skills[:15]:
    print(f"  {r['name']} ({r['lines']}行)")
if len(real_skills) > 15:
    print(f"  ... 还有 {len(real_skills)-15} 个")
