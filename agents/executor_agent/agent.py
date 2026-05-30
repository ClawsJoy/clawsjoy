#!/usr/bin/env python3
"""Agent - Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import re
from typing import Dict, Any, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.skill_loader_v3 import skill_loader


class ExecutorAgent(SmartAgent):
    name = "executor_agent"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)

    def process(self, user_input: str, context=None) -> Dict:
        numbers = re.findall(r'\d+', user_input)
        if len(numbers) >= 2:
            a, b = int(numbers[0]), int(numbers[1])
            result = skill_loader.execute("add", {"a": a, "b": b})
            # 提取数字
            val = result.get('result', 0)
            if isinstance(val, dict):
                val = val.get('result', 0)
            return {
                "success": True,
                "response": str(val),      # 必须有 response 字段
                "result": val,
                "agent": self.name,
                "user_id": self.user_id
            }
        return {
            "success": False,
            "response": "无法解析，请提供如 15+27 格式",
            "agent": self.name,
            "user_id": self.user_id
        }


executor_agent = ExecutorAgent()
