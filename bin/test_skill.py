#!/usr/bin/env python3
"""统一测试技能"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
import importlib

def test_skill(skill_name, params):
    """通用技能测试"""
    try:
        module = importlib.import_module(f"skills.{skill_name}")
        if hasattr(module, 'skill'):
            result = module.skill.execute(params)
            print(f"结果: {result}")
        elif hasattr(module, skill_name.capitalize()):
            SkillClass = getattr(module, skill_name.capitalize())
            skill = SkillClass()
            result = skill.execute(params)
            print(f"结果: {result}")
        else:
            print(f"无法找到技能接口")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: test_skill.py <技能名> <参数JSON>")
        sys.exit(1)
    
    import json
    skill_name = sys.argv[1]
    params = json.loads(sys.argv[2])
    test_skill(skill_name, params)
