"""Prompt优化器 - 系统自己优化prompt"""
import requests
import json
import re
from lib.memory_simple import memory

class PromptOptimizerSkill:
    name = "prompt_optimizer"
    description = "自动优化prompt"
    version = "1.0.0"
    category = "optimization"

    def execute(self, params):
        skill_name = params.get("skill_name", "")
        current_prompt = params.get("current_prompt", "")
        feedback = params.get("feedback", "")
        
        # 让LLM分析并优化
        prompt = f"""当前技能「{skill_name}」的prompt:
{current_prompt}

用户反馈问题:
{feedback}

请输出优化后的prompt，保持原有功能，解决反馈问题。

输出JSON: {{"optimized_prompt": "新的prompt内容"}}
"""
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                             json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False})
        raw = resp.json()["response"]
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
                # 记录到记忆
                memory.remember(
                    f"prompt优化|{skill_name}|原prompt:{current_prompt[:50]}|新prompt:{result['optimized_prompt'][:50]}",
                    category="prompt_history"
                )
                return result
            except:
                pass
        
        return {"optimized_prompt": current_prompt}

skill = PromptOptimizerSkill()
