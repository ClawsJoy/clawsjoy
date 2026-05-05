#!/usr/bin/env python3
"""ClawsJoy Skill 执行器"""

import sys
import json
import importlib.util
from pathlib import Path

SKILLS_DIR = Path("/home/flybo/clawsjoy/skills")


def list_skills():
    skills = []
    for d in SKILLS_DIR.iterdir():
        if d.is_dir() and (d / "execute.py").exists():
            skills.append(d.name)
    return skills


def execute_skill(skill_name, params):
    exec_file = SKILLS_DIR / skill_name / "execute.py"
    if not exec_file.exists():
        return {"error": f"Skill '{skill_name}' not found"}

    spec = importlib.util.spec_from_file_location(f"{skill_name}_exec", exec_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.execute(params)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python skill.py <skill_name> '<json_params>'")
        sys.exit(1)

    skill = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    result = execute_skill(skill, params)
    print(json.dumps(result, indent=2))
