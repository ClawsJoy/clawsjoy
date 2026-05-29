import logging

"""决策师 Agent - LLM 驱动的智能决策"""

import json
import re
from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.workspace_manager import workspace_manager
from core.lib.smart_adapter import smart_adapter


class DecisionAgent(SmartAgent):
    name = "decision_agent"
    description = "智能决策与建议"
    type = "core"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.behavior = workspace_manager.get_behavior_config("decision_agent")
        print(f"🎖️ 决策师 已上岗")

    def process(self, user_input: str, context=None) -> Dict:
        print(f"[决策师] 收到: {user_input}")

        routing = self.behavior.get('routing', {}) if self.behavior else {}
        rules = routing.get('rules', [])
        default_response = routing.get('default_response', "我可以帮您分析问题和提供建议。")

        # 1. 先尝试规则匹配（快速路径）
        for rule in rules:
            for pattern in rule.get('patterns', []):
                if pattern in user_input:
                    action = rule.get('action', 'respond')
                    if action == 'delegate':
                        target = rule.get('target')
                        if target:
                            return self._delegate(target, user_input)
                    else:  # respond
                        response = rule.get('response', default_response)
                        return {"success": True, "response": response, "agent": self.name, "user_id": self.user_id}

        # 2. 规则不匹配，使用 LLM 决策
        prompt = f"""你是决策师。用户输入: "{user_input}"

请返回 JSON，只输出 JSON，不要有其他内容:
{{
    "action": "delegate",
    "target": "executor_agent"
}}
或
{{
    "action": "respond", 
    "response": "回复内容"
}}"""

        try:
            llm_response = smart_adapter.generate(prompt, auto_select=True)
            print(f"[决策师] LLM: {llm_response[:100]}")

            # 提取 JSON
            match = re.search(r'\{[^{}]*\}', llm_response)
            if match:
                result = json.loads(match.group())
                if result.get('action') == 'delegate':
                    target = result.get('target', 'executor_agent')
                    return self._delegate(target, user_input)
                else:
                    response = result.get('response', default_response)
                    return {"success": True, "response": response, "agent": self.name, "user_id": self.user_id}
        except Exception as e:
            print(f"[决策师] LLM 解析失败: {e}")

        return {"success": True, "response": default_response, "agent": self.name, "user_id": self.user_id}

    def _delegate(self, target: str, message: str) -> Dict:
        """委托任务"""
        print(f"[决策师] 委托给: {target}")
        result = self.http_call(target, message)
        return result


    def decide(self, context: dict, options: list = None) -> dict:
        """做出决策"""
        return {
            "decision": options[0] if options else "default",
            "confidence": 0.8,
            "reasoning": "基于当前上下文"
        }

    def evaluate(self, decision: dict) -> dict:
        """评估决策结果"""
        return {
            "decision": decision,
            "score": 0.75,
            "feedback": "决策合理"
        }

    def get_decision(self, decision_id: str = None) -> dict:
        """获取决策历史"""
        return {
            "decision_id": decision_id or "latest",
            "result": "success"
        }

    def set_criteria(self, criteria: dict) -> bool:
        """设置决策标准"""
        self._criteria = criteria
        return True

decision_agent = DecisionAgent()
