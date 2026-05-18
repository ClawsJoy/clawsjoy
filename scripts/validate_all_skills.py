#!/usr/bin/env python3
"""逐个验证所有技能的语法和导入"""

import sys
import subprocess
from pathlib import Path

SKILLS_DIR = Path("/mnt/d/clawsjoy_clean/skills")

def check_syntax(file_path):
    """检查 Python 语法"""
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", str(file_path)],
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stderr

def check_import(file_path):
    """检查导入是否正常"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("temp_module", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("技能全面验证")
    print("=" * 60)
    
    results = []
    
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        
        script_file = skill_dir / "scripts" / "main.py"
        if script_file.exists():
            print(f"\n检查: {skill_dir.name}")
            
            # 语法检查
            syntax_ok, syntax_err = check_syntax(script_file)
            if syntax_ok:
                print(f"  ✅ 语法正确")
            else:
                print(f"  ❌ 语法错误: {syntax_err[:100]}")
            
            # 导入检查
            import_ok, import_err = check_import(script_file)
            if import_ok:
                print(f"  ✅ 导入正常")
            else:
                print(f"  ❌ 导入错误: {import_err[:100]}")
            
            results.append({
                "name": skill_dir.name,
                "syntax": syntax_ok,
                "import": import_ok
            })
        else:
            print(f"\n⚠️ {skill_dir.name}: 缺少 scripts/main.py")
            results.append({
                "name": skill_dir.name,
                "syntax": False,
                "import": False,
                "missing": True
            })
    
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    passed = sum(1 for r in results if r.get('syntax') and r.get('import'))
    total = len(results)
    
    print(f"总技能数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    
    if total - passed > 0:
        print("\n问题技能:")
        for r in results:
            if not (r.get('syntax') and r.get('import')):
                print(f"  ❌ {r['name']}")

if __name__ == "__main__":
    main()
