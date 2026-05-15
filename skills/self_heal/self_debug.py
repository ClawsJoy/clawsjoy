"""自调试 - 系统自己分析错误"""
import subprocess
import requests
import json
import re

class SelfDebugSkill:
    name = "self_debug"
    description = "系统自调试"
    version = "1.0.0"
    category = "debug"

    def execute(self, params):
        log_file = params.get("log_file", "logs/gateway.log")
        
        # 读取最近日志
        result = subprocess.run(['tail', '-100', log_file], capture_output=True, text=True)
        logs = result.stdout
        
        # 提取错误
        errors = []
        for line in logs.split('\n'):
            if 'ERROR' in line or 'Exception' in line or 'Traceback' in line or 'failed' in line.lower():
                errors.append(line)
        
        if not errors:
            # 检查执行结果
            return {"has_error": False, "message": "未发现错误"}
        
        # 让LLM分析
        prompt = f"""分析以下错误日志，找出问题原因和解决方案：

{chr(10).join(errors[-10:])}

输出JSON:
{{
    "error_type": "错误类型",
    "root_cause": "根本原因", 
    "suggested_fix": "修复方案",
    "affected_file": "相关文件"
}}
"""
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                             json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False})
        raw = resp.json()["response"]
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        
        return {"has_error": True, "errors": errors[-5:], "analysis": raw}

skill = SelfDebugSkill()
