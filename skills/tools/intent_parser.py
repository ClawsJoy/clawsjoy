"""意图解析器 - 模糊诉求转具体标准（基于记忆+公式）"""
import requests
import json
import re
from lib.memory_simple import memory

class IntentParserSkill:
    name = "intent_parser"
    description = "解析用户意图，生成具体任务标准"
    version = "1.0.0"
    category = "analysis"

    # 视频参数换算公式
    FORMULA = {
        "duration_per_100_words": 30,  # 100字约30秒
        "min_duration": 20,
        "max_duration": 180,
        "min_words": 60,
        "max_words": 600
    }

    def execute(self, params):
        user_input = params.get("input", "")
        
        # 1. 查询历史相似任务的成功经验
        similar = memory.recall(user_input, category="task_success_reference")
        
        # 2. 从输入中提取关键信息
        # 提取时长（如果用户说了"3分钟"等）
        import re
        duration_match = re.search(r'(\d+)\s*分', user_input)
        if duration_match:
            default_duration = int(duration_match.group(1)) * 60
        else:
            # 默认使用历史经验或公式
            if similar:
                # 从历史成功经验中提取时长
                import ast
                try:
                    last_success = similar[0]
                    duration_match = re.search(r'时长:(\d+\.?\d*)', last_success)
                    default_duration = float(duration_match.group(1)) if duration_match else 60
                except:
                    default_duration = 60
            else:
                default_duration = 60
        
        # 3. 根据公式计算字数
        default_words = int(default_duration / self.FORMULA["duration_per_100_words"] * 100)
        default_words = max(self.FORMULA["min_words"], min(self.FORMULA["max_words"], default_words))
        
        prompt = f"""用户诉求：「{user_input}」

历史相似诉求成功经验：{similar[0][:300] if similar else "无"}

推断参数：
- 时长: {default_duration}秒
- 字数: {default_words}字

请确认或调整，输出JSON：
{{
    "topic": "提取的主题",
    "target": {{
        "duration": {default_duration},
        "script_length": {default_words},
        "scene_count": 3
    }},
    "keywords": ["关键词"],
    "quality_threshold": 70
}}
"""
        resp = requests.post("http://127.0.0.1:11434/api/generate",
                             json={"model": "qwen2.5:7b", "prompt": prompt, 
                                   "stream": False, "temperature": 0.7})
        raw = resp.json()["response"]
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        
        # 降级：使用公式默认值
        return {
            "topic": user_input[:50],
            "target": {
                "duration": default_duration,
                "script_length": default_words,
                "scene_count": 3
            },
            "keywords": [],
            "quality_threshold": 60
        }

skill = IntentParserSkill()
