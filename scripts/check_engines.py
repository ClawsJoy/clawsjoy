#!/usr/bin/env python3
"""引擎规范检查器"""

import sys
from pathlib import Path

def check_engine(engine_path: Path) -> dict:
    """检查单个引擎是否符合规范"""
    core_file = engine_path / "core.py"
    if not core_file.exists():
        return {"name": engine_path.name, "status": "missing", "errors": ["core.py not found"]}
    
    content = core_file.read_text()
    errors = []
    warnings = []
    
    # 检查必需方法
    required_methods = ['def process', 'def get_stats']
    optional_methods = ['def reload', 'def health_check']
    
    for method in required_methods:
        if method not in content:
            errors.append(f"Missing {method}")
    
    for method in optional_methods:
        if method not in content:
            warnings.append(f"Missing {method} (optional)")
    
    # 检查类定义
    if 'class' not in content:
        warnings.append("No class definition found")
    
    # 检查实例化
    if '_engine' not in content and 'engine' not in content:
        warnings.append("No engine instance found")
    
    return {
        "name": engine_path.name,
        "status": "ok" if not errors else "error",
        "errors": errors,
        "warnings": warnings
    }

def main():
    engine_dir = Path("engine")
    print("="*60)
    print("引擎规范检查报告")
    print("="*60)
    
    results = []
    for subdir in engine_dir.iterdir():
        if subdir.is_dir() and not subdir.name.startswith('_'):
            if subdir.name in ['base', 'lib', 'events', 'generator', 'workflows']:
                continue
            result = check_engine(subdir)
            results.append(result)
    
    errors = [r for r in results if r['status'] == 'error']
    ok = [r for r in results if r['status'] == 'ok']
    
    print(f"\n总计: {len(results)} 个引擎")
    print(f"  ✅ 通过: {len(ok)}")
    print(f"  ❌ 错误: {len(errors)}")
    
    for r in errors:
        print(f"\n❌ {r['name']}:")
        for e in r['errors']:
            print(f"     - {e}")
    
    for r in results:
        if r.get('warnings', []):
            print(f"\n⚠️ {r['name']}:")
            for w in r['warnings']:
                print(f"     - {w}")
    
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main())
