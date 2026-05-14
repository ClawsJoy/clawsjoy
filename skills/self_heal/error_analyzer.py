"""错误分析器 - 让 LLM 分析新错误并生成修复方案"""
import requests
import json
import re
from lib.memory_simple import memory

class ErrorAnalyzerSkill:
    name = "error_analyzer"
    description = "分析新错误，生成修复方案"
    version = "1.0.0"
    category = "debug"

    def execute(self, params):
        error_msg = params.get("error", "")
        
        # 查询知识库
        from skills.error_knowledge_base import skill as kb
        existing = kb.find_fix(error_msg)
        if existing and existing.get('fix'):
            return {"known": True, "fix": existing['fix']}
        
        # 让 LLM 分析
        prompt = f"""分析以下错误，给出修复方案：

错误信息：{error_msg}

输出 JSON：
{{"error_type": "错误类型", "root_cause": "原因", "fix": "修复命令", "confidence": 0.0-1.0}}
"""
        try:
            resp = requests.post("http://127.0.0.1:11434/api/generate",
                                 json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
                                 timeout=60)
            raw = resp.json()["response"]
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                result = json.loads(match.group())
                # 存入知识库
                if result.get('fix'):
                    kb.add_knowledge(error_msg[:50], result['fix'], result.get('confidence', 0.7))
                    memory.remember(f"ai_learned|{error_msg[:50]}|fix:{result['fix']}", category="ai_learned")
                    return {"known": False, "fix": result['fix'], "source": "ai"}
        except:
            pass
        
        return {"known": False, "fix": None, "message": "无法分析"}

skill = ErrorAnalyzerSkill()
