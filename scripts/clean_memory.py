#!/usr/bin/env python3
"""清理记忆中的失败记录"""
import json
from pathlib import Path

def main():
    memory_file = Path("data/memory_simple.json")
    if not memory_file.exists():
        return
    
    with open(memory_file, 'r') as f:
        data = json.load(f)
    
    # 清理工作流失败记录
    if 'workflow_outcome' in data['categories']:
        old = data['categories']['workflow_outcome']
        new = [item for item in old if '成功' in item or '摘要' in item]
        data['categories']['workflow_outcome'] = new
    
    # 清理 items
    before = len(data['items'])
    data['items'] = [
        item for item in data['items'] 
        if item.get('category') != 'workflow_outcome' or '成功' in item.get('fact', '') or '摘要' in item.get('fact', '')
    ]
    
    with open(memory_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"清理完成: items {before} -> {len(data['items'])}")

if __name__ == "__main__":
    main()
