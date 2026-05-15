import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
import requests
import json
import re
from pathlib import Path
from lib.skill_validator import SkillValidator
from lib.memory_simple import memory

class SkillGeneratorV2Skill:
    name = "skill_generator_v2"
    description = "安全地生成新原子技能"
    version = "1.0.0"
    category = "generation"

    def execute(self, params):
        requirement = params.get("requirement", "")
        auto_approve = params.get("auto_approve", False)
        
        if not requirement:
            return {"success": False, "error": "需要提供需求描述"}
        
        # 1. LLM 生成代码
        prompt = f"""生成一个 Python 函数实现：{requirement}

要求：
- 只使用标准库或 PIL
- 函数名: execute
- 参数: params (dict)
- 返回: dict
- 不要做任何危险操作

只输出代码：
"""
        try:
            resp = requests.post("http://127.0.0.1:11434/api/generate",
                                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                                timeout=90)
            code = resp.json()["response"]
        except Exception as e:
            return {"success": False, "error": f"LLM 错误: {e}"}
        
        # 提取代码
        match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if match:
            code = match.group(1)
        
        # 2. 安全验证
        validation = SkillValidator.validate(code)
        
        if not validation["safe"]:
            return {
                "success": False,
                "error": "安全验证失败",
                "issues": validation["issues"],
                "suggestions": SkillValidator.suggest_fix(code, validation["issues"]),
                "code_preview": code[:300]
            }
        
        # 3. 保存待审核
        skill_name = f"req_{requirement[:20].replace(' ', '_')}"
        skill_path = Path(f"skills/pending_{skill_name}.py")
        skill_path.write_text(code, encoding='utf-8')
        
        # 4. 记录到记忆
        memory.remember(
            f"pending_skill|{skill_name}|需求:{requirement[:50]}|验证通过",
            category="pending_skills"
        )
        
        return {
            "success": True,
            "skill_name": skill_name,
            "file": str(skill_path),
            "status": "pending_review",
            "message": "技能已生成，等待人工审核后注册",
            "code_preview": code[:300]
        }

skill = SkillGeneratorV2Skill()
