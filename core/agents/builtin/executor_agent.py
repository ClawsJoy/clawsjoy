#!/usr/bin/env python3
"""Executor Agent - Executor Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.smart_adapter import smart_adapter


class ExecutorAgent(SmartAgent):
    name = "executor_agent"
    description = "任务执行器"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_agent_config()
        print("⚡ ExecutorAgent 初始化完成")

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        print(f"[执行器] 收到: {user_input}")
        
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
