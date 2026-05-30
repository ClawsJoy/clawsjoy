#!/usr/bin/env python3
"""Decision Agent - Decision Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from typing import Dict
from core.agents.base.smart_agent import SmartAgent


class DecisionAgent(SmartAgent):
    name = "decision_agent"
    description = "决策学习内容"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print("🎖️ 决策师 已上岗")

    def decide_what_to_learn(self, analysis: Dict) -> Dict:
        """决定学习什么"""
        if not analysis.get("has_unknown"):
            return {"need_learn": False, "tasks": []}
        
        tasks = []
        for suggestion in analysis.get("suggestions", []):
            tasks.append({
                "action": "learn",
                "question": suggestion["question"],
                "priority": suggestion["priority"],
                "source": "auto_analysis"
            })
        
        return {
            "need_learn": len(tasks) > 0,
            "tasks": tasks,
            "message": f"需要学习 {len(tasks)} 个新问题"
        }
    
    def process(self, user_input: str, context=None) -> Dict:
        return self.decide_what_to_learn(user_input if isinstance(user_input, dict) else {})
