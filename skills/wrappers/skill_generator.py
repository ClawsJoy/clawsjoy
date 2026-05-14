import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
import requests
import json
import re
from pathlib import Path
from lib.data_contract import DataContract

class SkillGeneratorSkill:
    name = "skill_generator"
    description = "根据需求生成新的原子技能"
    version = "1.0.0"
    category = "generation"

    def execute(self, params):
        requirement = params.get("requirement", "")
        if not requirement:
            return {"success": False, "error": "需要提供需求描述"}
        
        # 简化的 prompt，要求输出安全代码
        prompt = f"""生成一个简单的 Python 函数来实现：{requirement}

要求：
- 只使用 PIL (Pillow) 库
- 不要使用 os, subprocess, eval, exec
- 代码要短小精悍

只输出代码，不要解释。
"""
        try:
            resp = requests.post("http://127.0.0.1:11434/api/generate",
                                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                                timeout=120)  # 增加超时
            code = resp.json()["response"]
        except Exception as e:
            return {"success": False, "error": f"LLM 超时: {e}"}
        
        # 提取代码
        match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if match:
            code = match.group(1)
        
        # 安全检查
        dangerous = ['os.system', 'subprocess', 'eval', 'exec', '__import__', 'open(']
        if any(d in code for d in dangerous):
            return {"success": False, "error": "代码包含危险操作", "code_preview": code[:200]}
        
        # 保存
        skill_name = f"auto_{requirement[:15].replace(' ', '_')}"
        skill_path = Path(f"skills/generated_{skill_name}.py")
        skill_path.write_text(code, encoding='utf-8')
        
        return {
            "success": True,
            "skill_name": skill_name,
            "file": str(skill_path)
        }

skill = SkillGeneratorSkill()
