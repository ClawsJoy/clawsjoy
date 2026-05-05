#!/usr/bin/env python3
"""ClawsJoy Skill 执行器 - 增强错误处理版"""

import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime

SKILLS_DIR = Path("/home/flybo/clawsjoy/skills")
LOG_FILE = Path("/home/flybo/clawsjoy/logs/skill.log")


def log_execution(skill_name, params, result, error=None):
    """记录执行日志"""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(
            json.dumps(
                {
                    "timestamp": datetime.now().isoformat(),
                    "skill": skill_name,
                    "params": params,
                    "result": result if result else None,
                    "error": error,
                },
                ensure_ascii=False,
            )
            + "\n"
        )


def execute_skill(skill_name, params, tenant_id="1"):
    """执行 Skill - 带错误处理"""
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.exists():
        return {"error": f"Skill '{skill_name}' not found"}

    exec_file = skill_dir / "execute.py"
    if not exec_file.exists():
        return {"error": f"Skill '{skill_name}' has no execute.py"}

    try:
        spec = importlib.util.spec_from_file_location(f"{skill_name}_exec", exec_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 注入 tenant_id
        if "tenant_id" not in params:
            params["tenant_id"] = tenant_id

        result = module.execute(params)
        log_execution(skill_name, params, result)
        return result

    except Exception as e:
        log_execution(skill_name, params, None, str(e))
        return {
            "success": False,
            "error": str(e),
            "skill": skill_name,
            "fallback": True,
        }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python skill_runner.py <skill_name> '<json_params>'")
        print('示例: python skill_runner.py auth \'{"action":"health"}\'')
        sys.exit(1)

    skill = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    tenant_id = params.get("tenant_id", "1")

    result = execute_skill(skill, params, tenant_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))
