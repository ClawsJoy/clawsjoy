#!/usr/bin/env python3
"""Decision Agent - 决策师"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter


class DecisionAgent(SmartAgent):
    name = "decision_agent"
    description = "决策师，负责方案评估和决策"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_agent_config()
        print("🎯 决策师 已上岗")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[决策师] 收到: {user_input}")

        result = smart_adapter.generate(
            user_input,
            model=self.llm_model,
            temperature=self.llm_temperature
        )

        return {
            "success": True,
            "response": result,
            "agent": self.name,
            "user_id": self.user_id
        }
