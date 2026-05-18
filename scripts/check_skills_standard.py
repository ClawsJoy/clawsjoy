#!/usr/bin/env python3
"""检查原子技能是否符标准"""

import json
import inspect
from pathlib import Path
from typing import Dict, List

SKILLS_DIR = Path("/mnt/d/clawsjoy_clean/skills")
REQUIRED_KEYS = ['name', 'version', 'description', 'execute']

def check_skill(skill_path: Path) -> Dict:
    """检查单个技能"""
    result = {
        "name": skill_path.stem,
        "status": "unknown",
        "issues": []
    }
    
    try:
        # 尝试导入
        import importlib.util
        spec = importlib.util.spec_from_file_location(skill_path.stem, skill_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 检查是否有 execute 函数
        if hasattr(module, 'execute'):
            result["status"] = "pass"
            result["has_execute"] = True
        else:
            result["status"] = "fail"
            result["issues"].append("缺少 execute 函数")
        
        # 检查是否有技能信息
        if hasattr(module, 'skill_info'):
            info = module.skill_info
            missing = [k for k in REQUIRED_KEYS if k not in info]
            if missing:
                result["issues"].append(f"缺少技能信息字段: {missing}")
        
    except Exception as e:
        result["status"] = "error"
        result["issues"].append(str(e)[:100])
    
    return result

def main():
    print("=" * 60)
    print("原子技能标准化检查")
    print("=" * 60)
    
    skills = list(SKILLS_DIR.glob("*.py"))
    results = []
    
    for skill_path in skills:
        if skill_path.name.startswith('__'):
            continue
        result = check_skill(skill_path)
        results.append(result)
    
    print(f"\n📊 检查结果:")
    print(f"   总技能数: {len(results)}")
    print(f"   通过: {sum(1 for r in results if r['status'] == 'pass')}")
    print(f"   失败: {sum(1 for r in results if r['status'] == 'fail')}")
    print(f"   错误: {sum(1 for r in results if r['status'] == 'error')}")
    
    # 显示问题技能
    failed = [r for r in results if r['status'] != 'pass']
    if failed:
        print(f"\n⚠️ 问题技能 ({len(failed)}):")
        for f in failed[:10]:
            print(f"   - {f['name']}: {', '.join(f['issues'])}")
    
    return 0 if len(failed) < 5 else 1

if __name__ == "__main__":
    exit(main())
