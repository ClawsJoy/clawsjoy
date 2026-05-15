"""任务优化器 - 动态标准 + 闭环优化"""
import requests
import json
import re
from lib.memory_simple import memory

class TaskOptimizerSkill:
    name = "task_optimizer"
    description = "动态生成标准，闭环优化"
    version = "1.0.0"
    category = "optimization"

    def execute(self, params):
        task = params.get("task", "")
        previous_result = params.get("previous_result", None)
        
        # 1. 动态生成任务标准
        if previous_result:
            # 有历史结果，生成改进方案
            prompt = f"""任务：{task}

上次执行结果：
- 时长: {previous_result.get('duration', 0)}秒 (目标未定)
- 脚本长度: {previous_result.get('script_length', 0)}字
- 关键词匹配: {previous_result.get('keyword_match', 0)}%
- 问题: {previous_result.get('issues', [])}

请分析并提出改进方案，输出JSON：
{{
    "target": {{
        "duration": 目标秒数,
        "script_length": 目标字数,
        "keyword_match_rate": 目标百分比
    }},
    "improvements": ["改进点1", "改进点2"],
    "adjusted_prompt": "调整后的生成提示词"
}}
"""
        else:
            # 首次执行，生成初始标准
            prompt = f"""为任务「{task}」生成合理的执行标准。

输出JSON：
{{
    "target": {{
        "duration": 目标秒数,
        "script_length": 目标字数,
        "keyword_match_rate": 目标百分比
    }},
    "key_points": ["关键内容1", "关键内容2"],
    "generation_prompt": "用于生成内容的提示词"
}}
"""
        
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                             json={"model": "qwen2.5:7b", "prompt": prompt, 
                                   "stream": False, "temperature": 0.7})
        raw = resp.json()["response"]
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"error": "解析失败"}

skill = TaskOptimizerSkill()
