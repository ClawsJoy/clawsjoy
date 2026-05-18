from lib.smart_config import smart_config
"""LLM 学习器 - 自动识别组合模式"""
import re
import json
import requests
from src.config.settings import settings
from src.lib.memory_brain import memory_brain

class LLMLearner:
    """LLM 学习器 - 分析用户意图，自动生成组合"""
    
    def __init__(self):
        self.ollama_url = settings.get_ollama_url()
        self.model = settings.DEFAULT_MODEL
    
    def analyze(self, user_input):
        """分析用户意图，返回执行计划"""
        # 先查记忆
        cached_plan = memory_brain.find_match(user_input)
        if cached_plan:
            return cached_plan
        
        # LLM 分析
        return self._llm_analyze(user_input)
    
    def _llm_analyze(self, user_input):
        """使用 LLM 分析并生成计划"""
        # 获取可用技能
        from src.api.gateway import _skills
        skills_desc = "\n".join([f"- {name}: {getattr(skill, 'description', name)}" 
                                  for name, skill in list(_skills.items())[:30]])
        
        prompt = f"""分析用户需求，生成执行计划。

用户: "{user_input}"

可用技能:
{skills_desc}

输出格式（只输出 JSON）:
{{"steps": [
    {{"skill": "技能名", "params": {{"参数": "值"}}}}
]}}

示例1: "把hello转成大写" -> {{"steps": [{{"skill": "to_upper", "params": {{"text": "hello"}}}}]}}
示例2: "把world转成大写然后反转" -> {{"steps": [
    {{"skill": "to_upper", "params": {{"text": "world"}}}},
    {{"skill": "reverse", "params": {{"text": "{{result}}"}}}}
]}}

只输出 JSON，不要解释。"""
        
        try:
            resp = requests.post(self.ollama_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3}
            }, timeout=60)
            response = resp.json().get("response", "")
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            print(f"LLM 分析失败: {e}")
        
        return {"steps": []}
    
    def learn_from_result(self, user_input, plan, result):
        """从执行结果中学习"""
        if result.get("success"):
            memory_brain.record_success(user_input, plan, result)

llm_learner = LLMLearner()
