#!/usr/bin/env python3
"""批量修复硬编码脚本"""

import os
import re
from pathlib import Path

# 项目根目录
ROOT = Path("str(smart_config.ROOT)")

# 需要修复的硬编码模式
PATTERNS = [
    # 路径硬编码
    (r"str(smart_config.ROOT)(_clean)?", "str(smart_config.ROOT)"),
    (r"'str(smart_config.ROOT)(_clean)?'", "'str(smart_config.ROOT)'"),
    (r'"str(smart_config.ROOT)(_clean)?"', '"str(smart_config.ROOT)"'),
    
    # localhost 硬编码（保留配置相关）
    (rf"{smart_config.get_service_url("(\d+)", r"http://smart_config.HOST:\1"),
    (r"http://127\.0\.0\.1:(\d+)", r"http://smart_config.HOST:\1"),
    
    # 端口硬编码
    (r":str(smart_config.get_port("gateway"))", ":str(smart_config.get_port("gateway"))"),
    (r":str(smart_config.get_port("multi_agent"))", ":str(smart_config.get_port("multi_agent"))"),
    (r":str(smart_config.get_port("comfyui"))", ":str(smart_config.get_port("comfyui"))"),
    (r":str(smart_config.get_port("ollama"))", ":str(smart_config.get_port("ollama"))"),
]

def fix_file(file_path):
    """修复单个文件"""
    if not file_path.exists():
        return False
    
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # 添加配置导入（如果还没有）
    if 'from lib.smart_config import smart_config' not in content:
        # 在 sys.path.insert 之后添加
        if 'sys.path.insert' in content:
            content = content.replace(
                'sys.path.insert',
                'from lib.smart_config import smart_config\nsys.path.insert'
            )
        else:
            content = 'from lib.smart_config import smart_config\n' + content
    
    # 替换硬编码
    for pattern, replacement in PATTERNS:
        content = re.sub(pattern, replacement, content)
    
    # 替换动态变量
    content = content.replace('str(smart_config.ROOT)', 'str(smart_config.ROOT)')
    content = content.replace('smart_config.HOST', 'smart_config.HOST')
    content = content.replace('str(smart_config.get_port("gateway"))', 'str(smart_config.get_port("gateway"))')
    content = content.replace('str(smart_config.get_port("multi_agent"))', 'str(smart_config.get_port("multi_agent"))')
    content = content.replace('str(smart_config.get_port("comfyui"))', 'str(smart_config.get_port("comfyui"))')
    content = content.replace('str(smart_config.get_port("ollama"))', 'str(smart_config.get_port("ollama"))')
    
    if content != original:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False

# 需要修复的文件列表
files_to_fix = []
for py_file in ROOT.rglob("*.py"):
    if '__pycache__' in str(py_file):
        continue
    if 'venv' in str(py_file):
        continue
    files_to_fix.append(py_file)

print(f"找到 {len(files_to_fix)} 个 Python 文件")

fixed = 0
for f in files_to_fix:
    if fix_file(f):
        fixed += 1
        print(f"✅ 修复: {f.relative_to(ROOT)}")

print(f"\n共修复 {fixed} 个文件")
