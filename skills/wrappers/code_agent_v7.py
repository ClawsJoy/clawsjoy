import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
import requests
import re

class CodeAgentV7Skill:
    name = "code_agent_v7"
    description = "生成代码（不自动保存）"
    version = "7.0.0"
    category = "code"

    def execute(self, params):
        requirement = params.get("requirement", "")
        
        prompt = f"生成 Python 代码: {requirement}. 只输出代码。"
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                            json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                            timeout=90)
        code = resp.json()["response"]
        
        match = re.search(r'```python\n(.*?)\n```', code, re.DOTALL)
        if match:
            code = match.group(1)
        
        return {"success": True, "code": code, "requirement": requirement}

skill = CodeAgentV7Skill()
