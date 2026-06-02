#!/usr/bin/env python3
"""Decision Engine - Decision Engine 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from core.v5.llm.client import llm


class DecisionEngine:
    """自主决策引擎"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.decision_history: List[Dict] = []
    
    def analyze(self, situation: str, context: Dict = None) -> Dict:
        """分析情况并做出决策"""

        prompt = f"""你是 {self.agent_name}，一个智能决策引擎。

当前情况: {situation}

上下文: {json.dumps(context or {}, ensure_ascii=False)}

请分析并返回JSON格式的决策：
{{
    "analysis": "情况分析",
    "options": ["方案1", "方案2", "方案3"],
    "recommended": "推荐方案",
    "reason": "推荐理由",
    "confidence": 0.0-1.0,
    "risk": "高/中/低",
    "next_actions": ["步骤1", "步骤2"]
}}"""

        response = llm.generate(prompt, model_type="decision", temperature=0.3)

        # 尝试解析JSON
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group())
            else:
                decision = {"analysis": response, "confidence": 0.5}
        except:
            decision = {"analysis": response, "confidence": 0.5}

        decision["timestamp"] = datetime.now().isoformat()
        self.decision_history.append(decision)

        return decision
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取决策历史"""
        return self.decision_history[-limit:]


class TaskPlanner:
    """任务规划器"""
    
    def __init__(self):
        self.plans: Dict[str, Dict] = {}
    
    def create_plan(self, goal: str, steps: List[str]) -> str:
        """创建计划"""
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.plans[plan_id] = {
            "goal": goal,
            "steps": steps,
            "current_step": 0,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        return plan_id
    
    def execute_step(self, plan_id: str) -> Optional[str]:
        """执行计划步骤"""
        plan = self.plans.get(plan_id)
        if not plan or plan["status"] != "pending":
            return None

        if plan["current_step"] >= len(plan["steps"]):
            plan["status"] = "completed"
            return None

        step = plan["steps"][plan["current_step"]]
        plan["current_step"] += 1

        return step
    
    def get_plan_status(self, plan_id: str) -> Dict:
        """获取计划状态"""
        return self.plans.get(plan_id, {})
