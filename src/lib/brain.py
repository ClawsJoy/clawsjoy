#!/usr/bin/env python3
"""Brain - Brain 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

"""智能大脑 - 集成记忆、LLM学习、工作流编排"""
import re

from src.lib.llm_learner import llm_learner
from src.lib.memory_brain import memory_brain
from src.lib.workflow_orchestrator import orchestrator


class SmartBrain:
    def __init__(self):
        self.ollama_url = (
            f"http://{smart_config.HOST}:{smart_config.get_port("ollama")}/api/generate"
        )

    def process(self, user_input):
        # 1. 快速规则匹配（数学）
        math_result = self._try_math(user_input)
        if math_result:
            return {"method": "math", "result": math_result}

        # 2. 简单技能（单步）
        simple = self._try_simple(user_input)
        if simple:
            return simple

        # 3. 特殊处理：遮天风格剧本
        if "遮天" in user_input or "叶凡" in user_input:
            return self._handle_zhetian(user_input)

        # 4. 智能规划
        plan = llm_learner.analyze(user_input)
        if plan.get("steps"):
            result = orchestrator.execute_plan(plan)
            if result.get("success"):
                llm_learner.learn_from_result(user_input, plan, result)
            return {"method": "smart", "plan": plan, "result": result}

        return {
            "method": "unknown",
            "result": {"success": False, "message": "无法处理"},
        }

    def _handle_zhetian(self, user_input):
        """处理遮天风格请求"""
        from src.skills.atomic.text.zhetian_script import skill as zhetian_script

        # 提取场景和角色
        scene = "opening"
        if "九龙拉棺" in user_input:
            scene = "opening"
        elif "荒古禁地" in user_input:
            scene = "training_ground"

        character = "male_lead"
        if "叶凡" in user_input:
            character = "male_lead"
        elif "狠人" in user_input:
            character = "mysterious_female"

        result = zhetian_script.execute({"scene": scene, "character": character})

        return {"method": "zhetian", "result": result}

    def _try_math(self, text):
        patterns = [
            (r"(\d+)\s*[+\+]\s*(\d+)", lambda a, b: a + b),
            (r"(\d+)\s*[*×]\s*(\d+)", lambda a, b: a * b),
        ]
        for pattern, func in patterns:
            m = re.search(pattern, text)
            if m:
                a, b = int(m.group(1)), int(m.group(2))
                return {"expression": f"{a} + {b}", "result": func(a, b)}
        return None

    def _try_simple(self, text):
        if "大写" in text and "然后" not in text:
            m = re.search(r"把(.+?)转成大写", text)
            if m:
                from src.skills.atomic.text.to_upper import skill as to_upper

                res = to_upper.execute({"text": m.group(1)})
                return {"method": "simple", "skill": "to_upper", "result": res}
        return None


brain = SmartBrain()
