#!/usr/bin/env python3
"""数据合并技能 - 直接读取步骤输出"""

import json
import sys

def execute(params):
    step_results = params.get('_step_results', {})
    
    all_items = []
    
    # 直接遍历所有步骤结果
    for step_name, step_data in step_results.items():
        if step_data.get('success'):
            output = step_data.get('output', {})
            if isinstance(output, dict):
                # 尝试多种字段名
                for field in ['data', 'items', 'results', 'output']:
                    items = output.get(field, [])
                    if items and isinstance(items, list):
                        all_items.extend(items)
                        print(f"从 {step_name} 获取 {len(items)} 条", file=sys.stderr)
                        break
    
    # 去重
    seen = set()
    unique = []
    for item in all_items:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    
    result = {
        "success": True,
        "data": unique,
        "count": len(unique),
        "items": unique,
        "sources": list(set([s for s in step_results.keys() if 'spider' in s]))
    }
    
    print(f"合并后共 {len(unique)} 条数据", file=sys.stderr)
    return result

if __name__ == "__main__":
    data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    result = execute(data)
    print(json.dumps(result, ensure_ascii=False))
