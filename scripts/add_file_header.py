#!/usr/bin/env python3
"""为 ClawsJoy v5 项目文件添加统一版本头"""

import os
import re
from pathlib import Path
from datetime import datetime

VERSION = "5.0.0"
AUTHOR = "ClawsJoy"

TARGET_DIRS = ["core", "agents", "api", "skills", "web", "scripts", "src"]
EXCLUDE_DIRS = ["__pycache__", "node_modules", "archive", "old", "backup", "dist", "build", ".git", "venv", "migrations"]

HEADER_TEMPLATE = '''#!/usr/bin/env python3
"""{module_name} - {description}

@version: {version}
@author: {author}
@date: {date}
"""

'''

def get_module_name(file_path):
    """从文件路径推断模块名"""
    name = Path(file_path).stem
    # 转换为可读名称，如 vector_memory -> Vector Memory
    parts = name.replace('_', ' ').split()
    if parts:
        return ' '.join(p.capitalize() for p in parts)
    return name

def has_header(content):
    """检查是否已有 @version 头部"""
    # 检查前500字符
    first_chars = content[:500]
    if '@version:' in first_chars:
        return True
    if '版本:' in first_chars:
        return True
    # 检查是否已有模块文档字符串
    if re.match(r'^"""[^"]+"""', first_chars):
        # 如果已经有文档字符串但没有版本信息，也需要添加
        if '@version:' not in first_chars:
            return False
    return False

def add_header(file_path, dry_run=False):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"   ⚠️ 读取失败: {file_path} - {e}")
        return False
    
    if has_header(content):
        return False
    
    module_name = get_module_name(file_path)
    description = f"{module_name} 模块"
    
    header = HEADER_TEMPLATE.format(
        module_name=module_name,
        description=description,
        version=VERSION,
        author=AUTHOR,
        date=datetime.now().strftime("%Y-%m-%d")
    )
    
    # 处理已有内容
    lines = content.split('\n')
    
    # 如果已有 shebang
    if lines and lines[0].startswith('#!/usr/bin/env python3'):
        # 移除原有的文档字符串（如果存在）
        new_lines = [lines[0]]
        idx = 1
        # 跳过原有的文档字符串
        if idx < len(lines) and lines[idx].startswith('"""'):
            # 找到文档字符串结束
            while idx < len(lines) and not (lines[idx].strip().endswith('"""') and lines[idx].strip() != '"""'):
                idx += 1
            if idx < len(lines):
                idx += 1  # 跳过结束行
        # 添加头部
        new_lines.append(header.rstrip())
        # 添加剩余内容
        new_lines.extend(lines[idx:])
        new_content = '\n'.join(new_lines)
    else:
        # 移除原有的文档字符串
        if lines and lines[0].startswith('"""'):
            idx = 0
            while idx < len(lines) and not (lines[idx].strip().endswith('"""') and lines[idx].strip() != '"""'):
                idx += 1
            if idx < len(lines):
                idx += 1
            remaining = lines[idx:]
        else:
            remaining = lines
        new_content = header + '\n'.join(remaining)
    
    if dry_run:
        print(f"  会添加头部: {file_path}")
        return True
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ {file_path}")
        return True
    except Exception as e:
        print(f"❌ 写入失败: {file_path} - {e}")
        return False

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', '-n', action='store_true')
    parser.add_argument('--file', '-f', type=str)
    parser.add_argument('--dir', '-d', type=str)
    args = parser.parse_args()
    
    files = []
    if args.file:
        files = [Path(args.file)]
    elif args.dir:
        for py_file in Path(args.dir).rglob("*.py"):
            if not any(ex in str(py_file) for ex in EXCLUDE_DIRS):
                files.append(py_file)
    else:
        for target in TARGET_DIRS:
            if Path(target).exists():
                for py_file in Path(target).rglob("*.py"):
                    if not any(ex in str(py_file) for ex in EXCLUDE_DIRS):
                        files.append(py_file)
    
    print(f"找到 {len(files)} 个 Python 文件")
    print("=" * 50)
    
    count = 0
    for f in files:
        if add_header(f, args.dry_run):
            count += 1
    
    print("=" * 50)
    if args.dry_run:
        print(f"预览完成，将添加头部到 {count} 个文件")
        print("去掉 --dry-run 执行实际添加")
    else:
        print(f"完成！已为 {count} 个文件添加头部")

if __name__ == "__main__":
    main()
